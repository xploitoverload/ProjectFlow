# Quick Integration Guide - Attack Prevention & Compliance

## 🚀 5-Minute Setup

### Step 1: Verify Modules Exist
```bash
# Check all security modules are in place
ls -la app/security/
```

Expected files:
```
✓ app/security/web_attack_prevention.py
✓ app/security/ad_attack_prevention.py
✓ app/security/compliance.py
```

### Step 2: Run Verification Tests
```bash
python verify_attack_prevention.py
```

Expected output:
```
✓ ALL ATTACK PREVENTION VERIFIED ✓
```

### Step 3: Update Flask App Factory

**File**: `app/__init__.py`

Add imports:
```python
from app.security.web_attack_prevention import validate_request_input
from flask_talisman import Talisman
```

Add CSP headers:
```python
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
         content_security_policy=csp)
```

### Step 4: Protect Routes

**Protect user input routes:**
```python
from app.security.web_attack_prevention import validate_request_input

@app.route('/submit', methods=['POST'])
@validate_request_input  # This line protects all inputs
def submit_form():
    # Inputs are already validated
    username = request.form.get('username')
    return jsonify({'success': True})
```

**Protect ad routes:**
```python
from app.security.ad_attack_prevention import validate_ad_request

@app.route('/api/ads/<ad_id>')
@validate_ad_request  # This line protects ad data
def get_ad(ad_id):
    # Ad data is already validated
    return jsonify(ad_data)
```

**Check compliance:**
```python
from app.security.compliance import compliance_audit

@app.route('/admin/compliance', methods=['GET'])
@compliance_audit  # Logs compliance events
def check_compliance():
    from app.security.compliance import ComplianceAudit
    return jsonify({
        'owasp': ComplianceAudit.audit_owasp_compliance(),
        'gdpr': ComplianceAudit.audit_gdpr_compliance(),
    })
```

### Step 5: Test It Works

```bash
# Start the app
python run.py

# Test SQL injection protection
curl "http://localhost:5000/api/users?id=1' OR '1'='1"
# Should return: 400 Bad Request

# Test XSS protection
curl "http://localhost:5000/api/post?content=<script>alert('xss')</script>"
# Should return: 400 Bad Request

# Test compliance
curl http://localhost:5000/admin/compliance
# Should return compliance audit results
```

---

## 📋 Common Scenarios

### Scenario 1: Register New User
```python
@app.route('/auth/register', methods=['POST'])
@validate_request_input
def register():
    # All inputs validated automatically
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Also check password policy
    from app.security.compliance import SecurityPolicyEnforcer
    result = SecurityPolicyEnforcer.enforce_password_policy(password)
    if not result['valid']:
        return jsonify({'error': result['issues'][0]}), 400
    
    # Create user
    user = User.create(username, email, password)
    return jsonify({'success': True, 'user_id': user.id})
```

### Scenario 2: Handle File Upload
```python
from app.security.web_attack_prevention import FileUploadProtection
from werkzeug.utils import secure_filename

@app.route('/upload/image', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    
    # Validate file type
    if not FileUploadProtection.is_allowed_file(file.filename, 'images'):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Validate file
    valid, msg = FileUploadProtection.validate_file(file)
    if not valid:
        return jsonify({'error': msg}), 400
    
    # Sanitize filename
    filename = FileUploadProtection.sanitize_filename(file.filename)
    
    # Save
    filepath = f"uploads/{filename}"
    file.save(filepath)
    return jsonify({'success': True, 'file': filename})
```

### Scenario 3: Serve Ad
```python
from app.security.ad_attack_prevention import AdSecurityScorer

@app.route('/api/ads/<ad_id>')
@validate_ad_request
def serve_ad(ad_id):
    ad = Ad.query.get(ad_id)
    
    # Score the ad for security
    score = AdSecurityScorer.score_ad({
        'content': ad.content,
        'domain': ad.domain,
    })
    
    # Check recommendation
    if score['recommendation'] == 'BLOCK':
        logger.warning(f"Ad blocked: {score['issues']}")
        return jsonify({'error': 'Ad blocked'}), 403
    
    if score['recommendation'] == 'REVIEW':
        logger.warning(f"Ad flagged for review: {score['issues']}")
    
    return jsonify(ad.to_dict())
```

### Scenario 4: Audit Compliance
```python
from app.security.compliance import ComplianceAudit

# Audit OWASP
owasp = ComplianceAudit.audit_owasp_compliance()
for check, result in owasp.items():
    print(f"{check}: {result['status']}")
    # Output:
    # A01_broken_access_control: PASS
    # A02_cryptographic_failures: PASS
    # ...

# Audit GDPR
gdpr = ComplianceAudit.audit_gdpr_compliance()
for item, result in gdpr.items():
    print(f"{item}: {result['status']}")
    # Output:
    # data_protection_by_design: PASS
    # consent_management: REVIEW
    # ...

# Audit CCPA
ccpa = ComplianceAudit.audit_ccpa_compliance()
for item, result in ccpa.items():
    status = "✓" if result['status'] == 'PASS' else "✗"
    print(f"{status} {item}")
```

---

## 🔍 What Each Module Does

### web_attack_prevention.py
**Detects & prevents**:
- SQL injection
- Cross-site scripting (XSS)
- Path traversal
- XXE attacks
- Command injection
- LDAP injection
- NoSQL injection
- Header injection
- CSRF attacks
- Clickjacking
- Malicious file uploads

**Key decorator**:
```python
@validate_request_input  # Protects all request parameters
```

### ad_attack_prevention.py
**Detects & prevents**:
- Click fraud
- Impression fraud
- Bot clicks
- Malware in ads
- Cookie stuffing
- Redirect hijacking

**Key decorator**:
```python
@validate_ad_request  # Validates ad requests
```

### compliance.py
**Audits compliance with**:
- OWASP Top 10
- GDPR
- CCPA
- PCI-DSS
- HIPAA
- ISO 27001
- SOC2

**Key function**:
```python
ComplianceAudit.audit_owasp_compliance()  # Full audit
```

---

## 🧪 Testing Examples

### Test SQL Injection Detection
```python
from app.security.web_attack_prevention import WebAttackDetection

test_cases = [
    "' OR '1'='1",
    "UNION SELECT * FROM users",
    "1; DROP TABLE users--"
]

for test in test_cases:
    if WebAttackDetection.detect_sql_injection(test):
        print(f"✓ Detected: {test}")
```

### Test XSS Detection
```python
from app.security.web_attack_prevention import WebAttackDetection

test_cases = [
    "<script>alert('XSS')</script>",
    "<img onerror='alert(1)'>",
    "javascript:alert('XSS')"
]

for test in test_cases:
    if WebAttackDetection.detect_xss(test):
        print(f"✓ Detected: {test}")
```

### Test Click Fraud
```python
from app.security.ad_attack_prevention import AdFraudDetection
from datetime import datetime

click_data = {
    'ip_address': '192.168.1.1',
    'user_agent': 'Mozilla/5.0 (compatible; Googlebot)',
    'referer': 'https://example.com',
    'timestamp': datetime.now(),
    'click_history': []
}

fraud = AdFraudDetection.detect_click_fraud(click_data)
if fraud['is_fraud']:
    print(f"Fraud detected (score: {fraud['score']}): {fraud['details']}")
```

---

## 📊 Monitoring

### Check Audit Logs
```bash
# View recent security events
tail -f logs/security_audit.log

# Filter for attacks
grep "attack\|injection\|fraud\|malware" logs/security_audit.log

# Check attack count
grep -c "detected" logs/security_audit.log
```

### Generate Report
```python
from app.security.compliance import ComplianceAudit

# Full compliance audit
compliance_report = {
    'owasp': ComplianceAudit.audit_owasp_compliance(),
    'gdpr': ComplianceAudit.audit_gdpr_compliance(),
    'ccpa': ComplianceAudit.audit_ccpa_compliance(),
    'pci': ComplianceAudit.audit_pci_dss_compliance(),
}

# Save report
import json
with open('compliance_report.json', 'w') as f:
    json.dump(compliance_report, f, indent=2)
```

---

## ⚠️ Important Notes

1. **Always run verification**: `python verify_attack_prevention.py`
2. **Enable CSP headers**: Use Talisman in production
3. **Monitor logs**: Check `logs/security_audit.log` regularly
4. **Update policies**: Customize `SecurityPolicyEnforcer` as needed
5. **Test thoroughly**: Test all protected routes
6. **Keep dependencies updated**: Run `pip install --upgrade`

---

## 🎯 Integration Checklist

- [ ] Copy security modules to `app/security/`
- [ ] Copy verification script
- [ ] Update `app/__init__.py` with security headers
- [ ] Add `@validate_request_input` to user input routes
- [ ] Add `@validate_ad_request` to ad routes
- [ ] Add `@compliance_audit` to compliance routes
- [ ] Run `python verify_attack_prevention.py`
- [ ] Test attack scenarios
- [ ] Monitor `logs/security_audit.log`
- [ ] Schedule compliance audits

---

## ✅ Verification Commands

```bash
# Run full verification
python verify_attack_prevention.py

# Check modules exist
python -c "from app.security.web_attack_prevention import WebAttackDetection; print('✓')"
python -c "from app.security.ad_attack_prevention import AdFraudDetection; print('✓')"
python -c "from app.security.compliance import ComplianceAudit; print('✓')"

# Test attack detection
python -c "
from app.security.web_attack_prevention import WebAttackDetection
assert WebAttackDetection.detect_sql_injection(\"' OR '1'='1\")
assert WebAttackDetection.detect_xss(\"<script>alert('xss')</script>\")
print('✓ Attack detection working')
"

# Test compliance
python -c "
from app.security.compliance import ComplianceAudit
results = ComplianceAudit.audit_owasp_compliance()
print(f\"✓ OWASP compliance checked: {len(results)} items\")
"
```

---

**Status**: ✅ Ready to integrate

All modules are implemented, tested, and ready for deployment. Follow this guide to quickly integrate the attack prevention system into your Flask application.
