"""
Great Expectations configuration and utilities for data validation in Airflow.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GreatExpectationsConfig:
    """
    Configuration manager for Great Expectations in Airflow ETL pipeline.
    """
    
    def __init__(self, context_root_dir: str = '/opt/airflow/great_expectations'):
        self.context_root_dir = context_root_dir
        self.default_datasource = 'postgres_dwh'
        
    def get_validation_config(self) -> Dict[str, Any]:
        """
        Get comprehensive validation configuration for ETL pipeline.
        
        Returns:
            Dictionary with validation settings and expectations
        """
        return {
            'context_root_dir': self.context_root_dir,
            'datasources': {
                'postgres_dwh': {
                    'type': 'postgres',
                    'connection_string': 'postgresql://dwh_user:password@localhost:5432/ecommerce',
                    'schema': 'marts'
                }
            },
            'checkpoints': self.get_checkpoint_configs(),
            'notification_settings': {
                'slack_webhook': True,
                'email_on_failure': True,
                'email_recipients': ['data-team@company.com']
            }
        }
    
    def get_checkpoint_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Define checkpoint configurations for different data validation scenarios.
        
        Returns:
            Dictionary of checkpoint configurations
        """
        return {
            'orders_data_quality': {
                'name': 'orders_data_quality',
                'config_version': 1.0,
                'class_name': 'SimpleCheckpoint',
                'validations': [
                    {
                        'batch_request': {
                            'datasource_name': 'postgres_dwh',
                            'data_connector_name': 'default_runtime_data_connector',
                            'data_asset_name': 'fact_orders',
                            'runtime_parameters': {
                                'query': """
                                    SELECT * FROM marts.fact_orders 
                                    WHERE DATE(order_date) = CURRENT_DATE - INTERVAL '1 day'
                                """
                            }
                        },
                        'expectation_suite_name': 'orders_suite'
                    }
                ],
                'action_list': [
                    {
                        'name': 'store_validation_result',
                        'action': {
                            'class_name': 'StoreValidationResultAction'
                        }
                    },
                    {
                        'name': 'update_data_docs',
                        'action': {
                            'class_name': 'UpdateDataDocsAction'
                        }
                    }
                ]
            },
            'customers_data_quality': {
                'name': 'customers_data_quality',
                'config_version': 1.0,
                'class_name': 'SimpleCheckpoint',
                'validations': [
                    {
                        'batch_request': {
                            'datasource_name': 'postgres_dwh',
                            'data_connector_name': 'default_runtime_data_connector',
                            'data_asset_name': 'dim_customers',
                            'runtime_parameters': {
                                'query': """
                                    SELECT * FROM marts.dim_customers 
                                    WHERE last_updated_at >= CURRENT_DATE - INTERVAL '1 day'
                                """
                            }
                        },
                        'expectation_suite_name': 'customers_suite'
                    }
                ]
            },
            'revenue_data_quality': {
                'name': 'revenue_data_quality',
                'config_version': 1.0,
                'class_name': 'SimpleCheckpoint',
                'validations': [
                    {
                        'batch_request': {
                            'datasource_name': 'postgres_dwh',
                            'data_connector_name': 'default_runtime_data_connector',
                            'data_asset_name': 'revenue_daily',
                            'runtime_parameters': {
                                'query': """
                                    SELECT * FROM marts.revenue_daily 
                                    WHERE date_day = CURRENT_DATE - INTERVAL '1 day'
                                """
                            }
                        },
                        'expectation_suite_name': 'revenue_suite'
                    }
                ]
            }
        }
    
    def get_expectation_suites(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Define expectation suites for data validation.
        
        Returns:
            Dictionary of expectation suites with their expectations
        """
        return {
            'orders_suite': [
                {
                    'expectation_type': 'expect_table_row_count_to_be_between',
                    'kwargs': {
                        'min_value': 100,
                        'max_value': 100000,
                        'meta': {
                            'notes': 'Daily orders should be between 100 and 100k'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {
                        'column': 'order_id',
                        'meta': {
                            'notes': 'Order ID is required for all records'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_unique',
                    'kwargs': {
                        'column': 'order_id',
                        'meta': {
                            'notes': 'Order IDs must be unique'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {
                        'column': 'customer_id',
                        'meta': {
                            'notes': 'Customer ID is required'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'total_amount',
                        'min_value': 0,
                        'max_value': 100000,
                        'meta': {
                            'notes': 'Order amounts should be reasonable'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_in_set',
                    'kwargs': {
                        'column': 'order_status_group',
                        'value_set': ['active', 'fulfilled', 'cancelled', 'unknown'],
                        'meta': {
                            'notes': 'Order status must be valid'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_dateutil_parseable',
                    'kwargs': {
                        'column': 'order_date',
                        'meta': {
                            'notes': 'Order dates must be valid timestamps'
                        }
                    }
                }
            ],
            'customers_suite': [
                {
                    'expectation_type': 'expect_table_row_count_to_be_between',
                    'kwargs': {
                        'min_value': 1000,
                        'max_value': 10000000,
                        'meta': {
                            'notes': 'Customer count should be within expected range'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_unique',
                    'kwargs': {
                        'column': 'customer_id',
                        'meta': {
                            'notes': 'Customer IDs must be unique'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {
                        'column': 'email',
                        'meta': {
                            'notes': 'Email is required for all customers'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_match_regex',
                    'kwargs': {
                        'column': 'email',
                        'regex': r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
                        'meta': {
                            'notes': 'Email addresses must be valid format'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'total_orders',
                        'min_value': 0,
                        'max_value': 10000,
                        'meta': {
                            'notes': 'Customer order counts should be reasonable'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_in_set',
                    'kwargs': {
                        'column': 'customer_segment',
                        'value_set': [
                            'prospect', 'vip', 'champion', 'loyal_customer',
                            'potential_loyalist', 'new_customer', 'at_risk',
                            'need_attention', 'cannot_lose_them', 'other'
                        ],
                        'meta': {
                            'notes': 'Customer segments must be valid'
                        }
                    }
                }
            ],
            'revenue_suite': [
                {
                    'expectation_type': 'expect_table_row_count_to_equal',
                    'kwargs': {
                        'value': 1,
                        'meta': {
                            'notes': 'Should have exactly one row per day'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'gross_revenue',
                        'min_value': 1000,
                        'max_value': 10000000,
                        'meta': {
                            'notes': 'Daily revenue should be within expected range'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'total_orders',
                        'min_value': 10,
                        'max_value': 50000,
                        'meta': {
                            'notes': 'Daily order count should be reasonable'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'fulfillment_rate',
                        'min_value': 0.7,
                        'max_value': 1.0,
                        'meta': {
                            'notes': 'Fulfillment rate should be at least 70%'
                        }
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'average_order_value',
                        'min_value': 10,
                        'max_value': 2000,
                        'meta': {
                            'notes': 'Average order value should be reasonable'
                        }
                    }
                }
            ]
        }


def initialize_great_expectations_context(config: GreatExpectationsConfig) -> Any:
    """
    Initialize Great Expectations context with configuration.
    
    Args:
        config: Great Expectations configuration object
        
    Returns:
        Initialized Great Expectations context
    """
    try:
        import great_expectations as ge
        from great_expectations.core.expectation_configuration import ExpectationConfiguration
        from great_expectations.core.expectation_suite import ExpectationSuite
        
        # Get or create context
        context = ge.get_context(context_root_dir=config.context_root_dir)
        
        # Create expectation suites if they don't exist
        expectation_suites = config.get_expectation_suites()
        
        for suite_name, expectations in expectation_suites.items():
            try:
                # Try to get existing suite
                suite = context.get_expectation_suite(suite_name)
                logger.info(f"Using existing expectation suite: {suite_name}")
            except Exception:
                # Create new suite
                suite = context.create_expectation_suite(
                    expectation_suite_name=suite_name,
                    overwrite_existing=True
                )
                
                # Add expectations to suite
                for expectation_config in expectations:
                    expectation = ExpectationConfiguration(
                        expectation_type=expectation_config['expectation_type'],
                        kwargs=expectation_config['kwargs']
                    )
                    suite.add_expectation(expectation)
                
                # Save suite
                context.save_expectation_suite(suite)
                logger.info(f"Created expectation suite: {suite_name}")
        
        return context
        
    except ImportError:
        logger.error("Great Expectations not installed. Run: pip install great_expectations")
        raise
    except Exception as e:
        logger.error(f"Error initializing Great Expectations context: {e}")
        raise


def run_validation_checkpoint(
    context,
    checkpoint_name: str,
    run_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a specific validation checkpoint.
    
    Args:
        context: Great Expectations context
        checkpoint_name: Name of checkpoint to run
        run_name: Optional custom run name
        
    Returns:
        Dictionary with validation results
    """
    try:
        if not run_name:
            run_name = f"{checkpoint_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get and run checkpoint
        checkpoint = context.get_checkpoint(checkpoint_name)
        result = checkpoint.run(run_name=run_name)
        
        # Extract key metrics
        validation_result = {
            'checkpoint_name': checkpoint_name,
            'run_name': run_name,
            'success': result.success,
            'run_id': str(result.run_id),
            'statistics': {},
            'validation_results': []
        }
        
        # Process validation results
        if hasattr(result, 'run_results'):
            for run_result in result.run_results.values():
                if hasattr(run_result, 'validation_result'):
                    vr = run_result['validation_result']
                    validation_result['validation_results'].append({
                        'success': vr.success,
                        'expectation_suite_name': vr.expectation_suite_name,
                        'statistics': vr.statistics,
                        'results': [
                            {
                                'expectation_type': er.expectation_config.expectation_type,
                                'success': er.success,
                                'result': er.result
                            }
                            for er in vr.results
                        ]
                    })
        
        logger.info(f"Validation checkpoint {checkpoint_name} completed: {result.success}")
        return validation_result
        
    except Exception as e:
        logger.error(f"Error running validation checkpoint {checkpoint_name}: {e}")
        raise


def generate_validation_report(validation_results: List[Dict[str, Any]]) -> str:
    """
    Generate a formatted validation report.
    
    Args:
        validation_results: List of validation results
        
    Returns:
        Formatted validation report as string
    """
    report_lines = [
        "# Data Quality Validation Report",
        f"Generated: {datetime.now().isoformat()}",
        ""
    ]
    
    total_checkpoints = len(validation_results)
    passed_checkpoints = sum(1 for r in validation_results if r['success'])
    
    report_lines.extend([
        "## Summary",
        f"- Total Checkpoints: {total_checkpoints}",
        f"- Passed: {passed_checkpoints}",
        f"- Failed: {total_checkpoints - passed_checkpoints}",
        f"- Success Rate: {passed_checkpoints/total_checkpoints*100:.1f}%",
        ""
    ])
    
    # Detailed results
    for result in validation_results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        report_lines.extend([
            f"## {result['checkpoint_name']} {status}",
            f"Run ID: {result['run_id']}",
            ""
        ])
        
        # Add expectation results
        for vr in result['validation_results']:
            suite_name = vr['expectation_suite_name']
            suite_success = vr['success']
            suite_status = "✅" if suite_success else "❌"
            
            report_lines.append(f"### {suite_name} {suite_status}")
            
            for expectation in vr['results']:
                exp_status = "✅" if expectation['success'] else "❌"
                exp_type = expectation['expectation_type']
                report_lines.append(f"- {exp_status} {exp_type}")
            
            report_lines.append("")
    
    return "\n".join(report_lines)
