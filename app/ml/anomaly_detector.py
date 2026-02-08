"""Anomaly Detection Engine - Detect unusual patterns in project data"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    UNUSUAL_ACTIVITY = "unusual_activity"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    DATA_QUALITY = "data_quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COST = "cost"


class SeverityLevel(Enum):
    """Severity levels for anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    id: str
    type: AnomalyType
    severity: SeverityLevel
    title: str
    description: str
    affected_entity: str
    affected_entity_id: str
    metric_name: str
    current_value: float
    expected_value: float
    timestamp: datetime
    is_active: bool = True
    acknowledged: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class StatisticalAnomalyDetector:
    """Detect anomalies using statistical methods"""
    
    @staticmethod
    def detect_outliers(values: List[float], threshold: float = 2.0) -> List[Tuple[int, float]]:
        """Detect outliers using z-score method
        
        Args:
            values: List of numeric values
            threshold: Z-score threshold (default 2.0 = 95% confidence)
        
        Returns:
            List of (index, z_score) tuples for outliers
        """
        if len(values) < 3:
            return []
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        if stdev == 0:
            return []
        
        outliers = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold:
                outliers.append((i, z_score))
        
        return outliers
    
    @staticmethod
    def detect_trend_change(values: List[float], window_size: int = 5) -> Optional[int]:
        """Detect significant trend changes
        
        Args:
            values: List of numeric values
            window_size: Size of comparison windows
        
        Returns:
            Index where trend changes, or None
        """
        if len(values) < window_size * 2:
            return None
        
        first_half = statistics.mean(values[:window_size])
        second_half = statistics.mean(values[-window_size:])
        
        # Calculate if change is significant (>30%)
        if first_half > 0:
            change_percent = abs(second_half - first_half) / first_half * 100
            if change_percent > 30:
                return len(values) - window_size
        
        return None
    
    @staticmethod
    def detect_spike(values: List[float], threshold: float = 3.0) -> Optional[int]:
        """Detect sudden spikes in data
        
        Args:
            values: List of numeric values
            threshold: Spike threshold multiplier
        
        Returns:
            Index of spike, or None
        """
        if len(values) < 3:
            return None
        
        for i in range(1, len(values) - 1):
            before = (values[i-1] + values[i]) / 2 if i > 0 else values[i-1]
            after = values[i]
            
            if before > 0 and after / before > threshold:
                return i
        
        return None


class AnomalyDetector:
    """Main anomaly detection engine"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.alerts: Dict[str, AnomalyAlert] = {}
        self.statistical_detector = StatisticalAnomalyDetector()
        self.thresholds = {
            'activity_spike': 2.5,  # 2.5x normal activity
            'issue_resolution': 3.0,  # Issues taking 3x longer
            'team_idle': 7,  # Team idle for 7 days
            'error_rate': 0.05,  # 5% error rate
            'cost_overrun': 1.2,  # 20% over budget
        }
        if config and isinstance(config, dict):
            self.update_thresholds(config.get('thresholds', {}))
    
    def update_thresholds(self, thresholds: Dict) -> None:
        """Update detection thresholds"""
        self.thresholds.update(thresholds)
        logger.info(f"Anomaly detection thresholds updated: {self.thresholds}")
    
    def detect_activity_anomalies(self, project_activities: List[Dict]) -> List[AnomalyAlert]:
        """Detect unusual activity patterns"""
        alerts = []
        
        if not project_activities:
            return alerts
        
        # Extract activity counts by day
        activity_by_day = {}
        for activity in project_activities:
            day = datetime.fromisoformat(activity['timestamp']).date()
            activity_by_day[day] = activity_by_day.get(day, 0) + 1
        
        activities = list(activity_by_day.values())
        
        # Detect spikes
        spike_idx = self.statistical_detector.detect_spike(activities, self.thresholds['activity_spike'])
        if spike_idx is not None:
            alert = AnomalyAlert(
                id=f"activity_spike_{spike_idx}",
                type=AnomalyType.UNUSUAL_ACTIVITY,
                severity=SeverityLevel.MEDIUM,
                title="Unusual Activity Spike",
                description=f"Activity spike detected ({activities[spike_idx]} activities)",
                affected_entity="project",
                affected_entity_id=project_activities[0].get('project_id', ''),
                metric_name="daily_activity_count",
                current_value=float(activities[spike_idx]),
                expected_value=float(statistics.mean(activities)),
                timestamp=datetime.now(),
            )
            alerts.append(alert)
        
        return alerts
    
    def detect_performance_anomalies(self, project_issues: List[Dict]) -> List[AnomalyAlert]:
        """Detect performance-related anomalies"""
        alerts = []
        
        if not project_issues:
            return alerts
        
        # Calculate issue resolution times
        resolution_times = []
        for issue in project_issues:
            if issue.get('status') == 'closed':
                created = datetime.fromisoformat(issue['created_at'])
                closed = datetime.fromisoformat(issue['closed_at'])
                days = (closed - created).days
                resolution_times.append(days)
        
        if not resolution_times:
            return alerts
        
        avg_time = statistics.mean(resolution_times)
        
        # Detect outliers (issues taking much longer)
        outliers = self.statistical_detector.detect_outliers(resolution_times, threshold=2.0)
        for idx, z_score in outliers:
            if idx < len(project_issues):
                issue = project_issues[idx]
                alert = AnomalyAlert(
                    id=f"slow_issue_{issue['id']}",
                    type=AnomalyType.PERFORMANCE,
                    severity=SeverityLevel.HIGH,
                    title="Slow Issue Resolution",
                    description=f"Issue taking {resolution_times[idx]} days (expected ~{avg_time:.0f})",
                    affected_entity="issue",
                    affected_entity_id=issue['id'],
                    metric_name="resolution_time_days",
                    current_value=float(resolution_times[idx]),
                    expected_value=avg_time,
                    timestamp=datetime.now(),
                )
                alerts.append(alert)
        
        return alerts
    
    def detect_user_behavior_anomalies(self, user_activity: List[Dict]) -> List[AnomalyAlert]:
        """Detect suspicious user behavior"""
        alerts = []
        
        if not user_activity:
            return alerts
        
        # Check for unusual patterns
        activity_times = []
        for activity in user_activity:
            timestamp = datetime.fromisoformat(activity['timestamp'])
            activity_times.append(timestamp)
        
        if not activity_times:
            return alerts
        
        # Detect if user has been idle
        now = datetime.now()
        last_activity = max(activity_times)
        idle_days = (now - last_activity).days
        
        if idle_days > self.thresholds['team_idle']:
            alert = AnomalyAlert(
                id=f"user_idle_{idle_days}",
                type=AnomalyType.SUSPICIOUS_BEHAVIOR,
                severity=SeverityLevel.LOW,
                title="User Inactivity",
                description=f"User has been inactive for {idle_days} days",
                affected_entity="user",
                affected_entity_id=user_activity[0].get('user_id', ''),
                metric_name="days_since_activity",
                current_value=float(idle_days),
                expected_value=0.0,
                timestamp=datetime.now(),
            )
            alerts.append(alert)
        
        # Detect bulk operations
        recent_activities = [a for a in activity_times if (now - a).days <= 1]
        if len(recent_activities) > 50:  # Many actions in 1 day
            alert = AnomalyAlert(
                id=f"bulk_operations",
                type=AnomalyType.SUSPICIOUS_BEHAVIOR,
                severity=SeverityLevel.MEDIUM,
                title="Bulk Operations Detected",
                description=f"{len(recent_activities)} operations in last 24 hours",
                affected_entity="user",
                affected_entity_id=user_activity[0].get('user_id', ''),
                metric_name="operations_per_day",
                current_value=float(len(recent_activities)),
                expected_value=10.0,
                timestamp=datetime.now(),
            )
            alerts.append(alert)
        
        return alerts
    
    def detect_cost_anomalies(self, project_costs: List[Dict]) -> List[AnomalyAlert]:
        """Detect cost-related anomalies"""
        alerts = []
        
        if not project_costs:
            return alerts
        
        # Check budget overruns
        for cost_data in project_costs:
            budget = cost_data.get('budget', 0)
            spent = cost_data.get('spent', 0)
            
            if budget > 0:
                ratio = spent / budget
                if ratio > self.thresholds['cost_overrun']:
                    alert = AnomalyAlert(
                        id=f"cost_overrun_{cost_data['id']}",
                        type=AnomalyType.COST,
                        severity=SeverityLevel.HIGH,
                        title="Budget Overspend",
                        description=f"Project spending {ratio*100:.0f}% of budget",
                        affected_entity="project",
                        affected_entity_id=cost_data['id'],
                        metric_name="budget_ratio",
                        current_value=ratio,
                        expected_value=1.0,
                        timestamp=datetime.now(),
                    )
                    alerts.append(alert)
        
        return alerts
    
    def detect_all_anomalies(self, project_data: Dict) -> List[AnomalyAlert]:
        """Run all anomaly detection checks"""
        all_alerts = []
        
        # Activity anomalies
        if 'activities' in project_data:
            all_alerts.extend(self.detect_activity_anomalies(project_data['activities']))
        
        # Performance anomalies
        if 'issues' in project_data:
            all_alerts.extend(self.detect_performance_anomalies(project_data['issues']))
        
        # User behavior anomalies
        if 'user_activities' in project_data:
            all_alerts.extend(self.detect_user_behavior_anomalies(project_data['user_activities']))
        
        # Cost anomalies
        if 'costs' in project_data:
            all_alerts.extend(self.detect_cost_anomalies(project_data['costs']))
        
        # Store alerts
        for alert in all_alerts:
            self.alerts[alert.id] = alert
        
        logger.info(f"Anomaly detection completed: {len(all_alerts)} alerts generated")
        return all_alerts
    
    def get_active_alerts(self) -> List[AnomalyAlert]:
        """Get all active (unacknowledged) alerts"""
        return [a for a in self.alerts.values() if a.is_active and not a.acknowledged]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            return True
        return False
    
    def get_alerts_summary(self) -> Dict:
        """Get summary of all alerts"""
        active = self.get_active_alerts()
        by_type = {}
        by_severity = {}
        
        for alert in active:
            type_name = alert.type.value
            severity_name = alert.severity.value
            
            by_type[type_name] = by_type.get(type_name, 0) + 1
            by_severity[severity_name] = by_severity.get(severity_name, 0) + 1
        
        return {
            'total_active': len(active),
            'by_type': by_type,
            'by_severity': by_severity,
            'total_all_time': len(self.alerts),
        }


# Global detector instance
anomaly_detector = AnomalyDetector()
