# Phase 1 Quick Testing Guide

## Setup
1. Start the Flask server: `python3 run.py`
2. Open browser: `http://127.0.0.1:5000`
3. Login credentials: **admin / admin123**

---

## Feature Testing

### 1. Search Autocomplete (CMD+K)
**Steps:**
1. Press `CMD+K` (or `Ctrl+K` on Windows/Linux)
2. Type a search query
3. Observe grouped results (Issues, Projects, Users)
4. Use ↑↓ arrow keys to navigate
5. Press `Enter` to select
6. Press `Esc` to close

**Expected:**
- Modal opens with search input focused
- Results appear after 300ms
- Keyboard navigation works
- Results show icons and descriptions

---

### 2. Project Switcher (G+P)
**Steps:**
1. Press `G` then `P` quickly
2. Modal should open with project list
3. Type to search/filter projects
4. Use arrow keys to navigate
5. Press `Enter` to select
6. Press `Esc` to close

**Expected:**
- Modal opens instantly
- Search filters projects in real-time
- Shows project key, name, status badge
- Navigation with keyboard works

---

### 3. Recent Items
**Steps:**
1. Navigate to a few issues/projects
2. Click "Recent" link in sidebar
3. Dropdown should show last 10 items
4. Click an item to navigate back

**Expected:**
- Dropdown appears with recent items
- Shows "Just now", "2m ago", etc.
- Icons match item type
- Max 10 items shown

---

### 4. Starred Items
**Steps:**
1. Find an issue or project card
2. Look for star button (☆)
3. Click to star it
4. Click "Starred" in sidebar
5. Dropdown shows starred items
6. Hover star button to unstar
7. Click to remove from starred

**Expected:**
- Star button appears on hover
- Star fills in yellow when clicked
- Sidebar shows count badge
- Dropdown groups by type
- Unstar removes from list

---

### 5. User Avatar Menu
**Steps:**
1. Click your avatar in sidebar footer
2. Menu opens with 6 options
3. Test each option:
   - Profile (navigates to profile)
   - Settings (navigates to settings)
   - Keyboard Shortcuts (opens modal with shortcuts)
   - What's New (opens modal with updates)
   - Theme (toggles light/dark mode)
   - Sign Out (logs out)

**Expected:**
- Menu appears above avatar
- All links work
- Modals display correctly
- Theme toggle updates icon
- Menu closes on click outside

---

### 6. Keyboard Shortcuts Modal
**Steps:**
1. Press `?` key anywhere
2. Modal should open showing all shortcuts
3. Grouped by category
4. Press `Esc` to close

**Expected:**
- Modal opens instantly
- Shows 15+ shortcuts
- Clean layout with kbd tags
- Closes on Esc or click outside

---

### 7. Notifications
**Steps:**
1. Look at bell icon in header
2. Should see red badge with number (5)
3. Click bell icon
4. Dropdown shows 5 sample notifications
5. Click checkmark to mark one as read
6. Click X to delete one
7. Click "Mark all as read" button
8. Click a notification to navigate

**Expected:**
- Badge shows unread count
- Dropdown has colored icons
- Unread notifications highlighted
- Actions work (mark read, delete)
- Badge updates in real-time
- Auto-polls every 30s

---

### 8. Sidebar Resize
**Steps:**
1. Hover over right edge of sidebar
2. Cursor changes to ↔
3. Line appears on edge
4. Click and drag left/right
5. Sidebar resizes smoothly
6. Release mouse
7. Refresh page
8. Width should be preserved

**Expected:**
- Handle visible on hover
- Drag is smooth
- Min width: 200px
- Max width: 400px
- Width persists after refresh
- Touch works on mobile

---

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `CMD+K` | Open Search |
| `G` + `D` | Go to Dashboard |
| `G` + `P` | Go to Projects / Open Project Switcher |
| `G` + `B` | Go to Board |
| `G` + `I` | Go to Issues |
| `G` + `R` | Go to Reports |
| `C` | Create Issue (when available) |
| `?` | Show Keyboard Shortcuts |
| `Esc` | Close Modal/Dropdown |
| `↑` `↓` | Navigate Lists |
| `Enter` | Select Item |

---

## Expected Behavior

### Dropdowns
- ✅ Smooth open/close animations
- ✅ Click outside to close
- ✅ Esc key closes
- ✅ Proper positioning (no overflow)

### Icons
- ✅ Lucide icons load correctly
- ✅ Icons have proper colors
- ✅ Icons scale appropriately

### Dark Mode
- ✅ Toggle works in user menu
- ✅ All components update colors
- ✅ Icons remain visible
- ✅ Dropdowns have correct backgrounds

### Performance
- ✅ Search debounce (300ms)
- ✅ Smooth animations (60fps)
- ✅ No layout shifts
- ✅ Fast API responses

---

## Troubleshooting

### Search not working
- Check if API endpoint returns data: `curl http://localhost:5000/api/v1/search/autocomplete?query=test`
- Check browser console for errors
- Verify JavaScript files loaded

### Notifications badge not showing
- Check database has notifications: Run migration again
- Check API endpoint: `curl http://localhost:5000/api/v1/notifications/unread-count`
- Check console for fetch errors

### Starred items not persisting
- Check if API returns starred items: `curl http://localhost:5000/api/v1/starred-items`
- Check database has starred_item table
- Verify toggle endpoint works

### Sidebar resize not saving
- Check browser localStorage: Dev tools → Application → Local Storage
- Should see key: `sidebar-width`
- Clear localStorage and try again

### Icons not appearing
- Verify Lucide library loaded
- Check network tab for lucide.min.js
- Verify `lucide.createIcons()` called

---

## Sample API Tests

```bash
# Get notifications
curl -X GET http://localhost:5000/api/v1/notifications

# Get unread count
curl -X GET http://localhost:5000/api/v1/notifications/unread-count

# Search autocomplete
curl -X GET "http://localhost:5000/api/v1/search/autocomplete?query=proj"

# Get recent items
curl -X GET http://localhost:5000/api/v1/recent-items

# Get starred items
curl -X GET http://localhost:5000/api/v1/starred-items

# Toggle star (requires authentication)
curl -X POST http://localhost:5000/api/v1/starred-items/toggle \
  -H "Content-Type: application/json" \
  -d '{"type":"issue","item_id":1,"title":"Test Issue","key":"PROJ-1"}'
```

---

## Browser Console Checks

Open browser developer tools (F12) and check:

### Successful Initialization
```
Recent items initialized
Project switcher setup complete
Search autocomplete initialized
Starred items initialized
User menu initialized
Sidebar resize initialized
Notifications initialized
```

### No Errors
- ❌ No red errors in console
- ❌ No 404s in Network tab
- ❌ No JavaScript exceptions

---

## Success Criteria

✅ All 7 features work as expected  
✅ No console errors  
✅ Smooth animations  
✅ Keyboard shortcuts functional  
✅ Dark mode works  
✅ Dropdowns position correctly  
✅ Icons load properly  
✅ API calls succeed  
✅ Data persists (starred, sidebar width)  
✅ Notifications update in real-time  

---

## Report Issues

If you find bugs:
1. Note the feature and steps to reproduce
2. Check browser console for errors
3. Check Network tab for failed requests
4. Check if database migration ran successfully
5. Verify all files were created/modified correctly

---

*Last Updated: January 23, 2026*
