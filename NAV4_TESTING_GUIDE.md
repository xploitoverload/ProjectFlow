# NAV4 Global Navigation - Testing Guide

**Date:** January 22, 2026  
**Status:** Ready for Testing  
**Server:** http://127.0.0.1:5000

---

## 🎯 Features Implemented

### 1. Command Palette (CMD+K)
**What it does:** Universal search and command execution interface

**How to test:**
1. Press `CMD+K` (Mac) or `CTRL+K` (Windows/Linux)
2. Command palette should appear with blur backdrop
3. Type to filter commands (try "dashboard", "issue", "settings")
4. Use arrow keys ↑↓ to navigate results
5. Press Enter to execute selected command
6. Press ESC to close

**Available Commands (20+):**
- **Navigate:** Dashboard, Issues, Backlog, Boards, Reports, Settings
- **Create:** Issue, Epic, Sprint, Project
- **View:** Calendar, Timeline, Gantt Chart
- **Settings:** User Settings, Project Settings, Notifications
- **Help:** Documentation, Support, Keyboard Shortcuts

### 2. Product Switcher (9-Dot Menu)
**What it does:** Access other Atlassian products

**How to test:**
1. Click the **grid icon** (9 dots) in top-left header
2. Dropdown should appear with 6 products
3. Hover over each product to see hover effect
4. Products available:
   - Jira Software
   - Confluence
   - Bitbucket
   - Trello
   - Opsgenie
   - Compass

### 3. Help Menu
**What it does:** Access documentation and support

**How to test:**
1. Click the **question mark icon** (help-circle) in header
2. Dropdown should appear with help options:
   - Documentation
   - Support Center
   - Help Center
   - Keyboard Shortcuts
   - What's New
3. Click "Keyboard Shortcuts" to see all available shortcuts

### 4. Enhanced Search Bar
**What it does:** Opens command palette on click

**How to test:**
1. Click the search bar in header (shows "Search or jump to...")
2. Should open command palette (same as CMD+K)
3. Notice the `⌘K` hint on right side of search bar

### 5. Keyboard Shortcuts
**What it does:** Quick navigation without mouse

**Shortcuts to test:**
- `CMD/CTRL + K` - Open command palette
- `CMD/CTRL + /` - Show keyboard shortcuts
- `C` - Create new issue
- `G then D` - Go to dashboard
- `ESC` - Close all open menus
- `/` - Focus search bar

### 6. Create Button
**What it does:** Quick access to create new items

**How to test:**
1. Click the blue "Create" button in header
2. Currently links to create issue page
3. (Future: will show dropdown with Issue, Epic, Sprint, Project options)

---

## 🎨 Visual Elements

### Header Layout (Left to Right):
```
[9-Dot Menu] [Sidebar Toggle] [Breadcrumb: Home > Dashboard]

[Search Bar with ⌘K] [Create Button] [Bell Icon] [Help Icon] [Theme Toggle] [Settings] [Sign Out]
```

### Command Palette Design:
- **Size:** 640px width, center screen
- **Backdrop:** Blur effect with dark overlay
- **Search:** Live filtering as you type
- **Navigation:** Arrow keys, Enter to select
- **Footer:** Shows keyboard hints (↑↓ Navigate, ↵ Select, Esc Close)

### Product Switcher Design:
- **Size:** 360px width
- **Layout:** 3-column grid
- **Icons:** Branded colors for each product
- **Hover:** Scale and background color change

### Help Menu Design:
- **Size:** 280px width
- **Sections:** Grouped by type
- **Icons:** Left-aligned with descriptions
- **Links:** External link indicator on right

---

## 🧪 Test Scenarios

### Scenario 1: Quick Navigation
1. Press `CMD+K`
2. Type "board"
3. Press Enter
4. Should navigate to boards page

### Scenario 2: Product Switching
1. Click 9-dot grid icon
2. Hover over "Confluence"
3. Click to navigate (currently shows alert)

### Scenario 3: Help Access
1. Click help icon (question mark)
2. Click "Keyboard Shortcuts"
3. Should show all available shortcuts

### Scenario 4: Theme Toggle
1. Click moon/sun icon
2. Theme should switch between dark/light
3. All navigation elements should respect theme

### Scenario 5: Search to Command
1. Click search bar
2. Command palette opens
3. Type command
4. Execute with Enter

---

## 🐛 What to Look For

### Expected Behavior:
✅ Command palette opens/closes smoothly  
✅ Keyboard shortcuts work in all contexts  
✅ Dropdowns position correctly  
✅ Icons render properly (Lucide icons)  
✅ Hover states work on all buttons  
✅ Theme toggle updates navigation colors  
✅ Mobile responsive (hide search bar on small screens)  

### Known Limitations:
⚠️ Product links show alerts (not real navigation)  
⚠️ Create button doesn't have dropdown yet  
⚠️ Recent items not tracked yet  
⚠️ Search autocomplete not implemented  
⚠️ Some commands navigate to placeholder pages  

---

## 📊 Implementation Status

**Phase 1 (NAV4 Navigation): 15% Complete**

**Completed (15 features):**
- ✅ Command palette with 20+ commands
- ✅ Product switcher with 6 products
- ✅ Help menu with 5 links
- ✅ Keyboard shortcuts system (6 shortcuts)
- ✅ Enhanced search bar
- ✅ Create button
- ✅ All CSS styling
- ✅ JavaScript event handlers

**In Progress (5 features):**
- 🔄 Quick switcher (projects/boards)
- 🔄 Recent items tracking
- 🔄 Starred items system
- 🔄 Search autocomplete
- 🔄 Custom keyboard shortcuts

**Not Started (80+ features):**
- ⏳ Sidebar navigation improvements
- ⏳ Breadcrumb overflow handling
- ⏳ Command history
- ⏳ Project-specific commands
- ⏳ And 76 more...

---

## 🔧 Technical Details

### Files Modified:
1. **templates/dashboard.html**
   - Added product switcher button with grid icon
   - Added help menu button with question-circle icon
   - Enhanced search bar with CMD+K hint
   - Added create button
   - Added command palette HTML structure
   - Added product switcher dropdown HTML
   - Added help menu dropdown HTML

2. **static/js/global-navigation.js** (NEW)
   - GlobalNavigation class with all methods
   - Command palette logic
   - Keyboard event handlers
   - Product switcher toggle
   - Help menu toggle
   - 20+ predefined commands

3. **static/css/global-navigation.css** (NEW)
   - Command palette modal styles
   - Product switcher dropdown styles
   - Help menu dropdown styles
   - Keyboard shortcut hint styles
   - Responsive breakpoints
   - Dark mode support

### Dependencies:
- Lucide Icons (already included)
- CSS Variables from design-system.css
- Theme Manager for dark mode

---

## 📝 Next Steps

### Immediate (Next Session):
1. Test all features listed above
2. Report any bugs or issues
3. Verify keyboard shortcuts work
4. Check responsive behavior on mobile

### Short Term (Phase 1 Completion):
1. Add create button dropdown menu
2. Implement quick switcher
3. Add recent items tracking
4. Enhance search with autocomplete
5. Add command history

### Long Term (Phases 2-14):
1. Service Desk features (107 items)
2. Calendar view (85 items)
3. Timeline/Roadmap (90 items)
4. AI features (40 items)
5. And 450+ more features...

---

## 🚀 How to Start Testing

1. **Ensure server is running:**
   ```bash
   cd "/home/KALPESH/Stuffs/Project Management"
   python app.py
   ```

2. **Open browser:**
   ```
   http://127.0.0.1:5000
   ```

3. **Login to dashboard**

4. **Test command palette:**
   - Press `CMD+K` or `CTRL+K`
   - Try searching for commands
   - Use arrow keys to navigate
   - Press Enter to execute

5. **Test product switcher:**
   - Click 9-dot grid icon in top-left
   - Hover over products
   - Verify dropdown appears

6. **Test help menu:**
   - Click question mark icon
   - Verify dropdown appears
   - Click on links

7. **Test keyboard shortcuts:**
   - Try all shortcuts listed above
   - Verify they work as expected

---

## ✅ Success Criteria

Navigation system is working if:
- ✅ Command palette opens with CMD+K
- ✅ All 20+ commands are searchable
- ✅ Keyboard navigation works (arrows, Enter, ESC)
- ✅ Product switcher shows all 6 products
- ✅ Help menu displays all links
- ✅ Search bar opens command palette
- ✅ Theme toggle updates all colors
- ✅ All icons render correctly
- ✅ No console errors
- ✅ Responsive on mobile

---

**Ready to test!** 🎉

Report any issues and I'll fix them immediately. After testing, we'll continue with the remaining 85% of Phase 1 features and then move on to Phases 2-14.
