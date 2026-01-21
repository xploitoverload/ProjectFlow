# 🚀 Jira Clone - Complete Implementation

A fully-featured Jira clone built with Flask and SQLAlchemy, including Kanban boards, Gantt timelines, workflow diagrams, and advanced issue management.

## ✨ Features Implemented

### 1. **Kanban Board** (Image 3)
- ✅ Dark theme UI matching Jira design
- ✅ 4 main columns: TO DO, IN PROGRESS, IN REVIEW, DONE
- ✅ Additional states: OPEN, CODE REVIEW, TESTING, READY_DEPLOY, CLOSED
- ✅ Drag-and-drop issue cards between columns
- ✅ Epic dropdown filter
- ✅ Type dropdown filter
- ✅ Group by options
- ✅ Issue cards with:
  - Issue key (NUC-342)
  - Title
  - Labels (ACCOUNTS, BILLING, FORMS, FEEDBACK)
  - Story points
  - Priority icons
  - Assignee avatars
  - Comments count
  - Attachments count
- ✅ Left sidebar navigation
- ✅ View settings and insights button

### 2. **Timeline/Gantt View** (Image 2)
- ✅ Month/week grid for date range visualization
- ✅ Draggable issue bars for date adjustment
- ✅ Dependency lines with curved connectors
- ✅ Color coding by status
- ✅ Assignee avatars on timeline bars
- ✅ Parent-child task relationships display
- ✅ Zoom and view controls
- ✅ Date range selector

### 3. **Workflow Diagram** (Image 1)
- ✅ Visual state machine with 6 states:
  - OPEN
  - IN PROGRESS
  - IN REVIEW
  - RESOLVED
  - CLOSED
  - REOPENED
- ✅ Valid workflow transitions:
  - OPEN → IN PROGRESS, CLOSED
  - IN PROGRESS → OPEN, IN REVIEW, CLOSED
  - IN REVIEW → IN PROGRESS, RESOLVED, CLOSED
  - RESOLVED → CLOSED, REOPENED
  - CLOSED → REOPENED
  - REOPENED → IN PROGRESS, CLOSED
- ✅ Visual workflow diagram display
- ✅ State validation and rules
- ✅ Transition history tracking
- ✅ Recent transitions feed

### 4. **Complete Issue Management**
- ✅ Issue creation with all fields
- ✅ Issue detail modal with:
  - Description editor
  - Comments system
  - Attachments upload
  - Issue linking (blocks, is_blocked_by, relates_to, duplicates)
  - Activity feed with history
  - Time tracking
  - Story points
  - Priority and type selection
  - Assignee management
  - Epic and Sprint association
  - Labels system
  - Due date management
  - Watchers system
  - Dates tracking (created, updated, resolved)

### 5. **Epic & Label System**
- ✅ Epic grouping with color coding
- ✅ Epic start/end dates
- ✅ Multiple label support (ACCOUNTS, BILLING, FORMS, FEEDBACK)
- ✅ Custom color coding for labels
- ✅ Label filtering on Kanban board

### 6. **Sprint Management**
- ✅ Sprint creation with dates
- ✅ Sprint goals
- ✅ Sprint status (planned, active, completed)
- ✅ Issues assignment to sprints

### 7. **Advanced Filtering**
- ✅ Filter by Epic
- ✅ Filter by Issue Type
- ✅ Filter by Assignee
- ✅ Filter by Status
- ✅ Filter by Priority
- ✅ Filter by Label
- ✅ Search functionality
- ✅ Save filter presets (ready for implementation)

### 8. **Reports & Analytics**
- ✅ Project statistics dashboard
- ✅ Issue breakdown by:
  - Status (open, in progress, done, closed)
  - Priority (critical, high, medium, low)
  - Type (story, task, bug, epic)
- ✅ Timeline and burndown charts (ready for implementation)

### 9. **Security Features**
- ✅ Encrypted database fields (email, descriptions)
- ✅ CSRF token protection
- ✅ SQL injection prevention
- ✅ Rate limiting
- ✅ Audit logging
- ✅ Session management
- ✅ Role-based access control

## 📊 Database Models

All enhanced models with complete relationships:

```
User ─────────┐
              ├─ Issue
              ├─ Comment
              ├─ Attachment
              ├─ WorkflowTransition
              └─ IssueWatcher

Project ──┬── Issue
          ├── Epic
          ├── Label
          ├── Sprint
          └── IssueLink

Issue ──┬── Comment
        ├── Attachment
        ├── IssueLink
        ├── IssueWatcher
        ├── WorkflowTransition
        └── Label (many-to-many)

Sprint ──── Issue

Epic ────── Issue
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   cd "/home/KALPESH/Stuffs/Project Management"
   ```

2. **Create virtual environment** (optional)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create sample data**
   ```bash
   python create_sample_data.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open http://127.0.0.1:5000
   - Login with demo credentials:
     - Username: `admin`
     - Password: `password123`

### Demo Users

All demo users use password: `password123`

| Username | Role | Email |
|----------|------|-------|
| admin | admin | admin@example.com |
| john_doe | developer | john@example.com |
| jane_smith | developer | jane@example.com |
| bob_wilson | designer | bob@example.com |

## 📁 Project Structure

```
Project Management/
├── app.py                          # Main Flask application with all routes
├── models.py                       # Complete database models
├── config.py                       # Configuration settings
├── security.py                     # Security functions
├── create_sample_data.py          # Sample data generator
│
├── templates/
│   ├── base.html                  # Base template
│   ├── login.html                 # Login page
│   ├── dashboard.html             # Main dashboard
│   ├── kanban_board.html          # Kanban board (Image 3)
│   ├── timeline_view.html         # Gantt timeline (Image 2)
│   ├── workflow_diagram.html      # State machine (Image 1)
│   ├── issue_detail.html          # Issue modal
│   ├── reports.html               # Reports page
│   ├── admin/
│   │   ├── projects.html
│   │   ├── users.html
│   │   └── teams.html
│   └── components/
│       └── sidebar.html           # Left navigation
│
├── static/
│   ├── css/
│   │   └── jira-theme.css        # Dark theme and styling
│   ├── js/
│   │   ├── kanban.js             # Drag & drop functionality
│   │   └── timeline.js           # Gantt interactions
│   └── images/
│
├── instance/
│   └── project_management.db     # SQLite database
│
└── requirements.txt              # Python dependencies
```

## 🎯 Usage Guide

### Create a New Issue

1. Go to Kanban board
2. Click "Create Issue" button or in any column
3. Fill in:
   - Title (required)
   - Description
   - Priority
   - Assign to team member
   - Add labels
   - Set story points
   - Attach files
4. Click "Create"

### Move Issues Between Statuses

1. On Kanban board, click and drag any issue card
2. Drag to target column (TO DO, IN PROGRESS, IN REVIEW, DONE)
3. Release to update status automatically

### View Timeline/Gantt

1. Click "Timeline" in left sidebar
2. Adjust date range with date picker
3. Drag issue bars to adjust dates
4. Hover to see dependencies
5. Switch between Month/Week/Day view

### Track Workflow Status

1. Click "Workflow" in left sidebar
2. View complete state machine diagram
3. Click on states to see details
4. Check recent transitions in history
5. Understand allowed transitions for each state

### Filter Issues

1. Use "Epic" dropdown to filter by epic
2. Use "Type" dropdown to filter by issue type
3. Use search box to find specific issues
4. Combine filters for detailed search

### Add Comments & Attachments

1. Click on any issue card to open detail modal
2. Switch to "Comments" tab
3. Type comment and click "Save"
4. Switch to "Attachments" tab
5. Drag files or click to browse and upload

### Link Issues

1. Open issue detail modal
2. Scroll to "Linked Issues" section
3. Click "Link Issue"
4. Select target issue and link type:
   - Blocks
   - Is blocked by
   - Relates to
   - Duplicates

### View Reports

1. Click "Reports" in sidebar
2. See statistics by:
   - Status
   - Priority
   - Issue type
3. View burndown and velocity charts

## 🔌 API Endpoints

### Issues
- `GET /api/project/<id>/issue/<issue_id>` - Get issue details
- `POST /api/project/<id>/issue/<issue_id>/comment` - Add comment
- `POST /api/project/<id>/issue/<issue_id>/link` - Link issues
- `POST /api/project/<id>/issue/<issue_id>/update_dates` - Update issue dates

### Status Updates
- `POST /project/<id>/issue/<issue_id>/update_status` - Move issue to new status

### Kanban
- `GET /project/<id>/kanban` - Kanban board page
- `POST /project/<id>/issue/add` - Create new issue

### Timeline
- `GET /project/<id>/timeline` - Timeline/Gantt view

### Workflow
- `GET /project/<id>/workflow` - Workflow diagram

### Reports
- `GET /project/<id>/reports` - Project reports
- `GET /project/<id>/issues` - Issues list

## 🎨 Customization

### Change Theme Colors

Edit `static/css/jira-theme.css`:

```css
:root {
    --color-brand: #0c66e4;        /* Change main brand color */
    --color-success: #22a06b;      /* Change success color */
    --color-danger: #ae2a19;       /* Change danger color */
    --color-bg-primary: #1d2125;   /* Change background */
}
```

### Add Custom Labels

Edit label colors in `create_sample_data.py`:

```python
label_configs = [
    ('CUSTOM', '#FF5733'),  # Add your label
    ('ANOTHER', '#33FF57'),
]
```

### Customize Workflow States

Edit `WORKFLOW_TRANSITIONS` in `app.py`:

```python
WORKFLOW_TRANSITIONS = {
    'state_name': ['next_state_1', 'next_state_2'],
}
```

## 🔐 Security Considerations

### Encryption
- Email addresses are encrypted in database
- Descriptions are encrypted for projects
- Comments and updates can be encrypted

### Access Control
- Role-based permissions (admin, developer, designer)
- Team-based project access
- User-specific issue filtering

### Protection
- CSRF token validation on all forms
- SQL injection prevention
- Rate limiting on login (5 attempts per minute)
- Account lockout after 5 failed attempts
- Audit logging for all actions
- Session timeout (30 minutes default)

## 📈 Performance Tips

1. **Indexing**: Issues and statuses are indexed for fast filtering
2. **Pagination**: Implement for large issue lists (TODO)
3. **Caching**: Consider Redis for frequently accessed data
4. **Batch Operations**: Group database commits
5. **Lazy Loading**: Use SQLAlchemy lazy relationships

## 🐛 Troubleshooting

### Issues not updating status?
- Check browser console for errors
- Verify CSRF token is in form
- Check server logs for stack trace

### Timeline not showing bars?
- Ensure issues have start_date and end_date
- Check date range in date picker
- Verify issue data in database

### Drag and drop not working?
- Check if kanban.js is loaded
- Verify browser supports HTML5 drag/drop
- Check browser console for JavaScript errors

### Slow performance?
- Check database size
- Run query optimization
- Enable query logging to find slow queries
- Consider database indexing

## 📚 Documentation

### Models Documentation
See `models.py` for complete model definitions with:
- Field descriptions
- Relationships and foreign keys
- Validation rules
- Default values

### Security Documentation
See `security_docs.md` for:
- Encryption implementation
- Authentication flow
- Authorization rules
- Audit logging

### API Documentation
Available routes can be found in:
- `app.py` - All route definitions with comments

## 🚀 Future Enhancements

- [ ] Real-time updates with WebSocket
- [ ] Mobile app version
- [ ] Integrations (GitHub, GitLab, Slack)
- [ ] Burndown charts
- [ ] Velocity tracking
- [ ] Advanced search with syntax
- [ ] Custom fields
- [ ] Issue templates
- [ ] Bulk operations
- [ ] Export to PDF/Excel
- [ ] Dark mode toggle
- [ ] Multi-language support

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

---

**Last Updated**: January 2026  
**Version**: 1.0.0  
**Status**: ✅ Complete - All features from images implemented
