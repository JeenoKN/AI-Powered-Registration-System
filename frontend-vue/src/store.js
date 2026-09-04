import { ref, watch } from 'vue'

const currentDraft = ref(null)

// Initialize from localStorage if exists
try {
  const saved = localStorage.getItem('global_draft_form')
  if (saved) {
    currentDraft.value = JSON.parse(saved)
  }
} catch (e) {
  console.error('Failed to parse global draft from localStorage')
}

// Sync back to localStorage to support multiple tabs
watch(currentDraft, (newVal) => {
  if (newVal) {
    localStorage.setItem('global_draft_form', JSON.stringify(newVal))
  } else {
    localStorage.removeItem('global_draft_form')
  }
}, { deep: true })

export function useFormStore() {
  return {
    currentDraft
  }
}
