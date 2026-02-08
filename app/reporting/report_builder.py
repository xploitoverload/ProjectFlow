"""Custom report builder."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Column:
    """Report column definition."""
    name: str
    label: str
    type: str  # 'text', 'number', 'date', 'percentage'
    format: Optional[str] = None
    width: int = 150


@dataclass
class Filter:
    """Report filter."""
    field: str
    operator: str  # '=', '>', '<', 'contains', 'in'
    value: Any


@dataclass
class CustomReportConfig:
    """Custom report configuration."""
    name: str
    description: str
    data_source: str  # 'projects', 'issues', 'users', 'teams'
    columns: List[Column] = field(default_factory=list)
    filters: List[Filter] = field(default_factory=list)
    group_by: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = 'asc'
    limit: int = 1000


class ReportBuilder:
    """Custom report builder."""
    
    def __init__(self):
        """Initialize report builder."""
        self.custom_configs: Dict[str, CustomReportConfig] = {}
        self.available_columns: Dict[str, List[str]] = self._get_available_columns()
    
    def _get_available_columns(self) -> Dict[str, List[str]]:
        """Get available columns per data source."""
        return {
            'projects': [
                'id', 'name', 'status', 'completion_rate', 'team_size',
                'created_at', 'deadline', 'description', 'priority'
            ],
            'issues': [
                'id', 'title', 'status', 'priority', 'assigned_to',
                'created_at', 'resolved_at', 'description', 'type'
            ],
            'users': [
                'id', 'name', 'email', 'role', 'status', 'issues_resolved',
                'projects_count', 'joined_at'
            ],
            'teams': [
                'id', 'name', 'lead', 'member_count', 'projects',
                'avg_productivity', 'created_at'
            ]
        }
    
    def create_custom_report(self, config: CustomReportConfig) -> str:
        """
        Create a custom report configuration.
        
        Args:
            config: CustomReportConfig instance
            
        Returns:
            Configuration ID
        """
        config_id = f"custom_report_{int(datetime.now().timestamp() * 1000)}"
        self.custom_configs[config_id] = config
        logger.info(f"Custom report created: {config_id}")
        return config_id
    
    def add_column(self, config_id: str, column: Column) -> bool:
        """
        Add column to custom report.
        
        Args:
            config_id: Configuration ID
            column: Column definition
            
        Returns:
            True if successful
        """
        if config_id not in self.custom_configs:
            return False
        
        # Validate column exists in data source
        data_source = self.custom_configs[config_id].data_source
        if column.name not in self.available_columns.get(data_source, []):
            logger.warning(f"Invalid column for {data_source}: {column.name}")
            return False
        
        self.custom_configs[config_id].columns.append(column)
        return True
    
    def add_filter(self, config_id: str, filter_obj: Filter) -> bool:
        """
        Add filter to custom report.
        
        Args:
            config_id: Configuration ID
            filter_obj: Filter definition
            
        Returns:
            True if successful
        """
        if config_id not in self.custom_configs:
            return False
        
        self.custom_configs[config_id].filters.append(filter_obj)
        return True
    
    def set_grouping(self, config_id: str, group_by: str) -> bool:
        """
        Set grouping for custom report.
        
        Args:
            config_id: Configuration ID
            group_by: Column to group by
            
        Returns:
            True if successful
        """
        if config_id not in self.custom_configs:
            return False
        
        config = self.custom_configs[config_id]
        data_source = config.data_source
        
        if group_by not in self.available_columns.get(data_source, []):
            logger.warning(f"Invalid grouping column: {group_by}")
            return False
        
        config.group_by = group_by
        return True
    
    def set_sorting(self, config_id: str, sort_by: str, order: str = 'asc') -> bool:
        """
        Set sorting for custom report.
        
        Args:
            config_id: Configuration ID
            sort_by: Column to sort by
            order: 'asc' or 'desc'
            
        Returns:
            True if successful
        """
        if config_id not in self.custom_configs:
            return False
        
        config = self.custom_configs[config_id]
        data_source = config.data_source
        
        if sort_by not in self.available_columns.get(data_source, []):
            logger.warning(f"Invalid sort column: {sort_by}")
            return False
        
        if order not in ['asc', 'desc']:
            return False
        
        config.sort_by = sort_by
        config.sort_order = order
        return True
    
    def generate_preview(self, config_id: str, sample_rows: int = 5) -> Dict:
        """
        Generate preview for custom report.
        
        Args:
            config_id: Configuration ID
            sample_rows: Number of sample rows
            
        Returns:
            Preview data
        """
        if config_id not in self.custom_configs:
            return {'error': 'Configuration not found'}
        
        config = self.custom_configs[config_id]
        
        # Generate sample data based on data source
        sample_data = self._generate_sample_data(config, sample_rows)
        
        return {
            'config': {
                'name': config.name,
                'data_source': config.data_source,
                'columns': len(config.columns),
                'filters': len(config.filters)
            },
            'columns': [
                {'name': c.name, 'label': c.label, 'type': c.type}
                for c in config.columns
            ],
            'data': sample_data
        }
    
    def _generate_sample_data(self, config: CustomReportConfig, 
                             rows: int) -> List[Dict]:
        """Generate sample data for preview."""
        sample = []
        
        for i in range(rows):
            row = {}
            for column in config.columns:
                if column.type == 'number':
                    row[column.name] = 100 + i * 10
                elif column.type == 'percentage':
                    row[column.name] = 50 + (i * 5) % 50
                elif column.type == 'date':
                    row[column.name] = datetime.now().isoformat()
                else:
                    row[column.name] = f"{column.label} {i + 1}"
            sample.append(row)
        
        return sample
    
    def get_available_columns(self, data_source: str) -> List[str]:
        """
        Get available columns for data source.
        
        Args:
            data_source: Data source name
            
        Returns:
            List of available columns
        """
        return self.available_columns.get(data_source, [])
    
    def delete_config(self, config_id: str) -> bool:
        """
        Delete custom report configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if successful
        """
        if config_id in self.custom_configs:
            del self.custom_configs[config_id]
            logger.info(f"Config deleted: {config_id}")
            return True
        return False
    
    def get_stats(self) -> Dict:
        """
        Get builder statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'custom_configs': len(self.custom_configs),
            'data_sources': list(self.available_columns.keys()),
            'total_columns_available': sum(
                len(cols) for cols in self.available_columns.values()
            )
        }
