# Security Implementation Guide

## Overview

This guide explains the comprehensive security framework implemented in the Project Management application. The security system includes:

1. **Role-Based Access Control (RBAC)**
2. **Database Encryption (AES-256-GCM)**
3. **Request Tamper Protection (HMAC-SHA256)**
4. **Public Key Infrastructure (PKI)**

---

## 1. Role-Based Access Control (RBAC)

### Role Hierarchy

The system implements a 6-level role hierarchy:

```
Level 0: viewer        (Read-only access)
Level 1: user          (Basic user operations)
Level 2: manager       (Team management)
Level 3: team_lead     (Advanced team operations)
Level 4: admin         (Full administrative access)
Level 5: super_admin   (System-level access)
```

### User Roles and Permissions

#### Viewer (Level 0)
- `view_dashboard`: View own dashboard

#### User (Level 1)
- `view_dashboard`: View own dashboard
- `create_user_report`: Create personal reports

#### Manager (Level 2)
- All User permissions +
- `view_team_dashboard`: View team metrics
- `manage_team_members`: Manage team roster

#### Team Lead (Level 3)
- All Manager permissions +
- `view_team_analytics`: Advanced analytics
- `manage_team_projects`: Manage team projects

#### Admin (Level 4)
- All Team Lead permissions +
- `view_admin_dashboard`: Full admin dashboard
- `manage_users`: Create/edit/delete users
- `view_user_tracking`: User activity tracking
- `manage_security`: Security settings
- `view_audit_logs`: Security audit logs
- `manage_roles`: Assign user roles

#### Super Admin (Level 5)
- All Admin permissions +
- `system_settings`: Modify system configuration
- All security and system-level operations

### Implementation

The RBAC system is implemented in `app/security/rbac.py`:

```python
from app.security.rbac import rbac_required, admin_only, super_admin_only
from flask import current_user
from functools import wraps

# Protect routes with decorators
@app.route('/admin/dashboard')
@admin_only
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Require specific permission
@app.route('/api/v1/users')
@rbac_required('manage_users')
def list_users():
    return jsonify(users)

# Require team_lead or admin
@app.route('/api/v1/team/analytics')
@team_lead_or_admin
def team_analytics():
    return jsonify(analytics)
```

### Checking Permissions Programmatically

```python
from app.security.rbac import has_permission, get_user_role

# Check if user has permission
if has_permission(current_user, 'view_user_tracking'):
    # Show tracking data
    pass

# Get user's role level
role = get_user_role(current_user)
print(f"User role: {role}")
```

---

## 2. Database Encryption (AES-256-GCM)

### Overview

Sensitive database fields are automatically encrypted using AES-256-GCM, a authenticated encryption mode that prevents tampering.

### Configuration

```python
# In app/__init__.py
from app.security.encryption import DatabaseEncryption

# Initialize encryption
db_key = os.getenv('DB_ENCRYPTION_KEY')
db_encryption = DatabaseEncryption(db_key)

app.db_encryption = db_encryption
```

### Encrypting Fields

Use the `EncryptedField` SQLAlchemy type:

```python
from app.security.encryption import EncryptedField
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    
    # Encrypted field - transparent encryption/decryption
    email = db.Column(EncryptedField, nullable=False, unique=True)
    phone = db.Column(EncryptedField)
    ssn = db.Column(EncryptedField)
```

### Manual Encryption

```python
from app.security.encryption import DatabaseEncryption

enc = DatabaseEncryption(encryption_key)

# Encrypt
encrypted_email = enc.encrypt('user@example.com')

# Decrypt
original_email = enc.decrypt(encrypted_email)
```

### Algorithm Details

- **Algorithm**: AES-256-GCM (Advanced Encryption Standard, 256-bit)
- **Mode**: GCM (Galois/Counter Mode) - authenticated encryption
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Key Size**: 256 bits (32 bytes)
- **IV Size**: 96 bits (12 bytes, random per encryption)
- **Authentication Tag**: 128 bits (16 bytes)
- **Salt**: 128 bits (16 bytes, random per key derivation)
- **Iterations**: 100,000 (PBKDF2)

### Security Properties

✅ **Confidentiality**: Only authorized parties can read encrypted data
✅ **Integrity**: Authentication tag prevents tampering
✅ **Authenticity**: GCM provides built-in authentication
✅ **Non-repudiation**: Encryption proves data wasn't modified

---

## 3. Request Tamper Protection (HMAC-SHA256)

### Overview

All critical requests are signed with HMAC-SHA256 and verified server-side. This prevents:
- Request tampering
- Replay attacks
- Man-in-the-middle attacks

### Configuration

```python
# In app/__init__.py
from app.security.tamper_protection import TamperProtection

# Initialize tamper protection
tamper_protection = TamperProtection(app.config['SECRET_KEY'])
app.tamper_protection = tamper_protection

# Register middleware
@app.before_request
def verify_request_integrity():
    if request.method in ['POST', 'PUT', 'DELETE']:
        tamper_protection.verify_request_integrity(request)
```

### Protecting Routes

```python
from app.security.tamper_protection import require_signature

@app.route('/api/v1/users', methods=['POST'])
@require_signature
def create_user():
    data = request.get_json()
    # Process signed request
    return jsonify({'status': 'created'})
```

### Client-Side Request Signing

```javascript
// Sign request on client
const data = { name: 'John', email: 'john@example.com' };
const timestamp = Date.now();
const signature = generateHMAC(data, SECRET_KEY, timestamp);

// Send with signature header
fetch('/api/v1/users', {
    method: 'POST',
    headers: {
        'X-Request-Signature': signature,
        'X-Request-Timestamp': timestamp,
    },
    body: JSON.stringify(data)
});
```

### Request Validation

```python
from app.security.tamper_protection import RequestValidator

validator = RequestValidator()

# Validate email
if validator.validate_email('user@example.com'):
    # Valid email
    pass

# Detect suspicious patterns
if validator.detect_suspicious_activity(request.data):
    logger.warning("Suspicious activity detected")
```

### Algorithm Details

- **Signing**: HMAC-SHA256
- **Comparison**: Constant-time comparison (timing-safe)
- **Timestamp Window**: 5 minutes (prevents replay attacks)
- **Validation**: JSON schema, SQL injection patterns, XSS patterns

### Security Properties

✅ **Integrity**: HMAC detects any modifications
✅ **Replay Prevention**: Timestamp window prevents reuse
✅ **Attack Detection**: Pattern detection for SQLi, XSS, path traversal
✅ **Audit Logging**: All security events logged

---

## 4. Public Key Infrastructure (PKI)

### Overview

The PKI system manages X.509 certificates for identity verification and TLS/SSL communication.

### Certificate Structure

```
certs/
├── ca/                    # Certificate Authority
│   ├── ca.crt            # CA certificate (10-year validity)
│   └── ca.key            # CA private key (2048-bit RSA)
├── server/               # Server certificates
│   ├── server.crt        # Server certificate (1-year validity)
│   ├── server.key        # Server private key
│   └── server.csr        # Certificate signing request
└── client/               # Client certificates
    ├── client.crt        # Client certificate
    └── client.key        # Client private key
```

### Generate Certificates

```python
from app.security.pki import PKIManager

pki = PKIManager()

# Generate complete certificate chain
pki.generate_certificate_chain()
```

This creates:
1. **CA Certificate**: Self-signed root certificate (valid 10 years)
2. **Server Certificate**: Signed by CA (valid 1 year)
   - Subject Alternative Names: localhost, 127.0.0.1, admin.local
3. **Client Certificates**: Signed by CA (customizable validity)

### Use in Flask

```python
# In Flask app for HTTPS
if app.config.get('USE_PKI'):
    from app.security.pki import get_pki_manager
    
    pki = get_pki_manager()
    
    # Run with SSL
    app.run(
        ssl_context=(
            'certs/server/server.crt',
            'certs/server/server.key'
        ),
        host='0.0.0.0',
        port=443
    )
```

### Certificate Validation

```python
from app.security.pki import PKIManager

pki = PKIManager()

# Load and verify certificate
try:
    cert = pki._load_certificate('server/server.crt')
    is_valid = pki.verify_certificate(cert)
    
    if is_valid:
        print(f"Certificate valid")
        print(f"Subject: {cert.subject}")
        print(f"Expires: {cert.not_valid_after}")
except Exception as e:
    print(f"Certificate verification failed: {e}")
```

### Algorithm Details

- **Key Type**: RSA (Rivest-Shamir-Adleman)
- **Key Size**: 2048 bits
- **Signature Algorithm**: SHA-256
- **CA Validity**: 10 years
- **Server Certificate Validity**: 1 year
- **SANs**: localhost, 127.0.0.1, admin.local
- **Format**: X.509 v3 (DER encoded)

### Security Properties

✅ **Authentication**: Verify server/client identity
✅ **Encryption**: HTTPS/TLS support
✅ **Chain of Trust**: CA-signed certificates
✅ **Revocation Ready**: Support for CRLs

---

## Security Integration Checklist

- [ ] RBAC decorators applied to all admin routes
- [ ] Database encryption initialized in app factory
- [ ] Tamper protection middleware registered
- [ ] Environment variables configured (.env.security)
- [ ] PKI certificates generated
- [ ] SSL/TLS configured for HTTPS
- [ ] Audit logging enabled
- [ ] Security verification tests passing (8/8 checks)

## Running Security Verification

```bash
python verify_security.py
```

Expected output:
```
Result: 8/8 checks passed
✓ ALL SECURITY CHECKS PASSED
```

## Security Best Practices

1. **Never commit secrets**: Keep DB_ENCRYPTION_KEY in .env.security
2. **Rotate keys regularly**: Regenerate encryption keys periodically
3. **Audit logs**: Review security_audit.log regularly
4. **Certificate expiry**: Monitor certificate expiration dates
5. **Update dependencies**: Keep cryptography library updated
6. **Least privilege**: Always assign minimum required permissions
7. **Principle of defense in depth**: Use multiple security layers

---

## Troubleshooting

### Module Import Errors
```
ImportError: cannot import name 'PBKDF2HMAC'
```
**Solution**: Update cryptography library: `pip install --upgrade cryptography>=41.0.0`

### Certificate Errors
```
OSError: [Errno 2] No such file or directory: 'certs/ca/ca.crt'
```
**Solution**: Run PKI initialization: `python setup_security.py`

### Encryption Key Errors
```
ValueError: Invalid DB_ENCRYPTION_KEY
```
**Solution**: Generate new key: `python -c "from app.security.encryption import DatabaseEncryption; print(DatabaseEncryption.generate_key().hex())"`

---

## References

- [PBKDF2 Key Derivation](https://tools.ietf.org/html/rfc2898)
- [AES-256-GCM Encryption](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
- [HMAC-SHA256 Authentication](https://tools.ietf.org/html/rfc4868)
- [X.509 Certificates](https://en.wikipedia.org/wiki/X.509)
- [Cryptography.io Documentation](https://cryptography.io/)
