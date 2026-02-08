"""Advanced Reporting API routes."""

from flask import Blueprint, request, jsonify, current_app, send_file
from app.reporting import (
    report_engine, report_builder,
    report_scheduler, export_manager,
    ReportConfig, ReportType, CustomReportConfig, Column, Filter,
    Schedule, ScheduleFrequency, DeliveryMethod
)
import logging
import io

logger = logging.getLogger(__name__)

reporting_bp = Blueprint('reporting', __name__, url_prefix='/api/v1/reporting')


@reporting_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get available report templates."""
    try:
        templates = []
        for name, config in report_engine.report_templates.items():
            templates.append({
                'id': name,
                'name': config.name,
                'type': config.report_type.value,
                'metrics': config.metrics
            })
        
        return jsonify({'templates': templates})
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/create', methods=['POST'])
def create_report():
    """Create a new report."""
    try:
        data = request.json
        report_type = data.get('report_type')
        days = data.get('days', 30)
        created_by = data.get('created_by')
        
        if not all([report_type, created_by]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create config
        config = ReportConfig(
            name=data.get('name', f'{report_type} Report'),
            report_type=ReportType[report_type.upper()],
            date_range_days=days,
            metrics=data.get('metrics', [])
        )
        
        report = report_engine.create_report(config, created_by)
        
        return jsonify({
            'status': 'created',
            'report_id': report.id,
            'title': report.title
        })
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id):
    """Get report by ID."""
    try:
        report = report_engine.get_report(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        return jsonify({
            'id': report.id,
            'title': report.title,
            'created_at': report.created_at,
            'summary': report.summary,
            'sections': report.sections,
            'charts': report.charts
        })
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/list', methods=['GET'])
def list_reports():
    """List all reports."""
    try:
        created_by = request.args.get('created_by')
        reports = report_engine.list_reports(created_by)
        
        return jsonify({
            'total': len(reports),
            'reports': [
                {
                    'id': r.id,
                    'title': r.title,
                    'type': r.config.report_type.value,
                    'created_at': r.created_at,
                    'created_by': r.created_by
                }
                for r in reports
            ]
        })
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a report."""
    try:
        success = report_engine.delete_report(report_id)
        
        return jsonify({
            'status': 'deleted' if success else 'not_found'
        })
    except Exception as e:
        logger.error(f"Error deleting report: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/custom/create', methods=['POST'])
def create_custom_report():
    """Create custom report configuration."""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        data_source = data.get('data_source')
        
        if not all([name, data_source]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        config = CustomReportConfig(
            name=name,
            description=description,
            data_source=data_source
        )
        
        config_id = report_builder.create_custom_report(config)
        
        return jsonify({
            'status': 'created',
            'config_id': config_id
        })
    except Exception as e:
        logger.error(f"Error creating custom report: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/custom/<config_id>/preview', methods=['GET'])
def preview_custom_report(config_id):
    """Get preview of custom report."""
    try:
        preview = report_builder.generate_preview(config_id)
        return jsonify(preview)
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/<report_id>/export', methods=['GET'])
def export_report(report_id):
    """Export report in specified format."""
    try:
        format = request.args.get('format', 'pdf')
        report = report_engine.get_report(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Prepare report data
        report_data = {
            'id': report.id,
            'title': report.title,
            'period': f'Last {report.config.date_range_days} days',
            'sections': report.sections,
            'charts': report.charts
        }
        
        # Export
        result = export_manager.export_report(report_data, format)
        
        if result['status'] != 'success':
            return jsonify(result), 400
        
        # Return file
        if format == 'pdf':
            content = export_manager.export_to_pdf(report_data)
            mime_type = 'application/pdf'
        elif format == 'excel':
            content = export_manager.export_to_excel(report_data)
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif format == 'csv':
            content = export_manager.export_to_csv(report_data)
            mime_type = 'text/csv'
        else:
            content = export_manager.export_to_json(report_data)
            mime_type = 'application/json'
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/schedule/create', methods=['POST'])
def create_schedule():
    """Create report schedule."""
    try:
        data = request.json
        report_config_id = data.get('report_config_id')
        frequency = data.get('frequency')
        
        if not all([report_config_id, frequency]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        schedule = report_scheduler.create_schedule(
            report_config_id=report_config_id,
            frequency=ScheduleFrequency[frequency.upper()],
            hour=data.get('hour', 9),
            minute=data.get('minute', 0),
            delivery_methods=[
                DeliveryMethod[m.upper()]
                for m in data.get('delivery_methods', ['email'])
            ],
            recipients=data.get('recipients', []),
            day_of_week=data.get('day_of_week'),
            day_of_month=data.get('day_of_month')
        )
        
        return jsonify({
            'status': 'created',
            'schedule_id': schedule.id,
            'next_run': schedule.next_run
        })
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/schedule/<schedule_id>/enable', methods=['POST'])
def enable_schedule(schedule_id):
    """Enable a schedule."""
    try:
        success = report_scheduler.enable_schedule(schedule_id)
        
        return jsonify({
            'status': 'enabled' if success else 'not_found'
        })
    except Exception as e:
        logger.error(f"Error enabling schedule: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/schedule/<schedule_id>/disable', methods=['POST'])
def disable_schedule(schedule_id):
    """Disable a schedule."""
    try:
        success = report_scheduler.disable_schedule(schedule_id)
        
        return jsonify({
            'status': 'disabled' if success else 'not_found'
        })
    except Exception as e:
        logger.error(f"Error disabling schedule: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get reporting statistics."""
    try:
        stats = {
            'report_engine': report_engine.get_stats(),
            'builder': report_builder.get_stats(),
            'scheduler': report_scheduler.get_stats(),
            'export': export_manager.get_stats()
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/health', methods=['GET'])
def health():
    """Health check."""
    try:
        return jsonify({
            'status': 'healthy',
            'reports_count': len(report_engine.reports),
            'schedules_count': len(report_scheduler.schedules)
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'error': str(e)}), 500
