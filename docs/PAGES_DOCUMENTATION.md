# Watchtower v2 - Pages Documentation

## Overview

This document provides comprehensive documentation for the **Overview** and **Assistants** pages in Watchtower v2, including all features, optimizations, and file locations for easy maintenance and future development.

---

## 📊 Overview Page

### **Location**: `dashboard/templates/dashboard/Overview.html`

### **Purpose**
The Overview page serves as the main dashboard homepage, displaying key metrics, quick actions, and system status.

### **Key Features**

#### 1. **Dynamic Breadcrumb Navigation**
- **File**: `templates/components/breadcrumb.html`
- **Usage**: Shows "Home" breadcrumb with dynamic organization context
- **Data Source**: `dashboard/views.py` - `overview()` function

#### 2. **Metric Cards System**
- **Component**: `templates/components/metric_card.html`
- **Layout**: 4-column responsive grid (1 column on mobile, 2 on tablet, 4 on desktop)
- **Metrics Displayed**:
  - Total Calls (with phone icon)
  - Success Rate (with check-circle icon)
  - Average Duration (with clock icon)
  - Total Cost (with dollar-sign icon)

#### 3. **Action Buttons**
- **Component**: `templates/components/button.html`
- **Buttons**:
  - "Create Assistant" (primary variant with plus icon)
  - "View Documentation" (secondary variant with book-open icon)

#### 4. **Icon System**
- **Sprite Component**: `templates/components/icon_sprite.html`
- **Fallback Component**: `templates/components/icon.html`
- **Sprite File**: `static/icons/sprite.svg`

### **File Structure**
```
Overview Page Files:
├── dashboard/templates/dashboard/Overview.html     # Main template
├── dashboard/views.py                              # Backend logic
├── templates/components/
│   ├── breadcrumb.html                            # Navigation component
│   ├── metric_card.html                           # Metric display
│   ├── button.html                                # Standardized buttons
│   ├── icon.html                                  # Legacy icon component
│   └── icon_sprite.html                           # Optimized icon component
└── static/icons/sprite.svg                        # SVG icon sprite
```

### **Data Flow**
1. **Request** → `dashboard/urls.py` → `dashboard/views.overview()`
2. **Context Data**:
   ```python
   context = {
       'organization': {...},           # Org details
       'breadcrumb_items': [...],       # Navigation
       'metrics': {...}                 # Dashboard metrics
   }
   ```
3. **Template Rendering** → Components → Final HTML

---

## 🤖 Assistants Page

### **Location**: `dashboard/templates/dashboard/Assistants.html`

### **Purpose**
The Assistants page provides a comprehensive interface for managing AI assistants, including configuration sections, metrics, and real-time controls.

### **Architecture Overview**

#### **1. Fixed Header Bar**
- **Position**: Fixed at top, spans full width minus sidebar
- **Background**: Dark theme with DaisyUI `bg-neutral`
- **Components**:
  - Assistant name + status badge
  - Segmented control buttons (Code/Test/Chat/Call)
  - "Talk to Assistant" primary button

#### **2. Metric Tiles Strip**
- **Layout**: 4 compact tiles below header
- **Metrics**: Cost/min, Avg Latency, Call Success, ASR WER
- **Interaction**: Click handlers for future drawer functionality

#### **3. Scrollable Content Area**
- **Offset**: 140px top padding to clear fixed header
- **Sections**: 7 main configuration sections
- **Navigation**: Smooth scrolling with tab highlighting

### **Configuration Sections**

#### **Main Sections** (with dividers and subsections):

1. **MODEL** 🧠
   - **Model**: Model selection and parameters
   - Contains: Provider dropdowns, temperature slider, max tokens, etc.

2. **VOICE** 🎙️
   - **Voice & Persona**: Voice configuration
   - **Voice Parameters**: Additional voice settings

3. **TRANSCRIBER** 📝
   - **Speech-to-Text**: Transcription settings
   - Contains: Provider selection, language settings, custom vocabulary

4. **TOOLS** 🔧
   - **Connected Tools**: External integrations

5. **ANALYSIS** 📊
   - **Analytics & Insights**: Analysis configuration

6. **ADVANCED** ⚙️
   - **Advanced Settings**: Low-level configuration

7. **WIDGET** 🎨
   - **UI Components**: Widget customization

### **Interactive Features**

#### **1. Collapsible Sections**
- **File**: `static/js/modules/collapsible.js`
- **Features**:
  - Smooth expand/collapse animations
  - ARIA accessibility attributes
  - Dynamic height calculation
  - Rotating chevron indicators

#### **2. Navigation System**
- **File**: `static/js/modules/navigation.js`
- **Features**:
  - Smooth scrolling to sections
  - Active tab highlighting
  - Scroll offset compensation
  - Hash-based deep linking

#### **3. Custom Tooltips**
- **Implementation**: Pure CSS with Tailwind
- **Features**:
  - Hover-triggered display
  - Animated entrance/exit
  - Custom arrow styling
  - Context-aware positioning

### **File Structure**
```
Assistants Page Files:
├── dashboard/templates/dashboard/Assistants.html  # Main template (1457 lines)
├── dashboard/views.py                             # Backend logic
├── static/js/
│   ├── assistants.js                             # Main page controller
│   └── modules/
│       ├── collapsible.js                       # Accordion functionality
│       ├── navigation.js                        # Scroll & tab navigation
│       └── performance.js                       # Performance optimizations
├── static/css/components.css                     # Utility classes
└── templates/components/                         # Shared components
```

---

## 🚀 Performance Optimizations

### **1. SVG Icon Sprite System**

#### **Implementation**
- **Sprite File**: `static/icons/sprite.svg` (213 lines)
- **Component**: `templates/components/icon_sprite.html`
- **Usage**: `{% include 'components/icon_sprite.html' with name="phone" size="sm" %}`

#### **Benefits**
- **Before**: 333 inline SVG elements
- **After**: 1 sprite file + references
- **DOM Reduction**: ~70%
- **Caching**: Single file vs multiple elements

#### **Available Icons**
```
Navigation: home, users, phone, campaigns, analytics, tickets, reports
Actions: search, plus, settings, chevron-down, chevron-right, help-circle
AI/Model: brain, mic, headphones, waveform
Tools: wrench, zap, external-link
Status: check-circle, x-circle, alert-circle
Metrics: dollar-sign, clock, activity, trending-up
Organization: building, credit-card, globe, server
```

### **2. CSS Architecture**

#### **File**: `static/css/components.css` (345 lines)

#### **Key Features**
- **CSS Custom Properties**: Consistent spacing, colors, shadows
- **Critical CSS**: Prevents FOUC for above-the-fold content
- **Hardware Acceleration**: `transform: translateZ(0)` for animations
- **Scroll Optimization**: Touch scrolling for mobile

#### **Important Classes**
```css
/* Layout */
.header-fixed              /* Fixed header positioning */
.content-with-fixed-header /* Content offset */

/* Performance */
.smooth-transform          /* Hardware acceleration */
.lazy                      /* Lazy loading placeholder */
.skeleton-loader          /* Loading animation */

/* Components */
.btn-enhanced             /* Button standardization */
.metric-grid-4           /* Responsive metric layout */
.breadcrumb-enhanced     /* Navigation styling */
```

### **3. JavaScript Modules**

#### **Main Controller**: `static/js/assistants.js`
- ES6 class-based architecture
- Module coordination
- Performance optimization integration

#### **Core Modules**:

**`collapsible.js`**:
```javascript
class CollapsibleManager {
    // Handles accordion animations
    // ARIA accessibility
    // Dynamic height calculation
}
```

**`navigation.js`**:
```javascript
class NavigationManager {
    // Smooth scrolling
    // Active tab highlighting
    // Hash navigation
}
```

**`performance.js`**:
```javascript
// SVG sprite preloading
// Lazy loading utilities
// Debounce/throttle helpers
// Resource optimization
```

### **4. Resource Preloading**

#### **File**: `templates/base.html`
```html
<!-- Performance Optimizations -->
<link rel="preload" href="{% static 'icons/sprite.svg' %}" as="image" type="image/svg+xml">
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

---

## 🛠️ Development Guide

### **Adding New Features**

#### **1. New Configuration Section**
```html
<!-- In Assistants.html -->
<div class="divider-with-icon">
  <svg class="w-4 h-4 text-primary">...</svg>
  <span>NEW SECTION</span>
</div>

<section class="space-y-6" id="new-section">
  <!-- Section content -->
</section>
```

#### **2. New Metric Card**
```python
# In dashboard/views.py
context['metrics']['new_metric'] = {
    'title': 'New Metric',
    'value': '123',
    'icon': 'new-icon',
    'color': 'text-primary'
}
```

```html
<!-- In Overview.html -->
{% include 'components/metric_card.html' with title=metrics.new_metric.title value=metrics.new_metric.value icon=metrics.new_metric.icon color=metrics.new_metric.color %}
```

#### **3. New Icon**
```xml
<!-- In static/icons/sprite.svg -->
<symbol id="icon-new-icon" viewBox="0 0 24 24">
  <path d="...icon path data..."/>
</symbol>
```

### **File Editing Locations**

#### **Page Templates**
- **Overview**: `dashboard/templates/dashboard/Overview.html`
- **Assistants**: `dashboard/templates/dashboard/Assistants.html`

#### **Backend Logic**
- **Views**: `dashboard/views.py`
- **URLs**: `dashboard/urls.py`

#### **Components**
- **Shared**: `templates/components/`
- **Icons**: `static/icons/sprite.svg`
- **Styles**: `static/css/components.css`

#### **JavaScript**
- **Main**: `static/js/assistants.js`
- **Modules**: `static/js/modules/`

#### **Configuration**
- **Base Template**: `templates/base.html`
- **Settings**: `backend/settings.py`

### **Testing Changes**

#### **1. Local Development**
```bash
# Start Django server
python manage.py runserver

# Access pages
http://localhost:8000/              # Overview
http://localhost:8000/assistants/   # Assistants
```

#### **2. Performance Testing**
```bash
# Run CSS build script
node scripts/build-css.js

# Check network performance in browser DevTools
# Monitor with Django Debug Toolbar
```

### **Common Customizations**

#### **1. Color Scheme**
```css
/* In static/css/components.css */
:root {
  --primary-color: #cyan-500;
  --secondary-color: #slate-600;
  /* Update color variables */
}
```

#### **2. Layout Adjustments**
```css
/* Sidebar width */
--sidebar-width: 320px;

/* Header height */
--header-height: 140px;

/* Spacing scale */
--space-lg: 1.5rem;
```

#### **3. New Animations**
```css
/* Add to components.css */
.custom-animation {
  transition: all 0.3s ease;
  will-change: transform;
}
```

---

## 📋 Maintenance Checklist

### **Regular Tasks**
- [ ] Update icon sprite when adding new icons
- [ ] Run CSS minification for production builds
- [ ] Test responsive design on multiple screen sizes
- [ ] Validate ARIA accessibility attributes
- [ ] Monitor JavaScript console for errors

### **Performance Monitoring**
- [ ] Check First Contentful Paint times
- [ ] Monitor bundle sizes
- [ ] Validate lazy loading functionality
- [ ] Test scroll performance on mobile devices

### **Code Quality**
- [ ] Lint JavaScript with ESLint
- [ ] Validate HTML with W3C validator
- [ ] Check CSS with Stylelint
- [ ] Test cross-browser compatibility

---

## 🔍 Troubleshooting

### **Common Issues**

#### **Icons Not Displaying**
1. Check sprite file exists: `static/icons/sprite.svg`
2. Verify icon name in sprite
3. Check `STATIC_URL` configuration
4. Browser console for 404 errors

#### **Animations Not Working**
1. Check CSS custom properties support
2. Verify JavaScript module loading
3. Check browser console for errors
4. Test with hardware acceleration disabled

#### **Layout Issues**
1. Check sidebar width calculations
2. Verify header offset values
3. Test responsive breakpoints
4. Check CSS grid/flexbox support

#### **Performance Problems**
1. Check resource preloading
2. Monitor network requests
3. Validate lazy loading implementation
4. Test with slow network simulation

### **Debug Commands**
```bash
# Check Django static files
python manage.py collectstatic

# Validate templates
python manage.py check

# Test JavaScript modules
# Open browser console and check for import errors
```

---

## 📚 Additional Resources

- **DaisyUI Documentation**: https://daisyui.com/
- **Tailwind CSS Guide**: https://tailwindcss.com/docs
- **Django Templates**: https://docs.djangoproject.com/en/stable/topics/templates/
- **ES6 Modules**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
- **Web Performance**: https://web.dev/performance/

---

*Last Updated: [Current Date]*
*Version: Watchtower v2*
*Maintainers: Development Team*
