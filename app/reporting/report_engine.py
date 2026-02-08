"""Core report engine."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports."""
    PROJECT_SUMMARY = "project_summary"
    TEAM_PERFORMANCE = "team_performance"
    ISSUE_ANALYSIS = "issue_analysis"
    FINANCIAL = "financial"
    CUSTOM = "custom"


class ReportFormat(Enum):
    """Report output formats."""
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    CSV = "csv"


@dataclass
class ReportConfig:
    """Report configuration."""
    name: str
    report_type: ReportType
    date_range_days: int = 30
    include_charts: bool = True
    include_summary: bool = True
    include_details: bool = True
    metrics: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    sort_by: Optional[str] = None


@dataclass
class Report:
    """Generated report."""
    id: str
    config: ReportConfig
    created_at: str
    created_by: str
    title: str
    summary: Dict
    sections: List[Dict] = field(default_factory=list)
    charts: List[Dict] = field(default_factory=list)
    export_formats: List[ReportFormat] = field(default_factory=list)


class ReportEngine:
    """Core report generation engine."""
    
    def __init__(self):
        """Initialize report engine."""
        self.reports: Dict[str, Report] = {}
        self.report_templates: Dict[str, ReportConfig] = {}
        self.generated_count = 0
        self._setup_templates()
    
    def _setup_templates(self):
        """Setup default report templates."""
        # Project Summary template
        self.report_templates['project_summary'] = ReportConfig(
            name='Project Summary Report',
            report_type=ReportType.PROJECT_SUMMARY,
            date_range_days=30,
            metrics=['issues_count', 'completion_rate', 'team_size', 'velocity']
        )
        
        # Team Performance template
        self.report_templates['team_performance'] = ReportConfig(
            name='Team Performance Report',
            report_type=ReportType.TEAM_PERFORMANCE,
            date_range_days=30,
            metrics=['productivity', 'issues_resolved', 'code_quality', 'availability']
        )
        
        # Issue Analysis template
        self.report_templates['issue_analysis'] = ReportConfig(
            name='Issue Analysis Report',
            report_type=ReportType.ISSUE_ANALYSIS,
            date_range_days=30,
            metrics=['issue_count', 'avg_resolution_time', 'priority_distribution', 'status_breakdown']
        )
    
    def create_report(self, config: ReportConfig, created_by: str) -> Report:
        """
        Create a new report.
        
        Args:
            config: Report configuration
            created_by: User ID creating report
            
        Returns:
            Generated Report
        """
        report_id = f"report_{int(datetime.now().timestamp() * 1000)}"
        
        report = Report(
            id=report_id,
            config=config,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            title=config.name,
            summary={},
            sections=[],
            charts=[]
        )
        
        # Generate report content
        self._generate_report_content(report)
        
        self.reports[report_id] = report
        self.generated_count += 1
        
        logger.info(f"Report created: {report_id}")
        return report
    
    def _generate_report_content(self, report: Report) -> None:
        """
        Generate report content.
        
        Args:
            report: Report instance
        """
        # Summary section
        report.summary = self._generate_summary(report.config)
        
        # Sections based on report type
        if report.config.report_type == ReportType.PROJECT_SUMMARY:
            report.sections = self._generate_project_sections()
        elif report.config.report_type == ReportType.TEAM_PERFORMANCE:
            report.sections = self._generate_team_sections()
        elif report.config.report_type == ReportType.ISSUE_ANALYSIS:
            report.sections = self._generate_issue_sections()
        
        # Charts
        if report.config.include_charts:
            report.charts = self._generate_charts(report.config)
    
    def _generate_summary(self, config: ReportConfig) -> Dict:
        """Generate summary section."""
        return {
            'report_type': config.report_type.value,
            'period': f'Last {config.date_range_days} days',
            'generated': datetime.now().isoformat(),
            'metrics_count': len(config.metrics)
        }
    
    def _generate_project_sections(self) -> List[Dict]:
        """Generate project report sections."""
        return [
            {
                'name': 'Project Overview',
                'type': 'overview',
                'content': {
                    'active_projects': 5,
                    'completed_projects': 2,
                    'at_risk_projects': 1,
                    'total_team_members': 12
                }
            },
            {
                'name': 'Issue Statistics',
                'type': 'statistics',
                'content': {
                    'total_issues': 145,
                    'resolved_issues': 98,
                    'pending_issues': 47,
                    'avg_resolution_time': '4.2 days'
                }
            },
            {
                'name': 'Team Metrics',
                'type': 'metrics',
                'content': {
                    'team_velocity': '45 points/sprint',
                    'utilization': '92%',
                    'top_contributor': 'John Doe'
                }
            }
        ]
    
    def _generate_team_sections(self) -> List[Dict]:
        """Generate team performance sections."""
        return [
            {
                'name': 'Team Performance',
                'type': 'performance',
                'content': {
                    'avg_completion_rate': '94%',
                    'quality_score': '8.7/10',
                    'delivery_on_time': '91%'
                }
            },
            {
                'name': 'Individual Metrics',
                'type': 'individual',
                'content': {
                    'members': 12,
                    'avg_issues_resolved': '7.2',
                    'avg_code_review_time': '2.3 hours'
                }
            }
        ]
    
    def _generate_issue_sections(self) -> List[Dict]:
        """Generate issue analysis sections."""
        return [
            {
                'name': 'Issue Overview',
                'type': 'overview',
                'content': {
                    'total_issues': 145,
                    'new_this_period': 32,
                    'resolved': 28,
                    'pending': 47
                }
            },
            {
                'name': 'Priority Distribution',
                'type': 'distribution',
                'content': {
                    'critical': 5,
                    'high': 22,
                    'medium': 65,
                    'low': 53
                }
            },
            {
                'name': 'Resolution Analysis',
                'type': 'analysis',
                'content': {
                    'avg_time': '4.2 days',
                    'median_time': '3.1 days',
                    'fastest_resolution': '0.5 days',
                    'slowest_resolution': '45 days'
                }
            }
        ]
    
    def _generate_charts(self, config: ReportConfig) -> List[Dict]:
        """Generate chart configurations."""
        charts = []
        
        # Trend chart
        charts.append({
            'type': 'line',
            'title': 'Issues Over Time',
            'data': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'datasets': [{
                    'label': 'Created',
                    'data': [12, 19, 3, 5]
                }, {
                    'label': 'Resolved',
                    'data': [8, 15, 2, 7]
                }]
            }
        })
        
        # Distribution chart
        charts.append({
            'type': 'pie',
            'title': 'Priority Distribution',
            'data': {
                'labels': ['Critical', 'High', 'Medium', 'Low'],
                'datasets': [{
                    'data': [5, 22, 65, 53],
                    'backgroundColor': ['#ff4444', '#ff8800', '#ffcc00', '#44ff44']
                }]
            }
        })
        
        # Bar chart
        charts.append({
            'type': 'bar',
            'title': 'Team Performance',
            'data': {
                'labels': ['John', 'Jane', 'Mike', 'Sarah', 'Tom'],
                'datasets': [{
                    'label': 'Issues Resolved',
                    'data': [12, 19, 8, 15, 10]
                }]
            }
        })
        
        return charts
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get report by ID.
        
        Args:
            report_id: Report ID
            
        Returns:
            Report or None
        """
        return self.reports.get(report_id)
    
    def list_reports(self, created_by: str = None) -> List[Report]:
        """
        List reports.
        
        Args:
            created_by: Filter by creator
            
        Returns:
            List of reports
        """
        reports = list(self.reports.values())
        
        if created_by:
            reports = [r for r in reports if r.created_by == created_by]
        
        return sorted(reports, key=lambda r: r.created_at, reverse=True)
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: Report ID
            
        Returns:
            True if successful
        """
        if report_id in self.reports:
            del self.reports[report_id]
            logger.info(f"Report deleted: {report_id}")
            return True
        return False
    
    def get_stats(self) -> Dict:
        """
        Get report engine statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'total_reports': len(self.reports),
            'generated_count': self.generated_count,
            'templates': len(self.report_templates),
            'template_names': list(self.report_templates.keys())
        }
