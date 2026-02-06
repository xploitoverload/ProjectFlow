# Security Quick Start Guide

## Overview

This guide provides quick steps to enable security in your Flask application.

## 5-Minute Setup

### 1. Verify Installation
```bash
python verify_security.py
```

Expected: `✓ ALL SECURITY CHECKS PASSED (8/8)`

### 2. Check Security Files

All these should exist:
```
✓ app/security/rbac.py
✓ app/security/tamper_protection.py
✓ app/security/encryption.py
✓ app/security/pki.py
✓ certs/ca/ca.crt
✓ certs/server/server.crt
✓ .env.security
```

### 3. Environment Configuration

The `.env.security` file contains:
```ini
DB_ENCRYPTION_KEY=<your-256-bit-key>
SECRET_KEY=<your-flask-secret>
ENABLE_RBAC=true
ENABLE_TAMPER_PROTECTION=true
PKI_ENABLED=true
```

**Generate new keys if needed:**
```bash
# DB Encryption Key (256-bit hex)
python -c "from app.security.encryption import DatabaseEncryption; print(DatabaseEncryption.generate_key().hex())"

# Flask Secret Key
python -c "import secrets; print(secrets.token_hex(32))"
```

## Protecting Routes

### 1. Admin-Only Routes
```python
from app.security.rbac import admin_only
from flask import render_template

@app.route('/admin/dashboard')
@admin_only
def admin_dashboard():
    return render_template('admin/dashboard.html')
```

Result: Non-admin users get 403 Forbidden ❌

### 2. Specific Permission
```python
from app.security.rbac import rbac_required

@app.route('/api/v1/users', methods=['POST'])
@rbac_required('manage_users')
def create_user():
    # Only users with 'manage_users' permission
    pass
```

### 3. Role-Level Check
```python
from app.security.rbac import team_lead_or_admin

@app.route('/api/v1/team/analytics')
@team_lead_or_admin
def team_analytics():
    # Only team_lead or admin
    pass
```

## Using Encryption

### Auto-Encrypt Fields
```python
from app.security.encryption import EncryptedField
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EncryptedField)  # Auto-encrypted!
    ssn = db.Column(EncryptedField)
```

Fields encrypt on save, decrypt on read automatically.

### Manual Encryption
```python
from app.security.encryption import DatabaseEncryption

enc = DatabaseEncryption(encryption_key)

# Encrypt
secret = enc.encrypt('sensitive data')

# Decrypt
data = enc.decrypt(secret)
```

## Checking Permissions

### In Routes
```python
from app.security.rbac import has_permission
from flask import current_user, abort

@app.route('/data')
def view_data():
    if not has_permission(current_user, 'view_data'):
        abort(403)
    
    return jsonify({'data': 'restricted'})
```

### Get User Role
```python
from app.security.rbac import get_user_role

role = get_user_role(current_user)
print(f"User is: {role}")  # viewer, user, manager, team_lead, admin, super_admin
```

## Role Reference

```
Level 5: super_admin    ← System-level access
         ↓
Level 4: admin          ← Full administrative
         ↓
Level 3: team_lead      ← Team management
         ↓
Level 2: manager        ← Department management
         ↓
Level 1: user           ← Basic operations
         ↓
Level 0: viewer         ← Read-only access
```

Lower levels CAN'T access higher level features.

## Available Permissions

```python
# All permissions by role:

viewer:
  - view_dashboard

user:
  - view_dashboard
  - create_user_report

manager:
  - view_dashboard
  - create_user_report
  - view_team_dashboard
  - manage_team_members

team_lead:
  - [all manager permissions]
  - view_team_analytics
  - manage_team_projects

admin:
  - [all team_lead permissions]
  - view_admin_dashboard
  - manage_users
  - view_user_tracking
  - manage_security
  - view_audit_logs
  - manage_roles

super_admin:
  - [all admin permissions]
  - system_settings
```

## Security Decorators

### @admin_only
```python
@app.route('/admin')
@admin_only
def admin_panel():
    pass
```
Only `admin` and `super_admin` can access.

### @super_admin_only
```python
@app.route('/system/settings')
@super_admin_only
def system_settings():
    pass
```
Only `super_admin` can access.

### @rbac_required(permission)
```python
@app.route('/sensitive')
@rbac_required('manage_users')
def sensitive_op():
    pass
```
User must have the specified permission.

### @team_lead_or_admin
```python
@app.route('/team/analytics')
@team_lead_or_admin
def team_analytics():
    pass
```
User must be `team_lead`, `admin`, or `super_admin`.

## Audit Logging

All security events are logged automatically.

### View Logs
```bash
tail -f logs/security_audit.log
```

### Log Contents
```
INFO: User admin logged in
WARNING: Failed login attempt for user: john
ERROR: SQL injection detected in parameter: search
CRITICAL: Unauthorized access attempt to /admin/users
```

## Request Signing (Advanced)

For API clients that need to sign requests:

### Python
```python
import hmac
import hashlib
import json
from datetime import datetime

def sign_request(data, secret_key):
    timestamp = int(datetime.now().timestamp() * 1000)
    message = f"{json.dumps(data, sort_keys=True)}{timestamp}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'signature': signature,
        'timestamp': timestamp
    }

# Use in request
data = {'username': 'john'}
sig_data = sign_request(data, SECRET_KEY)

headers = {
    'X-Request-Signature': sig_data['signature'],
    'X-Request-Timestamp': sig_data['timestamp']
}

response = requests.post('/api/v1/users', 
    json=data, 
    headers=headers
)
```

### JavaScript
```javascript
async function signRequest(data, secretKey) {
    const timestamp = Date.now();
    const message = JSON.stringify(data) + timestamp;
    
    const encoder = new TextEncoder();
    const msgBuffer = encoder.encode(message);
    const keyBuffer = encoder.encode(secretKey);
    
    const hashBuffer = await crypto.subtle.sign(
        'HMAC',
        await crypto.subtle.importKey(
            'raw', keyBuffer, 
            {name: 'HMAC', hash: 'SHA-256'},
            false, ['sign']
        ),
        msgBuffer
    );
    
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const signature = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    
    return {signature, timestamp};
}

// Use in fetch
const data = {username: 'john'};
const {signature, timestamp} = await signRequest(data, SECRET_KEY);

const response = await fetch('/api/v1/users', {
    method: 'POST',
    headers: {
        'X-Request-Signature': signature,
        'X-Request-Timestamp': timestamp
    },
    body: JSON.stringify(data)
});
```

## HTTPS Configuration

Run app with SSL:

```python
from flask import Flask

app = Flask(__name__)

# Option 1: Development
app.run(
    ssl_context=('certs/server/server.crt', 'certs/server/server.key'),
    debug=True
)

# Option 2: Production (gunicorn)
# gunicorn --certfile=certs/server/server.crt --keyfile=certs/server/server.key app:app
```

Now access via: `https://localhost/`

## Troubleshooting

### "Module not found" error
```bash
# Install dependencies
pip install cryptography flask flask-login sqlalchemy
```

### "No such file or directory: .env.security"
```bash
# Create environment file
touch .env.security
# Add keys manually or run setup
python setup_security.py
```

### "Certificate verification failed"
```bash
# Regenerate certificates
rm -rf certs/
python -c "from app.security.pki import PKIManager; PKIManager().generate_certificate_chain()"
```

### "Invalid DB_ENCRYPTION_KEY"
```bash
# Generate new key
python -c "from app.security.encryption import DatabaseEncryption; print(DatabaseEncryption.generate_key().hex())"
# Add to .env.security
```

## Common Tasks

### Change User Role
```python
from app import db
from app.models import User

user = User.query.filter_by(email='john@example.com').first()
user.role = 'admin'
db.session.commit()
```

### Check User Permissions (Debug)
```python
from app.security.rbac import ROLE_PERMISSIONS

role = user.role
print(f"Permissions for {role}:")
for perm in ROLE_PERMISSIONS.get(role, []):
    print(f"  - {perm}")
```

### View All Audit Logs
```bash
grep -i "critical\|error\|warning" logs/security_audit.log
```

### Reset Encryption Key
```bash
# ⚠️ WARNING: Will require re-encrypting all database fields!

# 1. Backup database
cp database.db database.db.backup

# 2. Generate new key
python -c "from app.security.encryption import DatabaseEncryption; print(DatabaseEncryption.generate_key().hex())"

# 3. Update .env.security
# 4. Re-encrypt fields (custom migration needed)
```

## Best Practices

✅ **DO**:
- Keep .env.security secret
- Rotate keys every 6-12 months
- Monitor audit logs daily
- Test permission changes
- Keep dependencies updated

❌ **DON'T**:
- Commit .env.security to git
- Use same key everywhere
- Ignore audit warnings
- Deploy with debug=True
- Use weak passwords

## Quick Commands

```bash
# Verify security
python verify_security.py

# View audit log
tail -f logs/security_audit.log

# Generate new DB key
python -c "from app.security.encryption import DatabaseEncryption; print(DatabaseEncryption.generate_key().hex())"

# Generate new secret
python -c "import secrets; print(secrets.token_hex(32))"

# Check user role in shell
python
>>> from app.models import User
>>> user = User.query.first()
>>> print(user.role)
```

---

## For More Details

- **Full Guide**: [SECURITY_IMPLEMENTATION_GUIDE.md](SECURITY_IMPLEMENTATION_GUIDE.md)
- **Status Report**: [SECURITY_HARDENING_COMPLETE.md](SECURITY_HARDENING_COMPLETE.md)
- **Verification**: `python verify_security.py`
