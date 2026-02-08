# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to the repository owner. All security vulnerabilities will be promptly addressed.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- Confirmation of receipt within 48 hours
- An initial assessment of the vulnerability within 7 days
- Regular updates on the progress toward a fix and full announcement
- Notification when the vulnerability is fixed

## Security Best Practices

When deploying this application:

1. **Always use HTTPS** in production
2. **Set a strong SECRET_KEY** - Never use the default
3. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt` regularly
4. **Use environment variables** for sensitive configuration
5. **Enable rate limiting** to prevent brute force attacks
6. **Regular backups** of your database
7. **Monitor logs** for suspicious activity
8. **Use strong passwords** and enable 2FA for admin accounts
9. **Keep Python and system packages updated**
10. **Use Redis** for session storage and caching in production

## Security Features

This application includes:

- ✅ Password hashing with Argon2
- ✅ CSRF protection on all forms
- ✅ XSS prevention with bleach
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Rate limiting on authentication endpoints
- ✅ Security headers (via Flask-Talisman)
- ✅ Session security with secure cookies
- ✅ Input validation and sanitization
- ✅ Two-factor authentication (TOTP)
- ✅ Facial recognition authentication (optional)

## Known Limitations

- Facial recognition features require proper lighting and camera setup
- SQLite is suitable for development but PostgreSQL recommended for production
- Rate limiting requires Redis in production

## Contact

For security concerns, contact: [Repository Owner]

## Acknowledgments

We appreciate the security research community and all responsible disclosures.
