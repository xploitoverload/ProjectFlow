# 📊 Progress Reports & Status System - User Guide

## Overview

The Progress Reports & Status system allows team members to add daily, weekly, and monthly progress updates that automatically sync across the dashboard and track project status in real-time.

## Features

### 1. **Multiple Reporting Periods**
- **Daily Reports**: Track daily progress and blockers
- **Weekly Reports**: Summarize weekly achievements and status
- **Monthly Reports**: Overview of monthly progress and completion

### 2. **Status Tracking**
Three status levels to indicate project health:
- ✅ **On Track**: Project is progressing as planned
- ⚠️ **At Risk**: Some issues but manageable
- 🛑 **Blocked**: Critical blockers preventing progress

### 3. **Progress Metrics**
Track detailed metrics for each report:
- 📊 Progress percentage (0-100%)
- ⏱️ Hours worked
- 👥 Team members involved
- 📅 Estimated days to completion
- 🔴 Blockers and impediments

### 4. **Real-time Analytics**
Dashboard displays:
- Total reports in selected period
- On Track/At Risk/Blocked counts
- Project status overview
- Automatic updates every 30 seconds

## How to Add a Report

### Method 1: Reports Page
1. Navigate to **Reports** in the sidebar
2. Click **+ Add Report** button
3. Select project and reporting period
4. Fill in status, progress, and details
5. Click **Submit Report**

### Method 2: Filter by Period
On Reports page, use filter buttons:
- **Today**: Last 24 hours
- **This Week**: Last 7 days
- **This Month**: Last 30 days
- **All Time**: All reports

## Report Fields Explained

### Required Fields
- **Project**: Select which project this report is for
- **Status**: One of On Track, At Risk, or Blocked
- **Description**: What work was done and current status

### Optional Fields
- **Progress (%)**: 0-100% completion indicator
- **Hours Worked**: Total hours spent on this work
- **Team Members**: Number of people working on this
- **Days to Complete**: Estimated remaining days
- **Blockers**: Any obstacles preventing progress

### Reporting Period
Choose the timeframe for this report:
- Daily: Daily standup/checkpoint
- Weekly: Weekly status review
- Monthly: Monthly progress review

## Examples

### Example 1: Daily Report
```
Project: Lunar Rover
Period: Daily
Status: ✅ On Track
Progress: 65%
Hours Worked: 8.5
Team Members: 4
Days to Complete: 3
Description: "Completed rover navigation system pathfinding algorithm. Tested on 3 terrain types. Ready for hardware integration tomorrow."
```

### Example 2: Weekly Report
```
Project: Lunar Rover
Period: Weekly
Status: ⚠️ At Risk
Progress: 72%
Hours Worked: 42
Team Members: 8
Days to Complete: 5
Blockers: "Camera calibration equipment delayed - expected next week"
Description: "Completed: hardware testing, motor control integration. In Progress: wheel assembly, suspension calibration. Blocked by camera equipment."
```

### Example 3: Blocked Report
```
Project: Lunar Rover
Period: Daily
Status: 🛑 Blocked
Progress: 55%
Description: "Cannot proceed with transmission testing - test rig under maintenance."
Blockers: "Test rig being serviced - estimated 2 hours"
```

## Statistics & Dashboard

The Reports page shows:

### Summary Cards
- **Total Reports**: Number of updates in selected period
- **On Track**: Projects with good progress
- **At Risk**: Projects needing attention
- **Blocked**: Projects stopped

### Update List
Each report card displays:
- Project name and status badge
- User and timestamp
- Progress bar (visual completion %)
- Description of work done
- Key metrics (hours, team size, days left)
- Blockers section (if any)

## Filtering Reports

Click the period buttons to filter:
- **Today**: Only reports from last 24 hours
- **This Week**: Last 7 days worth
- **This Month**: Last 30 days worth
- **All Time**: All reports ever submitted

Results update automatically with statistics.

## Best Practices

### 1. **Be Specific**
- Don't just say "Working on project"
- Include what was done and what's next
- Mention blockers early

### 2. **Update Regularly**
- Daily reports: Once per day (morning or end-of-day)
- Weekly reports: Once per week (Friday recommended)
- Monthly reports: Once per month (month-end)

### 3. **Keep Progress Realistic**
- 0-25%: Early stages, design phase
- 25-50%: Core development underway
- 50-75%: Major features complete
- 75-99%: Testing and refinement
- 100%: Complete and deployed

### 4. **Document Blockers**
- Mention blockers as soon as identified
- Include required action to unblock
- Update status to "At Risk" or "Blocked"

### 5. **Engage the Team**
- Reference team member contributions
- Highlight dependencies
- Call out needs for help

## API Integration

Reports data is automatically synced via:

### GET /reports
Retrieve all progress reports (with filters)
- Filters: `?filter=daily|weekly|monthly|all`
- Returns: List of all updates for user's team

### POST /project/{id}/add-status
Submit a new progress report
```json
{
  "status": "on_track|at_risk|blocked",
  "progress": 65,
  "description": "What was accomplished...",
  "hours_worked": 8.5,
  "team_members": 4,
  "completion_days": 3,
  "blockers": "Any issues...",
  "reporting_period": "daily|weekly|monthly"
}
```

## Permissions

- **Admin**: Can view all team reports
- **Developer/Designer**: Can see team reports, submit own
- **Guest**: View-only access

## Troubleshooting

### Reports not showing?
1. Make sure you're logged in
2. Check that project is assigned to your team
3. Verify report date is within selected period

### Can't add report?
1. Select a project first
2. Fill in required fields (marked with *)
3. Check that description is not empty
4. Ensure you have edit permission

### Statistics not updating?
1. Refresh the page
2. Check browser console for errors
3. Verify reports have correct status values

## Data Storage

All reports are encrypted:
- Description encrypted with Fernet
- Blockers notes encrypted
- User identity linked to report
- Timestamps in UTC

## Related Features

- **Dashboard**: Quick status overview
- **Kanban Board**: Issue-level tracking
- **Timeline/Gantt**: Project schedule view
- **Workflow Diagram**: Process visualization

---

**Last Updated**: January 21, 2026
**Version**: 1.0
