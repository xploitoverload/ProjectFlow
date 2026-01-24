# 🚀 Project Management System v2.0

A production-grade, enterprise-level project management system built with Flask, featuring modern UI/UX, comprehensive security, and robust architecture.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Security](https://img.shields.io/badge/Security-OWASP%20Compliant-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎨 Modern UI/UX
- **Dark/Light Mode** - Full theme switching with CSS variables
- **Responsive Design** - Mobile-first, works on all devices
- **Accessibility** - WCAG 2.1 AA compliant
- **Modern Design System** - Consistent components and spacing

### 🔐 Enterprise Security
- **OWASP Top 10** - Protection against common vulnerabilities
- **Argon2 Password Hashing** - Industry-leading password security
- **Rate Limiting** - Per-endpoint request throttling
- **CSP Headers** - Content Security Policy protection
- **Session Fingerprinting** - Prevent session hijacking
- **CSRF Protection** - Cross-site request forgery prevention
- **Audit Logging** - Comprehensive activity tracking

### 👥 Role-Based Access Control (RBAC)
- **Super Admin** - Full system access
- **Admin** - User and project management
- **Manager** - Team and project oversight
- **Employee** - Standard project access
- **Viewer** - Read-only access

### 📊 Project Management
- **Kanban Boards** - Visual task management
- **Gantt Charts** - Timeline and milestone tracking
- **Issue Tracking** - JIRA-style workflow management
- **Reports & Analytics** - Team performance insights

### 🛠️ Developer Experience
- **Clean Architecture** - MVC pattern with service layer
- **API v1** - RESTful API with versioning
- **Application Factory** - Flexible Flask configuration
- **CLI Tools** - Database, migrations, and utility commands

---

## 🏗️ Architecture

### Python Package Structure

This project is now structured as an installable Python package with the following architecture:

```
project-management-system/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── middleware/              # Auth decorators, RBAC
│   ├── routes/                  # Blueprint controllers
│   │   ├── auth.py             # Authentication routes
│   │   ├── main.py             # Dashboard, profile
│   │   ├── admin.py            # Admin panel
│   │   ├── projects.py         # Project management
│   │   └── api.py              # REST API v1
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── project_service.py
│   │   ├── issue_service.py
│   │   ├── report_service.py
│   │   └── audit_service.py
│   ├── utils/                  # Utilities
│   │   ├── security.py         # Argon2, sanitization
│   │   └── validators.py       # Input validation
│   └── models/                 # Database models
├── templates/                   # Jinja2 templates
│   ├── admin/                  # Admin panel templates
│   └── components/             # Reusable components
├── static/
│   ├── css/
│   │   └── design-system.css   # Theme & components
│   └── js/                     # Frontend JavaScript
├── pyproject.toml              # Python package configuration
├── setup.cfg                   # Additional package metadata
├── MANIFEST.in                 # Package file inclusion rules
├── config.py                   # Configuration classes
├── models.py                   # SQLAlchemy models
├── run.py                      # Application entry point
└── requirements.txt            # Python dependencies
```

### Installation Benefits

Installing as a package provides:
- ✅ **CLI Commands**: Use `project-management`, `pm-init-db`, etc. from anywhere
- ✅ **Import Anywhere**: Import modules from `app` package in your scripts
- ✅ **Dependency Management**: Automatic handling of all dependencies
- ✅ **Version Control**: Package versioning and distribution
- ✅ **Development Mode**: Changes reflect immediately with `pip install -e .`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or pipenv
- (Optional) Redis for production caching

### Installation

#### Option 1: Install as a Python Package (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/project-management.git
   cd project-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install the package in development mode**
   ```bash
   pip install -e .
   # Or with development dependencies:
   pip install -e ".[dev]"
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   pm-init-db
   # Or use the traditional way:
   python run.py init-db
   ```

6. **Run the application**
   ```bash
   project-management
   # Or use the traditional way:
   python run.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

#### Option 2: Traditional Installation (Legacy)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/project-management.git
   cd project-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   python run.py init-db
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 🔧 CLI Commands

### Package-Based Commands (When installed with `pip install -e .`)

```bash
# Start development server
project-management

# Initialize database
pm-init-db
pm-init-db --with-sample-data

# Run database migrations
pm-migrate

# Show all routes
pm-routes
```

### Traditional Commands (Legacy)

```bash
# Start development server
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

---

## 🔐 Security Configuration

### Password Requirements
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Rate Limits
| Endpoint | Limit |
|----------|-------|
| `/auth/login` | 5/minute |
| `/api/v1/*` | 100/hour |
| Global | 200/day |

### Headers
- Strict-Transport-Security
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

---

## 🌐 API Documentation

### Authentication
```bash
# Login
POST /auth/login
Content-Type: application/json
{
    "email": "user@example.com",
    "password": "your-password"
}

# Logout
POST /auth/logout
```

### Projects API (v1)
```bash
# List projects
GET /api/v1/projects

# Get project
GET /api/v1/projects/{id}

# Create project
POST /api/v1/projects
Content-Type: application/json
{
    "name": "New Project",
    "key": "PROJ",
    "description": "Project description"
}

# Update project
PUT /api/v1/projects/{id}

# Delete project
DELETE /api/v1/projects/{id}
```

### Issues API (v1)
```bash
# List issues
GET /api/v1/projects/{id}/issues

# Create issue
POST /api/v1/projects/{id}/issues

# Update issue status
PATCH /api/v1/issues/{id}/status
```

---

## 🎨 Theming

### Dark Mode
The application supports dark mode with automatic theme detection and manual toggle:

```javascript
// Toggle theme
document.documentElement.dataset.theme = 'dark'; // or 'light'

// Save preference
localStorage.setItem('theme', 'dark');
```

### CSS Variables
Customize the design system in `static/css/design-system.css`:

```css
:root {
    --primary-500: #6366f1;
    --bg-primary: #ffffff;
    /* ... */
}

[data-theme="dark"] {
    --primary-500: #818cf8;
    --bg-primary: #09090b;
    /* ... */
}
```

---

## 🚢 Production Deployment

### Using Gunicorn
```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run production server
gunicorn -w 4 -b 0.0.0.0:8000 "run:create_app('production')"
```

### Environment Variables (Production)
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...
```

### Docker (Coming Soon)
```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 📁 File Structure Reference

| File/Directory | Purpose |
|---------------|---------|
| `run.py` | Application entry point |
| `config.py` | Configuration classes |
| `models.py` | Database models |
| `app/__init__.py` | Application factory |
| `app/routes/` | Blueprint controllers |
| `app/services/` | Business logic |
| `app/middleware/` | Auth & RBAC decorators |
| `app/utils/` | Security & validation |
| `templates/` | Jinja2 templates |
| `static/css/` | Design system |
| `.env.example` | Environment template |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Flask team for the excellent microframework
- OWASP for security best practices
- Tailwind CSS for design inspiration
- The open-source community

---

<p align="center">
  Built with ❤️ for enterprise project management
</p>
