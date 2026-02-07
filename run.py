#!/usr/bin/env python3
"""
Project Management System - Application Entry Point
====================================================

This is the main entry point for the Project Management application.
It uses the application factory pattern for flexibility and testability.

Usage:
------
Development:
    python run.py
    
Production (with Gunicorn):
    gunicorn -w 4 -b 0.0.0.0:8000 "run:create_app('production')"
    
Environment Variables:
----------------------
    FLASK_ENV       : development | production | testing (default: development)
    SECRET_KEY      : Application secret key (required in production)
    DATABASE_URL    : Database connection string
    REDIS_URL       : Redis URL for caching and rate limiting
    
For more configuration options, see config.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_app(config_name=None):
    """Create and configure the Flask application.
    
    This function is the main application factory, suitable for use
    with Gunicorn, pytest, and other WSGI servers.
    
    Args:
        config_name: Configuration to use (development, production, testing)
                    Defaults to FLASK_ENV environment variable
    
    Returns:
        Flask application instance
    """
    from app import create_app as factory
    return factory(config_name)


def run_development_server():
    """Run the development server with debug mode enabled."""
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Check for HTTPS certificates
    use_https = False
    ssl_context = None
    protocol = 'http'
    
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        use_https = True
        protocol = 'https'
        ssl_context = ('cert.pem', 'key.pem')
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                 Project Management System v2.0                    ║
╠══════════════════════════════════════════════════════════════════╣
║  Environment: {config_name:<15}                                  ║
║  Server:      {protocol}://{host}:{port:<5}                             ║
║  Debug Mode:  {'Enabled' if config_name == 'development' else 'Disabled':<8}                                        ║
║  SSL/TLS:     {'Enabled (for camera access)' if use_https else 'Disabled':<8}                             ║
║                                                                  ║
║  📝 Access via HTTPS ONLY: https://localhost:5000/              ║
║     (HTTP requests will be redirected to HTTPS)                 ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Create the application
    app = create_app(config_name)
    
    # If HTTPS is enabled, run on HTTPS only (HTTP redirect handled by Flask middleware)
    # Run the development server
    app.run(
        host=host,
        port=port,
        debug=config_name == 'development',
        threaded=True,
        use_reloader=False,
        ssl_context=ssl_context if use_https else None
    )


def init_database():
    """Initialize the database with tables and sample data."""
    
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        from app import db
        
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if we should add sample data
        if '--with-sample-data' in sys.argv:
            print("Adding sample data...")
            try:
                from create_sample_data import create_sample_data
                create_sample_data()
                print("✓ Sample data added successfully!")
            except ImportError:
                print("⚠ Sample data script not found")
            except Exception as e:
                print(f"✗ Error adding sample data: {e}")


def run_migrations():
    """Run database migrations."""
    
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        try:
            from flask_migrate import upgrade
            upgrade()
            print("✓ Migrations applied successfully!")
        except Exception as e:
            print(f"✗ Error running migrations: {e}")


def show_routes():
    """Display all registered routes."""
    
    app = create_app('development')
    
    print("\n📍 Registered Routes:")
    print("=" * 80)
    
    rules = sorted(app.url_map.iter_rules(), key=lambda x: str(x))
    
    for rule in rules:
        methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"  {rule.endpoint:<40} {methods:<15} {rule}")
    
    print("=" * 80)
    print(f"Total routes: {len(list(app.url_map.iter_rules()))}")


def main():
    """Main entry point with CLI support."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'run':
            run_development_server()
        elif command == 'init-db':
            init_database()
        elif command == 'migrate':
            run_migrations()
        elif command == 'routes':
            show_routes()
        elif command == 'shell':
            app = create_app('development')
            with app.app_context():
                import code
                code.interact(local=dict(app=app, db=app.extensions['sqlalchemy']))
        elif command == '--help' or command == '-h':
            print(__doc__)
            print("""
Commands:
---------
    run             Start the development server
    init-db         Initialize the database
    migrate         Run database migrations
    routes          Show all registered routes
    shell           Open an interactive Python shell with app context
    --help, -h      Show this help message
            """)
        else:
            print(f"Unknown command: {command}")
            print("Use --help for available commands")
            sys.exit(1)
    else:
        # Default: run the development server
        run_development_server()


# WSGI entry point for production servers
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    main()
