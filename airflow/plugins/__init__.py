"""
Airflow plugins for database replication.
"""

from airflow.plugins_manager import AirflowPlugin

from operators.incremental_replication_operator import (
    IncrementalReplicationOperator,
    ReplicationValidationOperator
)
from hooks.postgres_replication_hook import PostgreSQLReplicationHook


class ReplicationPlugin(AirflowPlugin):
    """Plugin for database replication operators and hooks."""
    
    name = "replication_plugin"
    
    operators = [
        IncrementalReplicationOperator,
        ReplicationValidationOperator
    ]
    
    hooks = [
        PostgreSQLReplicationHook
    ]
    
    # Make operators available in the web UI
    operator_extra_links = []
    
    # Plugin configuration
    flask_blueprints = []
    admin_views = []
    menu_links = []
