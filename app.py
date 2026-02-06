# app.py - Main Application Entry Point
"""
Application entry point using Flask Application Factory pattern.
All routes are defined in blueprints under app/routes/.
"""

import os
from app import create_app

# Create application instance using factory
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)