# Python Package Installation Guide

This project has been converted to a proper Python package, providing both modern package-based installation and traditional installation methods.

## 🎯 What Changed?

The project now includes:
- `pyproject.toml` - Modern Python package configuration
- `setup.cfg` - Additional package metadata and tool settings
- `MANIFEST.in` - Package file inclusion rules
- CLI entry points for convenient commands

## 📦 Installation Methods

### Method 1: Package Installation (Recommended)

Install the project as a Python package in development mode:

```bash
# Clone the repository
git clone https://github.com/xploitoverload/project-management.git
cd project-management

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install as editable package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

**Benefits:**
- ✅ CLI commands available globally in your environment
- ✅ Import modules from anywhere in your scripts
- ✅ Automatic dependency management
- ✅ Easy to distribute and deploy
- ✅ Changes reflect immediately in development mode

### Method 2: Traditional Installation (Legacy)

Install dependencies manually:

```bash
# Clone the repository
git clone https://github.com/xploitoverload/project-management.git
cd project-management

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Running the Application

### Using Package Commands (After Method 1)

```bash
# Start the development server
project-management

# Initialize database
pm-init-db
pm-init-db --with-sample-data

# Run database migrations
pm-migrate

# Show all routes
pm-routes
```

### Using Traditional Commands (Works with Both Methods)

```bash
# Start the development server
python run.py
python run.py run

# Initialize database
python run.py init-db
python run.py init-db --with-sample-data

# Run database migrations
python run.py migrate

# Show all routes
python run.py routes

# Open interactive shell
python run.py shell

# Show help
python run.py --help
```

## 📝 Available CLI Commands

| Package Command | Traditional Command | Description |
|----------------|---------------------|-------------|
| `project-management` | `python run.py` | Start the development server |
| `pm-init-db` | `python run.py init-db` | Initialize the database |
| `pm-migrate` | `python run.py migrate` | Run database migrations |
| `pm-routes` | `python run.py routes` | Show all registered routes |
| N/A | `python run.py shell` | Open interactive Python shell |

## 🔧 Configuration

Both installation methods use the same configuration:

1. **Environment Variables** - Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Configuration Classes** - See `config.py` for different environments:
   - `development` - Local development
   - `production` - Production deployment
   - `testing` - Running tests

## 🚢 Deployment

### Render.com / Heroku (Using Package Installation)

Update your `render.yaml` or similar config:

```yaml
buildCommand: pip install .
startCommand: gunicorn run:app --bind 0.0.0.0:$PORT
```

### Docker (Using Package Installation)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000"]
```

### Traditional Deployment

Still works with `requirements.txt`:

```yaml
buildCommand: pip install -r requirements.txt
startCommand: gunicorn run:app --bind 0.0.0.0:$PORT
```

## 📚 Importing in Scripts

After package installation, you can import modules from anywhere:

```python
# Import the application factory
from app import create_app

# Import models
from app.models import User, Project, Issue

# Import services
from app.services.auth_service import AuthService

# Create app instance
app = create_app('development')
```

## 🧪 Running Tests

```bash
# With package installation and dev dependencies
pip install -e ".[dev]"
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 🛠️ Development Workflow

### Recommended (Package Installation)

```bash
# 1. Install in development mode
pip install -e ".[dev]"

# 2. Make your changes to the code

# 3. Changes are immediately available (no reinstall needed)

# 4. Run the app
project-management

# 5. Test your changes
pytest
```

### Traditional

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make your changes to the code

# 3. Run the app
python run.py

# 4. Test your changes
pytest
```

## 📦 Building Distribution Package

To create a distribution package for PyPI or internal use:

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/project-management-system-2.0.0.tar.gz (source)
# - dist/project_management_system-2.0.0-py3-none-any.whl (wheel)
```

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'app'"

- Make sure you installed the package: `pip install -e .`
- Or make sure you're in the project directory when using traditional method

### "Command not found: project-management"

- Make sure you installed the package: `pip install -e .`
- Check if `~/.local/bin` is in your PATH (Linux/Mac)
- Restart your terminal after installation

### "Database file not found"

- Create the instance directory: `mkdir -p instance`
- Initialize the database: `pm-init-db` or `python run.py init-db`

## 📖 Additional Resources

- [README.md](README.md) - Full project documentation
- [pyproject.toml](pyproject.toml) - Package configuration
- [requirements.txt](requirements.txt) - Legacy dependency list
- [config.py](config.py) - Configuration options

## 🔄 Migration from Legacy Setup

If you were using the traditional method:

1. **No breaking changes** - Traditional commands still work
2. **Optional upgrade** - You can continue using `python run.py`
3. **Recommended** - Try the package installation for better experience

To upgrade:
```bash
# In your existing project directory
pip install -e .

# Now you can use both methods!
```

## 💡 Tips

1. **Use package installation for development** - It's more convenient with global CLI commands
2. **Use traditional installation for CI/CD** - If you prefer explicit `requirements.txt`
3. **Both methods are fully supported** - Choose what works best for your workflow
4. **Development mode** - With `pip install -e .`, changes are immediately available without reinstalling
