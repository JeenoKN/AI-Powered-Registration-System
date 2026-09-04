with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the old section to replace
old_start = '         </div>\n         <div v-else class="forms-grid-directory">\n           <div v-for="form in filteredDirectoryForms" :key="form.id" class="directory-card animate-fade">'
old_end = '         </div>\n       </div>\n       \n       <div class="dashboard-view-container" v-show="currentTab === \'dashboard\'">'

new_section = '''         <!-- Bento Glass Grid -->
         <div v-else style="position: relative; z-index: 1; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; padding: 8px 32px 32px;">
           <div
             v-for="(form, idx) in filteredDirectoryForms"
             :key="form.id"
             class="dir-glass-card"
             :class="{ 'dir-card-wide': idx === 0 }"
           >
             <!-- Decorative corner blob -->
             <div class="dir-blob-tr" :style="ackground: linear-gradient(to bottom-left, 44, transparent)"></div>
             <div class="dir-blob-bl"></div>

             <!-- Top Row: Badge + Duplicate button -->
             <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 2;">
               <span class="dir-badge" :style="ackground: 18; color: ; border: 1px solid 30;">
                 <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :stroke="form.theme_color || '#6366f1'" stroke-width="2.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                 {{ form.input_type_used || 'Text Prompt' }}
               </span>
               <button class="dir-more-btn" @click.stop="duplicateForm(form)" title="Duplicate form">
                 <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
               </button>
             </div>

             <!-- Title + Description -->
             <div style="position: relative; z-index: 2; margin-top: 14px; flex: 1;">
               <h3 class="dir-card-title-new">{{ form.title }}</h3>
               <p style="font-size: 13px; color: #6b7280; margin: 6px 0 0; line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{{ form.description || 'No description provided.' }}</p>
             </div>

             <div style="flex-grow: 1; min-height: 20px;"></div>

             <!-- Footer: Edit button + date + delete -->
             <div style="position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: center; padding-top: 18px; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.45);">
               <button class="dir-btn-edit" @click="openViewModal(form)" :style="color: ; border: 1px solid 30;">
                 <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                 View Details
               </button>
               <div style="display: flex; align-items: center; gap: 8px;">
                 <span style="font-size: 11px; color: #9ca3af; display: flex; align-items: center; gap: 3px; white-space: nowrap;">
                   <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                   {{ formatDate(form.created_at) }}
                 </span>
                 <button class="dir-btn-del-new" @click.stop="deleteSavedForm(form.id)" title="Delete form">
                   <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                 </button>
               </div>
             </div>
           </div>
         </div>
       </div>
       
       <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">'''

# Use line-based approach
lines = text.split('\n')
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'v-else class="forms-grid-directory"' in line:
        start_line = i - 1  # include the closing </div> before
        break

if start_line is not None:
    for j in range(start_line, len(lines)):
        if 'dashboard-view-container' in lines[j] and 'v-show' in lines[j]:
            end_line = j
            break
    
    if end_line is not None:
        print(f"Found section: lines {start_line+1} to {end_line+1}")
        print("Before:", lines[start_line].strip())
        print("After:", lines[end_line].strip())
        
        new_lines_section = new_section.split('\n')
        lines = lines[:start_line] + new_lines_section + lines[end_line+1:]
        
        text = '\n'.join(lines)
        with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Done! Replaced directory grid section.")
    else:
        print("Could not find end line")
else:
    print("Could not find start line")
