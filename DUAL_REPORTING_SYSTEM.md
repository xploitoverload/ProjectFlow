# 📊 Dual Reporting System - User & Team Panels

## Overview

The Reports page now features **separate tracking panels** for:
1. **👤 My Reports Panel** - Individual user progress tracking
2. **👥 Team Reports Panel** - Team-wide performance tracking

## User Reports Panel

### Features:
✅ **Personal Status Reports** - View your submitted reports
✅ **Add New Report** - Submit daily/weekly/monthly updates
✅ **Progress Tracking** - Visual progress bars (0-100%)
✅ **Status Indicators** - On Track / At Risk / Blocked
✅ **Metrics Display**:
   - Hours worked
   - Team members involved
   - Days to completion
   - Blockers/Issues

### Statistics:
- **Total Reports** - All reports submitted by you
- **On Track** - Green count of on-track projects
- **At Risk** - Yellow count of at-risk projects
- **Blocked** - Red count of blocked projects

### Usage:
1. Go to `/reports`
2. Click "**My Reports**" tab (default)
3. View your submitted reports with filters
4. Click "**+ Add Report**" to submit new update

### Report Card Details:
```
Project Name [STATUS BADGE]
PERIOD Report • Date Time

                                Progress: XX%
Hours Worked | Team Members | Days to Complete
[Progress Bar]
Description: Work completed and current status...
🚫 Blocker: What's blocking progress?
```

---

## Team Reports Panel

### Features:
✅ **All Team Member Reports** - See entire team's progress
✅ **Team Statistics** - Aggregate team metrics
✅ **Status Filtering** - Filter by On Track/At Risk/Blocked
✅ **Sortable Table** - User, Project, Status, Progress, Hours, Period, Date
✅ **Color-Coded Status** - Visual indicators for each status
✅ **User Information** - User name and role for each report

### Table Columns:
| Column | Shows |
|--------|-------|
| User | Team member name and role |
| Project | Project being reported on |
| Status | On Track / At Risk / Blocked (color-coded) |
| Progress | Progress bar with percentage |
| Hours | Hours worked on project |
| Period | Daily / Weekly / Monthly |
| Date | Report submission date |

### Statistics:
- **Total Team Reports** - All reports from team members
- **Team On Track** - Green count
- **Team At Risk** - Yellow count
- **Team Blocked** - Red count

### Usage:
1. Go to `/reports`
2. Click "**Team Reports**" tab
3. View all team member reports in table format
4. Filter by status using dropdown
5. Review team performance metrics

### Example View:
```
User: john_doe (Developer)
Project: Lunar Rover
Status: ON_TRACK [Green]
Progress: ████████░ 85%
Hours: 8.5 hrs
Period: Daily
Date: Feb 5, 2026
```

---

## Tab Navigation

### How to Switch:
```
┌─────────────┬──────────────┐
│ 👤 My Reports │ 👥 Team Reports│
└─────────────┴──────────────┘
```

- Click "**My Reports**" → Show personal reports & statistics
- Click "**Team Reports**" → Show team reports & statistics

---

## API Endpoints

### Get User Reports (Existing)
```
GET /reports
```
Returns user's personal reports with statistics

### Get Team Reports (New)
```
GET /api/team/reports
```
Returns:
```json
{
  "success": true,
  "reports": [
    {
      "id": 1,
      "user_name": "john_doe",
      "user_role": "Developer",
      "project_name": "Lunar Rover",
      "status": "on_track",
      "progress": 85,
      "hours_worked": 8.5,
      "reporting_period": "daily",
      "date": "2026-02-05T13:48:40",
      "description": "Completed API integration..."
    }
  ],
  "stats": {
    "total": 12,
    "on_track": 8,
    "at_risk": 3,
    "blocked": 1
  }
}
```

### Submit Report (Existing)
```
POST /api/reports/add
```
```json
{
  "project_id": 1,
  "description": "Work completed...",
  "status": "on_track",
  "progress": 85,
  "hours_worked": 8.5,
  "team_members": 3,
  "completion_days": 3,
  "blockers": "Waiting on design",
  "reporting_period": "daily"
}
```

---

## Access Control

### Who Can See What:
- **Users** → See only their own reports in "My Reports" tab
- **All Users** → See team reports in "Team Reports" tab (if in same team)
- **Admins** → Can potentially see all reports across organization (future enhancement)

### Team Filtering:
- Team Reports only show reports from your team members
- If user has no team → Team Reports shows empty message

---

## Color Coding

### Status Indicators:
- 🟢 **On Track** - Green (#10b981)
- 🟡 **At Risk** - Yellow (#f59e0b)
- 🔴 **Blocked** - Red (#ef4444)

### Applied To:
- Status badges on report cards
- Status column in team table
- Progress bar colors
- Statistics card borders

---

## Features Implemented

✅ Dual panel system (User + Team)
✅ Tab navigation with icons
✅ User reports list with cards
✅ Team reports table with sorting
✅ Status filtering for team reports
✅ Real-time statistics for both panels
✅ Add report modal dialog
✅ Color-coded status indicators
✅ Progress bars with percentages
✅ User role display in team view
✅ Date/time formatting
✅ Empty state messages

---

## Next Steps (Future Enhancements)

- [ ] Export team reports to PDF/Excel
- [ ] Schedule automated reports
- [ ] Report templates
- [ ] Email notifications for at-risk projects
- [ ] Team report comments/discussions
- [ ] Historical trend analysis
- [ ] Manager-specific analytics
- [ ] Custom report builders
- [ ] Integration with calendar

---

## Files Modified

- `templates/reports.html` - Added dual panels and JavaScript
- `app/routes/api.py` - Added `/api/team/reports` endpoint

## Testing

### Test User Reports:
1. Login as admin
2. Go to `/reports`
3. Click "+ Add Report" button
4. Fill form and submit
5. See report appear in "My Reports" panel
6. Check statistics update

### Test Team Reports:
1. Ensure users are in same team
2. Go to `/reports`
3. Click "Team Reports" tab
4. See all team member reports in table
5. Filter by status
6. View team statistics

---

**Last Updated**: 5 February 2026  
**Status**: ✅ Implemented and Ready  
**Testing**: Complete  
