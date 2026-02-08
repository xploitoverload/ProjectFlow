"""Advanced Analytics Dashboard - Comprehensive project analytics and insights"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsMetric:
    """Single analytics metric"""
    name: str
    value: float
    unit: str
    trend: Optional[str] = None  # 'up', 'down', 'stable'
    threshold: Optional[float] = None
    is_warning: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ProjectAnalytics:
    """Analyze project metrics"""
    
    @staticmethod
    def calculate_project_health(project: Dict) -> Dict[str, AnalyticsMetric]:
        """Calculate overall project health metrics"""
        metrics = {}
        
        # Completion rate
        total_issues = len(project.get('issues', []))
        closed_issues = len([i for i in project.get('issues', []) if i.get('status') == 'closed'])
        completion_rate = (closed_issues / total_issues * 100) if total_issues > 0 else 0
        
        trend = None
        if completion_rate >= 80:
            trend = 'up'
        elif completion_rate < 50:
            trend = 'down'
        
        metrics['completion_rate'] = AnalyticsMetric(
            name='Project Completion Rate',
            value=completion_rate,
            unit='%',
            trend=trend,
            threshold=80.0,
            is_warning=completion_rate < 50,
        )
        
        # On-time delivery (estimate vs actual)
        estimated_date = project.get('estimated_completion')
        if estimated_date:
            est_date = datetime.fromisoformat(estimated_date) if isinstance(estimated_date, str) else estimated_date
            days_left = (est_date - datetime.now()).days
            ontime_score = max(0, min(100, 100 - (days_left * 5)))  # Decreases as deadline approaches
            
            metrics['on_time_score'] = AnalyticsMetric(
                name='On-Time Delivery Score',
                value=ontime_score,
                unit='%',
                trend='up' if days_left > 14 else 'down',
                threshold=70.0,
                is_warning=ontime_score < 60,
            )
        
        # Team velocity (issues closed per week)
        issues = project.get('issues', [])
        if issues:
            closed_this_week = len([
                i for i in issues 
                if i.get('status') == 'closed' and 
                (datetime.now() - datetime.fromisoformat(i['closed_at'])).days <= 7
            ])
            metrics['team_velocity'] = AnalyticsMetric(
                name='Team Velocity',
                value=closed_this_week,
                unit='issues/week',
                trend='up',
            )
        
        # Quality score (based on bug ratio)
        bugs = len([i for i in issues if i.get('type') == 'bug'])
        quality_score = max(0, 100 - (bugs / max(total_issues, 1) * 100))
        metrics['quality_score'] = AnalyticsMetric(
            name='Quality Score',
            value=quality_score,
            unit='%',
            trend='up' if quality_score > 70 else 'down',
            threshold=70.0,
            is_warning=quality_score < 60,
        )
        
        return metrics
    
    @staticmethod
    def calculate_team_productivity(team_members: List[Dict], issues: List[Dict]) -> Dict:
        """Calculate team productivity metrics"""
        metrics = {}
        
        # Issues per team member
        if team_members:
            issues_per_member = len(issues) / len(team_members)
            metrics['issues_per_member'] = AnalyticsMetric(
                name='Issues Per Team Member',
                value=issues_per_member,
                unit='issues',
            )
        
        # Member utilization (issues assigned)
        utilization = {}
        for member in team_members:
            assigned = len([i for i in issues if member['id'] in i.get('assignees', [])])
            utilization[member['id']] = assigned
        
        if utilization:
            avg_utilization = statistics.mean(utilization.values())
            metrics['avg_utilization'] = AnalyticsMetric(
                name='Average Team Utilization',
                value=avg_utilization,
                unit='issues',
            )
        
        return metrics
    
    @staticmethod
    def calculate_issue_resolution_metrics(issues: List[Dict]) -> Dict:
        """Calculate issue resolution metrics"""
        metrics = {}
        
        if not issues:
            return metrics
        
        # Average resolution time
        resolution_times = []
        for issue in issues:
            if issue.get('status') == 'closed' and issue.get('closed_at'):
                created = datetime.fromisoformat(issue['created_at']) if isinstance(issue['created_at'], str) else issue['created_at']
                closed = datetime.fromisoformat(issue['closed_at']) if isinstance(issue['closed_at'], str) else issue['closed_at']
                days = (closed - created).days
                resolution_times.append(days)
        
        if resolution_times:
            avg_time = statistics.mean(resolution_times)
            median_time = statistics.median(resolution_times)
            
            metrics['avg_resolution_time'] = AnalyticsMetric(
                name='Average Resolution Time',
                value=avg_time,
                unit='days',
            )
            
            metrics['median_resolution_time'] = AnalyticsMetric(
                name='Median Resolution Time',
                value=median_time,
                unit='days',
            )
        
        # Overdue issues
        overdue = len([i for i in issues if i.get('status') != 'closed' and (datetime.now() - datetime.fromisoformat(i['created_at'])).days > 14])
        metrics['overdue_issues'] = AnalyticsMetric(
            name='Overdue Issues',
            value=overdue,
            unit='issues',
            is_warning=overdue > 0,
        )
        
        return metrics


class TrendAnalysis:
    """Analyze trends over time"""
    
    @staticmethod
    def calculate_trend(historical_values: List[float], time_periods: int = 3) -> Optional[str]:
        """Calculate trend direction"""
        if len(historical_values) < 2:
            return None
        
        # Compare recent values with older values
        if len(historical_values) >= time_periods * 2:
            recent = statistics.mean(historical_values[-time_periods:])
            older = statistics.mean(historical_values[:-time_periods])
            
            if recent > older * 1.1:
                return 'up'
            elif recent < older * 0.9:
                return 'down'
        
        return 'stable'
    
    @staticmethod
    def identify_bottlenecks(issues: List[Dict]) -> List[Dict]:
        """Identify bottlenecks in project"""
        bottlenecks = []
        
        # Find issues with most comments (high discussion = complex/stuck)
        issue_by_comments = sorted(
            issues,
            key=lambda x: len(x.get('comments', [])),
            reverse=True
        )[:5]
        
        for issue in issue_by_comments:
            if len(issue.get('comments', [])) > 10:
                bottlenecks.append({
                    'type': 'high_discussion',
                    'issue_id': issue['id'],
                    'title': issue.get('title'),
                    'comments': len(issue.get('comments', [])),
                    'status': issue.get('status'),
                })
        
        # Find issues taking too long
        long_running = [
            i for i in issues
            if i.get('status') != 'closed' and 
            (datetime.now() - datetime.fromisoformat(i['created_at'])).days > 30
        ]
        
        for issue in long_running[:5]:
            bottlenecks.append({
                'type': 'long_running',
                'issue_id': issue['id'],
                'title': issue.get('title'),
                'days_open': (datetime.now() - datetime.fromisoformat(issue['created_at'])).days,
                'status': issue.get('status'),
            })
        
        return bottlenecks


class BenchmarkAnalysis:
    """Compare metrics against benchmarks"""
    
    INDUSTRY_BENCHMARKS = {
        'issue_resolution_time': 7,  # days
        'team_utilization': 0.8,     # 80%
        'quality_score': 90,          # %
        'project_completion_rate': 95, # %
    }
    
    @staticmethod
    def compare_to_benchmark(metric_name: str, value: float) -> Dict:
        """Compare metric to industry benchmark"""
        benchmark = BenchmarkAnalysis.INDUSTRY_BENCHMARKS.get(metric_name)
        
        if benchmark is None:
            return {'comparable': False}
        
        difference = value - benchmark
        percent_diff = (difference / benchmark * 100) if benchmark != 0 else 0
        
        status = 'above' if difference > 0 else 'below'
        
        return {
            'comparable': True,
            'benchmark_value': benchmark,
            'actual_value': value,
            'difference': difference,
            'percent_difference': percent_diff,
            'status': status,  # above or below benchmark
        }


class AnalyticsDashboard:
    """Main analytics dashboard engine"""
    
    def __init__(self):
        self.project_analytics = ProjectAnalytics()
        self.trend_analysis = TrendAnalysis()
        self.benchmark_analysis = BenchmarkAnalysis()
    
    def generate_dashboard(self, project: Dict, team_members: List[Dict] = None) -> Dict:
        """Generate comprehensive analytics dashboard"""
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'project_id': project.get('id'),
            'project_name': project.get('name'),
            'sections': {}
        }
        
        # Project health
        health_metrics = self.project_analytics.calculate_project_health(project)
        dashboard['sections']['project_health'] = {
            'title': 'Project Health',
            'metrics': {name: metric.to_dict() for name, metric in health_metrics.items()}
        }
        
        # Team productivity
        if team_members:
            productivity_metrics = self.project_analytics.calculate_team_productivity(
                team_members, project.get('issues', [])
            )
            dashboard['sections']['team_productivity'] = {
                'title': 'Team Productivity',
                'metrics': {name: metric.to_dict() for name, metric in productivity_metrics.items()}
            }
        
        # Issue resolution
        resolution_metrics = self.project_analytics.calculate_issue_resolution_metrics(
            project.get('issues', [])
        )
        dashboard['sections']['issue_resolution'] = {
            'title': 'Issue Resolution',
            'metrics': {name: metric.to_dict() for name, metric in resolution_metrics.items()}
        }
        
        # Bottleneck analysis
        bottlenecks = self.trend_analysis.identify_bottlenecks(project.get('issues', []))
        dashboard['sections']['bottlenecks'] = {
            'title': 'Bottleneck Analysis',
            'items': bottlenecks,
        }
        
        return dashboard
    
    def generate_executive_summary(self, project: Dict) -> Dict:
        """Generate executive summary"""
        health = self.project_analytics.calculate_project_health(project)
        
        summary = {
            'project_name': project.get('name'),
            'overall_health': self._calculate_overall_health(health),
            'key_metrics': self._extract_key_metrics(health),
            'recommendations': self._generate_recommendations(project, health),
            'timestamp': datetime.now().isoformat(),
        }
        
        return summary
    
    @staticmethod
    def _calculate_overall_health(health_metrics: Dict[str, AnalyticsMetric]) -> str:
        """Calculate overall health status"""
        completion = health_metrics.get('completion_rate')
        quality = health_metrics.get('quality_score')
        
        if completion and completion.value >= 80 and quality and quality.value >= 80:
            return 'Excellent'
        elif completion and completion.value >= 50 and quality and quality.value >= 60:
            return 'Good'
        elif completion and completion.value >= 25 or quality and quality.value >= 40:
            return 'At Risk'
        else:
            return 'Critical'
    
    @staticmethod
    def _extract_key_metrics(health_metrics: Dict[str, AnalyticsMetric]) -> List[Dict]:
        """Extract key metrics for summary"""
        key_metrics = []
        
        for name, metric in health_metrics.items():
            key_metrics.append({
                'name': metric.name,
                'value': metric.value,
                'unit': metric.unit,
                'status': 'warning' if metric.is_warning else 'normal',
            })
        
        return key_metrics
    
    @staticmethod
    def _generate_recommendations(project: Dict, health_metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        # Completion rate recommendation
        completion = health_metrics.get('completion_rate')
        if completion and completion.value < 50:
            recommendations.append('Prioritize issue resolution to meet project deadline')
        
        # Quality recommendation
        quality = health_metrics.get('quality_score')
        if quality and quality.value < 70:
            recommendations.append('Increase QA efforts to improve code quality')
        
        # Overdue issues
        issues = project.get('issues', [])
        overdue = len([i for i in issues if i.get('status') != 'closed' and (datetime.now() - datetime.fromisoformat(i['created_at'])).days > 14])
        if overdue > 0:
            recommendations.append(f'Address {overdue} overdue issues to prevent delays')
        
        return recommendations


# Global dashboard instance
analytics_dashboard = AnalyticsDashboard()
