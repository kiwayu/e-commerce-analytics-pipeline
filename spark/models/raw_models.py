"""
SQLAlchemy models for raw data tables.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class RawOrders(Base):
    """SQLAlchemy model for raw.raw_orders table."""
    
    __tablename__ = 'raw_orders'
    __table_args__ = {'schema': 'raw'}
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=text('uuid_generate_v4()')
    )
    
    # Business fields
    order_id = Column(String(100), nullable=False, index=True)
    customer_id = Column(String(100), index=True)
    order_date = Column(DateTime(timezone=True))
    order_status = Column(String(50))
    total_amount = Column(String(20))  # Store as string initially for validation
    currency = Column(String(3))
    payment_method = Column(String(50))
    
    # Address information (JSONB)
    shipping_address = Column(JSONB)
    billing_address = Column(JSONB)
    
    # Order items (JSONB array)
    order_items = Column(JSONB)
    
    # Financial details
    discount_amount = Column(String(20))
    tax_amount = Column(String(20))
    shipping_cost = Column(String(20))
    
    # Additional information
    notes = Column(Text)
    
    # Metadata fields
    source_system = Column(String(50), nullable=False, index=True)
    source_file = Column(String(255))
    ingestion_timestamp = Column(
        DateTime(timezone=True), 
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp()
    )
    batch_id = Column(String(100), index=True)
    record_hash = Column(String(64), index=True)
    
    # Data quality fields
    is_valid = Column(Boolean, default=True, index=True)
    validation_errors = Column(JSONB)
    
    def __repr__(self) -> str:
        return f"<RawOrders(id={self.id}, order_id={self.order_id}, source_system={self.source_system})>"
    
    @classmethod
    def from_api_response(
        cls, 
        api_data: Dict[str, Any], 
        source_system: str = 'api',
        batch_id: Optional[str] = None
    ) -> 'RawOrders':
        """Create RawOrders instance from API response data."""
        import hashlib
        import json
        
        # Generate record hash for deduplication
        record_data = json.dumps(api_data, sort_keys=True, default=str)
        record_hash = hashlib.sha256(record_data.encode()).hexdigest()
        
        return cls(
            order_id=str(api_data.get('id', api_data.get('order_id', ''))),
            customer_id=str(api_data.get('customer_id', api_data.get('customerId', ''))),
            order_date=cls._parse_datetime(api_data.get('order_date', api_data.get('orderDate'))),
            order_status=api_data.get('status', api_data.get('order_status')),
            total_amount=str(api_data.get('total', api_data.get('total_amount', 0))),
            currency=api_data.get('currency', 'USD'),
            payment_method=api_data.get('payment_method', api_data.get('paymentMethod')),
            shipping_address=api_data.get('shipping_address', api_data.get('shippingAddress')),
            billing_address=api_data.get('billing_address', api_data.get('billingAddress')),
            order_items=api_data.get('items', api_data.get('order_items', [])),
            discount_amount=str(api_data.get('discount', api_data.get('discount_amount', 0))),
            tax_amount=str(api_data.get('tax', api_data.get('tax_amount', 0))),
            shipping_cost=str(api_data.get('shipping', api_data.get('shipping_cost', 0))),
            notes=api_data.get('notes', api_data.get('comments')),
            source_system=source_system,
            batch_id=batch_id,
            record_hash=record_hash,
            ingestion_timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def _parse_datetime(date_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string with multiple format support."""
        if not date_string:
            return None
            
        # Common date formats from APIs
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO format with microseconds
            '%Y-%m-%dT%H:%M:%SZ',         # ISO format
            '%Y-%m-%dT%H:%M:%S',          # ISO format without Z
            '%Y-%m-%d %H:%M:%S',          # Standard format
            '%Y-%m-%d',                   # Date only
            '%m/%d/%Y',                   # US format
            '%d/%m/%Y',                   # European format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # If all formats fail, return None and log warning
        import logging
        logging.warning(f"Could not parse date string: {date_string}")
        return None


class RawCustomers(Base):
    """SQLAlchemy model for raw.raw_customers table."""
    
    __tablename__ = 'raw_customers'
    __table_args__ = {'schema': 'raw'}
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=text('uuid_generate_v4()')
    )
    
    # Business fields
    customer_id = Column(String(100), nullable=False, index=True)
    email = Column(String(320), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(255))
    phone = Column(String(20))
    date_of_birth = Column(DateTime(timezone=True))
    gender = Column(String(20))
    registration_date = Column(DateTime(timezone=True))
    last_login = Column(DateTime(timezone=True))
    customer_status = Column(String(30))
    preferred_language = Column(String(10))
    marketing_consent = Column(Boolean)
    
    # Address information (JSONB)
    addresses = Column(JSONB)
    
    # Demographics
    country = Column(String(2))
    state_province = Column(String(100))
    city = Column(String(100))
    postal_code = Column(String(20))
    timezone = Column(String(50))
    
    # Customer segments and preferences
    customer_segment = Column(String(50))
    preferences = Column(JSONB)
    tags = Column(JSONB)
    
    # Metadata fields
    source_system = Column(String(50), nullable=False, index=True)
    source_file = Column(String(255))
    ingestion_timestamp = Column(
        DateTime(timezone=True), 
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp()
    )
    batch_id = Column(String(100), index=True)
    record_hash = Column(String(64), index=True)
    
    # Data quality fields
    is_valid = Column(Boolean, default=True, index=True)
    validation_errors = Column(JSONB)
    
    def __repr__(self) -> str:
        return f"<RawCustomers(id={self.id}, customer_id={self.customer_id}, email={self.email})>"


class RawShipments(Base):
    """SQLAlchemy model for raw.raw_shipments table."""
    
    __tablename__ = 'raw_shipments'
    __table_args__ = {'schema': 'raw'}
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=text('uuid_generate_v4()')
    )
    
    # Business fields
    shipment_id = Column(String(100), nullable=False, index=True)
    order_id = Column(String(100), nullable=False, index=True)
    tracking_number = Column(String(100), index=True)
    carrier = Column(String(100))
    shipping_method = Column(String(100))
    
    # Shipment status and timing
    shipment_status = Column(String(50), index=True)
    shipped_date = Column(DateTime(timezone=True))
    estimated_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    
    # Address information (JSONB)
    origin_address = Column(JSONB)
    destination_address = Column(JSONB)
    
    # Package details
    package_count = Column(String(10))  # Store as string initially
    total_weight = Column(String(20))
    weight_unit = Column(String(10), default='kg')
    dimensions = Column(JSONB)
    
    # Costs
    shipping_cost = Column(String(20))
    insurance_cost = Column(String(20))
    currency = Column(String(3))
    
    # Delivery details
    delivery_instructions = Column(Text)
    signature_required = Column(Boolean, default=False)
    delivered_to = Column(String(255))
    delivery_notes = Column(Text)
    
    # Return information
    is_return = Column(Boolean, default=False)
    return_reason = Column(String(255))
    return_date = Column(DateTime(timezone=True))
    
    # Metadata fields
    source_system = Column(String(50), nullable=False, index=True)
    source_file = Column(String(255))
    ingestion_timestamp = Column(
        DateTime(timezone=True), 
        nullable=False,
        default=datetime.utcnow,
        server_default=func.current_timestamp()
    )
    batch_id = Column(String(100), index=True)
    record_hash = Column(String(64), index=True)
    
    # Data quality fields
    is_valid = Column(Boolean, default=True, index=True)
    validation_errors = Column(JSONB)
    
    def __repr__(self) -> str:
        return f"<RawShipments(id={self.id}, shipment_id={self.shipment_id}, order_id={self.order_id})>"
