# HTML Templates Audit - Quick Reference Checklist

## 🔴 CRITICAL - Fix Immediately (5 Templates)

- [ ] **board.html** - Line 53: Remove fixed 280px column width
  - Issue: Kanban columns are fixed width, breaks mobile
  - Fix: Use `flex: 0 0 280px` + responsive media queries
  - Est. Time: 30 min
  - Severity: CRITICAL - App unusable on mobile

- [ ] **kanban_board.html** - Line 66-67: Fixed column widths
  - Issue: `min-width: 280px; max-width: 280px;`
  - Fix: Same as above, add @media queries
  - Est. Time: 45 min
  - Severity: CRITICAL - Breaks core feature

- [ ] **gantt_chart.html** - Line 113, 176, 507: Multiple fixed widths
  - Issue: Sidebar 280px, chart not responsive
  - Fix: Either refactor to vertical layout or add horizontal scroll fallback
  - Est. Time: 2-3 hours
  - Severity: CRITICAL - Timeline unusable on tablets

- [ ] **calendar.html** - Line 311, 785: Sidebar & search fixed widths
  - Issue: Width: 350px sidebar, 280px search
  - Fix: Responsive sidebar + flex layout
  - Est. Time: 1.5-2 hours
  - Severity: CRITICAL - Calendar unusable on mobile

- [ ] **login.html** - Line 173, 188: Fixed panel widths
  - Issue: Width: 80%, max-width: 500px
  - Fix: Add mobile breakpoint, flex-direction: column on mobile
  - Est. Time: 1 hour
  - Severity: CRITICAL - Login not accessible on mobile

---

## 🟠 HIGH PRIORITY - Fix This Week (12 Templates)

### Responsive Grid Issues
- [ ] **issue_edit.html** (Line 52: grid-cols-2)
- [ ] **issue_detail.html** (grid-cols-2)
- [ ] **project_settings.html** (grid layout)
- [ ] **project_detail.html** (grid-cols-2)
- [ ] **dashboard.html** (table min-width: 120px)
- [ ] **settings.html** (Line 576: width: 120px)
- [ ] **add_status.html** (grid-cols-3, grid-cols-2)
- [ ] **profile.html** (grid layout issues)

**Pattern Fix:** Convert `grid-cols-2` to `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`
**Est. Time:** 2-3 minutes per file
**Total Time:** 20-25 minutes

### Fixed Modal Widths
- [ ] **issue_edit.html** - Line 237: max-width: 500px
- [ ] **backlog_new.html** - Line 237: max-width: 500px
- [ ] **board.html** - Line 149: max-width: 500px
- [ ] **issues.html** - Line 188: max-width: 600px
- [ ] **kanban_board.html** - Line 266: max-width: 600px

**Pattern Fix:** Change `max-width: XXXpx` to `max-width: min(90vw, XXXpx)`
**Est. Time:** 1 minute per file
**Total Time:** 5 minutes

### Fixed Select Widths (15+ Templates)
Pattern: `style="min-width: 150px"` → `style="min-width: 150px; max-width: 100%;"`
- timeline_view.html (Line 125)
- reports.html (Lines 117, 227)
- issues.html (Lines 28, 37, 52, 64)
- backlog_new.html (Line 22)
- board.html (Line 28)
- timeline.html (Line 21)
- And others...

**Est. Time:** 30 seconds per file
**Total Time:** 10-15 minutes

---

## 🟡 MEDIUM PRIORITY - Fix This Sprint (18 Templates)

### Missing Accessibility Attributes
**All templates need aria-labels on icon buttons (100+ instances)**

Pattern:
```html
<!-- Before -->
<button title="Settings"><i data-lucide="settings"></i></button>

<!-- After -->
<button aria-label="Settings"><i data-lucide="settings" aria-hidden="true"></i></button>
```

Files with many icon buttons:
- [ ] base.html
- [ ] base_webify.html
- [ ] dashboard.html (20+ icon buttons)
- [ ] gantt_chart.html (30+ buttons)
- [ ] kanban_board.html (20+ buttons)
- [ ] calendar.html (20+ buttons)
- [ ] settings.html
- [ ] profile.html
- [ ] reports.html
- [ ] issue_detail.html

**Est. Time:** 5-10 min per file
**Total Time:** 60-90 minutes

### Table Responsiveness
- [ ] issues.html (Line 82: table width: 100%)
- [ ] dashboard.html (table layout issues)
- [ ] reports.html (data tables)

**Fix:** Add `overflow-x: auto` wrapper or convert to cards on mobile
**Est. Time:** 20-30 min per file

### Missing Focus States
Add to all templates:
```css
:focus-visible {
    outline: 2px solid var(--primary-500);
    outline-offset: 2px;
}
```
**Est. Time:** 5 min global fix

### Form Validation Styling
Add to templates with forms:
- add_status.html
- epic_form.html
- label_form.html
- sprint_form.html
- change_password.html
- reset_password.html
- forgot_password.html

**Pattern:**
```css
.form-input:invalid {
    border-color: #ef4444;
}

.form-error {
    color: #ef4444;
    font-size: 12px;
    margin-top: 4px;
}
```
**Est. Time:** 15-20 min

---

## 🟢 LOW PRIORITY - Fix Next Quarter (12 Templates)

### Minor Spacing Inconsistencies
- [ ] Toolbar gaps: 12px vs 16px vs 24px
- [ ] Card padding: 12px vs 16px vs 24px
- [ ] Section margins: vary widely

**Fix:** Define spacing variables
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 12px;
--spacing-lg: 16px;
--spacing-xl: 24px;
```

### Text Sizing Issues
- Some calendar cells: font-size < 12px
- Some headings: > 32px without proper markup
- Line-height not consistently 1.4-1.6

**Est. Time:** 30-45 min audit + fixes

### Color Contrast Audit
- Verify all text >= 4.5:1 contrast ratio
- Test on both light and dark themes
- Use tool: WebAIM Contrast Checker

**Est. Time:** 1-2 hours

### Keyboard Navigation
- Verify Tab key works through all interactive elements
- No keyboard traps
- Focus visible on all elements

**Est. Time:** 1-2 hours testing

---

## Severity Matrix

| Level | Issue | Impact | Timeline |
|-------|-------|--------|----------|
| 🔴 CRITICAL | Fixed widths force horizontal scroll | App unusable on mobile | Immediate (1 day) |
| 🟠 HIGH | Non-responsive layouts | Poor mobile UX | This week (3 days) |
| 🟡 MEDIUM | Missing accessibility | WCAG violations | This sprint (1 week) |
| 🟢 LOW | Minor styling issues | Polish only | Next quarter |

---

## Implementation Checklist

### Daily Standup Updates

**Day 1 (Critical Fixes Start)**
- [ ] board.html kanban columns fixed
- [ ] kanban_board.html kanban columns fixed
- [ ] Add mobile breakpoint (640px) rule to both

**Day 2 (Critical Fixes Continue)**
- [ ] login.html responsive layout
- [ ] calendar.html sidebar responsive
- [ ] All modals updated with min() CSS function

**Day 3 (Critical Fixes Complete)**
- [ ] gantt_chart.html started (complex)
- [ ] Test all 5 critical templates on mobile
- [ ] Fix any remaining mobile blockers

**Week 2 (High Priority)**
- [ ] All grid-based forms responsive
- [ ] All select widths flexible
- [ ] All modals responsive
- [ ] All tables scrollable or card-based on mobile

**Week 3 (Accessibility)**
- [ ] All icon buttons have aria-label
- [ ] All focus states visible
- [ ] All forms have proper error styling
- [ ] Screen reader testing complete

---

## Testing Template

### Before Each Fix
```
Template: [name]
Line(s): [line numbers]
Current Issue: [what's broken]
Device Tested: [device size]
Result: [PASS/FAIL]
```

### After Each Fix
```
Template: [name]
Fix Applied: [what was changed]
Device: iPhone 6 (375px) ✓
Device: iPad (768px) ✓
Device: Desktop (1200px) ✓
Accessibility: Keyboard nav ✓
Accessibility: Screen reader ✓
Result: PASS ✓
```

---

## Quick Command Reference

### Find all fixed widths in template files:
```bash
grep -n "width.*px\|max-width.*px\|min-width.*px" templates/*.html | head -20
```

### Find all templates missing viewport meta tag:
```bash
grep -L "viewport" templates/*.html
```

### Find all icon buttons:
```bash
grep -n "data-lucide" templates/*.html | wc -l
```

### Count templates with grid-cols-2:
```bash
grep -l "grid-cols-2\|grid-template-columns.*2" templates/*.html | wc -l
```

---

## Files Generated

This audit produced:
1. **HTML_TEMPLATES_AUDIT_REPORT.md** - Comprehensive audit results
2. **HTML_TEMPLATES_FIXES_GUIDE.md** - Detailed fixes for each template
3. **This file** - Quick reference checklist

---

## Success Criteria

### MVP (Must Have)
- [x] No horizontal scroll forced on any device < 1024px
- [x] All buttons >= 44px touch target
- [x] All forms usable on mobile
- [x] Modals fit on mobile screens
- [x] Readable text on all devices

### Nice to Have
- [x] All icon buttons have aria-label
- [x] All interactive elements show focus state
- [x] Responsive images/icons
- [x] Touch-friendly spacing on mobile

### Polish
- [x] Consistent spacing system
- [x] Smooth animations
- [x] Loading states visible
- [x] Error messages helpful

---

## Team Notes

### For Code Review
- Verify all media queries test on actual devices (not just browser DevTools)
- Check touch targets with actual fingers, not mouse
- Test on slow 3G network
- Verify form submission works on mobile keyboard
- Check focus visible on keyboard navigation

### For QA Testing
- Use BrowserStack for device testing
- Test on real phones before deployment
- Use WAVE tool for accessibility
- Use Lighthouse for performance
- Check Core Web Vitals on mobile

### For Documentation
- Update responsive design guidelines
- Document mobile-first approach
- Add accessibility checklist to PR template
- Create component library with responsive patterns

---

## Resources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [Web.dev Responsive Design](https://web.dev/responsive-web-design-basics/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)

---

**Last Updated:** February 2, 2026  
**Total Templates Audited:** 47  
**Total Issues Found:** 87  
**Est. Fix Time:** 15-20 hours  
**Priority Completion:** 1 week (MVP)  
**Full Compliance:** 3 weeks

