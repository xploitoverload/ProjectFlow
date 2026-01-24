# JIRA UI Features - Complete Analysis

## ⚠️ IMPORTANT FINDINGS

The 3 JIRA HTML files analyzed are **Single-Page Applications (SPAs)** that render their UI dynamically using JavaScript. The exported HTML files contain:

1. **Minimal Server-Rendered HTML** - Only basic document structure (head, body)
2. **JavaScript Module Preloading** - UI components loaded via JavaScript modules
3. **Embedded Configuration** - Feature flags, A/B testing configs, and experiments in JSON
4. **CSS-in-JS Styling** - Atlassian Design System (ADS) tokens and utility classes

---

## 📁 FILES ANALYZED

### 1. Service Desk - Custom Queue View
**File:** `https___kalpeshsolanki1337.atlassian.net_jira_servicedesk_projects_SUP_queues_custom_3.html`
- **Lines:** 1,698
- **Product:** JIRA Service Management
- **View:** Agent queue view for support tickets

### 2. Software - Calendar View
**File:** `https___kalpeshsolanki1337.atlassian.net_jira_software_c_projects_TEST_boards_1_calendar.html`
- **Lines:** 1,697
- **Product:** JIRA Software
- **View:** Calendar board view for sprint planning

### 3. Software - Timeline/Roadmap View
**File:** `https___kalpeshsolanki1337.atlassian.net_jira_software_c_projects_TEST_boards_1_timeline.html`
- **Lines:** 1,728
- **Product:** JIRA Software
- **View:** Timeline/roadmap view for epic planning

---

## 🎨 DESIGN SYSTEM - ATLASSIAN DESIGN SYSTEM (ADS)

### CSS Custom Properties (Design Tokens)

```css
/* Color System */
--ds-surface: #FFFFFF;                    /* Base surface color */
--ds-surface-overlay: #FFFFFF;            /* Overlay surface */
--ds-surface-raised: #F4F5F7;            /* Elevated surface */
--ds-surface-sunken: #F4F5F7;            /* Depressed surface */

--ds-text: #172B4D;                       /* Primary text */
--ds-text-subtle: #6B778C;               /* Secondary text */
--ds-text-subtlest: #6B6E76;            /* Tertiary text */
--ds-text-inverse: #FFFFFF;              /* Text on dark backgrounds */

--ds-border: #0B120E24;                   /* Default border */
--ds-border-bold: #7D818A;               /* Emphasized border */
--ds-border-input: #8C8F97;              /* Form input borders */
--ds-border-focused: #4688EC;            /* Focus state */
--ds-border-selected: #1868DB;           /* Selected state */
--ds-border-inverse: #FFFFFF;            /* Inverse border */

/* Accent Colors */
--ds-border-accent-blue: #357DE8;        /* Blue accent */
--ds-border-accent-purple: #AF59E1;      /* Purple accent */
--ds-border-accent-lime: #6A9A23;        /* Lime accent */

/* Border Widths */
--ds-border-width: 1px;
--ds-border-width-selected: 2px;
--ds-border-width-focused: 2px;

/* Border Radius */
--ds-radius-xsmall: 2px;
--ds-radius-small: 4px;
--ds-radius-medium: 6px;
--ds-radius-large: 8px;
--ds-radius-xlarge: 12px;
--ds-radius-full: 50%;

/* Spacing Scale (8px base) */
--ds-space-0: 0px;
--ds-space-025: 2px;
--ds-space-050: 4px;
--ds-space-075: 6px;
--ds-space-100: 8px;
--ds-space-150: 12px;
--ds-space-200: 16px;
--ds-space-250: 20px;
--ds-space-300: 24px;
--ds-space-400: 32px;
--ds-space-500: 40px;
--ds-space-600: 48px;

/* Elevation/Shadows */
--ds-elevation-surface: #FFFFFF;
--ds-elevation-surface-current: #FFFFFF;
--ds-shadow-raised: 0px 1px 1px rgba(9,30,66,0.25);
--ds-shadow-overlay: 0px 8px 12px rgba(9,30,66,0.15);

/* Color Mode */
--ds-color-mode: light;
```

### Typography System

```css
/* Font Family */
font-family: "Atlassian Sans", ui-sans-serif, -apple-system, 
             BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", 
             sans-serif;

/* Code Font */
font-family: "Atlassian Mono", ui-monospace, Menlo, "Segoe UI Mono", 
             "Ubuntu Mono", monospace;

/* Font Tokens */
--ds-font-heading-xxlarge: normal 600 35px/40px;
--ds-font-heading-xlarge: normal 600 29px/32px;
--ds-font-heading-large: normal 600 24px/28px;
--ds-font-heading-medium: normal 600 20px/24px;
--ds-font-heading-small: normal 600 16px/20px;
--ds-font-heading-xsmall: normal 600 14px/16px;
--ds-font-heading-xxsmall: normal 600 12px/16px;

--ds-font-body-large: normal 400 16px/24px;
--ds-font-body: normal 400 14px/20px;
--ds-font-body-small: normal 400 11px/16px;
--ds-font-body-UNSAFE_small: normal 400 12px/16px;

--ds-font-code: normal 400 0.875em/1;
```

---

## 🔧 JAVASCRIPT MODULE ARCHITECTURE

### Module Types Loaded

#### Service Desk Modules
```javascript
// Navigation
"servicedesk-queues-agent-and-issue-view"
"atlassian-navigation"
"jira-horizontal-nav-entrypoint"

// Core Functionality
"servicedesk-common"
"servicedesk-agents-view"
"jira-spa-runtime"

// Shared Libraries
"shared-vendor-modules"
"commons-modules"
"atlaskit-components"
```

#### Calendar View Modules
```javascript
// Calendar Specific
"calendar-view-entrypoint"
"empty.js" // Contextual entrypoint

// Navigation
"jira-horizontal-nav-entrypoint"
"nav4-projects-content-view-query"

// Core
"jira-spa-runtime"
"bifrost-frontend-assets"
```

#### Timeline View Modules
```javascript
// Roadmap Specific
"classic-roadmap-entrypoint"
"timeline-view-components"

// Navigation
"nav4-jsw-project-entry-point"
"nav4-projects-content-view-query"
```

---

## 🎯 UI COMPONENT PATTERNS (From CSS Classes)

### 1. **Button Components**

```css
/* Button Base Classes */
._2rkom6m2 {
  border-radius: var(--ds-radius-small, 4px) !important;
}

._zs12m6m2 button {
  border-radius: var(--ds-radius-small, 4px) !important;
}

/* Button Transitions */
._v564imuv {
  transition: background 0.1s ease-out, 
              box-shadow 0.15s cubic-bezier(0.47, 0.03, 0.49, 1.38);
}

._v5641rzy {
  transition: transform 0.15s ease-out, 
              box-shadow 0.15s ease-out;
}
```

**Implementation Example:**
```html
<button class="_2rkom6m2 _v564imuv" 
        style="
          background: var(--ds-background-neutral-subtle);
          color: var(--ds-text);
          padding: var(--ds-space-100) var(--ds-space-200);
          border: var(--ds-border-width) solid var(--ds-border);
          border-radius: var(--ds-radius-small);
          transition: background 0.1s ease-out;
        ">
  Button Text
</button>
```

---

### 2. **Input Fields**

```css
/* Text Field Container */
._1a851mok > [data-ds--text-field--container] {
  border-radius: var(--ds-radius-large, 8px);
}

._1sixia51 > [data-ds--text-field--container] {
  border: var(--ds-border-width, 1px) solid var(--ds-border, #0B120E24);
}

/* Input Focus State */
._19itt0uh {
  border: var(--ds-border-width, 1px) solid var(--ds-border-focused, #4688EC);
}

._19itfyzg {
  border: var(--ds-border-width, 1px) solid var(--ds-border-selected, #1868DB);
}
```

**Implementation Example:**
```html
<div data-ds--text-field--container class="_1a851mok">
  <input type="text" 
         placeholder="Search..." 
         style="
           border: var(--ds-border-width) solid var(--ds-border);
           border-radius: var(--ds-radius-large);
           padding: var(--ds-space-100) var(--ds-space-150);
           font: var(--ds-font-body);
         ">
</div>
```

---

### 3. **Checkbox Components**

```css
/* Checkbox Base */
._1yc0glyw input[type="checkbox"] {
  border: none;
}

._rfx31qll:before {
  border-radius: var(--ds-radius-full, 50%);
}

/* Checkbox Transitions */
._pdykkete:before {
  transition: transform 0.2s ease;
}

._1abj1mn3 > input[type="checkbox"] + span > svg {
  transition: color 0.2s ease-in-out, fill 0.2s ease-in-out;
}

/* Focus State */
._den5vp1g > input[type="checkbox"]:focus + span:after {
  border: var(--ds-border-width-selected, 2px) solid 
          var(--ds-border-focused, #4688EC);
}

._zh8l1b66 > input[type="checkbox"]:focus + span:after {
  border-radius: var(--ds-space-050, 4px);
}
```

**Implementation Example:**
```html
<label class="_1abj1mn3">
  <input type="checkbox" style="opacity: 0; position: absolute;">
  <span style="
    display: inline-flex;
    width: 16px;
    height: 16px;
    border: var(--ds-border-width) solid var(--ds-border);
    border-radius: var(--ds-radius-xsmall);
    transition: all 0.2s ease-in-out;
  ">
    <svg width="16" height="16">
      <path d="M5 8l2 2 4-4" stroke="currentColor" fill="none"/>
    </svg>
  </span>
</label>
```

---

### 4. **Radio Buttons**

```css
/* Radio Base */
._19it3vzd {
  border: var(--ds-border-width, 1px) solid var(--radio-border-color);
}

._v56415j1 {
  transition: border-color 0.2s ease-in-out, 
              background-color 0.2s ease-in-out;
}

/* Selected State */
._16r2ucr4:after {
  background: var(--radio-dot-color);
}

._qc5orqeg:after {
  transition: background-color 0.2s ease-in-out, 
              opacity 0.2s ease-in-out;
}
```

**Implementation Example:**
```html
<label class="_v56415j1">
  <input type="radio" name="option" style="opacity: 0; position: absolute;">
  <span style="
    display: inline-flex;
    width: 20px;
    height: 20px;
    border: var(--ds-border-width) solid var(--ds-border);
    border-radius: var(--ds-radius-full);
    position: relative;
  ">
    <span style="
      width: 8px;
      height: 8px;
      background: var(--ds-background-selected-bold);
      border-radius: var(--ds-radius-full);
      margin: auto;
      opacity: 0;
      transition: opacity 0.2s ease-in-out;
    "></span>
  </span>
</label>
```

---

### 5. **Border Styles**

```css
/* Border Variants */
._19it1axi {
  border: var(--ds-border-width, 1px) solid var(--ds-border-bold, #7D818A);
}

._19it1ps9 {
  border: var(--ds-border-width, 1px) solid var(--ds-border-inverse, #FFFFFF);
}

._19it1uh4 {
  border: var(--ds-border-width-selected, 2px) solid 
          var(--ds-border, #0B120E24);
}

._19itz0c1 {
  border: var(--ds-border-width-selected, 2px) solid 
          var(--ds-border-selected, #1868DB);
}

._19itno8c {
  border: var(--ds-border-width, 1px) solid 
          var(--ds-border-input, #8C8F97);
}

/* Accent Borders */
._19it1cdj {
  border: var(--ds-border-width, 1px) solid 
          var(--ds-border-accent-lime, #6A9A23);
}

._19itnf5y {
  border: var(--ds-border-width, 1px) solid 
          var(--ds-border-accent-purple, #AF59E1);
}

._19it1usj {
  border: var(--ds-border-width, 1px) solid 
          var(--ds-border-accent-blue, #357DE8);
}

._19it11e4 {
  border: var(--ds-border, #DFE1E6) var(--ds-border-width, 1px) solid;
}
```

---

### 6. **Border Radius Utilities**

```css
._2rkom6m2 { border-radius: var(--ds-radius-small, 4px) !important; }
._2rko1eiz { border-radius: var(--ds-radius-small, 6px); }
._2rkoy0do { border-radius: var(--ds-radius-small, 8px); }
._2rkobz73 { border-radius: var(--ds-radius-large, 6px); }
._2rko8r4n { border-radius: var(--ds-radius-small, 0.25rem); }
._2rko1ps5 { border-radius: var(--ds-radius-xlarge, 12px) !important; }
._2rko18qm { border-radius: var(--ds-radius-large, 3px); }
._2rko1b66 { border-radius: var(--ds-space-050, 4px); }
._2rko1kw7 { border-radius: inherit; }
._2rkoglyw { border-radius: none; }
._2rkov47k { border-radius: var(--ds-space-250, 20px); }
._rfx31qll:before { border-radius: var(--ds-radius-full, 50%); }
```

---

### 7. **Transitions**

```css
/* Transform Transitions */
._v5641b8g { transition: transform 0.35s ease-in-out; }
._v564kete { transition: transform 0.2s ease; }
._v5641e03 { transition: transform; }
._v5641rzy { transition: transform 0.15s ease-out, box-shadow 0.15s ease-out; }
._v5641qqv { transition: padding-top 0.2s ease-out; }

/* Opacity Transitions */
._v564glyw { transition: none; }
._v564g17y { transition: opacity 0.3s; }
._v5644ql6 { transition: opacity 0.36s ease-in; }
._v5641hrg { transition: opacity 0.2s ease; }
._v56414fr { transition: opacity 0.3s ease-in-out; }
._v564brmi { transition: opacity; }
._v564m7ou { transition: opacity 0.2s ease-in-out; }

/* Max-Height Transitions */
._v5641xzp { transition: max-height 0.3s; }
._v5641376 { transition: max-height 0.6s ease-in-out, opacity 0.6s ease-in-out; }
._v564wor5 { transition: max-height; }
._v564pilp { transition: opacity 0.6s ease, max-height 0.6s ease; }

/* Color Transitions */
._v564h5h4 { transition: color 0.2s ease; }
._v564mfn2 { transition: background-color 0.2s ease; }
._v56415j1 { transition: border-color 0.2s ease-in-out, background-color 0.2s ease-in-out; }

/* Box Shadow Transitions */
._v564nm7n { transition: box-shadow 0.25s ease-in-out; }
._v564imuv { transition: background 0.1s ease-out, box-shadow 0.15s cubic-bezier(0.47, 0.03, 0.49, 1.38); }

/* Complex Transitions */
._v564f3tm { transition: all 0.12s ease-out; }
._v564fnf5 { transition: 0.2s; }
._v5641gvb { transition: all 0.2s ease-in-out; }
._v564ybtr { transition: all 0.3s; }
._v5641eho { transition: all 0.1s; }
._v564thzt { transition: background 0.2s; }
._v564b9zd { transition: margin-top 0.5s ease; }
._v5641rb3 { transition: width 0.3s; }
```

---

### 8. **Spacing/Gap Utilities**

```css
._zulpze3t { gap: var(--ds-space-0, 0); }
._zulp1ejb { gap: var(--ds-space-300, 24px); }
._zulpxy5q { gap: var(--ds-space-400, 32px); }
._zulp1yov { gap: var(--ds-space-100, 10px); }

._14wu1b66 > span { gap: var(--ds-space-050, 4px); }
._1all1b66 > a { gap: var(--ds-space-050, 4px); }
```

---

### 9. **Gradients**

```css
/* Overlay Gradients */
._11q7kiet {
  background: linear-gradient(180deg, transparent 0%, 
              var(--ds-surface-overlay, #FFFFFF) 100%);
}

._11q71ord {
  background: linear-gradient(180deg, #101214, #0E162400) no-repeat;
}

._11q780lm {
  background: linear-gradient(0deg, #101214, #0E162400);
}

/* Shimmer/Loading Gradient */
._11q7gl65 {
  background: linear-gradient(90deg, 
    var(--ds-text-subtlest, #6B6E76) 0%, 
    var(--ds-text-subtlest, #6B6E76) 20%, 
    #C7CDDC 40%, 
    var(--ds-text-subtlest, #6B6E76) 60%, 
    var(--ds-text-subtlest, #6B6E76) 80%, 
    #C7CDDC 90%, 
    var(--ds-text-subtlest, #6B6E76) 100%);
}

/* Fade Gradients for Overflow */
._13xs1ypl:last-of-type {
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--ds-elevation-surface-current, #FFFFFF) 10%);
}

/* Disabled Fade Overlay */
._nhkt1ecz.disabled:after {
  background: linear-gradient(270deg, 
    rgba(255, 255, 255, 0.95) 40.23%, 
    rgba(255, 255, 255, 0.55) 58.33%, 
    rgba(255, 255, 255, 0) 77.49%);
}

._j5n71tsn.disabled + ._j5n71tsn.disabled:after {
  background: linear-gradient(90deg, 
    rgba(255, 255, 255, 0.95) 40.23%, 
    rgba(255, 255, 255, 0.55) 58.33%, 
    rgba(255, 255, 255, 0) 77.49%);
}

/* Dark Mode Variants */
._nhktj96x.disabled:after {
  background: linear-gradient(270deg, 
    rgba(34, 39, 43, 0.95) 40.23%, 
    rgba(34, 39, 43, 0.55) 58.33%, 
    rgba(34, 39, 43, 0) 77.49%);
}

._j5n7zopo.disabled + ._j5n7zopo.disabled:after {
  background: linear-gradient(90deg, 
    rgba(34, 39, 43, 0.95) 40.23%, 
    rgba(34, 39, 43, 0.55) 58.33%, 
    rgba(34, 39, 43, 0) 77.49%);
}

/* Conic Gradients (Color Wheels/Spinners) */
._1s6kssrl:before {
  background: conic-gradient(from 0deg, 
    #1868DB 0deg, #1868DB 30deg, 
    #FCA700 31deg, #FCA700 40deg, 
    #FCA700 75deg, #FCA700 85deg, 
    #BF63F3 86deg, #BF63F3 120deg, 
    #BF63F3 165deg, #BF63F3 175deg, 
    #82B536 176deg, #82B536 210deg, 
    #82B536 255deg, #82B536 265deg, 
    #1868DB 266deg, #1868DB 300deg, 
    #1868DB 360deg);
}

._11q73430 {
  background: conic-gradient(from 0deg, 
    #1868DB 0deg, #1868DB 45deg, 
    #FCA700 46deg, #FCA700 90deg, 
    #FCA700 135deg, #BF63F3 136deg, 
    #BF63F3 180deg, #BF63F3 225deg, 
    #82B536 226deg, #82B536 270deg, 
    #82B536 315deg, #1868DB 316deg, 
    #1868DB 360deg);
}
```

---

### 10. **Animations**

```css
/* Loading Animations */
._y44v1gpk { animation: k1w4xhaz 1.5s infinite forwards; }
._y44v18gg { animation: k1iz2f8l 1.5s infinite forwards; }
._y44voqx9 { animation: kzhlxv2 1.5s infinite forwards; }

/* Pulse/Blink Animations */
._y44v1a73 { animation: k1b1crim 1s step-end infinite; }
._y44vrrgq { animation: kw9jhjt 1s step-end infinite; }
._y44v1y3w { animation: kaptqs9 1s step-end infinite; }

/* Spin Animation */
._y44vgcf4 { animation: k1cqqt0g 4s linear infinite; }

/* Particle Animations */
._y44v7u0o { 
  animation: reaction-particle-fade ease-in-out, 
             reaction-particle-float ease; 
}

/* Flicker Animation */
._y44vkmg5 { animation: flickerAnimation 2s infinite; }

/* Fade In Animation */
._1xqk11a8 .ProseMirror { animation: kgnpaw5 0.3s ease-in forwards; }

/* Scale Animation */
._16qqwbcu:before { animation: kriycry 0.4s ease-out 0.1s; }
```

---

### 11. **Focus States**

```css
/* Outline Focus */
._1a37dfik {
  outline: var(--ds-border-width-focused, 2px) solid 
           var(--ds-border-focused, #4688EC);
}

._1a371kqe {
  outline: var(--ds-border-width-focused, 2px) solid 
           var(--ds-border-focused, #85B8FF);
}

button:focus + ._1hlmjc5g {
  outline: solid var(--ds-border-width-focused, 2px) 
           var(--ds-border-focused, #4C9AFF);
}

/* Border Focus */
._19itt0uh {
  border: var(--ds-border-width, 1px) solid 
          var(--ds-border-focused, #4688EC);
}
```

---

### 12. **Grid/Layout**

```css
/* Grid Area */
._nd5l1cy2 { grid-area: title; }

/* Inset */
._1tesidpf:before { inset: 0; }
```

---

### 13. **Margins & Padding**

```css
/* Margins */
._18s8ze3t { margin: var(--ds-space-0, 0); }

/* Padding */
._1yt41uce { 
  padding: var(--ds-space-100, 8px) var(--ds-space-100, 8px); 
}
```

---

### 14. **Font Variations**

```css
/* Heading Fonts */
._11c8nbxd {
  font: var(--ds-font-heading-small, normal 600 16px/20px ui-sans-serif, 
        -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, 
        "Helvetica Neue", sans-serif);
}

/* Body Fonts */
._11c8fhey {
  font: var(--ds-font-body, normal 400 14px/20px "Atlassian Sans", 
        ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", 
        Ubuntu, "Helvetica Neue", sans-serif);
}

._11c8dcr7 {
  font: var(--ds-font-body-UNSAFE_small, normal 400 12px/16px ui-sans-serif, 
        -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, 
        "Helvetica Neue", sans-serif);
}

._11c81o8v {
  font: var(--ds-font-body-small, normal 400 11px/16px ui-sans-serif, 
        -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, 
        "Helvetica Neue", sans-serif);
}

._11c82smr {
  font: var(--ds-font-body, normal 400 14px/20px ui-sans-serif, 
        -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, 
        "Helvetica Neue", sans-serif);
}

/* Code Font */
._11c819w5 {
  font: var(--ds-font-code, normal 400 0.875em/1 "Atlassian Mono", 
        ui-monospace, Menlo, "Segoe UI Mono", "Ubuntu Mono", monospace);
}

/* Profile Card */
._vvzr1d4k#profilecard-name-label {
  font: var(--ds-font-body-large, normal 400 16px/24px "Atlassian Sans", 
        ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", 
        Ubuntu, "Helvetica Neue", sans-serif);
}

/* Menu Headings */
._92d7rymc [role="group"] [data-ds--menu--heading-item]:first-of-type {
  font: var(--ds-font-body-UNSAFE_small, normal 400 12px/16px 
        "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, 
        "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif);
}

/* Contextual Fonts */
._szplfhey:before,
._10hwfhey:first-of-type,
._nccufhey li,
._1i7vfhey p,
._12nxfhey h1 {
  font: var(--ds-font-body, normal 400 14px/20px "Atlassian Sans", 
        ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", 
        Ubuntu, "Helvetica Neue", sans-serif);
}
```

---

### 15. **List Styles**

```css
/* Remove List Styles */
._qtt8agmp {
  list-style: none !important;
}

._d1n8glyw ul {
  list-style: none;
}
```

---

### 16. **Table Styles (ProseMirror Rich Text Editor)**

```css
/* Table Header */
._1bqmidpf:last-of-type,
.ProseMirror .pm-table-wrapper > table thead ._2eacidpf:last-of-type,
.pm-table-wrapper > table thead ._1rmlidpf:last-of-type {
  border: 0;
}

._13xs1ypl:last-of-type,
.ProseMirror .pm-table-wrapper > table thead ._19xw1ypl:last-of-type,
.pm-table-wrapper > table thead ._ex0g1ypl:last-of-type {
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--ds-elevation-surface-current, #FFFFFF) 10%);
}

._19itidpf,
.ProseMirror .pm-table-wrapper > table thead ._aks5idpf,
.pm-table-wrapper > table thead ._1u3bidpf {
  border: 0;
}

/* Table Body */
._11c8fhey,
.ProseMirror .pm-table-wrapper > table tbody ._1otxfhey,
.pm-table-wrapper > table tbody ._1wi1fhey {
  font: var(--ds-font-body, normal 400 14px/20px "Atlassian Sans", 
        ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", 
        Ubuntu, "Helvetica Neue", sans-serif);
}

._19itidpf,
.ProseMirror .pm-table-wrapper > table tbody ._1i5zidpf,
.pm-table-wrapper > table tbody ._aifmidpf {
  border: 0;
}
```

---

### 17. **Emoji/Icon Styles**

```css
/* Emoji Sprite Background */
._jr50scvx .emoji-common-emoji-sprite {
  background: transparent no-repeat;
}

/* Emoji Node Styling */
._1wcg1qi0 .emoji-common-node {
  border-radius: var(--ds-radius-medium, 6px);
}
```

---

### 18. **Custom Item Styles (Menus/Dropdowns)**

```css
._1gxw12b0 .custom-item-style {
  border-radius: var(--ds-radius-small, 4px);
}
```

---

### 19. **Tab Styles**

```css
._qwyt1qi0 [role="tab"] {
  border-radius: var(--ds-radius-medium, 6px);
}
```

---

### 20. **Slider (Range Input) Styles**

```css
/* Webkit Slider Thumb */
._h2ksglyw::-webkit-slider-thumb { border: none; }

._1kdl1qll::-webkit-slider-thumb {
  border-radius: var(--ds-radius-full, 50%);
}

._m8f8bpmo::-webkit-slider-thumb {
  outline: solid var(--ds-border-width-selected, 2px) var(--thumb-border);
}

._1yz62hjt::-webkit-slider-thumb {
  transition: background-color 0.2s ease-in-out;
  -webkit-transition: background-color 0.2s ease-in-out;
}

/* Webkit Slider Track */
._10lridpf::-webkit-slider-runnable-track { border: 0; }

._g6tdlb4i::-webkit-slider-runnable-track {
  border-radius: var(--ds-radius-xsmall, 2px);
}

._vi4t2hjt::-webkit-slider-runnable-track {
  transition: background-color 0.2s ease-in-out;
  -webkit-transition: background-color 0.2s ease-in-out;
}

/* Firefox Slider Thumb */
._1yq0glyw::-moz-range-thumb { border: none; }

._108m1qll::-moz-range-thumb {
  border-radius: var(--ds-radius-full, 50%);
}

._1rf3bpmo::-moz-range-thumb {
  outline: solid var(--ds-border-width-selected, 2px) var(--thumb-border);
}

._1yeu2hjt::-moz-range-thumb {
  transition: background-color 0.2s ease-in-out;
  -moz-transition: background-color 0.2s ease-in-out;
}

/* Firefox Slider Track */
._15raidpf::-moz-focus-outer { border: 0; }

._e8hnidpf::-moz-range-progress { border: 0; }

._37ywlb4i::-moz-range-progress {
  border-radius: var(--ds-radius-xsmall, 2px);
}

._1tcb2hjt::-moz-range-progress {
  transition: background-color 0.2s ease-in-out;
  -moz-transition: background-color 0.2s ease-in-out;
}
```

---

## 🧩 EMBEDDED FEATURE FLAGS & EXPERIMENTS

The JavaScript configuration contains extensive feature flags and A/B testing experiments. These indicate UI features that may be conditionally rendered:

### Feature Flags Found

```javascript
// Context Menu
"isContextMenuCollapsible": true

// Grid Navigation
"isGridNavigationEnabled": true

// Work Item Display
"showRecurringWorkToggle": true

// Search Platform Experiments
"search_platform_experiment_layer"
"search_platform_results_experiment"
"jira_search_result_view_page_experiments"

// Calendar Specific
"calendar_view_settings"
"issue_date_range_selector"
"calendar_time_tracking"
```

---

## 📱 RESPONSIVE DESIGN PATTERNS

While specific breakpoints aren't visible in the exported HTML, the Atlassian Design System uses these standard breakpoints:

```css
/* Breakpoints (typical ADS values) */
@media (min-width: 480px)  { /* Mobile landscape */ }
@media (min-width: 768px)  { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop small */ }
@media (min-width: 1280px) { /* Desktop large */ }
@media (min-width: 1600px) { /* Desktop XL */ }
```

---

## 🎪 ACCESSIBILITY FEATURES

```css
/* Focus Indicators */
outline: var(--ds-border-width-focused, 2px) solid 
         var(--ds-border-focused, #4688EC);

/* ARIA Attributes Used */
aria-label
aria-labelledby
aria-describedby
role="button"
role="tab"
role="group"
role="navigation"

/* Data Attributes */
data-ds--text-field--container
data-ds--menu--heading-item
data-test-id
```

---

## 🏗️ HTML DOCUMENT STRUCTURE

```html
<!DOCTYPE html>
<html lang="en-US" 
      data-theme="light" 
      data-color-mode="light"
      data-light-theme="light"
      data-dark-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="apple-mobile-web-app-capable" content="yes">
  
  <!-- Atlassian Cloud Metadata -->
  <meta name="ajs-cloud-id" content="...">
  <meta name="ajs-atlassian-account-id" content="...">
  <meta name="ajs-trace-id" content="...">
  <meta name="ajs-locale" content="en_US">
  <meta name="ajs-product-editions" content="...">
  
  <!-- Favicons -->
  <link rel="icon" type="image/png" href="...">
  <link rel="apple-touch-icon" href="...">
  
  <!-- Font Preloading -->
  <link rel="preload" 
        href="/fonts/atlassian-sans-v4-latin-400.woff2" 
        as="font" 
        type="font/woff2" 
        crossorigin="anonymous">
  
  <!-- Module Preloading -->
  <link rel="modulepreload" href="..." nonce="...">
  
  <!-- Inline Scripts -->
  <script nonce="..." type="module">
    // Performance marking
    // Feature flag initialization
    // Config bootstrap
  </script>
</head>
<body style="
  background-color: var(--ds-surface);
  color: var(--ds-text);
  margin: 0;
">
  <!-- App root - content rendered by JavaScript -->
  <div id="app-root"></div>
  
  <!-- Module scripts -->
  <script type="module" src="..."></script>
</body>
</html>
```

---

## 🔐 SECURITY PATTERNS

```html
<!-- Content Security Policy via Nonce -->
<script nonce="RANDOM_NONCE_VALUE">
  // Script content
</script>

<link rel="modulepreload" href="..." nonce="RANDOM_NONCE_VALUE">
```

---

## 💡 IMPLEMENTATION RECOMMENDATIONS

### 1. **Use Design Tokens**
```css
/* ✅ DO */
.button {
  background: var(--ds-background-neutral);
  color: var(--ds-text);
  border-radius: var(--ds-radius-small);
  padding: var(--ds-space-100) var(--ds-space-200);
}

/* ❌ DON'T */
.button {
  background: #F4F5F7;
  color: #172B4D;
  border-radius: 4px;
  padding: 8px 16px;
}
```

### 2. **Component Pattern**
```html
<!-- Base Component Structure -->
<div class="component-wrapper">
  <div class="component-container" data-ds--component-type>
    <div class="component-header">
      <!-- Header content -->
    </div>
    <div class="component-body">
      <!-- Main content -->
    </div>
    <div class="component-footer">
      <!-- Footer content -->
    </div>
  </div>
</div>
```

### 3. **Transition Pattern**
```css
.interactive-element {
  /* Define all transitionable properties */
  transition: 
    background-color 0.2s ease-in-out,
    border-color 0.2s ease-in-out,
    box-shadow 0.15s cubic-bezier(0.47, 0.03, 0.49, 1.38),
    transform 0.15s ease-out;
}

.interactive-element:hover {
  transform: translateY(-1px);
  box-shadow: var(--ds-shadow-raised);
}

.interactive-element:active {
  transform: translateY(0);
}
```

### 4. **Focus Management**
```css
.focusable-element {
  outline: none; /* Remove default */
  position: relative;
}

.focusable-element:focus {
  outline: var(--ds-border-width-focused, 2px) solid 
           var(--ds-border-focused, #4688EC);
  outline-offset: 2px;
}

/* Or use box-shadow for inset focus */
.focusable-element:focus {
  box-shadow: 0 0 0 var(--ds-border-width-focused, 2px) 
              var(--ds-border-focused, #4688EC);
}
```

---

## 📊 KEY STATISTICS

- **Total Lines:** 5,123 (across 3 files)
- **CSS Classes Identified:** 500+ utility classes
- **Design Tokens:** 60+ CSS custom properties
- **Animations:** 15+ named animations
- **JavaScript Modules:** 20+ lazy-loaded modules
- **Supported Browsers:** Modern evergreen browsers (Chrome, Firefox, Safari, Edge)

---

## 🎯 PRACTICAL IMPLEMENTATION GUIDE

### Creating a JIRA-Style Card Component

```html
<div class="jira-card" style="
  background: var(--ds-surface-raised);
  border: var(--ds-border-width) solid var(--ds-border);
  border-radius: var(--ds-radius-large);
  padding: var(--ds-space-200);
  box-shadow: var(--ds-shadow-raised);
  transition: box-shadow 0.15s ease-out, transform 0.15s ease-out;
">
  <!-- Card Header -->
  <div class="card-header" style="
    display: flex;
    align-items: center;
    gap: var(--ds-space-100);
    margin-bottom: var(--ds-space-150);
  ">
    <span class="issue-key" style="
      font: var(--ds-font-body-small);
      color: var(--ds-text-subtle);
    ">PROJ-123</span>
    
    <span class="priority-icon" style="
      width: 16px;
      height: 16px;
      border-radius: var(--ds-radius-xsmall);
    ">
      <svg width="16" height="16"><!-- Priority icon --></svg>
    </span>
  </div>
  
  <!-- Card Title -->
  <h3 class="card-title" style="
    font: var(--ds-font-heading-small);
    color: var(--ds-text);
    margin: 0 0 var(--ds-space-100) 0;
  ">
    Implement user authentication
  </h3>
  
  <!-- Card Metadata -->
  <div class="card-metadata" style="
    display: flex;
    align-items: center;
    gap: var(--ds-space-150);
    font: var(--ds-font-body-small);
    color: var(--ds-text-subtle);
  ">
    <span class="assignee">
      <img src="avatar.jpg" 
           alt="User" 
           style="
             width: 20px;
             height: 20px;
             border-radius: var(--ds-radius-full);
           ">
    </span>
    
    <span class="status-badge" style="
      padding: var(--ds-space-025) var(--ds-space-100);
      border-radius: var(--ds-radius-small);
      background: var(--ds-background-accent-blue-subtlest);
      color: var(--ds-text-accent-blue);
    ">
      In Progress
    </span>
  </div>
</div>

<style>
.jira-card:hover {
  box-shadow: var(--ds-shadow-overlay);
  transform: translateY(-2px);
}
</style>
```

### Creating a JIRA-Style Button

```html
<button class="jira-button jira-button--primary" style="
  /* Base styles */
  font: var(--ds-font-body);
  font-weight: 500;
  padding: var(--ds-space-075) var(--ds-space-150);
  border: none;
  border-radius: var(--ds-radius-small);
  cursor: pointer;
  
  /* Primary variant */
  background: var(--ds-background-brand-bold);
  color: var(--ds-text-inverse);
  
  /* Transitions */
  transition: 
    background-color 0.1s ease-out,
    box-shadow 0.15s cubic-bezier(0.47, 0.03, 0.49, 1.38);
">
  Create Issue
</button>

<style>
.jira-button:hover {
  background: var(--ds-background-brand-bold-hovered);
}

.jira-button:active {
  background: var(--ds-background-brand-bold-pressed);
}

.jira-button:focus {
  outline: var(--ds-border-width-focused) solid var(--ds-border-focused);
  outline-offset: 2px;
}

/* Secondary variant */
.jira-button--secondary {
  background: transparent;
  color: var(--ds-text);
  border: var(--ds-border-width) solid var(--ds-border);
}

.jira-button--secondary:hover {
  background: var(--ds-background-neutral-hovered);
}

/* Subtle variant */
.jira-button--subtle {
  background: transparent;
  color: var(--ds-text);
}

.jira-button--subtle:hover {
  background: var(--ds-background-neutral-subtle-hovered);
}
</style>
```

### Creating a JIRA-Style Input Field

```html
<div class="jira-input-wrapper" style="position: relative;">
  <label class="jira-label" style="
    display: block;
    font: var(--ds-font-body-small);
    font-weight: 600;
    color: var(--ds-text-subtle);
    margin-bottom: var(--ds-space-075);
  ">
    Summary
  </label>
  
  <div data-ds--text-field--container style="
    position: relative;
    border-radius: var(--ds-radius-small);
  ">
    <input type="text" 
           class="jira-input" 
           placeholder="What needs to be done?"
           style="
             width: 100%;
             font: var(--ds-font-body);
             padding: var(--ds-space-100);
             border: var(--ds-border-width) solid var(--ds-border);
             border-radius: var(--ds-radius-small);
             background: var(--ds-surface);
             color: var(--ds-text);
             outline: none;
             transition: border-color 0.2s ease-in-out;
           ">
  </div>
</div>

<style>
.jira-input:hover {
  border-color: var(--ds-border-input);
}

.jira-input:focus {
  border-color: var(--ds-border-focused);
  box-shadow: 0 0 0 1px var(--ds-border-focused);
}

.jira-input::placeholder {
  color: var(--ds-text-subtlest);
}
</style>
```

---

## 🔍 CONCLUSION

These JIRA HTML exports are **client-side rendered SPAs** with:

1. **Minimal Static HTML** - Just document structure and config
2. **Dynamic UI Rendering** - All UI components loaded via JavaScript modules
3. **Design Token System** - Comprehensive CSS custom properties for theming
4. **Utility-First CSS** - Atomic CSS classes with hashed names
5. **Feature Flag Architecture** - Conditional rendering via experiments
6. **Modern Build System** - Module federation, code splitting, lazy loading

To replicate JIRA's UI:
- **Use the design tokens provided above**
- **Follow the component patterns shown**
- **Implement similar transitions and interactions**
- **Maintain accessibility with proper ARIA attributes**
- **Use a modern build system for code splitting**

---

## 📚 ADDITIONAL RESOURCES

### Atlassian Design System
- [Design Tokens](https://atlassian.design/foundations/design-tokens)
- [Component Library](https://atlassian.design/components)
- [Accessibility Guidelines](https://atlassian.design/foundations/accessibility)

### Implementation Libraries
- [@atlaskit/css-reset](https://www.npmjs.com/package/@atlaskit/css-reset)
- [@atlaskit/tokens](https://www.npmjs.com/package/@atlaskit/tokens)
- [@atlaskit/primitives](https://www.npmjs.com/package/@atlaskit/primitives)

---

**Document Version:** 1.0  
**Generated:** Based on JIRA Cloud exports (3 files, 5,123 total lines)  
**Coverage:** Design tokens, component patterns, animations, and implementation examples
