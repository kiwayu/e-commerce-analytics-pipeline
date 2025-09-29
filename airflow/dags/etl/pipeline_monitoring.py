"""
Pipeline monitoring utilities for ETL orchestration.
Provides comprehensive monitoring, alerting, and performance tracking.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
from airflow import settings

logger = logging.getLogger(__name__)


class PipelineMonitor:
    """
    Comprehensive monitoring for ETL pipeline execution.
    """
    
    def __init__(self, dag_id: str):
        self.dag_id = dag_id
        self.session = settings.Session()
    
    def get_pipeline_metrics(self, execution_date: datetime) -> Dict[str, Any]:
        """
        Get comprehensive metrics for pipeline execution.
        
        Args:
            execution_date: Execution date to analyze
            
        Returns:
            Dictionary with pipeline metrics
        """
        try:
            # Get DAG run
            dag_run = self.session.query(DagRun).filter(
                DagRun.dag_id == self.dag_id,
                DagRun.execution_date == execution_date
            ).first()
            
            if not dag_run:
                return {'error': 'DAG run not found', 'execution_date': execution_date.isoformat()}
            
            # Get task instances
            task_instances = self.session.query(TaskInstance).filter(
                TaskInstance.dag_id == self.dag_id,
                TaskInstance.execution_date == execution_date
            ).all()
            
            # Calculate metrics
            metrics = {
                'dag_id': self.dag_id,
                'execution_date': execution_date.isoformat(),
                'dag_run_state': dag_run.state,
                'start_date': dag_run.start_date.isoformat() if dag_run.start_date else None,
                'end_date': dag_run.end_date.isoformat() if dag_run.end_date else None,
                'duration_seconds': None,
                'task_metrics': self._calculate_task_metrics(task_instances),
                'performance_metrics': self._calculate_performance_metrics(task_instances),
                'sla_metrics': self._calculate_sla_metrics(task_instances),
                'error_analysis': self._analyze_errors(task_instances)
            }
            
            # Calculate total duration
            if dag_run.start_date and dag_run.end_date:
                duration = dag_run.end_date - dag_run.start_date
                metrics['duration_seconds'] = duration.total_seconds()
                metrics['duration_formatted'] = str(duration)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting pipeline metrics: {e}")
            return {'error': str(e)}
        finally:
            self.session.close()
    
    def _calculate_task_metrics(self, task_instances: List[TaskInstance]) -> Dict[str, Any]:
        """Calculate task-level metrics."""
        task_states = {}
        task_durations = {}
        task_retries = {}
        
        for ti in task_instances:
            state = ti.state or 'no_state'
            task_states[state] = task_states.get(state, 0) + 1
            
            # Calculate duration
            if ti.start_date and ti.end_date:
                duration = (ti.end_date - ti.start_date).total_seconds()
                task_durations[ti.task_id] = duration
            
            # Track retries
            if ti.try_number > 1:
                task_retries[ti.task_id] = ti.try_number - 1
        
        return {
            'total_tasks': len(task_instances),
            'task_states': task_states,
            'task_durations': task_durations,
            'task_retries': task_retries,
            'longest_task': max(task_durations.items(), key=lambda x: x[1]) if task_durations else None,
            'total_retries': sum(task_retries.values())
        }
    
    def _calculate_performance_metrics(self, task_instances: List[TaskInstance]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        successful_tasks = [ti for ti in task_instances if ti.state == State.SUCCESS]
        failed_tasks = [ti for ti in task_instances if ti.state == State.FAILED]
        
        # Calculate success rate
        total_tasks = len(task_instances)
        success_rate = len(successful_tasks) / total_tasks if total_tasks > 0 else 0
        
        # Calculate average duration for successful tasks
        successful_durations = []
        for ti in successful_tasks:
            if ti.start_date and ti.end_date:
                duration = (ti.end_date - ti.start_date).total_seconds()
                successful_durations.append(duration)
        
        avg_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0
        
        return {
            'success_rate': success_rate,
            'failure_rate': 1 - success_rate,
            'avg_task_duration_seconds': avg_duration,
            'successful_tasks_count': len(successful_tasks),
            'failed_tasks_count': len(failed_tasks),
            'performance_score': self._calculate_performance_score(success_rate, avg_duration)
        }
    
    def _calculate_sla_metrics(self, task_instances: List[TaskInstance]) -> Dict[str, Any]:
        """Calculate SLA compliance metrics."""
        sla_misses = []
        sla_compliant = []
        
        for ti in task_instances:
            if hasattr(ti, 'task') and ti.task.sla:
                expected_duration = ti.task.sla.total_seconds()
                
                if ti.start_date and ti.end_date:
                    actual_duration = (ti.end_date - ti.start_date).total_seconds()
                    
                    if actual_duration > expected_duration:
                        sla_misses.append({
                            'task_id': ti.task_id,
                            'expected_seconds': expected_duration,
                            'actual_seconds': actual_duration,
                            'overage_seconds': actual_duration - expected_duration
                        })
                    else:
                        sla_compliant.append(ti.task_id)
        
        total_sla_tasks = len(sla_misses) + len(sla_compliant)
        sla_compliance_rate = len(sla_compliant) / total_sla_tasks if total_sla_tasks > 0 else 1.0
        
        return {
            'sla_compliance_rate': sla_compliance_rate,
            'sla_misses': sla_misses,
            'sla_compliant_tasks': sla_compliant,
            'total_sla_monitored_tasks': total_sla_tasks
        }
    
    def _analyze_errors(self, task_instances: List[TaskInstance]) -> Dict[str, Any]:
        """Analyze errors and failure patterns."""
        failed_tasks = [ti for ti in task_instances if ti.state == State.FAILED]
        error_patterns = {}
        retry_patterns = {}
        
        for ti in failed_tasks:
            # Categorize error types (simplified)
            if ti.log and 'ConnectionError' in str(ti.log):
                error_type = 'connection_error'
            elif ti.log and 'TimeoutError' in str(ti.log):
                error_type = 'timeout_error'
            elif ti.log and 'ValidationError' in str(ti.log):
                error_type = 'validation_error'
            else:
                error_type = 'unknown_error'
            
            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
            
            # Analyze retry patterns
            if ti.try_number > 1:
                retry_patterns[ti.task_id] = ti.try_number - 1
        
        return {
            'total_failed_tasks': len(failed_tasks),
            'error_patterns': error_patterns,
            'retry_patterns': retry_patterns,
            'most_common_error': max(error_patterns.items(), key=lambda x: x[1]) if error_patterns else None
        }
    
    def _calculate_performance_score(self, success_rate: float, avg_duration: float) -> float:
        """Calculate overall performance score (0-100)."""
        # Weighted score based on success rate (70%) and speed (30%)
        success_component = success_rate * 70
        
        # Speed component (inverse relationship with duration)
        # Assume 300 seconds (5 minutes) as baseline good performance
        speed_component = max(0, (300 - avg_duration) / 300 * 30) if avg_duration > 0 else 30
        
        return min(100, success_component + speed_component)


class AlertManager:
    """
    Manages alerts and notifications for pipeline monitoring.
    """
    
    def __init__(self, alert_config: Dict[str, Any]):
        self.alert_config = alert_config
        self.thresholds = alert_config.get('thresholds', {})
    
    def should_alert(self, metrics: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Determine if alerts should be sent based on metrics.
        
        Args:
            metrics: Pipeline metrics
            
        Returns:
            Dictionary with alert types and reasons
        """
        alerts = {
            'critical': [],
            'warning': [],
            'info': []
        }
        
        # Check critical conditions
        if metrics.get('dag_run_state') == State.FAILED:
            alerts['critical'].append('Pipeline execution failed')
        
        task_metrics = metrics.get('task_metrics', {})
        failed_count = task_metrics.get('task_states', {}).get(State.FAILED, 0)
        
        if failed_count > 0:
            alerts['critical'].append(f'{failed_count} tasks failed')
        
        # Check SLA violations
        sla_metrics = metrics.get('sla_metrics', {})
        sla_compliance = sla_metrics.get('sla_compliance_rate', 1.0)
        
        if sla_compliance < self.thresholds.get('min_sla_compliance', 0.9):
            alerts['warning'].append(f'SLA compliance below threshold: {sla_compliance:.2%}')
        
        # Check performance degradation
        performance_metrics = metrics.get('performance_metrics', {})
        performance_score = performance_metrics.get('performance_score', 100)
        
        if performance_score < self.thresholds.get('min_performance_score', 70):
            alerts['warning'].append(f'Performance score below threshold: {performance_score:.1f}')
        
        # Check duration
        duration = metrics.get('duration_seconds', 0)
        max_duration = self.thresholds.get('max_duration_hours', 4) * 3600
        
        if duration > max_duration:
            alerts['warning'].append(f'Pipeline duration exceeded threshold: {duration/3600:.1f} hours')
        
        # Check retry rate
        total_retries = task_metrics.get('total_retries', 0)
        max_retries = self.thresholds.get('max_total_retries', 5)
        
        if total_retries > max_retries:
            alerts['info'].append(f'High retry count: {total_retries} retries')
        
        return alerts
    
    def format_alert_message(
        self, 
        metrics: Dict[str, Any], 
        alerts: Dict[str, List[str]],
        alert_level: str = 'critical'
    ) -> str:
        """
        Format alert message for notification.
        
        Args:
            metrics: Pipeline metrics
            alerts: Alert information
            alert_level: Level of alert to format
            
        Returns:
            Formatted alert message
        """
        if alert_level == 'critical':
            emoji = '🚨'
            title = 'CRITICAL PIPELINE ALERT'
        elif alert_level == 'warning':
            emoji = '⚠️'
            title = 'PIPELINE WARNING'
        else:
            emoji = 'ℹ️'
            title = 'PIPELINE INFO'
        
        alert_messages = alerts.get(alert_level, [])
        
        if not alert_messages:
            return ""
        
        message_parts = [
            f"{emoji} **{title}** {emoji}",
            "",
            f"**DAG:** {metrics.get('dag_id', 'Unknown')}",
            f"**Execution Date:** {metrics.get('execution_date', 'Unknown')}",
            f"**Status:** {metrics.get('dag_run_state', 'Unknown')}",
            "",
            "**Issues:**"
        ]
        
        for alert_msg in alert_messages:
            message_parts.append(f"• {alert_msg}")
        
        # Add performance summary
        task_metrics = metrics.get('task_metrics', {})
        performance_metrics = metrics.get('performance_metrics', {})
        
        message_parts.extend([
            "",
            "**Summary:**",
            f"• Total Tasks: {task_metrics.get('total_tasks', 0)}",
            f"• Success Rate: {performance_metrics.get('success_rate', 0):.2%}",
            f"• Duration: {metrics.get('duration_formatted', 'Unknown')}",
            f"• Performance Score: {performance_metrics.get('performance_score', 0):.1f}/100"
        ])
        
        return "\n".join(message_parts)


def generate_pipeline_report(metrics: Dict[str, Any]) -> str:
    """
    Generate comprehensive pipeline execution report.
    
    Args:
        metrics: Pipeline metrics
        
    Returns:
        Formatted report string
    """
    report_lines = [
        "# ETL Pipeline Execution Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
        f"**DAG ID:** {metrics.get('dag_id', 'Unknown')}",
        f"**Execution Date:** {metrics.get('execution_date', 'Unknown')}",
        f"**Status:** {metrics.get('dag_run_state', 'Unknown')}",
        f"**Duration:** {metrics.get('duration_formatted', 'Unknown')}",
        ""
    ]
    
    # Task metrics section
    task_metrics = metrics.get('task_metrics', {})
    report_lines.extend([
        "## Task Metrics",
        f"- Total Tasks: {task_metrics.get('total_tasks', 0)}",
        f"- Total Retries: {task_metrics.get('total_retries', 0)}",
        ""
    ])
    
    # Task states
    task_states = task_metrics.get('task_states', {})
    if task_states:
        report_lines.append("### Task States")
        for state, count in task_states.items():
            report_lines.append(f"- {state}: {count}")
        report_lines.append("")
    
    # Performance metrics
    performance_metrics = metrics.get('performance_metrics', {})
    report_lines.extend([
        "## Performance Metrics",
        f"- Success Rate: {performance_metrics.get('success_rate', 0):.2%}",
        f"- Average Task Duration: {performance_metrics.get('avg_task_duration_seconds', 0):.1f} seconds",
        f"- Performance Score: {performance_metrics.get('performance_score', 0):.1f}/100",
        ""
    ])
    
    # SLA metrics
    sla_metrics = metrics.get('sla_metrics', {})
    if sla_metrics.get('total_sla_monitored_tasks', 0) > 0:
        report_lines.extend([
            "## SLA Compliance",
            f"- Compliance Rate: {sla_metrics.get('sla_compliance_rate', 0):.2%}",
            f"- SLA Misses: {len(sla_metrics.get('sla_misses', []))}",
            ""
        ])
    
    # Error analysis
    error_analysis = metrics.get('error_analysis', {})
    if error_analysis.get('total_failed_tasks', 0) > 0:
        report_lines.extend([
            "## Error Analysis",
            f"- Failed Tasks: {error_analysis.get('total_failed_tasks', 0)}",
        ])
        
        error_patterns = error_analysis.get('error_patterns', {})
        if error_patterns:
            report_lines.append("### Error Patterns")
            for error_type, count in error_patterns.items():
                report_lines.append(f"- {error_type}: {count}")
        
        report_lines.append("")
    
    return "\n".join(report_lines)
