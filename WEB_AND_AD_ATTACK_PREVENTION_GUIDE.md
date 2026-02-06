# Web Attack & Ad Attack Prevention - Complete Guide

## Overview

This comprehensive security solution protects your Flask application against:
- **OWASP Top 10 vulnerabilities**
- **Web attacks** (XSS, CSRF, SQL Injection, XXE, Command Injection, etc.)
- **Ad attacks** (Click fraud, impression fraud, malware)
- **Compliance requirements** (GDPR, CCPA, PCI-DSS, HIPAA, ISO27001, SOC2)

---

## 🛡️ Security Modules

### 1. Web Attack Prevention (`app/security/web_attack_prevention.py`)

**Attack Types Covered:**
- SQL Injection
- Cross-Site Scripting (XSS)
- Path Traversal
- LDAP Injection
- XML External Entity (XXE)
- Command Injection
- NoSQL Injection
- Log4j/JNDI Injection
- Header Injection
- CSRF (Cross-Site Request Forgery)
- Clickjacking
- Open Redirect

**Key Classes:**

#### WebAttackDetection
```python
from app.security.web_attack_prevention import WebAttackDetection

# Detect SQL injection
if WebAttackDetection.detect_sql_injection(user_input):
    abort(400)

# Detect XSS
if WebAttackDetection.detect_xss(user_input):
    abort(400)

# Comprehensive attack detection
if WebAttackDetection.detect_all_attacks(user_input):
    abort(400)
```

#### InputSanitizer
```python
from app.security.web_attack_prevention import InputSanitizer

# Sanitize HTML (removes dangerous tags/attributes)
clean_html = InputSanitizer.sanitize_html(user_html)

# Escape text for safe display
safe_text = InputSanitizer.sanitize_text(user_text)

# Validate and sanitize URLs
safe_url = InputSanitizer.sanitize_url(user_url)

# Sanitize uploaded filenames
safe_filename = InputSanitizer.sanitize_filename(file.filename)

# Validate email
if InputSanitizer.sanitize_email(email):
    # Email is valid
```

#### File Upload Protection
```python
from app.security.web_attack_prevention import FileUploadProtection

# Check if file extension is allowed
if FileUploadProtection.is_allowed_file(filename, 'images'):
    # Process file
    valid, msg = FileUploadProtection.validate_file(file_obj)
```

#### Decorators
```python
from app.security.web_attack_prevention import validate_request_input

@app.route('/submit', methods=['POST'])
@validate_request_input  # Validates all input parameters
def submit_form():
    # Safe to use request parameters
    pass
```

---

### 2. Ad Attack Prevention (`app/security/ad_attack_prevention.py`)

**Attack Types Covered:**
- Click Fraud
- Impression Fraud
- Malware in Ads
- Cookie Stuffing
- Redirect Hijacking
- Silent Installation

**Key Classes:**

#### AdFraudDetection
```python
from app.security.ad_attack_prevention import AdFraudDetection

# Detect click fraud
click_data = {
    'ip_address': '192.168.1.1',
    'user_agent': 'Mozilla/5.0...',
    'referer': 'https://example.com',
    'timestamp': datetime.now(),
    'click_history': []
}
fraud_result = AdFraudDetection.detect_click_fraud(click_data)
if fraud_result['is_fraud']:
    logger.warning(f"Click fraud detected: {fraud_result['details']}")

# Detect impression fraud
impression_data = {
    'visibility_ratio': 0.75,
    'in_viewport': True,
    'layering_index': 1,
    'viewport_size': 100000,
    'suspicious_cookies': False
}
fraud_result = AdFraudDetection.detect_impression_fraud(impression_data)

# Detect malware in ads
ad_data = {
    'content': '<img src="...">',
    'domain': 'ads.example.com',
    'domains': ['ads.example.com']
}
malware_result = AdFraudDetection.detect_malware(ad_data)
```

#### AdBlocking
```python
from app.security.ad_attack_prevention import AdBlocking

# Check if ad should be blocked
ad_data = {'domain': 'malicious-ads.com', 'content': '...'}
should_block, reason = AdBlocking.should_block_ad(ad_data)
if should_block:
    logger.warning(f"Ad blocked: {reason}")
```

#### Compliance Checking
```python
from app.security.ad_attack_prevention import AdComplianceChecker

# Check GDPR compliance
gdpr_result = AdComplianceChecker.check_gdpr_compliance(ad_data)
if not gdpr_result['gdpr_compliant']:
    logger.warning(f"GDPR issues: {gdpr_result['issues']}")

# Check CCPA compliance
ccpa_result = AdComplianceChecker.check_ccpa_compliance(ad_data)

# Check COPPA compliance (for children's ads)
coppa_result = AdComplianceChecker.check_coppa_compliance(ad_data)

# Check transparency (Ad labeling)
transparency = AdComplianceChecker.check_transparency(ad_data)
```

#### Ad Security Scoring
```python
from app.security.ad_attack_prevention import AdSecurityScorer

# Generate comprehensive security score
security_score = AdSecurityScorer.score_ad(
    ad_data=ad_data,
    impression_data=impression_data,
    click_data=click_data
)
# Returns: security_score (0-100), is_safe, issues, recommendation

if security_score['recommendation'] == 'BLOCK':
    # Block the ad
    pass
elif security_score['recommendation'] == 'REVIEW':
    # Manual review needed
    pass
else:
    # Allow the ad
    pass
```

---

### 3. Compliance Module (`app/security/compliance.py`)

**Standards Covered:**
- OWASP Top 10 2021
- GDPR (General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- PCI-DSS (Payment Card Industry Data Security Standard)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOC2 (Service Organization Control)
- ISO 27001 (Information Security Management)

**Key Classes:**

#### ComplianceAudit
```python
from app.security.compliance import ComplianceAudit

# Audit OWASP compliance
owasp_results = ComplianceAudit.audit_owasp_compliance()
for check, result in owasp_results.items():
    print(f"{check}: {result['status']} - {result['description']}")

# Audit GDPR compliance
gdpr_results = ComplianceAudit.audit_gdpr_compliance()

# Audit CCPA compliance
ccpa_results = ComplianceAudit.audit_ccpa_compliance()

# Audit PCI-DSS compliance
pci_results = ComplianceAudit.audit_pci_dss_compliance()

# Audit HIPAA compliance
hipaa_results = ComplianceAudit.audit_hipaa_compliance()

# Audit ISO 27001 compliance
iso_results = ComplianceAudit.audit_iso27001_compliance()
```

#### SecurityPolicyEnforcer
```python
from app.security.compliance import SecurityPolicyEnforcer

# Validate password against policy
password = 'MySecurePass123!'
result = SecurityPolicyEnforcer.enforce_password_policy(password)
if not result['valid']:
    # Show issues to user
    for issue in result['issues']:
        print(issue)

# Get session policy
session_policy = SecurityPolicyEnforcer.enforce_session_policy()
# Apply to Flask app

# Get API policy
api_policy = SecurityPolicyEnforcer.enforce_api_policy()
```

---

## 🔧 Integration Steps

### Step 1: Update Flask App Factory

```python
# app/__init__.py

from flask import Flask
from app.security.web_attack_prevention import CSRFProtection, validate_request_input
from app.security.ad_attack_prevention import validate_ad_request
from app.security.compliance import compliance_audit
from flask_talisman import Talisman

def create_app(config_name=None):
    app = Flask(__name__)
    
    # ... existing initialization ...
    
    # Register security blueprints
    from app.security import web_attack_prevention
    from app.security import ad_attack_prevention
    from app.security import compliance
    
    # Initialize Talisman for security headers
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'"],
        'style-src': ["'self'"],
        'img-src': ["'self'", "data:", "https:"],
        'frame-ancestors': "'self'",
        'form-action': "'self'",
        'base-uri': "'self'",
        'object-src': "'none'",
    }
    
    Talisman(app, 
             force_https=True,
             strict_transport_security=True,
             content_security_policy=csp,
             content_security_policy_nonce_in=['script-src'])
    
    return app
```

### Step 2: Protect Routes with Input Validation

```python
# app/routes/user.py

from flask import Blueprint, request
from app.security.web_attack_prevention import validate_request_input

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
@validate_request_input
def register():
    # All inputs automatically validated
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Process registration
    return jsonify({'status': 'success'})

@user_bp.route('/profile/update', methods=['POST'])
@validate_request_input
def update_profile():
    # Inputs validated, safe to process
    data = request.get_json()
    return jsonify({'status': 'updated'})
```

### Step 3: Sanitize User Inputs

```python
# In models or forms

from app.security.web_attack_prevention import InputSanitizer

class User(db.Model):
    username = db.Column(db.String(100))
    bio = db.Column(db.Text)
    website = db.Column(db.String(200))
    
    @staticmethod
    def create(username, bio, website):
        user = User()
        user.username = InputSanitizer.sanitize_text(username)
        user.bio = InputSanitizer.sanitize_html(bio)
        user.website = InputSanitizer.sanitize_url(website)
        
        db.session.add(user)
        db.session.commit()
        return user
```

### Step 4: Protect File Uploads

```python
# app/routes/upload.py

from flask import Blueprint, request, abort
from app.security.web_attack_prevention import FileUploadProtection
from werkzeug.utils import secure_filename
import os

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload/profile-picture', methods=['POST'])
def upload_profile_picture():
    file = request.files.get('file')
    
    # Validate file
    if not file or not FileUploadProtection.is_allowed_file(file.filename, 'images'):
        abort(400, "Invalid file type")
    
    valid, msg = FileUploadProtection.validate_file(file)
    if not valid:
        abort(400, msg)
    
    # Sanitize filename
    safe_filename = FileUploadProtection.sanitize_filename(file.filename)
    
    # Save file
    filepath = os.path.join('uploads', safe_filename)
    file.save(filepath)
    
    return jsonify({'status': 'uploaded'})
```

### Step 5: Validate Ads

```python
# app/routes/ads.py

from flask import Blueprint, request
from app.security.ad_attack_prevention import validate_ad_request, AdSecurityScorer

ads_bp = Blueprint('ads', __name__)

@ads_bp.route('/api/ads/<ad_id>', methods=['GET'])
@validate_ad_request
def get_ad(ad_id):
    # Ad data automatically validated
    ad = Ad.query.get(ad_id)
    
    # Score ad security
    security_score = AdSecurityScorer.score_ad({
        'content': ad.content,
        'domain': ad.domain,
    })
    
    if security_score['recommendation'] == 'BLOCK':
        return jsonify({'error': 'Ad blocked'}), 403
    
    return jsonify(ad.to_dict())
```

### Step 6: Audit Compliance

```python
# app/routes/compliance.py

from flask import Blueprint
from app.security.compliance import ComplianceAudit, compliance_audit

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/audit/owasp', methods=['GET'])
@compliance_audit
def audit_owasp():
    results = ComplianceAudit.audit_owasp_compliance()
    return jsonify(results)

@compliance_bp.route('/audit/gdpr', methods=['GET'])
@compliance_audit
def audit_gdpr():
    results = ComplianceAudit.audit_gdpr_compliance()
    return jsonify(results)

@compliance_bp.route('/audit/full', methods=['GET'])
@compliance_audit
def full_audit():
    return jsonify({
        'owasp': ComplianceAudit.audit_owasp_compliance(),
        'gdpr': ComplianceAudit.audit_gdpr_compliance(),
        'ccpa': ComplianceAudit.audit_ccpa_compliance(),
        'pci_dss': ComplianceAudit.audit_pci_dss_compliance(),
        'hipaa': ComplianceAudit.audit_hipaa_compliance(),
        'iso27001': ComplianceAudit.audit_iso27001_compliance(),
    })
```

---

## 📋 Attack Detection Examples

### SQL Injection Detection
```
Dangerous: " OR 1=1 --
Detected: ✓ SQL keyword + condition pattern
Response: 400 Bad Request
```

### XSS Detection
```
Dangerous: <script>alert('XSS')</script>
Detected: ✓ Script tag pattern
Response: 400 Bad Request
```

### Path Traversal Detection
```
Dangerous: ../../etc/passwd
Detected: ✓ Parent directory traversal pattern
Response: 400 Bad Request
```

### Click Fraud Detection
```
Detected indicators:
  - 5 clicks in 3 seconds from same IP
  - User agent contains "bot"
  - Missing referer
Score: 75/100 (FRAUD)
Response: Log and block
```

### Impression Fraud Detection
```
Detected indicators:
  - Ad visibility: 0% (off-screen)
  - Not in viewport
  - Suspicious cookie patterns
Score: 80/100 (FRAUD)
Response: Log and block
```

---

## 🔍 Compliance Audit Results

### OWASP Top 10 2021
✓ A01:2021 - Broken Access Control (RBAC implemented)
✓ A02:2021 - Cryptographic Failures (AES-256-GCM)
✓ A03:2021 - Injection (Detection & prevention)
✓ A04:2021 - Insecure Design (Security by design)
✓ A05:2021 - Security Misconfiguration (Secure defaults)
✓ A06:2021 - Vulnerable Components (Tracking & updates)
✓ A07:2021 - Auth Failures (Strong authentication)
✓ A08:2021 - Integrity Failures (HMAC-SHA256)
✓ A09:2021 - Logging Failures (Audit logging)
✓ A10:2021 - SSRF (URL validation)

### GDPR Compliance
✓ Data Protection by Design
⚠ Consent Management (UI needed)
⚠ Data Subject Rights (APIs needed)
✓ Encryption (AES-256-GCM)

### CCPA Compliance
✓ No data sales
⚠ Consumer disclosure
⚠ Opt-out mechanism (UI needed)

### PCI-DSS Compliance
✓ Encryption of cardholder data
✓ Access control
✓ Audit logging
✓ Vulnerability management

---

## 🧪 Testing Attack Detection

```python
from app.security.web_attack_prevention import WebAttackDetection

# Test SQL injection detection
assert WebAttackDetection.detect_sql_injection("' OR '1'='1")
assert WebAttackDetection.detect_sql_injection("UNION SELECT * FROM users")

# Test XSS detection
assert WebAttackDetection.detect_xss("<script>alert('XSS')</script>")
assert WebAttackDetection.detect_xss("<img onerror='alert(1)'>")

# Test path traversal
assert WebAttackDetection.detect_path_traversal("../../etc/passwd")
assert WebAttackDetection.detect_path_traversal("..\\..\\windows\\system32")

# Test command injection
assert WebAttackDetection.detect_command_injection("; rm -rf /")
assert WebAttackDetection.detect_command_injection("| cat /etc/passwd")

print("All attack detection tests passed!")
```

---

## 📊 Monitoring & Logging

All attacks are logged to `logs/security_audit.log`:

```
2026-02-06 14:32:15,123 WARNING: SQL Injection detected in: id=1' OR '1'='1
2026-02-06 14:33:42,456 WARNING: XSS attempt detected in: <script>alert('XSS')</script>
2026-02-06 14:34:18,789 WARNING: Click fraud detected: Score 75/100
2026-02-06 14:35:02,101 WARNING: Malicious ad blocked: Domain matches blocklist
```

---

## 🚀 Next Steps

1. **Review Security Modules**: Read through each module's code
2. **Integrate Into App**: Follow integration steps above
3. **Test Thoroughly**: Run security tests
4. **Monitor Logs**: Review security_audit.log regularly
5. **Compliance Audit**: Run `ComplianceAudit` classes
6. **Update Policies**: Customize `SecurityPolicyEnforcer` as needed
7. **Regular Reviews**: Audit compliance monthly

---

## Support & Documentation

- Security modules: `/app/security/`
- Compliance checker: `app/security/compliance.py`
- Web attack prevention: `app/security/web_attack_prevention.py`
- Ad attack prevention: `app/security/ad_attack_prevention.py`
- Logging: `logs/security_audit.log`

---

**Status**: ✅ All modules implemented and ready for integration
