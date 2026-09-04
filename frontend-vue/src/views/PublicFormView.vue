<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useFormStore } from '../store'

const route = useRoute()
const formId = route.params.formId

const { currentDraft } = useFormStore()

const form = ref(null)
const loading = ref(true)
const error = ref(null)

const isSubmitting = ref(false)
const isSubmitted = ref(false)
const alreadySubmitted = ref(false)

const formResponses = ref({})
const isDraftSaved = ref(false)

// --- Phase 2: Multi-step Form State ---
const currentStep = ref(0)
const publicFormRef = ref(null)

const nextStep = () => {
  if (publicFormRef.value && !publicFormRef.value.checkValidity()) {
    publicFormRef.value.reportValidity()
    return
  }
  if (form.value && currentStep.value < form.value.sections.length - 1) {
    currentStep.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// --- Phase 1: Auto-save Draft ---
let draftTimer = null
watch(formResponses, (newVal) => {
  if (isSubmitted.value || alreadySubmitted.value) return
  isDraftSaved.value = false
  clearTimeout(draftTimer)
  draftTimer = setTimeout(() => {
    localStorage.setItem(`draft_${formId}`, JSON.stringify(newVal))
    isDraftSaved.value = true
    setTimeout(() => { isDraftSaved.value = false }, 2000)
  }, 1000)
}, { deep: true })

onMounted(async () => {
  // Tier 1 Security: Check if already submitted
  if (localStorage.getItem(`submitted_${formId}`)) {
    alreadySubmitted.value = true
    loading.value = false
    return
  }

  try {
    let match = null
    
    try {
      if (formId !== 'preview') {
        const res = await fetch(`/api/v1/forms/${formId}`)
        if (res.ok) {
          const data = await res.json()
          if (data.form) {
            match = data.form
          }
        }
      }
    } catch (err) {
      console.warn("Failed to fetch from backend, falling back to local storage", err)
    }

    if (!match) {
      // Step 1: Check Form Directory localStorage
      const possibleKeys = ['savedForms', 'ai_forms_directory', 'saved_forms', 'ai_forms']
      for (const key of possibleKeys) {
        try {
          const data = JSON.parse(localStorage.getItem(key) || 'null')
          if (Array.isArray(data)) {
            match = data.find(f => f && (f.id === formId || f._aid === formId))
            if (match) break
          }
        } catch (e) {}
      }

      if (!match) {
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i)
          try {
            const data = JSON.parse(localStorage.getItem(key))
            if (Array.isArray(data)) {
              match = data.find(f => f && (f.id === formId || f._aid === formId))
              if (match) break
            }
          } catch (e) {}
        }
      }

      // Step 2: If not found in directory, use global state / preview draft
      if (!match && currentDraft.value) {
        const draft = currentDraft.value
        if (draft.id === formId || draft._aid === formId || formId === 'preview') {
          match = draft
        }
      }
    }

    if (!match) throw new Error('Form not found or has not been deployed yet.')
    form.value = match

    // Restore draft if exists
    nextTick(() => {
      const savedDraft = localStorage.getItem(`draft_${formId}`)
      if (savedDraft) {
        try {
          formResponses.value = JSON.parse(savedDraft)
        } catch (e) {}
      }
    })

  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  isSubmitting.value = true
  
  try {
    const res = await fetch(`/api/v1/submit/${formId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formResponses.value)
    })

    if (!res.ok) {
      throw new Error('Failed to submit response to server')
    }

    // Tier 1 Security: Mark as submitted only after API success
    localStorage.setItem(`submitted_${formId}`, 'true')
    localStorage.removeItem(`draft_${formId}`) // Clear draft
    isSubmitted.value = true
  } catch (err) {
    console.error(err)
    alert('An error occurred while submitting the form. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="public-container" :style="form?.theme?.bg_color ? `--bg-color: ${form.theme.bg_color}` : '--bg-color: #f8fafc'">
    
    <!-- Loading State -->
    <div v-if="loading" class="status-box">
      <div class="spinner"></div>
      <p>Loading form...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="status-box error-box">
      <div class="icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <!-- Already Submitted State -->
    <div v-else-if="alreadySubmitted" class="status-box success-box">
      <div class="icon">✋</div>
      <h2>Already Submitted</h2>
      <p>You have already responded to this form. Thank you!</p>
    </div>

    <!-- Success State -->
    <div v-else-if="isSubmitted" class="status-box success-box animate-scale">
      <div class="icon">✅</div>
      <h2>Thank You!</h2>
      <p>Your response has been successfully submitted.</p>
    </div>

    <!-- Form View -->
    <div v-else-if="form" class="form-wrapper">
      <div class="form-card animate-fade" :style="`--card-bg: ${form.theme?.card_bg || '#ffffff'}; --text-color: ${form.theme?.text_color || '#0f172a'}; --theme-color: ${form.theme_color || '#4f46e5'}; --border-color: ${form.theme?.border_color || '#e2e8f0'}; --border-radius: ${form.theme?.border_radius || '20px'}; --input-bg: ${form.theme?.input_bg || '#f8fafc'}; --input-text: ${form.theme?.input_text || '#334155'}; --label-color: ${form.theme?.label_color || '#475569'}`">
        
        <header class="form-header">
          <div v-if="form.theme?.logo_url" class="public-logo-container" style="text-align: center; margin-bottom: 24px;">
            <img :src="form.theme.logo_url" alt="Form Logo" style="max-height: 120px; border-radius: 12px; object-fit: contain; max-width: 100%;" />
          </div>
          <h1 class="form-title">{{ form.title }}</h1>
          <p v-if="form.description" class="form-description">{{ form.description }}</p>
        </header>

        <div v-if="form.sections && form.sections.length > 1">
          <div class="progress-bar-container" style="margin-bottom: 24px; background: var(--border-color, #e2e8f0); height: 6px; border-radius: 3px; overflow: hidden;">
            <div class="progress-bar-fill" :style="{ width: `${((currentStep + 1) / form.sections.length) * 100}%`, background: form.theme_color || '#4f46e5', height: '100%', transition: 'width 0.3s ease' }"></div>
          </div>
          <p style="text-align: right; font-size: 0.85rem; color: var(--label-color); margin-top: -16px; margin-bottom: 24px;">Step {{ currentStep + 1 }} of {{ form.sections.length }}</p>
        </div>

        <form ref="publicFormRef" @submit.prevent="handleSubmit" class="form-element">
          <template v-for="(section, sIdx) in form.sections" :key="sIdx">
            <fieldset v-if="sIdx === currentStep" class="form-section animate-fade">
              <legend class="section-legend">{{ section.title }}</legend>
              <p v-if="section.description" class="section-desc">{{ section.description }}</p>
            
            <div class="fields-grid">
              <div v-for="(field, fIdx) in section.fields" :key="fIdx" class="field-item" :style="field.width === 'half' ? 'grid-column: span 1' : 'grid-column: span 2'">
                <label class="field-label">
                  {{ field.label }} <span v-if="field.required" class="required-star">*</span>
                </label>
                
                <template v-if="field.type === 'textarea'">
                  <textarea v-model="formResponses[field.id || field.name || field.label]" class="field-input" :placeholder="field.placeholder" :required="field.required" rows="3"></textarea>
                </template>
                <template v-else-if="field.type === 'select'">
                  <select v-model="formResponses[field.id || field.name || field.label]" class="field-input" :required="field.required">
                    <option value="" disabled selected>{{ field.placeholder || 'Select an option' }}</option>
                    <option v-for="(opt, oIdx) in field.options" :key="oIdx" :value="opt">{{ opt }}</option>
                  </select>
                </template>
                <template v-else-if="field.type === 'radio'">
                  <div class="radio-group">
                    <label v-for="(opt, oIdx) in field.options" :key="oIdx" class="radio-label">
                      <input type="radio" v-model="formResponses[field.id || field.name || field.label]" :value="opt" :required="field.required" />
                      <span>{{ opt }}</span>
                    </label>
                  </div>
                </template>
                <template v-else-if="field.type === 'checkbox'">
                  <div class="radio-group">
                    <label v-for="(opt, oIdx) in field.options" :key="oIdx" class="radio-label">
                      <input type="checkbox" v-model="formResponses[field.id || field.name || field.label]" :value="opt" />
                      <span>{{ opt }}</span>
                    </label>
                  </div>
                </template>
                <template v-else>
                  <input :type="field.type" v-model="formResponses[field.id || field.name || field.label]" class="field-input" :placeholder="field.placeholder" :required="field.required" />
                </template>
              </div>
            </div>
            </fieldset>
          </template>

          <div class="form-footer" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <button type="button" v-if="currentStep > 0" @click="prevStep" class="submit-btn" style="background: var(--border-color, #e2e8f0); color: var(--text-color, #0f172a);">
              Previous
            </button>
            <div style="flex: 1;"></div>
            
            <div style="display: flex; align-items: center; gap: 16px;">
              <span v-if="isDraftSaved" style="color: #10b981; font-size: 0.9rem; font-weight: 600; display: flex; align-items: center; gap: 4px;" class="animate-fade">
                ✓ Draft saved
              </span>
              <button type="button" v-if="currentStep < form.sections.length - 1" @click="nextStep" class="submit-btn">
                Next
              </button>
              <button type="submit" v-else :disabled="isSubmitting" class="submit-btn">
                {{ isSubmitting ? 'Submitting...' : 'Submit Response' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.public-container {
  min-height: 100vh;
  background-color: var(--bg-color);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 20px;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}

.form-wrapper {
  width: 100%;
  max-width: 800px;
}

.form-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 40px;
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.08);
  color: var(--text-color);
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.form-description {
  font-size: 1.05rem;
  color: var(--label-color);
  line-height: 1.6;
}

.form-section {
  border: none;
  margin-bottom: 32px;
  padding: 0;
}

.section-legend {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-color);
}

.section-desc {
  font-size: 0.9rem;
  color: var(--label-color);
  margin-bottom: 16px;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--label-color);
}

.required-star {
  color: #ef4444;
  margin-left: 2px;
}

.field-input {
  width: 100%;
  padding: 12px 16px;
  background: var(--input-bg);
  color: var(--input-text);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.2s;
  outline: none;
}

.field-input:focus {
  border-color: var(--theme-color);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--theme-color) 20%, transparent);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  color: var(--input-text);
}

.form-footer {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.submit-btn {
  padding: 14px 40px;
  background: var(--theme-color);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px color-mix(in srgb, var(--theme-color) 40%, transparent);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--theme-color) 50%, transparent);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.status-box {
  background: #ffffff;
  border-radius: 20px;
  padding: 48px;
  text-align: center;
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.08);
  max-width: 400px;
  width: 100%;
}

.status-box .icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.status-box h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
}

.status-box p {
  color: #64748b;
  line-height: 1.6;
}

.error-box .icon { color: #ef4444; }
.success-box .icon { color: #10b981; }

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-fade { animation: fadeIn 0.4s ease-out; }
.animate-scale { animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}
</style>
