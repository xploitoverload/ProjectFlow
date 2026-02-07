# Project Management System with Facial ID Authentication

A professional-grade project management system with integrated facial recognition biometric authentication, role-based access control, and comprehensive security features.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Security Features](#security-features)
- [Facial ID Authentication](#facial-id-authentication)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Features
- Complete project management system with projects, tasks, teams, and issue tracking
- User management with role-based access control (Admin, Developer, Designer, Manager)
- Activity logging and audit trails for all operations
- Real-time dashboard with statistics and analytics
- Team collaboration features with member management

### Authentication & Security
- Traditional username/password authentication with password strength validation
- Two-factor authentication (2FA) using Time-based One-Time Password (TOTP)
- Facial ID biometric authentication using deep learning (CNN + HOG face detection)
- Session management with secure cookie handling
- CSRF protection on all forms
- Rate limiting to prevent brute force attacks
- Security headers via Flask-Talisman

### Facial ID Biometric System
- Face detection using Histogram of Oriented Gradients (HOG) model
- Face encoding using Convolutional Neural Networks (CNN) - 128-dimensional vectors
- Secure face encoding storage with encryption at rest
- Face verification with configurable confidence thresholds (50% minimum)
- Euclidean distance-based matching with strict tolerance (0.4)
- Face enrollment with multi-capture support
- Failed attempt tracking and account lockout protection
- Real-time camera capture using browser WebRTC API
- Professional UI with modern design and responsive layout

### Data Management
- SQLite database with migration support via Alembic/Flask-Migrate
- Secure password hashing using Argon2
- Role-based permission system
- Activity audit trails with timestamps
- Data validation and sanitization

## Architecture

### Directory Structure
```
project-root/
├── app/
│   ├── __init__.py                 # Application factory
│   ├── models.py                   # Database models
│   ├── admin_secure/
│   │   ├── __init__.py
│   │   ├── routes.py              # Admin panel routes
│   │   ├── facial_recognition.py  # Facial ID system
│   │   ├── auth.py                # Authentication logic
│   │   └── decorators.py          # Custom decorators
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py              # Main app routes
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py              # Auth routes
│   ├── security/
│   │   ├── __init__.py
│   │   └── audit.py               # Audit logging
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── facial_login_improved.html
│       ├── admin/
│       └── main/
├── config.py                       # Configuration management
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

### Technology Stack
- **Backend**: Flask 3.0.0 with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL recommended (production)
- **Authentication**: Flask-Login, PyOTP, cryptography
- **Facial Recognition**: face-recognition (dlib), OpenCV, NumPy
- **Security**: Flask-Talisman, Flask-Limiter, Argon2
- **Frontend**: HTML5, CSS3, JavaScript with WebRTC API
- **Web Server**: Gunicorn (production)

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser with WebRTC support (for facial ID features)
- 100MB free disk space (for database and face encodings)

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/project-management-system.git
cd project-management-system
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

### 4. Setup Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
FLASK_ENV=development
SECRET_KEY=your-secure-random-key-here
DATABASE_URL=sqlite:///instance/project_management.db
FACIAL_ID_TOLERANCE=0.4
FACIAL_ID_MIN_CONFIDENCE=0.5
```

### 5. Initialize Database

```bash
python run.py
```

On first run, the application will:
- Create the database structure
- Create an admin user (default: username="admin", password="Admin@123")
- Initialize all tables

**IMPORTANT**: Change the default admin password immediately after first login.

### 6. Run the Application

```bash
python run.py
```

Access the application at: `https://127.0.0.1:5000`

Note: The application uses self-signed SSL certificates for development. Accept the security warning in your browser.

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```
# Flask Configuration
FLASK_ENV=development|production
SECRET_KEY=generate-a-random-secure-key

# Database
DATABASE_URL=sqlite:///instance/project_management.db

# Facial ID Settings
FACIAL_ID_TOLERANCE=0.4              # Face matching distance tolerance
FACIAL_ID_MIN_CONFIDENCE=0.5         # Minimum confidence threshold (0.0-1.0)

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Two-Factor Authentication
OTP_WINDOW_SIZE=1

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_DEFAULT=100/hour

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

### Configuration File (config.py)

Modify `config.py` to change:
- Application name and version
- Database settings
- Password requirements
- Session timeouts
- Security settings

## Usage

### 1. First-Time Setup

1. Start the application
2. Login with default credentials (admin/Admin@123)
3. Change the admin password immediately
4. Create additional users as needed
5. Enroll facial ID for biometric authentication

### 2. Creating Users

1. Go to Admin Panel > User Management
2. Click "Add New User"
3. Fill in username, email, and password
4. Select user role (Admin, Developer, Designer, Manager)
5. Click Create

### 3. Enrolling Facial ID

1. Go to Facial ID Setup
2. Click "Start Enrollment"
3. Allow camera access
4. Position your face in the guide oval
5. Capture 3 different angles/expressions
6. System will verify and save your face
7. You can now login using facial recognition

### 4. Two-Factor Authentication

1. Go to Security Settings
2. Click "Enable 2FA"
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Enter verification code to confirm
5. Save backup codes in a secure location

### 5. Managing Projects

1. Go to Projects section
2. Create new projects or edit existing ones
3. Add team members to projects
4. Track tasks and issues
5. Monitor project progress on dashboard

## API Reference

### Authentication Endpoints

#### Login (POST)
```
POST /login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123",
  "remember_me": true
}

Response: 302 (Redirect to dashboard) or 401 (Invalid credentials)
```

#### Facial ID Login (GET)
```
GET /secure-mgmt-{TOKEN}/facial-login
Response: HTML page with camera interface
```

#### Facial ID Verification (POST)
```
POST /secure-mgmt-{TOKEN}/facial-login-verify
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "confidence": 0.95
}

Response:
{
  "success": true,
  "message": "Face verified successfully",
  "confidence": 0.87,
  "face_id": "1",
  "redirect": "/"
}
```

#### Two-Factor Setup (GET/POST)
```
GET /security/2fa-setup
Response: HTML page with QR code

POST /security/2fa-setup
Content-Type: application/json

{
  "token": "123456"
}

Response: {success: true, backup_codes: [...]}
```

### Project Management Endpoints

#### Get Projects (GET)
```
GET /api/projects
Response: [
  {
    "id": 1,
    "name": "Project Name",
    "description": "Description",
    "status": "active",
    "created_at": "2026-02-07T12:00:00Z"
  }
]
```

#### Create Project (POST)
```
POST /api/projects
Content-Type: application/json

{
  "name": "New Project",
  "description": "Project description",
  "status": "active"
}

Response: {id: 1, ...project data...}
```

## Database Schema

### Core Tables

#### User Table
- id: Primary key
- username: Unique username
- email: Email address
- password_hash: Argon2 hashed password
- role: User role (admin, developer, designer, manager)
- is_active: Account status
- created_at: Creation timestamp
- last_login: Last login time

#### FacialIDData Table
- id: Primary key
- admin_id: Foreign key to User
- facial_encoding: Encrypted 128D CNN vector
- face_preview: Base64 encoded preview image
- encoding_label: Label for this encoding (e.g., "Office", "Home")
- is_verified: Verification status
- enrolled_at: Enrollment timestamp
- verified_at: Verification timestamp
- successful_unlocks: Count of successful authentications
- failed_attempts: Count of failed authentication attempts
- last_unlock_at: Last successful authentication time
- last_failed_attempt_at: Last failed attempt time

#### Project Table
- id: Primary key
- name: Project name
- description: Project description
- owner_id: Foreign key to User (project owner)
- status: Project status (active, archived, completed)
- created_at: Creation timestamp
- updated_at: Last update timestamp

#### Team Table
- id: Primary key
- name: Team name
- description: Team description
- created_at: Creation timestamp

#### Issue Table
- id: Primary key
- title: Issue title
- description: Issue description
- project_id: Foreign key to Project
- assigned_to: Foreign key to User (assignee)
- status: Issue status (open, in_progress, closed, on_hold)
- priority: Priority level (critical, high, medium, low)
- created_at: Creation timestamp
- updated_at: Last update timestamp

#### AuditLog Table
- id: Primary key
- user_id: Foreign key to User
- action: Action type (CREATE, UPDATE, DELETE, LOGIN, LOGOUT)
- entity_type: Type of entity affected (User, Project, Team, Issue)
- entity_id: ID of affected entity
- old_values: Previous values (JSON)
- new_values: New values (JSON)
- timestamp: Action timestamp
- ip_address: IP address of request

## Security Features

### 1. Password Security
- Minimum 12 characters
- Requires uppercase, lowercase, numbers, and special characters
- Argon2 hashing with 4 rounds
- Password history tracking
- Account lockout after 5 failed attempts

### 2. Session Management
- Secure HTTP-only cookies
- CSRF token on all forms
- Session timeout after 30 minutes of inactivity
- Remember-me functionality with secure tokens

### 3. Two-Factor Authentication (2FA)
- Time-based One-Time Password (TOTP) implementation
- QR code generation for authenticator apps
- Backup codes for account recovery
- Optional enforcement per user

### 4. Facial ID Biometric Security
- Encrypted facial encoding storage
- Strict face matching tolerance (0.4)
- Minimum confidence threshold (50%)
- Failed attempt tracking and lockout (5 attempts)
- Distance-based verification using Euclidean metric
- Per-user face encoding isolation

### 5. Data Protection
- Input validation and sanitization with bleach
- SQL injection prevention via SQLAlchemy ORM
- XSS protection via template escaping
- HTTPS/TLS for all connections (enforced in production)

### 6. Audit & Monitoring
- Complete audit logs of all user actions
- Timestamp tracking for all entities
- Failed login attempt logging
- Suspicious activity monitoring
- Rate limiting (100 requests per hour default)

### 7. API Security
- JWT token-based endpoints (optional)
- CORS configuration for API access
- Rate limiting per IP address
- Request size limits

## Facial ID Authentication

### How It Works

The facial ID authentication system provides secure, passwordless login using deep learning:

#### 1. Face Detection (Enrollment & Verification)
- Uses HOG (Histogram of Oriented Gradients) algorithm
- Detects face region in image
- Extracts face bounding box
- Handles multiple faces (selects largest)

#### 2. Face Encoding
- Uses pre-trained CNN (Convolutional Neural Network) model
- Converts face image to 128-dimensional vector
- Captures unique facial features
- Invariant to lighting, angle, and expression changes

#### 3. Face Matching
- Calculates Euclidean distance between vectors
- Compares test encoding against all enrolled encodings
- Tolerance: 0.4 (stricter than default 0.6)
- Confidence threshold: 50% minimum

#### 4. Verification Logic

```
Face Image Input
    |
    v
HOG Face Detection
    |
    v
Extract Face Region
    |
    v
CNN Face Encoding (128D vector)
    |
    v
Calculate Distance from Enrolled Faces
    |
    v
Distance <= 0.4 AND Confidence >= 50%?
    |
    +---> YES: Login User, Set Session
    |
    +---> NO: Reject, Return 401
```

#### 5. Security Measures
- Encrypted storage of face encodings
- Per-user face isolation
- Limit 5 enrollment faces per user
- Lockout after 5 failed attempts
- Timestamp tracking of all authentications
- Failed attempt monitoring

### Enrollment Process

1. User navigates to Facial ID Setup
2. System prompts for camera permission
3. User captures 3 different angles/expressions
4. System detects face in each image
5. System generates 128D encodings
6. Encodings are encrypted and stored
7. Verification email sent
8. User confirms enrollment

### Verification Process

1. User navigates to Facial ID Login
2. System shows camera feed with guide oval
3. User positions face in guide
4. User clicks "Verify"
5. System captures image
6. HOG detects face
7. CNN generates encoding
8. System compares against enrolled faces
9. If match found and confident: logs in user
10. If no match or low confidence: shows error

### Configuration

Adjust facial ID settings in `.env`:

```
# Face matching strictness (0.0-1.0)
# Lower = stricter, Higher = lenient
# Default: 0.4 (secure)
FACIAL_ID_TOLERANCE=0.4

# Minimum confidence to accept match (0.0-1.0)
# Default: 0.5 (50% confidence required)
FACIAL_ID_MIN_CONFIDENCE=0.5
```

### Troubleshooting

**Face Not Detected**
- Ensure adequate lighting
- Position face within guide oval
- Face should be 20-40cm from camera
- Remove sunglasses or obstructions

**Face Not Recognized**
- Enroll faces in similar lighting conditions
- Re-enroll if appearance has changed significantly
- Ensure same angle as enrollment

**Low Confidence**
- Improve camera quality
- Better lighting conditions
- Clearer, frontal face position
- Re-enroll if needed

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Write docstrings for all functions
- Include unit tests for new features
- Ensure all tests pass before submitting PR

### Reporting Issues
- Check if issue already exists
- Provide detailed description
- Include steps to reproduce
- Specify Python version and OS

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review code comments and docstrings

## Acknowledgments

- Flask framework and extensions
- face-recognition library (dlib)
- SQLAlchemy ORM
- All open-source contributors

---

**Version**: 2.0.0
**Last Updated**: February 2026
**Status**: Production Ready
