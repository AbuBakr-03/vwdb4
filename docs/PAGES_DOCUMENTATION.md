# Watchtower v2 - Pages Documentation

## Overview

This document provides comprehensive documentation for the pages in Watchtower v2, including layout standards, features, optimizations, and file locations for easy maintenance and future development.

---

## 🎨 Layout Standards

### **Page Structure Standard**

All dashboard pages should follow this standardized layout pattern to ensure consistency, proper spacing, and optimal user experience:

#### 1. **Main Container Structure**
```html
{% block content %}
<div class="min-h-screen bg-base-100">
  <main class="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-10 space-y-10 pb-24">
    <!-- Page content sections here -->
  </main>
</div>
{% endblock %}
```

**Key Elements:**
- **Container**: `max-w-[1400px] mx-auto` - Centered with max width on large screens
- **Responsive Padding**: `px-4 sm:px-6 lg:px-8` - Consistent edge spacing
- **Vertical Spacing**: `py-6 lg:py-10` - Top/bottom padding that scales
- **Section Spacing**: `space-y-10` - Consistent vertical rhythm between sections
- **Bottom Padding**: `pb-24` - Extra space to prevent sticky footer overlap

#### 2. **Top Bar Pattern**
```html
<!-- Top Bar -->
<div class="grid grid-cols-1 md:grid-cols-2 items-start gap-4">
  <div>
    <h1 class="text-3xl font-bold text-base-content">Page Title</h1>
    <p class="text-base-content/70 mt-1">Page description</p>
  </div>
  <div class="md:justify-self-end flex flex-wrap gap-2">
    <!-- Action buttons -->
    <button class="btn btn-outline btn-sm h-9 min-h-9 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary">
      Action
    </button>
  </div>
</div>
```

**Features:**
- **Responsive Grid**: Title/description left, actions right
- **Consistent Button Height**: `h-9 min-h-9` for all action buttons
- **Accessible Focus**: `focus-visible:outline` for keyboard navigation
- **Flexible Actions**: Wraps properly on smaller screens

#### 3. **Filter Card Pattern**
```html
<!-- Filters Card -->
<div class="card bg-base-200/40 border border-base-content/10">
  <div class="card-body p-5 sm:p-6 lg:p-7 space-y-5">
    <!-- Search input -->
    <div class="relative">
      <input class="input input-bordered w-full pl-10 h-11 bg-base-100 border-base-content/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary" />
      <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-base-content/50">...</svg>
    </div>
    
    <!-- Filter controls -->
    <div class="flex flex-wrap items-center gap-3 sm:gap-4">
      <!-- Dropdowns, selects, buttons -->
    </div>
    
    <!-- Applied filters -->
    <div class="flex flex-wrap gap-2 pt-1">
      <!-- Filter chips -->
    </div>
  </div>
</div>
```

**Features:**
- **Generous Padding**: `p-5 sm:p-6 lg:p-7` scales with screen size
- **Consistent Height**: `h-11` for search inputs
- **Proper Spacing**: `space-y-5` for internal sections
- **Enhanced Dropdowns**: `shadow-xl border z-20` for better visibility

#### 4. **Card Grid Patterns**

**Featured/Recommended Grid:**
```html
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 lg:gap-7">
  <div class="card h-full bg-base-200/50 border border-base-content/10 hover:shadow-lg transition group">
    <!-- Card content -->
  </div>
</div>
```

**Compact Grid (All Items):**
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 lg:gap-5">
  <div class="card h-full bg-base-200/30 border border-base-content/10 hover:shadow-md transition group">
    <!-- Card content -->
  </div>
</div>
```

#### 5. **Card Structure Standard**
```html
<div class="card h-full bg-base-200/50 border border-base-content/10 hover:shadow-lg transition group">
  <figure class="relative aspect-square overflow-hidden rounded-t-2xl">
    <img class="w-full h-full object-cover" src="..." alt="..." />
    <!-- Overlay content -->
    <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
      <!-- Overlay buttons -->
    </div>
    <!-- Badges -->
    <div class="absolute top-2 left-2">
      <span class="badge badge-primary badge-sm">Badge</span>
    </div>
  </figure>
  <div class="card-body p-4 flex flex-col">
    <h3 class="card-title text-lg leading-tight">Title</h3>
    <p class="text-sm text-base-content/60">Description</p>
    
    <!-- Tags -->
    <div class="flex flex-wrap gap-1 mt-2">
      <span class="badge badge-outline badge-xs">Tag</span>
    </div>

    <!-- Footer - always at bottom -->
    <div class="mt-auto pt-3 flex justify-between items-center text-xs">
      <div class="font-mono text-sm">$0.03/min</div>
      <div class="text-base-content/60">~400ms</div>
    </div>
  </div>
</div>
```

**Key Features:**
- **Equal Height**: `h-full` ensures column alignment
- **Flexible Layout**: `flex flex-col` with `mt-auto` pushes footer down
- **Aspect Ratio**: `aspect-square` for consistent image sizing
- **Object Cover**: Prevents image distortion
- **Proper Contrast**: `text-base-content/60` for readable secondary text

#### 6. **Button Standards**

**Action Buttons (Top Bar):**
```html
<button class="btn btn-outline btn-sm h-9 min-h-9 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary">
  <svg class="w-4 h-4">...</svg>
  Action
</button>
```

**Card Action Buttons:**
```html
<button class="btn btn-ghost btn-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary" title="Action">
  <svg class="w-3 h-3">...</svg>
</button>
```

#### 7. **Typography & Spacing**

**Section Headers:**
```html
<h2 class="text-2xl font-semibold text-base-content mb-6">Section Title</h2>
```

**Meta Information:**
```html
<div class="text-sm text-base-content/60">8 items</div>
```

**Content Text:**
- Primary: `text-base-content`
- Secondary: `text-base-content/60` 
- Tertiary: `text-base-content/50` (use sparingly)

#### 8. **Accessibility Standards**

**Focus Indicators:**
- All interactive elements: `focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary`
- Keyboard navigation support
- Proper ARIA labels for icons

**Image Standards:**
- Always include `alt` attributes
- Use `object-cover` for consistent sizing
- `rounded-2xl` for consistent corner radius

#### 9. **Implementation Checklist**

When creating new pages, ensure:

- [ ] Main container uses standardized padding and spacing
- [ ] Top bar follows grid pattern with proper button heights
- [ ] Filter cards use generous padding and consistent input heights
- [ ] All cards have `h-full` for equal heights
- [ ] Card bodies use `flex flex-col` with `mt-auto` for footers
- [ ] Images use `aspect-square object-cover`
- [ ] All buttons include focus-visible styles
- [ ] Text contrast follows the `/60` pattern for secondary content
- [ ] Grids use appropriate gap sizes (`gap-6 lg:gap-7` for featured, `gap-4 lg:gap-5` for compact)
- [ ] Bottom padding includes space for sticky elements (`pb-24`)

This standard ensures all pages have consistent spacing, proper accessibility, and optimal user experience across all screen sizes.

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

## 🎊 Toast Notification System

### **Standardized Toast Notifications**

All pages now use a centralized, standardized toast notification system located in `base.html` for consistent user feedback across the application.

#### **Features:**
- **Global availability**: Available on all pages automatically
- **Consistent positioning**: Bottom-right corner (toast-bottom toast-end)
- **Multiple types**: Success, Error, Warning, Info
- **Smooth animations**: Slide-in from right with fade effects
- **Auto-dismiss**: Configurable duration with manual close option
- **Anti-stacking**: Only one toast visible at a time
- **Accessibility**: Proper ARIA labels and keyboard support

#### **Usage:**
```javascript
// Basic usage
showToast(message, type, duration);

// Convenience functions
showSuccessToast('Operation completed successfully!');
showErrorToast('Something went wrong!');
showWarningToast('Please check your input.');
showInfoToast('Information message here.');

// With custom duration
showSuccessToast('Custom message', 5000); // 5 seconds
```

#### **Toast Types and Styling:**
```javascript
// Success Toast (Green)
showSuccessToast('Voice added to project successfully!');

// Error Toast (Red) 
showErrorToast('Failed to copy voice ID to clipboard');

// Warning Toast (Yellow)
showWarningToast('Please select at least one item');

// Info Toast (Blue)
showInfoToast('Loading voice details...');
```

#### **Implementation in Templates:**

**For Django Messages Integration:**
```html
<!-- Django Messages Integration with Standardized Toast -->
{% if messages %}
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      {% for message in messages %}
        {% if message.tags == 'success' %}
          showSuccessToast('{{ message|escapejs }}');
        {% elif message.tags == 'error' %}
          showErrorToast('{{ message|escapejs }}');
        {% elif message.tags == 'warning' %}
          showWarningToast('{{ message|escapejs }}');
        {% else %}
          showInfoToast('{{ message|escapejs }}');
        {% endif %}
      {% endfor %}
    });
  </script>
{% endif %}
```

**For JavaScript Actions:**
```javascript
// Copy to clipboard with feedback
function copyVoiceId(voiceId) {
  navigator.clipboard.writeText(voiceId).then(() => {
    showSuccessToast(`Voice ID "${voiceId}" copied to clipboard!`);
  }).catch(() => {
    showErrorToast('Failed to copy voice ID to clipboard');
  });
}

// Form submission feedback
function saveSettings() {
  // ... save logic
  showSuccessToast('Settings saved successfully!');
}
```

#### **Toast Structure:**
```html
<div class="toast toast-bottom toast-end z-50 global-toast">
  <div class="alert alert-success shadow-lg border border-base-content/20 backdrop-blur">
    <div class="flex items-center gap-3">
      <svg class="w-5 h-5 flex-shrink-0">[Icon SVG]</svg>
      <span class="text-sm font-medium">Message text</span>
      <button class="btn btn-ghost btn-xs btn-circle ml-auto" onclick="this.closest('.global-toast').remove()">
        [Close icon]
      </button>
    </div>
  </div>
</div>
```

#### **Animation Classes:**
- **Entrance**: `slideInRight` - Slides in from right edge
- **Exit**: `slideOutRight` - Slides out to right edge
- **Duration**: 300ms for smooth transitions

#### **Configuration:**
```javascript
// Default durations
Success: 3000ms (3 seconds)
Error: 4000ms (4 seconds) 
Warning: 3500ms (3.5 seconds)
Info: 3000ms (3 seconds)
```

#### **Files Updated:**
- **`templates/base.html`**: Global toast system and animations
- **`dashboard/templates/dashboard/VoiceLibrary.html`**: Updated copyVoiceId function
- **`tools/templates/tools/tools_list.html`**: Django messages integration
- **Voice Details Drawer**: addVoiceToProject and duplicateVoice functions

---

## 🎪 Voice Details Drawer System

### **Global Responsive Voice Details Modal**

A comprehensive, responsive voice details drawer that's globally available across all pages for displaying detailed voice information.

#### **Features:**
- **Global availability**: Accessible from any page via `base.html`
- **Fully responsive**: Adapts to all screen sizes (mobile to desktop)
- **Interactive tabs**: Overview, Pricing, Latency, Samples
- **Smooth animations**: Slide-in from right with backdrop
- **Keyboard support**: ESC to close, full tab navigation
- **Touch-friendly**: Optimized for mobile interactions

#### **Screen Size Breakpoints:**
```css
Mobile (< 640px): max-w-md (384px)
Small (640px+): max-w-lg (512px)  
Medium (768px+): max-w-xl (576px)
Large (1024px+): max-w-2xl (672px)
Extra Large (1280px+): max-w-3xl (768px)
```

#### **Usage:**
```javascript
// Open voice details for specific voice
openVoiceDetails('voice-id-here');

// Functions automatically available globally
switchVoiceTab('pricing'); // Switch to pricing tab
addVoiceToProject(); // Add current voice to project
duplicateVoice(); // Duplicate current voice
```

#### **Responsive Design Features:**
- **Adaptive sizing**: Elements scale based on screen size
- **Flexible layout**: Stacked on mobile, side-by-side on desktop
- **Touch optimization**: Larger tap targets on mobile
- **Scrollable content**: Proper overflow handling
- **Readable text**: Font sizes adjust for readability

#### **Files:**
- **`templates/base.html`**: Global drawer HTML and JavaScript
- **`dashboard/templates/dashboard/VoiceLibrary.html`**: Content generation functions

---

## 🔐 API Keys Management System

### **Comprehensive API Keys Configuration Page**

A fully-featured API keys management page for securely storing and managing external service API credentials.

#### **Features:**
- **Secure form handling**: Password fields with show/hide toggles
- **Organized sections**: Grouped by service provider (Azure OpenAI, ElevenLabs)
- **Input validation**: URL validation and required field enforcement
- **Visual feedback**: Connection status indicators with color coding
- **Responsive design**: Mobile-optimized layout with proper spacing
- **Security notice**: Clear warnings about API key security

#### **Supported Services:**

**Azure OpenAI Realtime Model:**
- Endpoint URL configuration
- API key management
- Service-specific validation

**Azure GPT5 Mini:**
- Dedicated endpoint configuration
- Separate API key handling
- Model-specific settings

**ElevenLabs:**
- Voice synthesis API key
- Service integration ready
- Future expansion placeholder

#### **Form Structure:**
```html
<!-- Service Section Layout -->
<div class="space-y-6">
  <div class="flex items-center gap-3 pb-3 border-b">
    <div class="w-8 h-8 rounded-lg bg-[color]/10">
      <svg class="w-4 h-4 text-[color]">[Service Icon]</svg>
    </div>
    <div>
      <h3 class="text-lg font-semibold">Service Name</h3>
      <p class="text-sm text-base-content/60">Service description</p>
    </div>
  </div>
  
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Input fields with validation -->
  </div>
</div>
```

#### **Security Features:**
- **Password field masking**: All API keys hidden by default
- **Toggle visibility**: Show/hide buttons for verification
- **Form validation**: Client-side and server-side validation
- **CSRF protection**: Django CSRF tokens for security
- **Encrypted storage**: Ready for encrypted database storage

#### **JavaScript Functionality:**
```javascript
// Password visibility toggle
togglePasswordVisibility(fieldId)

// Form reset with original values
resetForm()

// Input validation (URL format checking)
// Form submission with loading states
// Auto-hide success messages
```

#### **Status Monitoring:**
- **Connection cards**: Visual status indicators for each service
- **Color-coded states**: Success (green), Warning (yellow), Error (red)
- **Real-time feedback**: Status updates based on API connectivity

#### **Layout Standards Applied:**
- **Consistent spacing**: Follows established `space-y-*` patterns
- **Responsive design**: Works on all screen sizes
- **Typography hierarchy**: Clear headings and descriptions
- **Button consistency**: Matches established button styles
- **Form patterns**: Consistent with other dashboard forms

#### **Files Created/Updated:**
- **`dashboard/templates/dashboard/api_keys.html`**: Main template
- **`dashboard/views.py`**: Added `api_keys` and `save_api_keys` views
- **`dashboard/urls.py`**: Added API keys URL patterns
- **`utils/navigation.py`**: Added API Keys to sidebar navigation
- **Documentation**: Updated with comprehensive API keys section

#### **URL Structure:**
```
/api-keys/          → View API keys page
/api-keys/save/     → Save API keys (POST)
```

#### **Navigation Integration:**
- **Sidebar placement**: Added as dedicated navigation item
- **Active state detection**: Proper highlighting in navigation
- **Icon design**: Key icon for clear visual identification
- **Mobile responsive**: Works in collapsed sidebar mode

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
