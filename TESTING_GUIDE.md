# Project Management System - Testing Guide

## 🎯 Production Readiness Testing

This document provides comprehensive testing procedures for the Project Management System before deploying to production.

---

## 📋 Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@123456 |

---

## 🔐 Authentication Testing

### 1. Login Tests
- [ ] **Valid Login**: Login with `admin` / `Admin@123456`
- [ ] **Invalid Password**: Try wrong password - should show error
- [ ] **Empty Fields**: Submit with empty fields - should show validation error
- [ ] **Rate Limiting**: Try 5+ wrong passwords - should lock out for 15 minutes
- [ ] **Remember Me**: Check "Remember me" - session should persist longer
- [ ] **Session Timeout**: Wait 30+ minutes - should auto-logout

### 2. Logout Tests
- [ ] **Logout Button**: Click logout - should redirect to login page
- [ ] **Session Cleared**: After logout, try accessing `/dashboard` - should redirect to login

---

## 🖥️ Dashboard Testing

### 3. Main Dashboard (`/dashboard`)
- [ ] **Load Page**: Dashboard loads without errors
- [ ] **Statistics Cards**: Shows correct project counts
- [ ] **Recent Projects**: Lists projects correctly
- [ ] **Quick Actions**: All buttons work

### 4. Sidebar Navigation
- [ ] **Dashboard Link**: Navigates to `/dashboard`
- [ ] **Reports Link**: Navigates to `/reports`
- [ ] **Issues Link**: Navigates to `/issues`
- [ ] **Board Link**: Navigates to `/board`
- [ ] **Backlog Link**: Navigates to `/backlog`
- [ ] **Timeline Link**: Navigates to `/timeline`
- [ ] **Admin Tools Link**: Navigates to `/admin/tools` (admin only)

---

## 📊 Project Management Testing

### 5. Projects List
- [ ] **View Projects**: Navigate to projects section
- [ ] **Create Project**: Click create - form should open
- [ ] **Edit Project**: Edit existing project
- [ ] **Delete Project**: Delete project (admin only)

### 6. Project Details
- [ ] **View Details**: Click on a project
- [ ] **Team Assignment**: View/edit team
- [ ] **Project Lead**: View/edit lead
- [ ] **Status Updates**: Add status updates

---

## 📋 Issues Testing

### 7. Issues Navigator (`/issues`)
- [ ] **Load Page**: Issues page loads with table
- [ ] **Filter by Project**: Project dropdown filters correctly
- [ ] **Filter by Status**: Status dropdown filters correctly
- [ ] **Filter by Priority**: Priority dropdown filters correctly
- [ ] **Create Issue**: Create new issue button works
- [ ] **View Issue**: Click on issue navigates to detail

### 8. Kanban Board (`/board`)
- [ ] **Load Page**: Board loads with columns
- [ ] **Project Selection**: Dropdown changes project view
- [ ] **Issue Cards**: Issues display in correct columns
- [ ] **Drag & Drop**: (If enabled) Move issues between columns

### 9. Backlog (`/backlog`)
- [ ] **Load Page**: Backlog loads correctly
- [ ] **Project Selection**: Dropdown changes project
- [ ] **Sprint View**: Sprints display correctly
- [ ] **Backlog Items**: Unassigned issues show

### 10. Timeline (`/timeline`)
- [ ] **Load Page**: Timeline loads correctly
- [ ] **Project Selection**: Dropdown works
- [ ] **Date Display**: Issues with dates appear on timeline

---

## 🔧 Admin Section Testing

### 11. Admin Dashboard (`/admin`)
- [ ] **Load Page**: Admin dashboard loads
- [ ] **Statistics**: User, Team, Project counts correct
- [ ] **Recent Activity**: Shows recent actions
- [ ] **Online Users**: Shows logged-in users

### 12. User Management (`/admin/users`)
- [ ] **List Users**: All users display
- [ ] **Create User**: Create new user works
- [ ] **Edit User**: Edit user details
- [ ] **Delete User**: Delete user (not self)
- [ ] **Role Assignment**: Change user roles

### 13. Team Management (`/admin/teams`)
- [ ] **List Teams**: All teams display
- [ ] **Create Team**: Create new team
- [ ] **Edit Team**: Edit team details
- [ ] **Team Members**: Add/remove members

### 14. Admin Tools (`/admin/tools`)
- [ ] **Tools Hub**: Shows all 10 tools
- [ ] **Automation**: Link works
- [ ] **Service Desk**: Link works
- [ ] **Integrations**: Link works
- [ ] **Search**: Search functionality works
- [ ] **Change Calendar**: Link works

---

## 🔒 Security Testing

### 15. Access Control
- [ ] **Admin Routes**: Non-admin cannot access `/admin/*`
- [ ] **CSRF Protection**: Forms have CSRF tokens
- [ ] **Session Security**: Session cookies are HTTP-only
- [ ] **Password Hashing**: Passwords stored with Argon2

### 16. Input Validation
- [ ] **XSS Prevention**: HTML tags are escaped
- [ ] **SQL Injection**: Special characters in search work safely
- [ ] **File Upload**: Only allowed file types accepted

---

## 📱 Responsive Testing

### 17. Mobile Compatibility
- [ ] **Dashboard**: Responsive on mobile
- [ ] **Sidebar**: Collapsible/hamburger menu
- [ ] **Tables**: Scrollable on small screens
- [ ] **Forms**: Usable on touch devices

---

## ⚡ Performance Testing

### 18. Load Times
- [ ] **Dashboard**: Loads in < 2 seconds
- [ ] **Issues List**: Handles 100+ issues
- [ ] **Search**: Returns results in < 1 second

---

## 🐛 Error Handling Testing

### 19. Error Pages
- [ ] **404 Page**: Access non-existent route
- [ ] **500 Page**: Force server error (dev only)
- [ ] **Flash Messages**: Error messages display correctly

---

## 📝 API Testing

### 20. REST API Endpoints
- [ ] **GET /api/v1/projects**: Returns projects JSON
- [ ] **GET /api/v1/issues**: Returns issues JSON
- [ ] **GET /api/v1/starred-items**: Returns starred items

---

## ✅ Pre-Production Checklist

- [ ] All tests above pass
- [ ] Database backed up
- [ ] Environment variables set (production)
- [ ] Debug mode OFF
- [ ] HTTPS configured
- [ ] Logging configured
- [ ] Error monitoring setup

---

## 🚀 Quick Test Commands

```bash
# Check server is running
curl -s http://127.0.0.1:5000/

# Test login page loads
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/login
# Expected: 200

# Test protected route (should redirect to login)
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/dashboard
# Expected: 302

# Test API endpoint (no auth)
curl -s http://127.0.0.1:5000/api/v1/projects
```

---

## 📄 Test Report Template

**Date**: ____________________  
**Tester**: ____________________  
**Build/Version**: ____________________  

| Category | Tests Passed | Tests Failed | Notes |
|----------|--------------|--------------|-------|
| Authentication | / | | |
| Dashboard | / | | |
| Projects | / | | |
| Issues | / | | |
| Admin | / | | |
| Security | / | | |
| Performance | / | | |

**Overall Result**: ⬜ PASS / ⬜ FAIL

**Issues Found**:
1. 
2. 
3. 

**Recommendations**:
1. 
2. 

---

## Need Help?

If you encounter issues during testing:
1. Check the server logs in the terminal
2. Check browser console for JavaScript errors
3. Verify database file exists at `instance/project_mgmt.db`
4. Ensure all requirements are installed: `pip install -r requirements.txt`
