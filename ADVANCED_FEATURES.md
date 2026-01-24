# Advanced Features Guide - ProjectFlow

## 🎨 Theme System

### Dark/Light Mode Toggle
- **Location**: Available in all views (Dashboard, Kanban Board, Calendar, Roadmap)
- **Keyboard Shortcut**: `Ctrl/Cmd + D`
- **Persistence**: Theme preference is saved in localStorage and persists across sessions
- **Toggle Button**: Click the sun/moon icon in the top toolbar

### Theme Colors

**Dark Theme (Default)**
- Background: #1d2125
- Cards: #22272b
- Text: #b6c2cf
- Borders: #2c333a

**Light Theme**
- Background: #f4f5f7
- Cards: #ffffff
- Text: #172b4d
- Borders: #dfe1e6

---

## 🔔 Notification System

### Features
- **Real-time Toast Notifications**: Appear in bottom-right corner
- **Notification Center**: Click bell icon to view all notifications
- **Badge Counter**: Shows unread notification count
- **Types**: Success, Error, Warning, Info
- **Persistence**: Stored in localStorage (last 100 notifications)

### Actions
- **Mark as Read**: Click on individual notification
- **Mark All as Read**: Button in notification panel header
- **Clear All**: Remove all notifications
- **Auto-dismiss**: Toast notifications auto-dismiss after 5 seconds

### Example Usage
```javascript
window.notificationManager.addNotification({
    title: 'Task Completed',
    message: 'Your task has been marked as done',
    type: 'success'
});
```

---

## 🎯 Drag and Drop (Kanban Board)

### Features
- **Visual Feedback**: Cards show dragging state
- **Column Highlighting**: Drop zones highlight on hover
- **Status Updates**: Automatically updates issue status on drop
- **Smooth Animations**: CSS transitions for professional feel

### How to Use
1. Click and hold any card
2. Drag to desired column
3. Release to drop
4. Status automatically updates via API

### Technical Details
- Uses HTML5 Drag and Drop API
- Sends PUT request to `/api/issues/{id}/status`
- Updates column counts automatically
- Shows success/error notifications

---

## 📥📤 Import/Export

### Export Features

**Kanban Board Export**
- Format: CSV
- Includes: ID, Title, Status
- Filename: `kanban-board-YYYY-MM-DD.csv`
- Button: Top toolbar → Download icon

**Calendar Export**
- Format: CSV
- Includes: Date, Title, Event Type
- Filename: `calendar-YYYY-MM-DD.csv`

**Roadmap Export**
- Format: CSV
- Includes: Release Name, Type
- Filename: `roadmap-YYYY-MM-DD.csv`

### Import Features

**Import Modal**
- Drag & drop CSV/Excel files
- Live preview of data
- Column matching
- Validation before import
- Progress notifications

**Supported Formats**
- .csv (Comma-separated values)
- .xlsx (Excel 2007+)
- .xls (Excel 97-2003)

**How to Import**
1. Click Import button in Kanban Board toolbar
2. Drag file or click to browse
3. Preview shows parsed data
4. Confirm import
5. Success notification appears

---

## ⌨️ Keyboard Shortcuts

### Global Shortcuts
- `Ctrl/Cmd + D`: Toggle dark/light theme
- `Ctrl/Cmd + K`: Focus search bar
- `Escape`: Close modals/panels

### Kanban Board
- `Ctrl/Cmd + N`: Create new issue
- `Ctrl/Cmd + K`: Focus issue search

### Calendar
- `Ctrl/Cmd + T`: Jump to today

---

## 🔍 Advanced Search & Filtering

### Features
- **Real-time Search**: Filters as you type
- **Multi-column Search**: Searches across all visible fields
- **Status Filters**: Filter by task status
- **Type Filters**: Filter by task type (Bug, Story, Task)
- **Assignee Filters**: Filter by assigned user
- **Quick Filters**: Pre-defined filter sets

### Search Locations
- Dashboard: Project search
- Kanban Board: Issue search
- Calendar: Event search
- Roadmap: Release search

---

## 🎨 UI/UX Features

### Collapsible Sidebar
- **Toggle Button**: Circle button on sidebar edge
- **States**: Expanded (280px) / Collapsed (60px)
- **Smooth Animation**: 0.3s ease transition
- **Icon-only Mode**: Shows only icons when collapsed

### Toast Notifications
- **Position**: Bottom-right corner
- **Stack**: Multiple toasts stack vertically
- **Duration**: 5 seconds auto-dismiss
- **Close Button**: Manual dismiss option
- **Color-coded**: Different colors for each type

### Team Avatars
- **Initials Display**: Shows first 2 letters of username
- **Color-coded**: Each user has unique color
- **Overflow**: Shows "+X" for additional members
- **Tooltips**: Hover to see full name

### Loading States
- **Smooth Transitions**: All state changes animated
- **Hover Effects**: Subtle hover states on all interactive elements
- **Focus States**: Keyboard navigation support
- **Disabled States**: Clear visual feedback

---

## 📊 Data Visualization

### Kanban Board
- **4-Column Layout**: To Do, In Progress, In Review, Done
- **Card Counts**: Live count in column headers
- **Color-coded Labels**: Visual category identification
- **Issue Types**: Story, Bug, Task with unique icons

### Calendar
- **Month View**: Full month grid with events
- **Event Types**: Color-coded (Task, Meeting, Deadline, Milestone)
- **Today Highlighting**: Current day highlighted in blue
- **Multiple Events**: Stack multiple events per day

### Roadmap Timeline
- **Horizontal Bars**: Visual timeline representation
- **Color-coded Releases**: Each release has unique color
- **Month Headers**: Clear time markers
- **Sprint View**: Separate sprint visualization

---

## 🔐 Security Features

### Data Persistence
- **localStorage**: Theme, notifications stored locally
- **Session Management**: Secure session handling
- **CSRF Protection**: All API calls protected
- **Input Validation**: Client and server-side validation

### Privacy
- **Local Storage Only**: No tracking cookies
- **No External Analytics**: Privacy-first approach
- **Secure API Calls**: HTTPS only in production

---

## 🚀 Performance Optimizations

### Frontend
- **Lazy Loading**: Icons loaded on demand
- **Debounced Search**: 300ms delay for search input
- **CSS Transitions**: GPU-accelerated animations
- **Minimal Reflows**: Optimized DOM manipulation

### Caching
- **localStorage**: Notifications and theme cached
- **Icon Cache**: Lucide icons cached after first load
- **Event Delegation**: Efficient event handling

---

## 📱 Responsive Design

### Breakpoints
- Desktop: > 1024px (Full sidebar)
- Tablet: 768px - 1024px (Collapsible sidebar)
- Mobile: < 768px (Hidden sidebar with toggle)

### Mobile Features
- Touch-friendly buttons (44px min size)
- Swipe gestures for navigation
- Responsive grids
- Stacked layouts on small screens

---

## 🎯 Browser Support

### Fully Supported
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

### Partial Support
- IE 11 (Basic functionality only)
- Older Safari (No some CSS features)

---

## 🔧 Developer Features

### JavaScript APIs

**Theme Manager**
```javascript
// Get current theme
window.themeManager.getTheme(); // 'dark' or 'light'

// Toggle theme
window.themeManager.toggleTheme();

// Apply specific theme
window.themeManager.applyTheme('dark');
```

**Notification Manager**
```javascript
// Add notification
window.notificationManager.addNotification({
    title: 'Title',
    message: 'Message',
    type: 'success' // or 'error', 'warning', 'info'
});

// Get all notifications
window.notificationManager.getNotifications();

// Mark as read
window.notificationManager.markAsRead(notificationId);

// Clear all
window.notificationManager.clearAll();
```

**Drag Drop Manager**
```javascript
const dragDrop = new DragDropManager({
    onDrop: (data) => {
        console.log('Dropped:', data);
        // data = { cardId, sourceStatus, targetStatus, element }
    }
});

// Refresh after DOM changes
dragDrop.refresh();
```

---

## 📈 Future Enhancements

### Planned Features
- [ ] Time tracking and timesheets
- [ ] Burndown charts
- [ ] Sprint planning tools
- [ ] Advanced reporting
- [ ] File attachments
- [ ] Comments and activity feeds
- [ ] Real-time collaboration (WebSockets)
- [ ] Mobile app
- [ ] Email notifications
- [ ] Webhooks and integrations

---

## 🐛 Troubleshooting

### Theme Not Persisting
- Check browser localStorage is enabled
- Clear cache and reload
- Check console for errors

### Notifications Not Showing
- Ensure JavaScript is enabled
- Check notification-manager.js is loaded
- Verify no console errors

### Drag and Drop Not Working
- Ensure modern browser (not IE)
- Check drag-drop.js is loaded
- Verify cards have draggable="true"

### Import Failing
- Check file format (CSV, XLSX)
- Ensure proper column headers
- Verify file size < 10MB

---

## 📞 Support

For issues or feature requests, please check:
- Project documentation
- Console logs for errors
- Browser compatibility
- Network tab for API errors

---

**Version**: 2.0.0
**Last Updated**: January 2026
**License**: MIT
