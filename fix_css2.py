with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Remove the broken part starting from the end of btn-premium-coral:disabled
# Look for:
# .btn-premium-coral:disabled {
#   opacity: 0.6;
#   cursor: not-allowed;
# }
# and everything after it until the end of the file

match = re.search(r'\.btn-premium-coral:disabled\s*\{\s*opacity:\s*0\.6;\s*cursor:\s*not-allowed;\s*\}', text)
if match:
    index = match.end()
    base_css = text[:index]
    
    # Now append the corrected block
    corrected_block = """

/* ==============================================================
   WARM MINIMALIST EDITORIAL - Design Tokens
   ============================================================== */
:root {
  --theme-dark-sidebar: linear-gradient(180deg, #2b2b2d 0%, #3f3f42 100%);
  --theme-dark-active: rgba(255, 255, 255, 0.12);
  --theme-canvas-bg: linear-gradient(180deg, #e4e4e7 0%, #ffffff 100%);
  --theme-card-bg: #FFFFFF;
  --theme-text-dark: #1A1A1A;
  --theme-text-muted: #6E6E6C;
  --theme-text-on-dark: #FFFFFF;
  --theme-text-on-dark-muted: rgba(255,255,255,0.60);
  --theme-border: rgba(26,26,26,0.10);
  --theme-shadow-soft: 0 2px 8px rgba(26,26,26,0.06), 0 8px 24px rgba(26,26,26,0.04);
  --theme-shadow-card: 0 1px 3px rgba(26,26,26,0.05), 0 6px 20px rgba(26,26,26,0.06);
  --theme-input-focus-shadow: 0 0 0 3px rgba(255,223,150,0.35);
  --theme-input-focus-border: rgba(255,200,80,0.60);
}

/* ---- Sidebar: Warm Dark Charcoal ---- */
.sidebar-nav {
  background: var(--theme-dark-sidebar) !important;
  color: var(--theme-text-on-dark) !important;
  border-right: 1px solid rgba(255,255,255,0.06) !important;
}
.sidebar-nav .brand-sub,
.sidebar-nav .menu-label {
  color: var(--theme-text-on-dark-muted) !important;
}
.sidebar-nav .nav-item {
  color: rgba(255,255,255,0.72) !important;
  border-radius: 999px;
  padding: 10px 16px;
  transition: background 0.2s, color 0.2s;
}
.sidebar-nav .nav-item:hover {
  background: rgba(255,255,255,0.08) !important;
  color: #ffffff !important;
}
.sidebar-nav .nav-item.active {
  background: var(--theme-dark-active) !important;
  color: #ffffff !important;
  font-weight: 600;
}

/* ---- Main Canvas: Warm Off-White ---- */
.workspace-container {
  background: var(--theme-canvas-bg) !important;
}
.directory-view-container,
.templates-view-container {
  background: transparent !important;
}

/* ---- Cards: Clean White + Soft Diffused Shadow ---- */
.directory-card {
  background: var(--theme-card-bg) !important;
  border-radius: 16px !important;
  box-shadow: var(--theme-shadow-card) !important;
  border: 1px solid var(--theme-border) !important;
}
.directory-card:hover {
  box-shadow: 0 4px 12px rgba(26,26,26,0.08), 0 16px 40px rgba(26,26,26,0.08) !important;
  transform: translateY(-3px) !important;
}
.field-item-box {
  background: var(--theme-card-bg) !important;
  border-radius: 16px !important;
  box-shadow: var(--theme-shadow-soft) !important;
  border: 1px solid var(--theme-border) !important;
}
.form-section {
  background: var(--theme-card-bg) !important;
  border-radius: 16px !important;
  box-shadow: var(--theme-shadow-soft) !important;
  border: 1px solid var(--theme-border) !important;
}

/* ---- Input Fields: Rounded + Warm Golden Focus Glow ---- */
input[type="text"],
input[type="email"],
input[type="number"],
input[type="date"],
input[type="tel"],
input[type="password"],
input[type="url"],
select,
textarea {
  border-radius: 10px !important;
  border: 1.5px solid rgba(26,26,26,0.14) !important;
  background: #FAFAF8 !important;
  color: var(--theme-text-dark) !important;
  transition: border-color 0.18s, box-shadow 0.18s !important;
}
input[type="text"]:focus,
input[type="email"]:focus,
input[type="number"]:focus,
input[type="date"]:focus,
input[type="tel"]:focus,
input[type="password"]:focus,
input[type="url"]:focus,
select:focus,
textarea:focus {
  outline: none !important;
  border-color: var(--theme-input-focus-border) !important;
  box-shadow: var(--theme-input-focus-shadow) !important;
  background: #FFFCF5 !important;
}

/* ---- Global Header: Warm Translucent Glass ---- */
.global-header {
  background: rgba(245,244,240,0.85) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border-bottom: 1px solid rgba(26,26,26,0.08) !important;
}
"""
    
    with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
        f.write(base_css + corrected_block)
    print("Fixed!")
else:
    print("Could not find anchor point.")
