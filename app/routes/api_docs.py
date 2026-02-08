# app/routes/api_docs.py
"""
API Documentation and Swagger setup.
"""

from flask import Blueprint, render_template_string, jsonify, current_app
from flasgger import Swagger, swag_from
import yaml

api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')
swagger = Swagger()


def init_swagger(app):
    """Initialize Swagger/Flasgger for API documentation."""
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'api_docs',
                "route": '/api/docs/spec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
        "title": "Project Management System API",
        "description": "Complete API documentation with interactive Swagger UI",
        "version": current_app.config.get('APP_VERSION', '2.0.0'),
        "termsOfService": "/terms",
        "contact": {
            "email": "api-support@example.com"
        }
    }
    
    swagger.init_app(app)
    app.config['SWAGGER'] = swagger_config
    
    return swagger


# API endpoint documentation examples

AUTH_LOGIN_SPEC = {
    'tags': ['Authentication'],
    'summary': 'User Login',
    'description': 'Authenticate user with credentials',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string', 'example': 'johndoe'},
                    'password': {'type': 'string', 'format': 'password'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'user_id': {'type': 'integer'},
                    'username': {'type': 'string'}
                }
            }
        },
        '401': {
            'description': 'Invalid credentials'
        },
        '429': {
            'description': 'Too many login attempts'
        }
    }
}

GET_ISSUES_SPEC = {
    'tags': ['Issues'],
    'summary': 'List Issues',
    'description': 'Get list of all issues with optional filtering',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 25},
        {'name': 'status', 'in': 'query', 'type': 'string', 'enum': ['pending', 'in_progress', 'completed']},
        {'name': 'priority', 'in': 'query', 'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']},
        {'name': 'project_id', 'in': 'query', 'type': 'integer'},
    ],
    'responses': {
        '200': {
            'description': 'List of issues',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'title': {'type': 'string'},
                                'status': {'type': 'string'},
                                'priority': {'type': 'string'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    },
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'page': {'type': 'integer'},
                            'per_page': {'type': 'integer'},
                            'total_items': {'type': 'integer'},
                            'total_pages': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        '401': {'description': 'Unauthorized'},
        '403': {'description': 'Forbidden'}
    }
}

CREATE_ISSUE_SPEC = {
    'tags': ['Issues'],
    'summary': 'Create Issue',
    'description': 'Create a new issue in a project',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['project_id', 'title', 'description'],
                'properties': {
                    'project_id': {'type': 'integer'},
                    'title': {'type': 'string', 'minLength': 5, 'maxLength': 255},
                    'description': {'type': 'string', 'maxLength': 5000},
                    'priority': {
                        'type': 'string',
                        'enum': ['low', 'medium', 'high', 'critical'],
                        'default': 'medium'
                    },
                    'assignee_id': {'type': 'integer'},
                    'due_date': {'type': 'string', 'format': 'date'}
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Issue created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'status': {'type': 'string'},
                            'created_at': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        '400': {'description': 'Invalid input'},
        '401': {'description': 'Unauthorized'},
        '403': {'description': 'Forbidden'}
    }
}


# Helper function to add documentation to routes
def document_endpoint(spec_dict):
    """Decorator to add Swagger documentation to endpoint."""
    def decorator(f):
        f._doc = spec_dict
        return f
    return decorator


# Create documentation blueprint routes
@api_docs_bp.route('/')
def swagger_ui():
    """Serve Swagger UI documentation."""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Documentation</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
            <script>
                window.onload = function() {
                    SwaggerUIBundle({
                        url: "/api/spec.json",
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "StandaloneLayout",
                        deepLinking: true
                    })
                }
            </script>
        </body>
        </html>
    '''), 200


@api_docs_bp.route('/endpoints')
def endpoints_list():
    """Get list of all documented endpoints."""
    endpoints = {
        'authentication': [
            {'method': 'POST', 'path': '/api/v1/auth/login', 'description': 'User login'},
            {'method': 'POST', 'path': '/api/v1/auth/register', 'description': 'User registration'},
            {'method': 'POST', 'path': '/api/v1/auth/logout', 'description': 'User logout'},
        ],
        'issues': [
            {'method': 'GET', 'path': '/api/v1/issues', 'description': 'List all issues'},
            {'method': 'POST', 'path': '/api/v1/issues', 'description': 'Create new issue'},
            {'method': 'GET', 'path': '/api/v1/issues/<id>', 'description': 'Get issue details'},
            {'method': 'PUT', 'path': '/api/v1/issues/<id>', 'description': 'Update issue'},
            {'method': 'DELETE', 'path': '/api/v1/issues/<id>', 'description': 'Delete issue'},
        ],
        'projects': [
            {'method': 'GET', 'path': '/api/v1/projects', 'description': 'List all projects'},
            {'method': 'POST', 'path': '/api/v1/projects', 'description': 'Create new project'},
            {'method': 'GET', 'path': '/api/v1/projects/<id>', 'description': 'Get project details'},
            {'method': 'PUT', 'path': '/api/v1/projects/<id>', 'description': 'Update project'},
            {'method': 'DELETE', 'path': '/api/v1/projects/<id>', 'description': 'Delete project'},
        ],
        'health': [
            {'method': 'GET', 'path': '/health', 'description': 'Health check'},
            {'method': 'GET', 'path': '/health/ready', 'description': 'Readiness check'},
            {'method': 'GET', 'path': '/metrics', 'description': 'Prometheus metrics'},
        ]
    }
    return jsonify(endpoints), 200
