# app/routes/custom_fields_routes.py
"""
Custom Fields & Metadata API Routes
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from app.metadata.custom_fields import custom_field_manager


def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.user_id = request.headers.get('X-User-ID', 'guest')
        return f(*args, **kwargs)
    return decorated_function


fields_bp = Blueprint('custom_fields', __name__, url_prefix='/api/v1/fields')


@fields_bp.route('/create', methods=['POST'])
@require_auth
def create_field():
    """Create custom field."""
    try:
        data = request.get_json()
        
        field = custom_field_manager.create_field(
            name=data.get('name', ''),
            field_type=data.get('field_type', 'text'),
            description=data.get('description', ''),
            required=data.get('required', False),
            options=data.get('options', [])
        )
        
        return jsonify({
            'status': 'success',
            'field': field.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/<field_id>', methods=['GET'])
@require_auth
def get_field(field_id):
    """Get field."""
    try:
        field = custom_field_manager.get_field(field_id)
        
        if not field:
            return jsonify({'error': 'Field not found'}), 404
        
        return jsonify({
            'status': 'success',
            'field': field.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/list', methods=['GET'])
@require_auth
def list_fields():
    """List all fields."""
    try:
        fields = custom_field_manager.list_fields()
        
        return jsonify({
            'status': 'success',
            'fields': fields,
            'total': len(fields)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/<field_id>/update', methods=['POST'])
@require_auth
def update_field(field_id):
    """Update field."""
    try:
        data = request.get_json()
        success = custom_field_manager.update_field(field_id, **data)
        
        if not success:
            return jsonify({'error': 'Field not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Field updated'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/templates/create', methods=['POST'])
@require_auth
def create_template():
    """Create field template."""
    try:
        data = request.get_json()
        
        template = custom_field_manager.create_template(
            name=data.get('name', ''),
            description=data.get('description', ''),
            field_ids=data.get('field_ids', [])
        )
        
        return jsonify({
            'status': 'success',
            'template': template.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/values/set', methods=['POST'])
@require_auth
def set_value():
    """Set field value."""
    try:
        data = request.get_json()
        
        success = custom_field_manager.set_field_value(
            entity_type=data.get('entity_type', ''),
            entity_id=data.get('entity_id', ''),
            field_id=data.get('field_id', ''),
            value=data.get('value')
        )
        
        if not success:
            return jsonify({'error': 'Failed to set value'}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Value set'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/values/<entity_type>/<entity_id>', methods=['GET'])
@require_auth
def get_entity_values(entity_type, entity_id):
    """Get entity field values."""
    try:
        values = custom_field_manager.get_entity_values(entity_type, entity_id)
        
        return jsonify({
            'status': 'success',
            'values': values,
            'total': len(values)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fields_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get metadata statistics."""
    try:
        stats = custom_field_manager.get_metadata_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
