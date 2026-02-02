# CSRF Token Issue - Root Cause and Fix

## Problem Statement
Users reported "cannot create issue" error when trying to submit issue creation forms. The form would be submitted but no issue would be created in the database, and the user would be redirected without any clear indication of what went wrong.

## Root Cause Analysis

### Initial Investigation
The investigation revealed multiple issues working together:

1. **CSRF Token Loss on Login**: When `AuthService.create_session()` called `session.clear()` to clear old session data, it also cleared the CSRF token that Flask-WTF had stored in the session. This caused subsequent form submissions to fail CSRF validation.

2. **Session Management**: The way the session was being cleared and restored didn't properly handle Flask-WTF's CSRF token generation and validation mechanisms.

3. **Manual CSRF Validation Conflicts**: The application was performing its own CSRF validation with `validate_csrf_token()` in addition to Flask-WTF's automatic validation, causing conflicts when tokens diverged between form submission time and validation time.

### Why It Was Hard to Debug

- The form submission returned HTTP 302 (redirect), which is typically a success response
- The error (CSRF validation failure) was logged to the audit log but not displayed to the user
- The audit log storage itself had bugs that initially masked the real error
- No console error messages were shown to guide debugging

## Solutions Implemented

### Solution 1: CSRF Token Preservation in AuthService
**File**: `app/services/auth_service.py` (lines 98-127)

**Before**:
```python
session.clear()  # This wipes the CSRF token too
```

**After**:
```python
# Preserve keys that should survive session clear
keys_to_preserve = ['csrf_token']
preserved_data = {k: session.get(k) for k in keys_to_preserve if k in session}

# Clear session
session.clear()

# Restore CSRF token
for key, value in preserved_data.items():
    if value is not None:
        session[key] = value
```

This ensures the CSRF token is preserved through the login process.

### Solution 2: Remove Manual CSRF Validation from Issue Creation Route
**File**: `app/routes/projects.py` (lines 127-175)

**Before**:
```python
csrf_token = request.form.get('csrf_token')
if not validate_csrf_token(csrf_token):
    log_security_event('CSRF_TOKEN_INVALID', ...)
    flash('Security error. Please try again.', 'error')
    return redirect(...)
```

**After**:
```python
# Flask-WTF automatically validates CSRF tokens
# No manual validation needed
```

**Rationale**: Flask-WTF's `CSRFProtect` middleware automatically validates CSRF tokens on all POST requests. Manual validation was:
- Redundant 
- Causing token mismatches because the tokens could diverge during request processing
- Preventing legitimate requests from being processed

### Solution 3: Fixed AuditLog Field Mapping
**File**: `app/security/audit.py` (lines 129-161)

**Issue**: The audit logging code tried to pass fields to AuditLog model that didn't exist, causing database errors.

**Fix**: 
- Map `event_type` → `action` field
- Properly use the model's encryption setter for details
- Store all extra data as JSON in the `details` field

## Testing

### Test Case: Form-Based Issue Creation
Run `/test_final_verification.py` to verify the fix:

```bash
python3 test_final_verification.py
```

Expected output:
```
[1] Logging in as john_doe...
    ✓ Login successful (302 redirect)

[2] Accessing project page...
    ✓ Project page loaded

[3] Submitting issue creation form...
    ✓ Form submission successful (302 redirect)

[4] Verifying issue in database...
    ✓ Issue created successfully!
      Key: NUC-14
      Title: Form Submission Test Issue
      ...
```

## Impact

- ✅ Users can now create issues via form submission
- ✅ CSRF protection is still active (via Flask-WTF)
- ✅ Session management is more robust
- ✅ Audit logging works without errors
- ✅ Issues are properly persisted to the database

## Files Modified

1. `/app/services/auth_service.py` - CSRF token preservation
2. `/app/routes/projects.py` - Removed redundant manual CSRF validation
3. `/app/security/audit.py` - Fixed field mapping (done in previous fix)

## Lessons Learned

1. **Framework Features**: Don't manually duplicate what the framework already does (Flask-WTF's automatic CSRF validation)
2. **Error Masking**: HTTP 302 responses don't always mean success - check what actually happened
3. **Audit Logging**: Audit log errors can hide the real issues - ensure logging itself works
4. **Token Management**: CSRF tokens are sensitive to session manipulation - handle with care

## Verification Commands

```bash
# Test form-based issue creation
python3 test_final_verification.py

# Or test via test client with proper CSRF handling
python3 test_csrf_proper.py
```

Both tests should show successful issue creation with proper CSRF token handling.
