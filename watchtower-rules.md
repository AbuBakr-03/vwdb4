# Django Project Rules & Guidelines

## General Principles

- **Organize code into multiple apps** - Avoid monolithic structures
- **Use Class Based Views (CBVs)** - Prefer CBVs over Function Based Views
- **Consistent field naming** - Maintain consistency across models, forms, and APIs
- **Always add type hints** - Improve code readability and IDE support
- **Use snake_case** - For variables, functions, and methods
- **Avoid massive import blocks** - Keep imports organized and minimal
- **Avoid "God functions"** - No all-in-one mega functions
- **Add meaningful comments** - Explain WHAT, WHY, and HOW
- **Write and maintain documentation** - Architecture and API documentation

## Models

- **Always use database indexes** - On fields used in filters, sorting, or joins
- **Implement `__str__` methods** - On all models for better debugging
- **Use `select_related`** - When querying related objects to avoid N+1 queries
- **Keep logic simple** - Focus on structures, relationships, validation, and querysets

## Views

**Keep views.py limited to:**

- Authentication
- Form processing
- HTTP responses
- Template rendering

- **Use CBVs instead of FBVs** - Class Based Views over Function Based Views

## Services

**Handle all business logic, workflows, and integrations:**

- File processing
- Email sending
- External API calls
- Complex calculations

- **Keep views thin** - Delegate business logic to services

## Forms

- **Forms handle validation only** - Keep form logic focused on validation

## Caching

- **Use Redis caching** - For expensive and repeated queries

## Testing

**Write tests for:**

- Models
- Views
- Forms
- API endpoints
- Utils
- Authentication
- Services

**Testing approach:**

- Include Unit, Integration, and End-to-End (e2e) tests
- Prefer high coverage and clear test naming

## Anti-Patterns (Avoid These)

- ❌ Business logic inside views/models
- ❌ Raw SQL in views
- ❌ Direct external API calls in models
- ❌ Overuse of custom CSS (should rely on daisyUI/Tailwind)

---

# Styling Rules (daisyUI 5 + Tailwind 4)

## Setup & Configuration

- **Use daisyUI 5 with Tailwind CSS 4**
- **Installation:** `npm i -D daisyui@latest`
- **CSS Setup:** Add `@plugin "daisyui";` in CSS
- **No `tailwind.config.js`** - Deprecated in Tailwind v4
- **Allowed styling:** Only daisyUI classes + Tailwind utilities
- **Avoid custom CSS** - Unless absolutely necessary

## Design Guidelines

- **Use responsive design** - `sm:`, `lg:` prefixes for flex/grid layouts
- **Use semantic daisyUI colors** - primary, secondary, accent, base, success, warning, error, info
- **Avoid raw Tailwind colors** - No `text-gray-800`, `bg-red-500` - use daisyUI semantic colors
- **Color usage:**
  - Use `base-*` colors for general layout backgrounds
  - Use `primary` for important CTAs
- **Follow Refactoring UI best practices** - For design decisions
- **Minimal body styling** - Don't add `bg-base-100 text-base-content` to `<body>` unless necessary
- **Placeholder images:** https://picsum.photos/200/300
- **Keep fonts minimal** - Only add custom fonts if essential

## daisyUI Resources

- **Documentation:** http://daisyui.com
- **Install Guide:** https://daisyui.com/docs/install/
- **Upgrade Guide:** https://daisyui.com/docs/upgrade/
- **Config Documentation:** https://daisyui.com/docs/config/
- **Theme Generator:** https://daisyui.com/theme-generator/

## Components

**Use daisyUI components directly:**

- accordion, alert, avatar, badge, breadcrumbs, button, card, carousel
- chat, checkbox, collapse, divider, drawer, dropdown, form elements
- modal, navbar, pagination, progress, table, tabs, toast, toggle, etc.

**For unsupported UI patterns:**

- Build with Tailwind utilities
- Avoid writing raw CSS components when a daisyUI component exists

## Theming

**Basic theme setup:**

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
}
```

**Custom themes:**

- Generate with daisyUI theme generator
- Store in a dedicated CSS file
- Use `@plugin "daisyui"` with light + dark themes enabled by default
