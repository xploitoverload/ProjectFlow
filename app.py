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
    # Check for HTTPS certificates for camera access
    cert_file = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_file = os.path.join(os.path.dirname(__file__), 'key.pem')
    
    ssl_context = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # Run with HTTPS if certificates exist
        ssl_context = (cert_file, key_file)
        app.run(debug=False, host='0.0.0.0', port=5000, ssl_context=ssl_context)
    else:
        # Run on localhost with HTTP as fallback (localhost still allows camera access)
        app.run(debug=False, host='127.0.0.1', port=5000)