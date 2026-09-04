with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

premium_css = """

/* ==============================================================
   IMAGE 853344.JPG - PREMIUM OVERHAUL TOKENS
   ============================================================== */
:root {
  /* Override the main canvas background to a subtle ambient multi-stop gradient */
  --theme-ambient-gradient: radial-gradient(circle at 100% 0%, rgba(220, 215, 255, 0.4) 0%, transparent 40%),
                            radial-gradient(circle at 0% 100%, rgba(245, 230, 255, 0.4) 0%, transparent 40%),
                            radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.5) 0%, transparent 100%),
                            #f2f3f7;
}

/* Redefine workspace container to the ambient gradient */
.workspace-container {
  background: var(--theme-ambient-gradient) !important;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

/* Floating Inner Card */
.workspace-inner-card {
  background: #ffffff;
  border-radius: 32px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0,0,0,0.02);
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Fix directory container inside the inner card */
.directory-view-container {
  padding: 40px 48px;
}

/* Pill Search Bar */
.dir-search-input {
  border-radius: 9999px !important;
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
  padding: 12px 20px 12px 44px !important;
  font-size: 14px;
}
.dir-search-input:focus {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05), 0 0 0 3px rgba(100, 116, 139, 0.1) !important;
  border-color: rgba(0, 0, 0, 0.15) !important;
}

/* Clean Cards */
.directory-card {
  background: #ffffff !important;
  border-radius: 16px !important;
  border: 1px solid rgba(0,0,0,0.04) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0,0,0,0.02) !important;
  padding: 0 !important; /* Remove any external padding */
}
.directory-card:hover {
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06), 0 4px 8px rgba(0,0,0,0.03) !important;
  transform: translateY(-2px) !important;
}

/* Date Pill Badge */
.date-pill-badge {
  background: #f4f4f5;
  color: #71717a;
  font-size: 12px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Premium Navy Action Button */
.btn-premium-navy {
  background: #1e293b;
  color: #ffffff;
  font-weight: 600;
  letter-spacing: -0.01em;
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(30, 41, 59, 0.15);
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1; /* allow it to grow in flex container */
}
.btn-premium-navy:hover {
  background: #0f172a;
  box-shadow: 0 6px 16px rgba(30, 41, 59, 0.25);
  transform: translateY(-1px);
}

/* Minimalist Icon Button (Trash) */
.btn-icon-minimal {
  background: #ffffff;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.btn-icon-minimal:hover {
  background: #f8fafc;
  color: #ef4444; /* Subtle red on hover for trash */
  border-color: #cbd5e1;
}
"""

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'a', encoding='utf-8') as f:
    f.write(premium_css)

print("Injected Premium CSS Tokens.")
