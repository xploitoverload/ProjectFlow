# app/routes/__init__.py
"""Route blueprints for modular routing."""

from .auth import auth_bp
from .main import main_bp
from .admin import admin_bp
from .api import api_bp
from .projects import projects_bp

__all__ = ['auth_bp', 'main_bp', 'admin_bp', 'api_bp', 'projects_bp']
