# Project Management System with Facial ID Authentication

A professional project management application featuring advanced facial recognition-based authentication, real-time collaboration tools, and comprehensive project tracking capabilities.

## Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

### Core Functionality
- **Project Management**: Create, manage, and track projects with comprehensive workflows
- **Team Collaboration**: Manage team members, assign tasks, and track progress in real-time
- **User Management**: Role-based access control with multiple permission levels
- **Task Tracking**: Create, assign, and monitor project tasks with status updates
- **Activity Logging**: Track all user actions and system events
- **Reporting**: Generate detailed reports on project metrics and team performance

### Security Features
- **Facial ID Authentication**: Biometric-grade facial recognition login
  - Tolerance: 0.4 (strict matching)
  - Minimum confidence: 50%
  - Prevention of false positives from unknown faces
- **Two-Factor Authentication**: Session-based 2FA verification
- **CSRF Protection**: Cross-Site Request Forgery prevention on all forms
- **Password Security**: Bcrypt hashing with salt for all user passwords
- **Encrypted Storage**: Sensitive data encrypted at rest
- **Session Management**: Secure Flask-Login integration with persistent sessions
- **Rate Limiting**: Protection against brute force attacks
- **Security Headers**: Best-practice HTTP security headers

### Advanced Features
- **Facial Recognition Infrastructure**:
  - HOG (Histogram of Oriented Gradients) face detection
  - CNN (Convolutional Neural Network) 128-dimensional face encoding
  - Euclidean distance-based face matching
  - Biometric-grade matching tolerance
  - Multi-angle face enrollment
  
- **Admin Dashboard**:
  - Real-time statistics and key metrics
  - Activity monitoring and audit logs
  - System health indicators
  - User management interface
  - Quick action buttons
  
- **Professional User Interface**:
  - Responsive design for all devices
  - Modern interface with smooth animations
  - Mobile-friendly layouts
  - Accessibility compliance

## System Requirements

- Python 3.8 or higher
- Flask 2.0 or higher
- SQLite3 (default database)
- Modern web browser with camera support (for facial authentication)
- Minimum 100MB disk space for application
- 2GB RAM recommended for optimal performance

### Python Dependencies
See `requirements.txt` for complete list. Key packages:
- Flask: Web framework
- SQLAlchemy: Database ORM
- Flask-Login: User session management
- face_recognition: Facial recognition library
- dlib: Face detection and encoding
- OpenCV: Image processing

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/project-management-facial-id.git
cd project-management-facial-id
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy and configure environment template:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
FLASK_ENV=development
SECRET_KEY=your-secure-secret-key-change-this
DATABASE_URL=sqlite:///app.db
ADMIN_TOKEN=your-secure-admin-token
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
SESSION_TIMEOUT=1800
FACIAL_VERIFICATION_TOLERANCE=0.4
FACIAL_VERIFICATION_MIN_CONFIDENCE=0.5
```

### 5. Initialize Database

```bash
python3
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 6. Run Application

```bash
python3 app.py
```

Access at `https://127.0.0.1:5000`

Default credentials:
- Username: `admin`
- Password: `admin` (Change on first login)

## Configuration

### Environment Variables

Key settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| FLASK_ENV | development | Environment mode (development/production) |
| SECRET_KEY | - | Secret key for session encryption (REQUIRED) |
| DATABASE_URL | sqlite:///app.db | Database connection string |
| ADMIN_TOKEN | - | Secure token for admin panel access |
| SESSION_TIMEOUT | 1800 | Session timeout in seconds (30 minutes) |
| FACIAL_VERIFICATION_TOLERANCE | 0.4 | Face matching tolerance (lower = stricter) |
| FACIAL_VERIFICATION_MIN_CONFIDENCE | 0.5 | Minimum confidence score (0.0-1.0) |
| UPLOAD_FOLDER | uploads | Directory for file uploads |
| MAX_CONTENT_LENGTH | 16777216 | Maximum upload size in bytes (16MB) |

### Application Configuration

Edit `config.py` for advanced settings:

```python
class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    FACIAL_ENCODING_TOLERANCE = 0.4
    FACIAL_CONFIDENCE_THRESHOLD = 0.5
```

## Usage

### Authentication

#### Standard Login
1. Open `https://127.0.0.1:5000/login`
2. Enter username and password
3. Click "Sign In"
4. Complete any required verification

#### Facial ID Login
1. Open login page
2. Click "Sign in with Facial ID"
3. Allow camera access when prompted
4. Position face in the guide oval
5. Click "Verify"
6. System authenticates if face matches
7. Automatically redirected to dashboard

### First-Time Facial ID Setup

1. Log in with credentials
2. Navigate to "Security Settings"
3. Click "Enroll Facial ID"
4. Capture 3 different face angles:
   - Full frontal view
   - 30-degree right angle
   - 30-degree left angle
5. System stores encrypted face encodings
6. Facial ID ready for authentication

### Dashboard

After login, dashboard displays:
- **Overview**: Key metrics and statistics
- **Projects**: List and manage all projects
- **Teams**: Manage members and permissions
- **Tasks**: Create and assign tasks
- **Users**: User account administration
- **Activity Log**: System activity history
- **Settings**: Configure system preferences

## Architecture

### Technology Stack

**Backend**
- Flask: Python web framework
- SQLAlchemy: Database ORM
- Flask-Login: User session and authentication
- Flask-WTF: Forms and CSRF protection
- Werkzeug: Security utilities

**Machine Learning**
- face_recognition: Facial recognition library
- dlib: Face detection and CNN encoding
- OpenCV: Image processing and manipulation
- NumPy: Numerical computations

**Frontend**
- HTML5: Semantic markup
- CSS3: Responsive styling
- JavaScript: Interactive features and camera capture
- Canvas API: Image processing in browser

**Database**
- SQLite: Default lightweight database
- SQLAlchemy ORM: Database abstraction layer

### Directory Structure

```
project-management-facial-id/
├── app/
│   ├── __init__.py              Application initialization
│   ├── models.py                Database models
│   ├── admin_secure/
│   │   ├── routes.py            Admin endpoints and views
│   │   ├── auth.py              Authentication logic
│   │   ├── facial_recognition.py Facial ID system
│   │   └── decorators.py        Custom route decorators
│   ├── static/
│   │   ├── css/                 Stylesheets
│   │   ├── js/                  JavaScript files
│   │   └── images/              Static images
│   └── templates/
│       ├── login.html           Login page
│       ├── dashboard.html       Admin dashboard
│       └── ...                  Additional templates
├── app.py                       Application entry point
├── config.py                    Configuration settings
├── requirements.txt             Python dependencies
├── .env.example                 Environment template
├── .gitignore                   Git ignore rules
├── README.md                    This documentation
└── LICENSE                      MIT License
```

### Face Verification Algorithm

The facial authentication system uses machine learning:

1. **Detection**: HOG cascade identifies faces in image
2. **Encoding**: CNN converts face to 128-dimensional vector
3. **Comparison**: Calculates Euclidean distance between vectors
4. **Scoring**: Converts distance to confidence percentage
5. **Validation**:
   - Distance check: <= 0.4 (strict tolerance)
   - Confidence check: >= 50% (minimum threshold)
6. **Authentication**: User authenticated if both conditions pass

**Security Implementation**:
- Tolerance 0.4 prevents false positives from unknown faces
- 50% confidence minimum ensures only strong matches
- Biometric-grade security suitable for admin access
- Failed attempts tracked and logged for security audit

### Data Models

#### Users
- User ID, Username, Email (unique)
- Password (bcrypt hashed)
- Role (admin, super_admin, developer, designer)
- Permissions (JSON array)
- Timestamps (created, last_login)

#### Facial ID Data
- Facial ID, Admin ID (foreign key)
- Facial encoding (encrypted 128D vector)
- Encoding label (e.g., "home", "office")
- Verification status
- Success/failure counters
- Timestamp tracking
- Device and camera information

#### Projects
- Project ID, Name, Description
- Owner (foreign key to User)
- Status, Priority
- Created/updated timestamps

#### Tasks
- Task ID, Project ID (foreign key)
- Title, Description, Status
- Assigned to (foreign key)
- Due date, Priority
- Timestamps

## Security

### Authentication Security
- Facial ID uses 0.4 tolerance (industry standard)
- 50% confidence threshold prevents false matches
- Failed authentication attempts logged
- Account lockout after 5 failed attempts

### Password Security
- Bcrypt hashing with salt
- Minimum password requirements
- Secure password reset via email
- Password change on first login

### Data Protection
- Database credentials in environment variables
- Sensitive data encrypted at rest
- HTTPS/TLS for data in transit
- CSRF tokens on all forms
- Input validation and sanitization
- SQL injection prevention via ORM

### Session Security
- Secure cookies (HttpOnly, SameSite)
- Configurable timeout (default 30 minutes)
- Session invalidation on logout
- Concurrent session limits for admin accounts

### Best Practices
- Regular security updates of dependencies
- Security headers (HSTS, CSP, X-Frame-Options)
- Rate limiting on authentication endpoints
- Audit logging of sensitive operations
- Regular database backups
- Code review before deployment

## Development

### Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 app.py
```

### Code Style

Follow PEP 8 guidelines. Format code with Black:

```bash
pip install black
black app/
```

### Running Tests

```bash
pip install pytest
pytest tests/
```

## Deployment

### Production Setup

1. Set `FLASK_ENV=production`
2. Generate secure `SECRET_KEY`
3. Configure strong database password
4. Enable HTTPS with valid SSL certificate
5. Set all environment variables
6. Run database migrations
7. Configure backup strategy
8. Enable monitoring and logging

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting

### Facial Recognition Issues

**Face Not Detected**
- Ensure adequate lighting (natural light preferred)
- Position face directly facing camera
- Ensure face occupies most of frame
- Check camera is not obstructed
- Try in well-lit area

**Face Not Recognized**
- Re-enroll facial ID with multiple angles
- Ensure consistent lighting with original enrollment
- Remove accessories obscuring face
- Try again if first attempt fails
- Check camera resolution and quality

**Camera Permission Denied**
- Check browser camera permissions
- Allow camera access in security settings
- Use HTTPS (required for camera)
- Try different browser
- Check system camera permissions

### Database Issues

**Database Locked**
```bash
rm app.db
python3 -c "from app import create_app, db; app = create_app(); db.create_all()"
```

**Connection Error**
- Check DATABASE_URL in .env
- Verify database file exists
- Check file permissions
- Ensure database is not corrupted

### Application Issues

**Port Already in Use**
```bash
lsof -i :5000  # Find process
kill -9 <PID>  # Kill process
```

**SSL Certificate Error**
- Application uses self-signed certificates for development
- Add exception in browser or disable SSL verification in development

## Contributing

Contributions welcome. To contribute:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open Pull Request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
- Open a GitHub issue
- Check existing documentation
- Review troubleshooting section

## Version History

### 1.0.0 (Current)
- Initial release with facial ID authentication
- Project management system
- Admin dashboard and team collaboration
- Complete security implementation
- Professional UI and user experience

---

**Last Updated**: February 8, 2026
