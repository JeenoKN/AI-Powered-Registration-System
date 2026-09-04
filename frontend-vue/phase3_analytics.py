import re

filepath = r"e:\NewSystem\frontend-vue\src\App.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────
# 1. ADD analytics state refs after existing state block
# ─────────────────────────────────────────────
state_addition = """
// ==========================================
// 📊 Analytics Engine State
// ==========================================
const fieldAnalytics = ref({})  // { fieldName: { label, focused: 0, filled: 0 } }

const sendAnalyticsLog = (fieldName, actionType, fieldLabel, value = '') => {
  if (!fieldName) return
  if (!fieldAnalytics.value[fieldName]) {
    fieldAnalytics.value[fieldName] = { label: fieldLabel || fieldName, focused: 0, filled: 0 }
  }
  if (actionType === 'focus') {
    fieldAnalytics.value[fieldName].focused++
  } else if (actionType === 'blur') {
    const strVal = String(value).trim()
    if (strVal.length > 0) {
      fieldAnalytics.value[fieldName].filled++
    }
  }
}

const analyticsRows = computed(() => {
  return Object.entries(fieldAnalytics.value).map(([name, data]) => {
    const dropOff = Math.max(0, data.focused - data.filled)
    const completionRate = data.focused > 0 ? Math.round((data.filled / data.focused) * 100) : 0
    return { name, label: data.label, focused: data.focused, filled: data.filled, dropOff, completionRate }
  }).sort((a, b) => a.completionRate - b.completionRate)
})

const totalInteractions = computed(() => Object.values(fieldAnalytics.value).reduce((s, d) => s + d.focused, 0))
const overallCompletion = computed(() => {
  const totalFocused = Object.values(fieldAnalytics.value).reduce((s, d) => s + d.focused, 0)
  const totalFilled  = Object.values(fieldAnalytics.value).reduce((s, d) => s + d.filled, 0)
  return totalFocused > 0 ? Math.round((totalFilled / totalFocused) * 100) : 0
})
const highDropOffField = computed(() => {
  const rows = analyticsRows.value
  if (rows.length === 0) return '—'
  return rows[0].label
})
"""

# Insert after "const editModalConditionValue = ref('')" line
insert_after = "const editModalConditionValue = ref('')"
content = content.replace(insert_after, insert_after + "\n" + state_addition)

# ─────────────────────────────────────────────
# 2. ENABLE input interactions in the Preview Canvas
#    Remove `disabled` and add @focus/@blur analytics events
# ─────────────────────────────────────────────

# Remove disabled from regular inputs and add events
old_input = """<input v-if=\"!['select', 'textarea', 'checkbox', 'radio'].includes(field.type)\" :type=\"field.type || 'text'\" class=\"field-input\" :placeholder=\"field.placeholder\" disabled />"""
new_input = """<input v-if=\"!['select', 'textarea', 'checkbox', 'radio'].includes(field.type)\" :type=\"field.type || 'text'\" class=\"field-input\" :placeholder=\"field.placeholder\" @focus=\"sendAnalyticsLog(field.name, 'focus', field.label)\" @blur=\"sendAnalyticsLog(field.name, 'blur', field.label, $event.target.value)\" />"""
content = content.replace(old_input, new_input)

# Remove disabled from textarea and add events
old_textarea = """<textarea v-else-if=\"field.type === 'textarea'\" class=\"field-input textarea-input\" :placeholder=\"field.placeholder\" disabled></textarea>"""
new_textarea = """<textarea v-else-if=\"field.type === 'textarea'\" class=\"field-input textarea-input\" :placeholder=\"field.placeholder\" @focus=\"sendAnalyticsLog(field.name, 'focus', field.label)\" @blur=\"sendAnalyticsLog(field.name, 'blur', field.label, $event.target.value)\"></textarea>"""
content = content.replace(old_textarea, new_textarea)

# Remove disabled from select and add events
old_select = """<select v-else-if=\"field.type === 'select'\" class=\"field-input\" disabled>
                        <option>{{ field.placeholder || 'Select...' }}</option>
                      </select>"""
new_select = """<select v-else-if=\"field.type === 'select'\" class=\"field-input\" @focus=\"sendAnalyticsLog(field.name, 'focus', field.label)\" @change=\"sendAnalyticsLog(field.name, 'blur', field.label, $event.target.value)\">
                        <option value="">{{ field.placeholder || 'Select...' }}</option>
                        <option v-for=\"opt in field.options\" :key=\"opt\" :value=\"opt\">{{ opt }}</option>
                      </select>"""
content = content.replace(old_select, new_select)

# Remove disabled from checkbox/radio
old_checkbox = """<input :type=\"field.type\" disabled /> {{ opt }}"""
new_checkbox = """<input :type=\"field.type\" @change=\"sendAnalyticsLog(field.name, 'blur', field.label, opt)\" /> {{ opt }}"""
content = content.replace(old_checkbox, new_checkbox)

# ─────────────────────────────────────────────
# 3. REPLACE Dashboard HTML with full Premium Analytics Dashboard
# ─────────────────────────────────────────────

old_dashboard = """      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
        <div class="view-header">
          <h2 class="view-title">Dashboard</h2>
          <p class="view-sub">System Analytics & Overview</p>
        </div>
        <div class="dashboard-stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ totalFormsInDb }}</div>
            <div class="stat-label">Total Forms Generated</div>
          </div>
          <div class="stat-card">
            <div class="stat-value" :class="mongoDbStatus === 'connected' ? 'status-ok' : 'status-err'">
              {{ mongoDbStatus === 'connected' ? 'Connected' : 'Error' }}
            </div>
            <div class="stat-label">MongoDB Status</div>
          </div>
        </div>
      </div>"""

new_dashboard = """      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
        <!-- Dashboard Header -->
        <div class="db-header">
          <div>
            <h2 class="db-title">Analytics Studio</h2>
            <p class="db-sub">Real-time form interaction &amp; drop-off intelligence</p>
          </div>
          <div class="db-status-badge" :class="mongoDbStatus === 'connected' ? 'db-ok' : 'db-err'">
            <span class="db-status-dot"></span>
            MongoDB {{ mongoDbStatus === 'connected' ? 'Connected' : 'Error' }}
          </div>
        </div>

        <!-- KPI Row -->
        <div class="kpi-row">
          <div class="kpi-card kpi-accent-indigo">
            <div class="kpi-icon">📋</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ totalFormsInDb }}</div>
              <div class="kpi-label">Forms in Library</div>
            </div>
          </div>
          <div class="kpi-card kpi-accent-violet">
            <div class="kpi-icon">👆</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ totalInteractions }}</div>
              <div class="kpi-label">Total Interactions</div>
            </div>
          </div>
          <div class="kpi-card kpi-accent-emerald">
            <div class="kpi-icon">✅</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ overallCompletion }}%</div>
              <div class="kpi-label">Overall Completion</div>
            </div>
          </div>
          <div class="kpi-card kpi-accent-rose">
            <div class="kpi-icon">⚠️</div>
            <div class="kpi-body">
              <div class="kpi-value kpi-truncate">{{ highDropOffField }}</div>
              <div class="kpi-label">Highest Drop-off Field</div>
            </div>
          </div>
        </div>

        <!-- Drop-off Funnel Chart -->
        <div class="analytics-panel">
          <div class="panel-header">
            <div class="panel-title">
              <span class="panel-icon">📉</span>
              Field Drop-off Funnel
            </div>
            <p class="panel-sub">Focus the form in the Canvas tab and interact with fields to populate this chart.</p>
          </div>

          <div v-if="analyticsRows.length === 0" class="analytics-empty">
            <div class="analytics-empty-icon">🖱️</div>
            <p class="analytics-empty-title">No interactions recorded yet</p>
            <p class="analytics-empty-sub">Go to the <strong>Create</strong> tab, generate a form, then click into the form fields to start capturing analytics.</p>
          </div>

          <div v-else class="funnel-chart">
            <div class="funnel-row funnel-header-row">
              <div class="funnel-label-col">Field</div>
              <div class="funnel-bar-col">Completion Rate</div>
              <div class="funnel-stats-col">Interactions</div>
            </div>
            <div v-for="row in analyticsRows" :key="row.name" class="funnel-row">
              <div class="funnel-label-col">
                <span class="funnel-field-label">{{ row.label }}</span>
              </div>
              <div class="funnel-bar-col">
                <div class="funnel-track">
                  <div
                    class="funnel-fill"
                    :style="`width: ${row.completionRate}%; background: ${row.completionRate >= 75 ? 'linear-gradient(90deg, #10b981, #34d399)' : row.completionRate >= 40 ? 'linear-gradient(90deg, #f59e0b, #fbbf24)' : 'linear-gradient(90deg, #ef4444, #f87171)'}`"
                  ></div>
                </div>
                <span class="funnel-pct" :class="row.completionRate >= 75 ? 'pct-green' : row.completionRate >= 40 ? 'pct-amber' : 'pct-red'">{{ row.completionRate }}%</span>
              </div>
              <div class="funnel-stats-col">
                <span class="stat-chip chip-focus">{{ row.focused }} focused</span>
                <span class="stat-chip chip-fill">{{ row.filled }} filled</span>
                <span v-if="row.dropOff > 0" class="stat-chip chip-drop">{{ row.dropOff }} dropped</span>
              </div>
            </div>
          </div>
        </div>
      </div>"""

content = content.replace(old_dashboard, new_dashboard)

# ─────────────────────────────────────────────
# 4. REPLACE old dashboard CSS with Premium CSS
# ─────────────────────────────────────────────

old_dashboard_css = """.dashboard-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: #ffffff;
  border: none;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.01);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

.stat-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}"""

new_dashboard_css = """/* ─── Dashboard: Premium Analytics Studio ─── */
.db-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 32px;
}
.db-title {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #0f172a;
  margin: 0 0 4px;
}
.db-sub {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}
.db-status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 600;
}
.db-ok { background: #f0fdf4; color: #15803d; }
.db-err { background: #fef2f2; color: #dc2626; }
.db-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* KPI Row */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}
.kpi-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
.kpi-accent-indigo::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
.kpi-accent-violet::before { background: linear-gradient(90deg, #7c3aed, #a78bfa); }
.kpi-accent-emerald::before { background: linear-gradient(90deg, #059669, #34d399); }
.kpi-accent-rose::before { background: linear-gradient(90deg, #e11d48, #fb7185); }
.kpi-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 12px;
}
.kpi-body { min-width: 0; }
.kpi-value {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
  letter-spacing: -0.03em;
}
.kpi-truncate {
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}
.kpi-label {
  font-size: 0.78rem;
  color: #94a3b8;
  font-weight: 500;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Analytics Panel */
.analytics-panel {
  background: #ffffff;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.panel-header { margin-bottom: 24px; }
.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}
.panel-icon { font-size: 1.2rem; }
.panel-sub { font-size: 0.82rem; color: #94a3b8; margin: 0; }

/* Analytics Empty State */
.analytics-empty {
  text-align: center;
  padding: 48px 24px;
  color: #94a3b8;
}
.analytics-empty-icon { font-size: 3rem; margin-bottom: 12px; }
.analytics-empty-title { font-size: 1rem; font-weight: 600; color: #64748b; margin: 0 0 6px; }
.analytics-empty-sub { font-size: 0.85rem; margin: 0; line-height: 1.6; }
.analytics-empty-sub strong { color: #475569; }

/* Funnel Chart */
.funnel-chart { display: flex; flex-direction: column; gap: 12px; }
.funnel-row {
  display: grid;
  grid-template-columns: 180px 1fr 200px;
  align-items: center;
  gap: 16px;
  padding: 10px 0;
}
.funnel-header-row {
  font-size: 0.72rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 8px;
}
.funnel-label-col { min-width: 0; }
.funnel-field-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}
.funnel-bar-col { display: flex; align-items: center; gap: 10px; }
.funnel-track {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 100px;
  overflow: hidden;
}
.funnel-fill {
  height: 100%;
  border-radius: 100px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.funnel-pct { font-size: 0.82rem; font-weight: 700; min-width: 36px; text-align: right; }
.pct-green { color: #10b981; }
.pct-amber { color: #f59e0b; }
.pct-red   { color: #ef4444; }
.funnel-stats-col { display: flex; gap: 6px; flex-wrap: wrap; }
.stat-chip {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 100px;
}
.chip-focus { background: #eff6ff; color: #3b82f6; }
.chip-fill  { background: #f0fdf4; color: #10b981; }
.chip-drop  { background: #fef2f2; color: #ef4444; }

/* Legacy classes kept for compat */
.dashboard-stats-grid { display: none; }"""

content = content.replace(old_dashboard_css, new_dashboard_css)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Phase 3 Analytics Dashboard applied successfully.")
