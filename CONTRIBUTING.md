# Contributing to Project Management System

Thank you for your interest in contributing to the Project Management System! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together and help each other
- **Be professional**: Keep discussions focused and constructive
- **Be inclusive**: Welcome people of all backgrounds and experience levels

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/project-management.git
   cd project-management
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

We welcome contributions in several forms:

### 1. Code Contributions

- Bug fixes
- New features
- Performance improvements
- Code refactoring
- Documentation improvements

### 2. Non-Code Contributions

- Report bugs
- Suggest features
- Improve documentation
- Write tutorials
- Help other users

### 3. Testing

- Write unit tests
- Perform manual testing
- Report test results

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment (venv or virtualenv)
- Redis (optional, for caching features)

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install development dependencies
pip install pytest pytest-cov flake8 black

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your local settings

# 5. Initialize database
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

# 6. Run the application
python run.py
```

### Running with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: Maximum 127 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped and sorted (stdlib, third-party, local)
- **Docstrings**: Google-style for functions and classes

### Code Formatting

Use **Black** for automatic code formatting:

```bash
# Format all Python files
black .

# Check without modifying
black --check .
```

### Linting

Use **Flake8** for linting:

```bash
# Lint all Python files
flake8 . --max-line-length=127 --exclude=venv,env,.venv,.git,__pycache__

# Fix common issues automatically
autopep8 --in-place --aggressive --recursive .
```

### Type Hints

We encourage the use of type hints:

```python
def create_project(name: str, owner_id: int) -> Project:
    """Create a new project.
    
    Args:
        name: Project name
        owner_id: ID of the project owner
        
    Returns:
        Created project object
    """
    project = Project(name=name, owner_id=owner_id)
    db.session.add(project)
    db.session.commit()
    return project
```

## Testing Guidelines

### Writing Tests

We use **pytest** for testing. Tests should be placed in the `tests/` directory:

```python
# tests/test_models.py
import pytest
from app.models import User

def test_create_user():
    """Test user creation."""
    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_password_hashing():
    """Test password hashing and verification."""
    user = User(username="testuser")
    user.set_password("password123")
    assert user.check_password("password123")
    assert not user.check_password("wrongpassword")
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_models.py::test_create_user
```

### Test Coverage

Aim for at least 80% code coverage for new code:

```bash
# Generate coverage report
pytest --cov=app --cov-report=term --cov-report=html

# View HTML report
open htmlcov/index.html  # On macOS
```

## Submitting Changes

### Commit Messages

Write clear and descriptive commit messages:

```
Add user profile edit functionality

- Add profile edit form
- Implement validation
- Add tests for profile updates
- Update documentation

Closes #123
```

**Format:**
- **First line**: Short summary (50 chars or less)
- **Blank line**
- **Body**: Detailed description (wrapped at 72 chars)
- **Footer**: Issue references

### Pull Request Process

1. **Ensure all tests pass**:
   ```bash
   pytest
   flake8 .
   black --check .
   ```

2. **Update documentation** if needed

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub:
   - Use a clear title
   - Describe your changes in detail
   - Reference related issues
   - Add screenshots for UI changes

5. **Respond to review feedback**

6. **Wait for approval** from maintainers

### Pull Request Checklist

- [ ] Code follows the style guidelines
- [ ] All tests pass
- [ ] New code is covered by tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Changes are minimal and focused

## Reporting Bugs

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Try the latest version** to see if it's already fixed
3. **Gather information** about the bug

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.11]
- Browser: [e.g., Chrome 120]

**Additional context**
Any other relevant information.
```

## Feature Requests

We welcome feature suggestions! Please provide:

1. **Clear description** of the feature
2. **Use case**: Why is this feature needed?
3. **Proposed solution**: How should it work?
4. **Alternatives**: Other solutions you've considered
5. **Additional context**: Mockups, examples, etc.

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Mockups, examples, or other context.
```

## Development Workflow

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-bug` - Critical fixes
- `refactor/component-name` - Code refactoring
- `docs/topic` - Documentation updates

### Git Workflow

```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Make changes and commit
git add .
git commit -m "Add new feature"

# 4. Push to your fork
git push origin feature/new-feature

# 5. Open Pull Request
```

## Code Review Process

### As a Contributor

- Be open to feedback
- Respond promptly to comments
- Make requested changes
- Ask questions if unclear

### As a Reviewer

- Be respectful and constructive
- Explain the reasoning behind suggestions
- Approve when ready
- Use appropriate labels

## Project Structure

```
project-management/
├── app/                    # Application package
│   ├── __init__.py        # App factory
│   ├── models.py          # Database models
│   ├── routes/            # Route blueprints
│   ├── static/            # Static files
│   └── templates/         # HTML templates
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── migrations/            # Database migrations
├── .github/               # GitHub workflows
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point
└── README.md             # Project documentation
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Questions?

If you have questions:

1. Check the [README](README.md)
2. Search [existing issues](https://github.com/xploitoverload/project-management/issues)
3. Open a new issue with the `question` label
4. Join our discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Project Management System! 🎉
