import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the accent div
text = re.sub(r'\s*<div class="dir-card-accent"[^>]*></div>', '', text)

# Replace dir-card-icon style to be a uniform grey square
text = re.sub(r'<div class="dir-card-icon" :style="ackground: \$\{\(template\.theme_color \|\| \'#6366f1\'\) \+ \'18\'\}">', '<div class="dir-card-icon" style="background: #f1f5f9; border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">', text)
text = re.sub(r'<div class="dir-card-icon" :style="ackground: \$\{\(form\.theme_color \|\| \'#6366f1\'\) \+ \'18\'\}">', '<div class="dir-card-icon" style="background: #f1f5f9; border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">', text)

# Fix SVG stroke color inside the icon to be grey
text = re.sub(r'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="template\.theme_color \|\| \'#6366f1\'"', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8"', text)
text = re.sub(r'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="form\.theme_color \|\| \'#6366f1\'"', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8"', text)

# Restructure the meta pill to be inside the dir-card-text for FORMS
# Original:
#                 </div>
#               </div>
#
#               <!-- Meta row -->
#               <div class="dir-card-meta">
#                 <span class="date-pill-badge">
#                   <svg ...>
#                   {{ formatDate(form.created_at) }}
#                 </span>
#               </div>
#
# Replacement:
#                   <div style="margin-top: 8px;">
#                     <span class="date-pill-badge">
#                       <svg ...>
#                       {{ formatDate(form.created_at) }}
#                     </span>
#                   </div>
#                 </div>
#               </div>

forms_meta_pattern = r'(\s*</div>\s*</div>)\s*<!-- Meta row -->\s*<div class="dir-card-meta">\s*(<span class="date-pill-badge">.*?</span>)\s*</div>'
text = re.sub(forms_meta_pattern, r'\n                  <div style="margin-top: 10px;">\n                    \2\n                  </div>\1', text, flags=re.DOTALL)

# Do the same for templates (if they have a meta row... wait, templates didn't have a meta row!)

# Now fix the global header positioning. Image 2 shows "WORKSPACE / DIRECTORY" small text above "Form Directory".
# Let's add that to the view-header.
header_pattern = r'(<h2 class="view-title">Form Directory</h2>)'
header_replacement = r'<div style="font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.05em; margin-bottom: 8px; text-transform: uppercase;">WORKSPACE <span style="margin: 0 4px; font-weight: 400;">/</span> <span style="color: #1e293b;">DIRECTORY</span></div>\n            \1'
text = re.sub(header_pattern, header_replacement, text)

# Image 2 also shows the search bar next to the view-header text, but vertically aligned better.
# Also the view-sub text is: "Organize and manage your high-performance and apply your intelligent forms in a unified workspace."
sub_pattern = r'<p class="view-sub">Browse, manage, and share your AI-generated forms with ease.</p>'
sub_replacement = r'<p class="view-sub" style="max-width: 450px; line-height: 1.5; color: #475569; margin-top: 8px;">Organize and manage your high-performance and apply your intelligent forms in a unified workspace.</p>'
text = re.sub(sub_pattern, sub_replacement, text)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Card structure refactored successfully.')
