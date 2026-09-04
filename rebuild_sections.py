with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

templates_start = text.find('<div class="templates-view-container directory-view-container" v-show="currentTab === \'templates\'">')
dashboard_start = text.find('<div class="dashboard-view-container" v-show="currentTab === \'dashboard\'">')

# Replace the broken templates+directory block with:
# 1. Correct templates section (restored to original)
# 2. New glassmorphism directory section

correct_templates = '''<div class="templates-view-container directory-view-container" v-show="currentTab === 'templates'">
        <div class="view-header" style="display: flex; justify-content: space-between; align-items: flex-end;">
          <div>
            <h2 class="view-title">Templates Library</h2>
            <p class="view-sub">Reusable form templates for quick starts.</p>
          </div>
        </div>
        <div v-if="loadingTemplates" class="directory-empty-state">
           Loading templates...
        </div>
        <div v-else-if="savedTemplates.length === 0" class="directory-empty-state">
           No templates saved yet. Generate a form and click "Save as Template".
        </div>
        <div v-else class="forms-grid-directory">
          <div v-for="template in savedTemplates" :key="template.id" class="directory-card animate-fade">
            <div class="dir-card-accent" :style="ackground: "></div>
            <div class="dir-card-inner">
              <div class="dir-card-content">
                <div class="dir-card-icon" :style="ackground: ">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="template.theme_color || '#6366f1'" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
                <div class="dir-card-text">
                  <h3 class="dir-card-title">{{ template.title }}</h3>
                  <p class="dir-card-desc">{{ template.description || 'No description provided.' }}</p>
                </div>
              </div>
              <div class="dir-card-meta">
                <span class="dir-meta-pill">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  {{ formatDate(template.created_at) }}
                </span>
              </div>
              <div class="dir-card-actions">
                <button class="dir-btn-load" @click="useTemplate(template)">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  Use Template
                </button>
                <button class="dir-btn-delete" @click="deleteTemplate(template.id)" title="Delete template">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FORM DIRECTORY — Glassmorphism Reskin -->
      <div class="directory-view-container" v-show="currentTab === 'directory'" style="padding: 0; position: relative;">

        <!-- Animated Mesh Background -->
        <div style="position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; border-radius: 24px;">
          <div class="dir-mesh-orb dir-orb-1"></div>
          <div class="dir-mesh-orb dir-orb-2"></div>
          <div class="dir-mesh-orb dir-orb-3"></div>
        </div>

        <!-- Page Header -->
        <div style="position: relative; z-index: 1; padding: 32px 32px 0;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; margin-bottom: 8px;">
            <div>
              <h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; color: #0b1c30; margin: 0 0 6px;">Form Directory</h1>
              <p style="font-size: 15px; color: #6b7280; margin: 0;">Manage and organize all your AI-generated forms.</p>
            </div>
            <div style="display: flex; align-items: center; background: rgba(255,255,255,0.65); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border-radius: 999px; padding: 10px 20px; border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 2px 8px rgba(0,0,0,0.04); gap: 8px; min-width: 260px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" v-model="searchQuery" placeholder="Search forms..." style="background: transparent; border: none; outline: none; font-size: 14px; color: #0b1c30; width: 100%; font-family: inherit;" />
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px; margin-bottom: 28px;">
            <button style="padding: 8px 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 999px; border: none; font-size: 12px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 10px rgba(99,102,241,0.3); white-space: nowrap;">All</button>
            <span style="font-size: 12px; color: #9ca3af; font-weight: 500;">{{ filteredDirectoryForms.length }} forms</span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loadingDirectory" style="position: relative; z-index: 1; display: flex; align-items: center; justify-content: center; padding: 80px 32px; gap: 12px; color: #6b7280;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="animation: spin 1s linear infinite;"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
          Loading forms...
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredDirectoryForms.length === 0" style="position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 32px; gap: 16px; text-align: center;">
          <div style="width: 64px; height: 64px; background: rgba(99,102,241,0.08); border-radius: 20px; display: flex; align-items: center; justify-content: center;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="1.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <p style="font-size: 15px; color: #6b7280; margin: 0;">No forms found. Create your first form!</p>
        </div>

        <!-- Bento Glass Grid -->
        <div v-else style="position: relative; z-index: 1; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; padding: 8px 32px 32px;">
          <div
            v-for="(form, idx) in filteredDirectoryForms"
            :key="form.id"
            class="dir-glass-card"
            :class="{ 'dir-card-wide': idx === 0 }"
          >
            <div class="dir-blob-tr" :style="{ background: 'linear-gradient(to bottom-left, ' + (form.theme_color || '#6366f1') + '44, transparent)' }"></div>
            <div class="dir-blob-bl"></div>

            <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 2;">
              <span class="dir-badge" :style="{ background: (form.theme_color || '#6366f1') + '18', color: form.theme_color || '#6366f1', border: '1px solid ' + (form.theme_color || '#6366f1') + '30' }">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" :stroke="form.theme_color || '#6366f1'" stroke-width="2.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                {{ form.input_type_used || 'Text Prompt' }}
              </span>
              <button class="dir-more-btn" @click.stop="duplicateForm(form)" title="Duplicate form">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              </button>
            </div>

            <div style="position: relative; z-index: 2; margin-top: 14px; flex: 1;">
              <h3 class="dir-card-title-new">{{ form.title }}</h3>
              <p style="font-size: 13px; color: #6b7280; margin: 6px 0 0; line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{{ form.description || 'No description provided.' }}</p>
            </div>

            <div style="flex-grow: 1; min-height: 20px;"></div>

            <div style="position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: center; padding-top: 18px; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.45);">
              <button class="dir-btn-edit" @click="openViewModal(form)" :style="{ color: form.theme_color || '#6366f1', border: '1px solid ' + (form.theme_color || '#6366f1') + '30' }">
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

      '''

text = text[:templates_start] + correct_templates + text[dashboard_start:]

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Structure rebuilt successfully!")
