import re

filepath = r"e:\NewSystem\frontend-vue\src\App.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# ===========================================================
# FIX 1 & 4: Replace entire analytics block with refactored
# version using stable _fid keys + Tab-Switch Focus Guard
# ===========================================================
OLD_ANALYTICS_BLOCK = """// ==========================================
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
})"""

NEW_ANALYTICS_BLOCK = """// ==========================================
// 📊 Analytics Engine State (v2 - Stable IDs)
// ==========================================
// Structure: analyticsStore[formAid][fieldFid] = { label, focused, filled, removed }
const analyticsStore = ref({})
const selectedAnalyticsFormId = ref(null)
const currentlyFocusedId = ref(null)  // Fix #4: Tab-Switch Focus Guard

// Helper: stable unique field ID
const _genFid = () => 'fid_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7)

// The analytics ID of the currently active form
const _currentFormAid = computed(() => generatedForm.value?._aid || null)

const _activeFormAnalytics = computed(() => {
  const aid = selectedAnalyticsFormId.value
  if (!aid || !analyticsStore.value[aid]) return {}
  return analyticsStore.value[aid]
})

// Fix #1 & #4: Use _fid as key; guard against duplicate tab-switch focus events
const sendAnalyticsLog = (fieldFid, actionType, fieldLabel, value = '') => {
  const aid = _currentFormAid.value
  if (!fieldFid || !aid) return
  if (!analyticsStore.value[aid]) analyticsStore.value[aid] = {}
  const store = analyticsStore.value[aid]
  if (!store[fieldFid]) store[fieldFid] = { label: fieldLabel || fieldFid, focused: 0, filled: 0, removed: false }
  // Always sync latest label (survives renames via Quick Tweaker)
  store[fieldFid].label = fieldLabel || store[fieldFid].label

  if (actionType === 'focus') {
    // Tab-Switch Focus Guard: ignore if this field is already the active focus
    if (currentlyFocusedId.value === fieldFid) return
    currentlyFocusedId.value = fieldFid
    store[fieldFid].focused++
  } else if (actionType === 'blur') {
    if (currentlyFocusedId.value === fieldFid) currentlyFocusedId.value = null
    const strVal = String(value).trim()
    if (strVal.length > 0) store[fieldFid].filled++
  }
}

// Fix #3: Smart Purge Logic - call this before removing a field from the form
const _purgeFieldAnalytics = (fieldFid) => {
  const aid = _currentFormAid.value
  if (!aid || !analyticsStore.value[aid]?.[fieldFid]) return
  const entry = analyticsStore.value[aid][fieldFid]
  if (entry.filled === 0) {
    // No real data → completely remove to avoid dashboard clutter
    delete analyticsStore.value[aid][fieldFid]
  } else {
    // Legacy data exists → keep but mark as [Removed]
    analyticsStore.value[aid][fieldFid].removed = true
  }
}

const analyticsRows = computed(() => {
  return Object.entries(_activeFormAnalytics.value).map(([fid, data]) => {
    const dropOff = Math.max(0, data.focused - data.filled)
    const completionRate = data.focused > 0 ? Math.round((data.filled / data.focused) * 100) : 0
    return { fid, label: data.label, focused: data.focused, filled: data.filled, dropOff, completionRate, removed: data.removed || false }
  }).sort((a, b) => {
    // Removed fields sink to bottom
    if (a.removed !== b.removed) return a.removed ? 1 : -1
    return a.completionRate - b.completionRate
  })
})

const totalInteractions = computed(() =>
  Object.values(_activeFormAnalytics.value).filter(d => !d.removed).reduce((s, d) => s + d.focused, 0)
)
const overallCompletion = computed(() => {
  const active = Object.values(_activeFormAnalytics.value).filter(d => !d.removed)
  const totalFocused = active.reduce((s, d) => s + d.focused, 0)
  const totalFilled  = active.reduce((s, d) => s + d.filled, 0)
  return totalFocused > 0 ? Math.round((totalFilled / totalFocused) * 100) : 0
})
const highDropOffField = computed(() => {
  const rows = analyticsRows.value.filter(r => !r.removed)
  if (rows.length === 0) return '—'
  return rows[0].label
})

// Fix #2: List of forms that have analytics data (for dashboard selector)
const analyticsFormList = computed(() => {
  return Object.keys(analyticsStore.value).map(aid => {
    const match = savedForms.value.find(f => (f.id === aid || f._aid === aid))
    let title = aid
    if (match) title = match.title
    else if (generatedForm.value?._aid === aid) title = generatedForm.value.title
    return { aid, title }
  })
})"""

content = content.replace(OLD_ANALYTICS_BLOCK, NEW_ANALYTICS_BLOCK)

# ===========================================================
# FIX 1: Assign _fid to fields when form is generated from API
# Inject after: generatedForm.value = formPayload
# ===========================================================
OLD_SET_FORM = "    generatedForm.value = formPayload\n\n    formResponses.value = {}"
NEW_SET_FORM = """    // Assign stable analytics IDs to each field and the form itself
    if (!formPayload._aid) formPayload._aid = formPayload.id || ('form_' + Date.now().toString(36))
    if (formPayload.sections) {
      formPayload.sections.forEach(sec => {
        if (sec.fields) sec.fields.forEach(f => { if (!f._fid) f._fid = _genFid() })
      })
    }
    generatedForm.value = formPayload
    selectedAnalyticsFormId.value = formPayload._aid

    formResponses.value = {}"""
content = content.replace(OLD_SET_FORM, NEW_SET_FORM)

# ===========================================================
# FIX 1: Also assign _fid in sandbox/mock form fallback
# ===========================================================
OLD_MOCK_FIELDS = """              { label: 'Mock Field 1', name: 'mock_1', type: 'text', placeholder: 'ทดสอบข้อมูล...' },
              { label: 'หมายเหตุ', name: 'notes', type: 'textarea', placeholder: 'ทดสอบกล่องข้อความ...' }"""
NEW_MOCK_FIELDS = """              { label: 'Mock Field 1', name: 'mock_1', _fid: _genFid(), type: 'text', placeholder: 'ทดสอบข้อมูล...' },
              { label: 'หมายเหตุ', name: 'notes', _fid: _genFid(), type: 'textarea', placeholder: 'ทดสอบกล่องข้อความ...' }"""
content = content.replace(OLD_MOCK_FIELDS, NEW_MOCK_FIELDS)

# Also patch the sandbox form to get _aid
OLD_SANDBOX_FORM = """      generatedForm.value = {
        title: `⚠️ Sandbox Mode (${activeFunction.value.label})`,"""
NEW_SANDBOX_FORM = """      const sandboxAid = 'sandbox_' + Date.now().toString(36)
      generatedForm.value = {
        _aid: sandboxAid,
        title: `⚠️ Sandbox Mode (${activeFunction.value.label})`,"""
content = content.replace(OLD_SANDBOX_FORM, NEW_SANDBOX_FORM)

# Set selectedAnalyticsFormId after sandbox form
OLD_AFTER_SANDBOX = """      formResponses.value = {
        'mock_1': '',
        'notes': ''
      }"""
NEW_AFTER_SANDBOX = """      selectedAnalyticsFormId.value = sandboxAid
      formResponses.value = {
        'mock_1': '',
        'notes': ''
      }"""
content = content.replace(OLD_AFTER_SANDBOX, NEW_AFTER_SANDBOX)

# ===========================================================
# FIX 1: Assign _fid when loadSavedForm is called
# ===========================================================
OLD_LOAD_FORM = """const loadSavedForm = (form) => {
  generatedForm.value = JSON.parse(JSON.stringify(form))
  currentTab.value = 'create'
}"""
NEW_LOAD_FORM = """const loadSavedForm = (form) => {
  const copy = JSON.parse(JSON.stringify(form))
  // Assign stable form analytics ID
  if (!copy._aid) copy._aid = copy.id || ('form_' + Date.now().toString(36))
  // Assign stable field IDs if missing
  copy.sections?.forEach(sec => sec.fields?.forEach(f => { if (!f._fid) f._fid = _genFid() }))
  generatedForm.value = copy
  selectedAnalyticsFormId.value = copy._aid
  currentTab.value = 'create'
}"""
content = content.replace(OLD_LOAD_FORM, NEW_LOAD_FORM)

# ===========================================================
# FIX 1: Assign _fid to new fields created inline / via modal
# ===========================================================
OLD_ADD_INLINE = """const addFieldAfterInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  const newField = {
    name: "new_field_" + Date.now(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  };
  generatedForm.value.sections[sIdx].fields.splice(fIdx + 1, 0, newField);
}"""
NEW_ADD_INLINE = """const addFieldAfterInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  const newField = {
    name: "new_field_" + Date.now(),
    _fid: _genFid(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  };
  generatedForm.value.sections[sIdx].fields.splice(fIdx + 1, 0, newField);
}"""
content = content.replace(OLD_ADD_INLINE, NEW_ADD_INLINE)

OLD_ADD_BEFORE = """const addFieldBefore = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const newField = {
    name: "new_field_" + Date.now(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  }
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 0, newField)
  closeEditModal()
}

const addFieldAfter = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const newField = {
    name: "new_field_" + Date.now(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  }
  generatedForm.value.sections[sIdx].fields.splice(fIdx + 1, 0, newField)
  closeEditModal()
}"""
NEW_ADD_BEFORE = """const addFieldBefore = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const newField = { name: "new_field_" + Date.now(), _fid: _genFid(), label: "New Field", type: "text", placeholder: "Enter value", required: false, width: "full" }
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 0, newField)
  closeEditModal()
}

const addFieldAfter = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const newField = { name: "new_field_" + Date.now(), _fid: _genFid(), label: "New Field", type: "text", placeholder: "Enter value", required: false, width: "full" }
  generatedForm.value.sections[sIdx].fields.splice(fIdx + 1, 0, newField)
  closeEditModal()
}"""
content = content.replace(OLD_ADD_BEFORE, NEW_ADD_BEFORE)

# ===========================================================
# FIX 3: Smart Purge in deleteFieldInline
# ===========================================================
OLD_DELETE_INLINE = """const deleteFieldInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  if (!confirm('ยืนยันการลบ Field นี้?')) return;
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1);
}"""
NEW_DELETE_INLINE = """const deleteFieldInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  if (!confirm('ยืนยันการลบ Field นี้?')) return;
  const field = generatedForm.value.sections[sIdx].fields[fIdx];
  if (field._fid) _purgeFieldAnalytics(field._fid);
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1);
}"""
content = content.replace(OLD_DELETE_INLINE, NEW_DELETE_INLINE)

# ===========================================================
# FIX 3: Smart Purge in deleteField (from modal)
# ===========================================================
OLD_DELETE_MODAL = """const deleteField = () => {
  if (!editingField.value || !generatedForm.value) return
  if (!confirm('ยืนยันการลบ Field นี้?')) return
  const { sIdx, fIdx } = editingField.value
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1)
  closeEditModal()
}"""
NEW_DELETE_MODAL = """const deleteField = () => {
  if (!editingField.value || !generatedForm.value) return
  if (!confirm('ยืนยันการลบ Field นี้?')) return
  const { sIdx, fIdx } = editingField.value
  const field = generatedForm.value.sections[sIdx].fields[fIdx]
  if (field._fid) _purgeFieldAnalytics(field._fid)
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1)
  closeEditModal()
}"""
content = content.replace(OLD_DELETE_MODAL, NEW_DELETE_MODAL)

# ===========================================================
# FIX 2: Auto-select form in analytics when switching to dashboard tab
# ===========================================================
OLD_WATCH = """watch(currentTab, (newTab) => {
  if (newTab === 'directory' || newTab === 'dashboard') {
    fetchForms()
  }
})"""
NEW_WATCH = """watch(currentTab, (newTab) => {
  if (newTab === 'directory' || newTab === 'dashboard') {
    fetchForms()
  }
  if (newTab === 'dashboard') {
    // Auto-select the current form's analytics if nothing selected yet
    const aid = _currentFormAid.value
    if (aid && !selectedAnalyticsFormId.value) {
      selectedAnalyticsFormId.value = aid
    } else if (!selectedAnalyticsFormId.value && analyticsFormList.value.length > 0) {
      selectedAnalyticsFormId.value = analyticsFormList.value[0].aid
    }
  }
})"""
content = content.replace(OLD_WATCH, NEW_WATCH)

# ===========================================================
# FIX 1: Update canvas template @focus/@blur to use field._fid
# ===========================================================
# Regular inputs
OLD_INPUT_EVENTS = """@focus=\"sendAnalyticsLog(field.name, 'focus', field.label)\" @blur=\"sendAnalyticsLog(field.name, 'blur', field.label, $event.target.value)\""""
NEW_INPUT_EVENTS = """@focus=\"sendAnalyticsLog(field._fid, 'focus', field.label)\" @blur=\"sendAnalyticsLog(field._fid, 'blur', field.label, $event.target.value)\""""
content = content.replace(OLD_INPUT_EVENTS, NEW_INPUT_EVENTS, 2)  # input + textarea

# Select
OLD_SELECT_FOCUS = """@focus=\"sendAnalyticsLog(field.name, 'focus', field.label)\" @change=\"sendAnalyticsLog(field.name, 'blur', field.label, $event.target.value)\""""
NEW_SELECT_FOCUS = """@focus=\"sendAnalyticsLog(field._fid, 'focus', field.label)\" @change=\"sendAnalyticsLog(field._fid, 'blur', field.label, $event.target.value)\""""
content = content.replace(OLD_SELECT_FOCUS, NEW_SELECT_FOCUS)

# Checkbox/radio
OLD_CHECK_EVENT = """@change=\"sendAnalyticsLog(field.name, 'blur', field.label, opt)\""""
NEW_CHECK_EVENT = """@change=\"sendAnalyticsLog(field._fid, 'blur', field.label, opt)\""""
content = content.replace(OLD_CHECK_EVENT, NEW_CHECK_EVENT)

# ===========================================================
# FIX 2: Replace Dashboard HTML — add form selector + [Removed] badge
# ===========================================================
OLD_DASHBOARD_HTML = """      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
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

NEW_DASHBOARD_HTML = """      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
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

        <!-- Fix #2: Form Selector (only shown when multiple forms have analytics) -->
        <div v-if="analyticsFormList.length > 0" class="form-selector-row">
          <label class="form-selector-label">📊 Viewing analytics for:</label>
          <select v-model="selectedAnalyticsFormId" class="form-selector-dropdown">
            <option v-for="item in analyticsFormList" :key="item.aid" :value="item.aid">
              {{ item.title }}
            </option>
          </select>
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
            <p class="panel-sub">Click into form fields in the Canvas to record interactions. Deleted fields with data show as [Removed].</p>
          </div>

          <div v-if="!selectedAnalyticsFormId" class="analytics-empty">
            <div class="analytics-empty-icon">📋</div>
            <p class="analytics-empty-title">No form selected</p>
            <p class="analytics-empty-sub">Generate or load a form in the <strong>Create</strong> tab to begin tracking.</p>
          </div>
          <div v-else-if="analyticsRows.length === 0" class="analytics-empty">
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
            <div v-for="row in analyticsRows" :key="row.fid" class="funnel-row" :class="{ 'funnel-row-removed': row.removed }">
              <div class="funnel-label-col">
                <span class="funnel-field-label">{{ row.label }}</span>
                <span v-if="row.removed" class="badge-removed">Removed</span>
              </div>
              <div class="funnel-bar-col">
                <div class="funnel-track">
                  <div
                    class="funnel-fill"
                    :style="`width: ${row.completionRate}%; background: ${row.removed ? 'linear-gradient(90deg, #cbd5e1, #e2e8f0)' : row.completionRate >= 75 ? 'linear-gradient(90deg, #10b981, #34d399)' : row.completionRate >= 40 ? 'linear-gradient(90deg, #f59e0b, #fbbf24)' : 'linear-gradient(90deg, #ef4444, #f87171)'}`"
                  ></div>
                </div>
                <span class="funnel-pct" :class="row.removed ? 'pct-muted' : row.completionRate >= 75 ? 'pct-green' : row.completionRate >= 40 ? 'pct-amber' : 'pct-red'">{{ row.completionRate }}%</span>
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

content = content.replace(OLD_DASHBOARD_HTML, NEW_DASHBOARD_HTML)

# ===========================================================
# Add CSS for form selector and [Removed] badge
# ===========================================================
CSS_ADDITION = """
/* ─── Fix #2: Form Selector Row ─── */
.form-selector-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 14px 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.form-selector-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  white-space: nowrap;
}
.form-selector-dropdown {
  flex: 1;
  max-width: 360px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.88rem;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}
.form-selector-dropdown:focus { border-color: #6366f1; }

/* ─── Fix #3: Removed field row & badge ─── */
.funnel-row-removed {
  opacity: 0.55;
}
.badge-removed {
  display: inline-block;
  margin-left: 8px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 6px;
  background: #f1f5f9;
  color: #94a3b8;
  border-radius: 100px;
  border: 1px solid #e2e8f0;
}
.pct-muted { color: #94a3b8; }
</style>
"""
content = content.replace("</style>", CSS_ADDITION)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Phase 3.5 bug fixes applied successfully.")
