"""
CSV processing utilities for PySpark incremental file ingestion.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    DecimalType, TimestampType, BooleanType
)
from pyspark.sql.functions import (
    col, lit, current_timestamp, input_file_name,
    regexp_replace, trim, upper, when, isnan, isnull,
    md5, concat_ws, monotonically_increasing_id
)
import uuid

logger = logging.getLogger(__name__)


class CSVSchemaManager:
    """Manages CSV schemas and validation for shipments data."""
    
    @staticmethod
    def get_shipments_schema() -> StructType:
        """
        Get the expected schema for shipments CSV files.
        
        Returns:
            StructType schema for shipments data
        """
        return StructType([
            # Required fields
            StructField("shipment_id", StringType(), False),
            StructField("order_id", StringType(), False),
            
            # Optional tracking fields
            StructField("tracking_number", StringType(), True),
            StructField("carrier", StringType(), True),
            StructField("shipping_method", StringType(), True),
            
            # Status and dates
            StructField("shipment_status", StringType(), True),
            StructField("shipped_date", StringType(), True),  # Will be converted to timestamp
            StructField("estimated_delivery_date", StringType(), True),
            StructField("actual_delivery_date", StringType(), True),
            
            # Package details
            StructField("package_count", StringType(), True),
            StructField("total_weight", StringType(), True),
            StructField("weight_unit", StringType(), True),
            StructField("length", StringType(), True),
            StructField("width", StringType(), True),
            StructField("height", StringType(), True),
            StructField("dimension_unit", StringType(), True),
            
            # Financial
            StructField("shipping_cost", StringType(), True),
            StructField("insurance_cost", StringType(), True),
            StructField("currency", StringType(), True),
            
            # Address information (will be stored as JSON strings)
            StructField("origin_street", StringType(), True),
            StructField("origin_city", StringType(), True),
            StructField("origin_state", StringType(), True),
            StructField("origin_postal_code", StringType(), True),
            StructField("origin_country", StringType(), True),
            
            StructField("destination_street", StringType(), True),
            StructField("destination_city", StringType(), True),
            StructField("destination_state", StringType(), True),
            StructField("destination_postal_code", StringType(), True),
            StructField("destination_country", StringType(), True),
            
            # Delivery details
            StructField("delivery_instructions", StringType(), True),
            StructField("signature_required", StringType(), True),
            StructField("delivered_to", StringType(), True),
            StructField("delivery_notes", StringType(), True),
            
            # Return information
            StructField("is_return", StringType(), True),
            StructField("return_reason", StringType(), True),
            StructField("return_date", StringType(), True),
        ])
    
    @staticmethod
    def get_flexible_schema() -> StructType:
        """
        Get a flexible schema that can handle variations in CSV structure.
        All fields are strings to allow for flexible parsing.
        
        Returns:
            Flexible StructType schema
        """
        # Start with core required fields, rest will be inferred
        return StructType([
            StructField("shipment_id", StringType(), True),
            StructField("order_id", StringType(), True),
        ])


class CSVProcessor:
    """Handles CSV file processing and validation for PySpark."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.schema_manager = CSVSchemaManager()
    
    def read_csv_file(
        self,
        file_path: str,
        schema: Optional[StructType] = None,
        header: bool = True,
        infer_schema: bool = False,
        options: Optional[Dict[str, str]] = None
    ) -> DataFrame:
        """
        Read a CSV file into a Spark DataFrame.
        
        Args:
            file_path: Path to the CSV file
            schema: Optional schema to use
            header: Whether CSV has header row
            infer_schema: Whether to infer schema from data
            options: Additional CSV reading options
            
        Returns:
            Spark DataFrame
        """
        default_options = {
            "header": str(header).lower(),
            "inferSchema": str(infer_schema).lower(),
            "multiline": "true",
            "quote": '"',
            "escape": '"',
            "nullValue": "",
            "emptyValue": "",
            "timestampFormat": "yyyy-MM-dd HH:mm:ss",
            "dateFormat": "yyyy-MM-dd",
            "mode": "PERMISSIVE",  # Handle malformed records
            "columnNameOfCorruptRecord": "_corrupt_record"
        }
        
        if options:
            default_options.update(options)
        
        logger.info(f"Reading CSV file: {file_path}")
        
        try:
            reader = self.spark.read.options(**default_options)
            
            if schema:
                reader = reader.schema(schema)
            
            df = reader.csv(file_path)
            
            # Add metadata columns
            df = df.withColumn("source_file", input_file_name()) \
                   .withColumn("ingestion_timestamp", current_timestamp()) \
                   .withColumn("batch_id", lit(str(uuid.uuid4())))
            
            logger.info(f"Successfully read CSV file: {file_path} ({df.count()} rows)")
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise
    
    def read_csv_with_fallback(
        self,
        file_path: str,
        primary_schema: Optional[StructType] = None,
        fallback_to_flexible: bool = True
    ) -> Tuple[DataFrame, List[str]]:
        """
        Read CSV with fallback to flexible schema if primary schema fails.
        
        Args:
            file_path: Path to the CSV file
            primary_schema: Primary schema to try first
            fallback_to_flexible: Whether to fallback to flexible schema
            
        Returns:
            Tuple of (DataFrame, list of warnings)
        """
        warnings = []
        
        # Try with primary schema first
        if primary_schema:
            try:
                df = self.read_csv_file(file_path, schema=primary_schema)
                return df, warnings
            except Exception as e:
                warning_msg = f"Primary schema failed for {file_path}: {e}"
                warnings.append(warning_msg)
                logger.warning(warning_msg)
        
        # Fallback to flexible schema
        if fallback_to_flexible:
            try:
                # Use schema inference for maximum flexibility
                df = self.read_csv_file(
                    file_path, 
                    schema=None,
                    infer_schema=True,
                    options={"mode": "PERMISSIVE"}
                )
                
                warnings.append(f"Used flexible schema for {file_path}")
                return df, warnings
                
            except Exception as e:
                error_msg = f"Flexible schema also failed for {file_path}: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        
        raise Exception(f"All schema attempts failed for {file_path}")
    
    def validate_shipments_data(self, df: DataFrame) -> Tuple[DataFrame, Dict[str, Any]]:
        """
        Validate shipments data and return cleaned DataFrame with validation stats.
        
        Args:
            df: Raw DataFrame from CSV
            
        Returns:
            Tuple of (cleaned_df, validation_stats)
        """
        logger.info("Validating shipments data...")
        
        original_count = df.count()
        validation_stats = {
            'original_rows': original_count,
            'valid_rows': 0,
            'invalid_rows': 0,
            'validation_errors': []
        }
        
        # Check for required fields
        required_fields = ['shipment_id', 'order_id']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            error_msg = f"Missing required fields: {missing_fields}"
            validation_stats['validation_errors'].append(error_msg)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Clean and validate data
        cleaned_df = df
        
        # Clean string fields - trim whitespace and handle nulls
        string_columns = [field.name for field in df.schema.fields if isinstance(field.dataType, StringType)]
        for col_name in string_columns:
            if col_name in df.columns:
                cleaned_df = cleaned_df.withColumn(
                    col_name,
                    when(col(col_name).isNull() | (trim(col(col_name)) == ""), None)
                    .otherwise(trim(col(col_name)))
                )
        
        # Validate required fields are not null or empty
        for field in required_fields:
            if field in cleaned_df.columns:
                cleaned_df = cleaned_df.filter(
                    col(field).isNotNull() & (col(field) != "")
                )
        
        # Standardize boolean fields
        boolean_fields = ['signature_required', 'is_return']
        for field in boolean_fields:
            if field in cleaned_df.columns:
                cleaned_df = cleaned_df.withColumn(
                    field,
                    when(upper(col(field)).isin(['TRUE', 'YES', '1', 'Y']), 'true')
                    .when(upper(col(field)).isin(['FALSE', 'NO', '0', 'N']), 'false')
                    .otherwise(None)
                )
        
        # Standardize currency codes
        if 'currency' in cleaned_df.columns:
            cleaned_df = cleaned_df.withColumn(
                'currency',
                when(col('currency').isNotNull(), upper(trim(col('currency'))))
                .otherwise(None)
            )
        
        # Validate currency format (3 letters)
        if 'currency' in cleaned_df.columns:
            cleaned_df = cleaned_df.withColumn(
                'currency',
                when(
                    col('currency').isNotNull() & 
                    (col('currency').rlike('^[A-Z]{3}$')),
                    col('currency')
                ).otherwise(None)
            )
        
        # Clean numeric fields
        numeric_fields = ['package_count', 'total_weight', 'shipping_cost', 'insurance_cost']
        for field in numeric_fields:
            if field in cleaned_df.columns:
                cleaned_df = cleaned_df.withColumn(
                    field,
                    regexp_replace(col(field), '[^0-9.]', '')
                )
        
        # Add validation flags
        cleaned_df = cleaned_df.withColumn(
            'is_valid',
            when(
                col('shipment_id').isNotNull() & 
                col('order_id').isNotNull() &
                (col('shipment_id') != '') &
                (col('order_id') != ''),
                True
            ).otherwise(False)
        )
        
        # Count valid rows
        valid_count = cleaned_df.filter(col('is_valid') == True).count()
        invalid_count = original_count - valid_count
        
        validation_stats['valid_rows'] = valid_count
        validation_stats['invalid_rows'] = invalid_count
        validation_stats['validation_rate'] = valid_count / original_count if original_count > 0 else 0
        
        logger.info(
            f"Validation complete: {valid_count}/{original_count} valid rows "
            f"({validation_stats['validation_rate']:.2%})"
        )
        
        return cleaned_df, validation_stats
    
    def add_metadata_columns(
        self, 
        df: DataFrame, 
        file_path: str, 
        batch_id: str,
        source_system: str = "file_ingestion"
    ) -> DataFrame:
        """
        Add metadata columns required for raw_shipments table.
        
        Args:
            df: DataFrame to enhance
            file_path: Source file path
            batch_id: Batch ID for tracking
            source_system: Source system identifier
            
        Returns:
            DataFrame with metadata columns
        """
        # Extract filename from path
        filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
        
        # Add metadata columns
        enhanced_df = df \
            .withColumn('source_system', lit(source_system)) \
            .withColumn('source_file', lit(filename)) \
            .withColumn('batch_id', lit(batch_id)) \
            .withColumn('ingestion_timestamp', current_timestamp())
        
        # Add record hash for deduplication
        hash_columns = [col_name for col_name in df.columns if col_name not in ['_corrupt_record']]
        if hash_columns:
            enhanced_df = enhanced_df.withColumn(
                'record_hash',
                md5(concat_ws('|', *[col(c) for c in hash_columns]))
            )
        
        # Add unique row ID
        enhanced_df = enhanced_df.withColumn(
            'row_id',
            monotonically_increasing_id()
        )
        
        return enhanced_df
    
    def convert_to_target_schema(self, df: DataFrame) -> DataFrame:
        """
        Convert DataFrame to match raw_shipments table schema.
        
        Args:
            df: Source DataFrame
            
        Returns:
            DataFrame with target schema
        """
        logger.info("Converting to target schema...")
        
        # Create address JSON objects
        df_with_addresses = df
        
        # Origin address JSON
        origin_columns = ['origin_street', 'origin_city', 'origin_state', 'origin_postal_code', 'origin_country']
        origin_exists = any(col_name in df.columns for col_name in origin_columns)
        
        if origin_exists:
            # Build JSON string for origin address
            df_with_addresses = df_with_addresses.withColumn(
                'origin_address',
                when(
                    col('origin_street').isNotNull() | 
                    col('origin_city').isNotNull(),
                    concat_ws(
                        '',
                        lit('{"street":"'), col('origin_street'), lit('",'),
                        lit('"city":"'), col('origin_city'), lit('",'),
                        lit('"state":"'), col('origin_state'), lit('",'),
                        lit('"postal_code":"'), col('origin_postal_code'), lit('",'),
                        lit('"country":"'), col('origin_country'), lit('"}')
                    )
                ).otherwise(None)
            )
        else:
            df_with_addresses = df_with_addresses.withColumn('origin_address', lit(None))
        
        # Destination address JSON
        dest_columns = ['destination_street', 'destination_city', 'destination_state', 'destination_postal_code', 'destination_country']
        dest_exists = any(col_name in df.columns for col_name in dest_columns)
        
        if dest_exists:
            df_with_addresses = df_with_addresses.withColumn(
                'destination_address',
                when(
                    col('destination_street').isNotNull() | 
                    col('destination_city').isNotNull(),
                    concat_ws(
                        '',
                        lit('{"street":"'), col('destination_street'), lit('",'),
                        lit('"city":"'), col('destination_city'), lit('",'),
                        lit('"state":"'), col('destination_state'), lit('",'),
                        lit('"postal_code":"'), col('destination_postal_code'), lit('",'),
                        lit('"country":"'), col('destination_country'), lit('"}')
                    )
                ).otherwise(None)
            )
        else:
            df_with_addresses = df_with_addresses.withColumn('destination_address', lit(None))
        
        # Dimensions JSON
        if any(col_name in df.columns for col_name in ['length', 'width', 'height']):
            df_with_addresses = df_with_addresses.withColumn(
                'dimensions',
                when(
                    col('length').isNotNull() | 
                    col('width').isNotNull() | 
                    col('height').isNotNull(),
                    concat_ws(
                        '',
                        lit('{"length":'), col('length'), lit(','),
                        lit('"width":'), col('width'), lit(','),
                        lit('"height":'), col('height'), lit(','),
                        lit('"unit":"'), col('dimension_unit'), lit('"}')
                    )
                ).otherwise(None)
            )
        else:
            df_with_addresses = df_with_addresses.withColumn('dimensions', lit(None))
        
        # Map columns to target schema
        target_df = df_with_addresses.select(
            # Required fields
            col('shipment_id'),
            col('order_id'),
            
            # Optional fields with defaults
            col('tracking_number'),
            col('carrier'),
            col('shipping_method'),
            col('shipment_status'),
            col('shipped_date'),
            col('estimated_delivery_date'),
            col('actual_delivery_date'),
            
            # Address JSON fields
            col('origin_address'),
            col('destination_address'),
            
            # Package details
            col('package_count'),
            col('total_weight'),
            when(col('weight_unit').isNotNull(), col('weight_unit')).otherwise(lit('kg')).alias('weight_unit'),
            col('dimensions'),
            
            # Costs
            col('shipping_cost'),
            col('insurance_cost'),
            col('currency'),
            
            # Delivery details
            col('delivery_instructions'),
            when(col('signature_required') == 'true', True).otherwise(False).alias('signature_required'),
            col('delivered_to'),
            col('delivery_notes'),
            
            # Return information
            when(col('is_return') == 'true', True).otherwise(False).alias('is_return'),
            col('return_reason'),
            col('return_date'),
            
            # Metadata
            col('source_system'),
            col('source_file'),
            col('ingestion_timestamp'),
            col('batch_id'),
            col('record_hash'),
            
            # Data quality
            when(col('is_valid').isNotNull(), col('is_valid')).otherwise(True).alias('is_valid'),
            lit(None).alias('validation_errors')
        )
        
        logger.info("Schema conversion completed")
        return target_df
    
    def get_processing_summary(
        self,
        original_count: int,
        processed_count: int,
        validation_stats: Dict[str, Any],
        file_path: str
    ) -> Dict[str, Any]:
        """
        Generate processing summary for a file.
        
        Args:
            original_count: Original row count
            processed_count: Final processed row count
            validation_stats: Validation statistics
            file_path: Source file path
            
        Returns:
            Processing summary dictionary
        """
        return {
            'file_path': file_path,
            'original_rows': original_count,
            'processed_rows': processed_count,
            'valid_rows': validation_stats.get('valid_rows', 0),
            'invalid_rows': validation_stats.get('invalid_rows', 0),
            'validation_rate': validation_stats.get('validation_rate', 0.0),
            'processing_rate': processed_count / original_count if original_count > 0 else 0.0,
            'validation_errors': validation_stats.get('validation_errors', [])
        }
