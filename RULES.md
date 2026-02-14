# Project Rules

## odoo19_src/ — READ ONLY
- `odoo19_src/` contains the **Odoo 19 Community Edition source code** (branch `19.0`)
- It is used **only as a reference** to understand Odoo 19 APIs, models, patterns, and conventions
- **DO NOT edit, modify, or delete** any files inside `odoo19_src/`
- When fixing compatibility issues, **read the source** to understand the correct patterns, then apply changes to our custom modules only

## Custom Modules
- All custom module code lives in module directories (e.g., `seriaflow_accounting/`)
- Changes should only be made to custom module files
- Always follow patterns found in `odoo19_src/` for Odoo 19 compatibility
