# app/export/exporters.py
"""
Data export functionality (CSV, Excel, PDF).
"""

import csv
import json
import logging
from io import StringIO, BytesIO
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('export')


class CSVExporter:
    """Export data to CSV format."""
    
    @staticmethod
    def export_issues(issues: List[Dict[str, Any]], 
                     include_fields: Optional[List[str]] = None) -> str:
        """
        Export issues to CSV.
        
        Args:
            issues: List of issue dictionaries
            include_fields: Fields to include (all if None)
        
        Returns:
            CSV string
        """
        if not issues:
            return ""
        
        # Default fields
        if include_fields is None:
            include_fields = ['id', 'title', 'status', 'priority', 'assigned_to', 'created_at']
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=include_fields, restval='')
        
        writer.writeheader()
        for issue in issues:
            # Filter to included fields
            row = {k: v for k, v in issue.items() if k in include_fields}
            # Convert datetime objects to strings
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.isoformat()
            writer.writerow(row)
        
        csv_string = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(issues)} issues to CSV")
        
        return csv_string
    
    @staticmethod
    def export_projects(projects: List[Dict[str, Any]],
                       include_fields: Optional[List[str]] = None) -> str:
        """
        Export projects to CSV.
        
        Args:
            projects: List of project dictionaries
            include_fields: Fields to include
        
        Returns:
            CSV string
        """
        if not projects:
            return ""
        
        if include_fields is None:
            include_fields = ['id', 'name', 'status', 'owner_id', 'created_at', 'issue_count']
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=include_fields, restval='')
        
        writer.writeheader()
        for project in projects:
            row = {k: v for k, v in project.items() if k in include_fields}
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.isoformat()
            writer.writerow(row)
        
        csv_string = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(projects)} projects to CSV")
        
        return csv_string
    
    @staticmethod
    def export_users(users: List[Dict[str, Any]],
                    include_fields: Optional[List[str]] = None) -> str:
        """Export users to CSV."""
        if not users:
            return ""
        
        if include_fields is None:
            include_fields = ['id', 'username', 'email', 'created_at']
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=include_fields, restval='')
        
        writer.writeheader()
        for user in users:
            row = {k: v for k, v in user.items() if k in include_fields}
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.isoformat()
            writer.writerow(row)
        
        csv_string = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(users)} users to CSV")
        
        return csv_string


class JSONExporter:
    """Export data to JSON format."""
    
    @staticmethod
    def export_issues(issues: List[Dict[str, Any]], pretty: bool = True) -> str:
        """Export issues to JSON."""
        # Convert datetime objects
        issues_copy = []
        for issue in issues:
            issue_copy = dict(issue)
            for key, value in issue_copy.items():
                if isinstance(value, datetime):
                    issue_copy[key] = value.isoformat()
            issues_copy.append(issue_copy)
        
        json_str = json.dumps(issues_copy, indent=2 if pretty else None)
        logger.info(f"Exported {len(issues)} issues to JSON")
        return json_str
    
    @staticmethod
    def export_projects(projects: List[Dict[str, Any]], pretty: bool = True) -> str:
        """Export projects to JSON."""
        projects_copy = []
        for project in projects:
            project_copy = dict(project)
            for key, value in project_copy.items():
                if isinstance(value, datetime):
                    project_copy[key] = value.isoformat()
            projects_copy.append(project_copy)
        
        json_str = json.dumps(projects_copy, indent=2 if pretty else None)
        logger.info(f"Exported {len(projects)} projects to JSON")
        return json_str


class PDFExporter:
    """Export data to PDF format (requires reportlab)."""
    
    @staticmethod
    def export_issues_to_pdf(issues: List[Dict[str, Any]], 
                           title: str = "Issues Report") -> BytesIO:
        """
        Export issues to PDF.
        
        Args:
            issues: List of issues
            title: Report title
        
        Returns:
            BytesIO object with PDF
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        except ImportError:
            logger.warning("reportlab not installed, PDF export disabled")
            return None
        
        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3 * 72))
        
        # Create table data
        table_data = [['ID', 'Title', 'Status', 'Priority', 'Assigned To']]
        
        for issue in issues[:50]:  # Limit to 50 for readability
            table_data.append([
                str(issue.get('id', '')),
                str(issue.get('title', '')[:30]),
                str(issue.get('status', '')),
                str(issue.get('priority', '')),
                str(issue.get('assigned_to', ''))
            ])
        
        # Create table
        if len(table_data) > 1:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
            ]))
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        logger.info(f"Exported {len(issues)} issues to PDF")
        
        return pdf_buffer
    
    @staticmethod
    def export_projects_to_pdf(projects: List[Dict[str, Any]],
                             title: str = "Projects Report") -> BytesIO:
        """Export projects to PDF."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        except ImportError:
            logger.warning("reportlab not installed")
            return None
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3 * 72))
        
        # Table data
        table_data = [['ID', 'Name', 'Status', 'Issues', 'Created']]
        
        for project in projects[:50]:
            table_data.append([
                str(project.get('id', '')),
                str(project.get('name', '')[:25]),
                str(project.get('status', '')),
                str(project.get('issue_count', '0')),
                str(project.get('created_at', ''))[:10] if project.get('created_at') else ''
            ])
        
        if len(table_data) > 1:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
            ]))
            elements.append(table)
        
        doc.build(elements)
        pdf_buffer.seek(0)
        
        logger.info(f"Exported {len(projects)} projects to PDF")
        
        return pdf_buffer


class ExportManager:
    """Manage data exports in various formats."""
    
    FORMATS = {
        'csv': CSVExporter,
        'json': JSONExporter,
        'pdf': PDFExporter
    }
    
    @staticmethod
    def export(data: List[Dict[str, Any]], data_type: str, 
              export_format: str, **kwargs) -> Any:
        """
        Export data in specified format.
        
        Args:
            data: List of data items
            data_type: Type of data ('issues', 'projects', 'users')
            export_format: Format ('csv', 'json', 'pdf')
            **kwargs: Additional arguments
        
        Returns:
            Exported data (string or BytesIO)
        """
        if export_format not in ExportManager.FORMATS:
            raise ValueError(f"Unsupported format: {export_format}")
        
        exporter_class = ExportManager.FORMATS[export_format]
        method_name = f"export_{data_type}"
        
        if not hasattr(exporter_class, method_name):
            raise ValueError(f"Cannot export {data_type} to {export_format}")
        
        method = getattr(exporter_class, method_name)
        return method(data, **kwargs)
    
    @staticmethod
    def get_filename(data_type: str, export_format: str) -> str:
        """Generate export filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = export_format if export_format != 'json' else 'json'
        return f"{data_type}_{timestamp}.{extension}"
