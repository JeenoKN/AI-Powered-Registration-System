<script setup>
import FormCard from '../components/FormCard.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useFormStore } from '../store'
import draggable from 'vuedraggable'

const _genFid = () => 'f_' + Math.random().toString(36).substr(2, 9)

const loading = ref(false)
const deploying = ref(false)
const selectedInputType = ref('text_prompt')
const textPrompt = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)

// Middle Chat Attachment
const chatFileInput = ref(null)
const handleChatFile = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  chatMessages.value.push({ sender: 'user', text: `[Uploading: ${file.name}...]` })
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch('/api/v1/upload', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (data.status === 'success') {
      textPrompt.value += `\n[Attached Image URL: ${data.url}]`
      chatMessages.value.pop()
      chatMessages.value.push({ sender: 'ai', text: ` File attached: ${file.name}` })
    }
  } catch (err) {
    chatMessages.value.pop()
    chatMessages.value.push({ sender: 'ai', text: ` Upload failed: ${err.message}` })
  }
}

// Logo Upload
const logoFileInput = ref(null)
const handleLogoUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch('/api/v1/upload', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (data.status === 'success' && generatedForm.value) {
      if (!generatedForm.value.theme) {
        generatedForm.value.theme = {}
      }
      generatedForm.value.theme.logo_url = data.url
    }
  } catch (err) {
    alert("Failed to upload logo: " + err.message)
  }
}



// Logo Layout Dragging State
const isDraggingLogo = ref(false)
const ghostPos = ref({ x: 0, y: 0 })
const dragOffset = ref({ x: 0, y: 0 })
const hoverZone = ref(null)

const logoLayout = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return 'left'
    return generatedForm.value.theme.logo_layout || 'left'
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) generatedForm.value.theme = {}
    generatedForm.value.theme.logo_layout = val
  }
})

const logoAlign = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return 'left'
    return generatedForm.value.theme.logo_align || 'left'
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) generatedForm.value.theme = {}
    generatedForm.value.theme.logo_align = val
  }
})


// Logo Resize & Layout State
const logoSize = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return 120
    return generatedForm.value.theme.logo_size || 120
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) generatedForm.value.theme = {}
    generatedForm.value.theme.logo_size = val
  }
})

const isResizingLogo = ref(false)
const showLogoToolbar = ref(false)

const startLogoResize = (e) => {
  e.stopPropagation()
  e.preventDefault()
  isResizingLogo.value = true
  
  const startX = e.clientX
  const startSize = logoSize.value
  
  const onMouseMove = (ev) => {
    const diff = ev.clientX - startX
    let newSize = startSize + diff
    if (newSize < 60) newSize = 60
    if (newSize > 350) newSize = 350
    logoSize.value = newSize
  }
  
  const onMouseUp = () => {
    isResizingLogo.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

const removeLogo = () => {
  if (generatedForm.value && generatedForm.value.theme) {
    generatedForm.value.theme.logo_url = null
  }
}

// Ensure old state variables like logoLayout and startLogoDrag are not redefined
const startLogoDrag = (e) => {
  if (e.target.closest('.form-logo-overlay')) return 
  if (e.target.tagName.toLowerCase() === 'input') return
  
  const rect = e.currentTarget.getBoundingClientRect()
  
  isDraggingLogo.value = true
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  ghostPos.value = { x: e.clientX - dragOffset.value.x, y: e.clientY - dragOffset.value.y }
  hoverZone.value = logoLayout.value

  document.addEventListener('mousemove', onLogoDrag)
  document.addEventListener('mouseup', stopLogoDrag)
  e.preventDefault()
}

const onLogoDrag = (e) => {
  if (!isDraggingLogo.value) return
  ghostPos.value = {
    x: e.clientX - dragOffset.value.x,
    y: e.clientY - dragOffset.value.y
  }
  
  // Determine drop zone based on mouse position relative to header
  const headerEl = document.querySelector('.form-header-container')
  if (headerEl) {
    const hRect = headerEl.getBoundingClientRect()
    // Relative mouse Y inside header
    const relY = e.clientY - hRect.top
    const relX = e.clientX - hRect.left
    
    if (relY < 60) {
      hoverZone.value = 'top'
      if (relX > hRect.width / 2) {
        logoAlign.value = 'center'
      } else {
        logoAlign.value = 'left'
      }
    } else {
      if (relX < hRect.width / 2) hoverZone.value = 'left'
      else hoverZone.value = 'right'
    }
  }
}

const stopLogoDrag = () => {
  if (isDraggingLogo.value && hoverZone.value) {
    logoLayout.value = hoverZone.value
  }
  isDraggingLogo.value = false
  hoverZone.value = null
  document.removeEventListener('mousemove', onLogoDrag)
  document.removeEventListener('mouseup', stopLogoDrag)
}




const generatedForm = ref(null) 
const { currentDraft } = useFormStore()

// --- Phase 1: Undo / Redo State ---
const formHistory = ref([])
const historyIndex = ref(-1)
let isUndoRedoing = false
let historyDebounceTimer = null

const pushHistory = (newVal) => {
  if (isUndoRedoing || !newVal) return
  
  clearTimeout(historyDebounceTimer)
  historyDebounceTimer = setTimeout(() => {
    const currentSnapshot = JSON.stringify(newVal)
    if (historyIndex.value >= 0 && formHistory.value[historyIndex.value] === currentSnapshot) return
    
    if (historyIndex.value < formHistory.value.length - 1) {
      formHistory.value = formHistory.value.slice(0, historyIndex.value + 1)
    }
    formHistory.value.push(currentSnapshot)
    historyIndex.value = formHistory.value.length - 1
  }, 500)
}

const undoHistory = () => {
  if (historyIndex.value > 0) {
    isUndoRedoing = true
    historyIndex.value--
    generatedForm.value = JSON.parse(formHistory.value[historyIndex.value])
    setTimeout(() => isUndoRedoing = false, 50)
  }
}

const redoHistory = () => {
  if (historyIndex.value < formHistory.value.length - 1) {
    isUndoRedoing = true
    historyIndex.value++
    generatedForm.value = JSON.parse(formHistory.value[historyIndex.value])
    setTimeout(() => isUndoRedoing = false, 50)
  }
}

watch(generatedForm, (newVal) => {
  currentDraft.value = newVal
  pushHistory(newVal)
}, { deep: true })

// --- Phase 1: Device Preview State ---
const deviceMode = ref('desktop') // 'desktop', 'tablet', 'mobile'


const formResponses = ref({})

// แท็บที่กำลังทำงานอยู่และรายการฟอร์มจาก MongoDB
const toasts = ref([])
const showToast = (message, type = 'success') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id) }, 3000)
}
const currentTab = ref('create') // 'create', 'directory', 'dashboard'
const savedForms = ref([])
const loadingDirectory = ref(false)

const searchQuery = ref('')
const viewFormModal = ref(null)

const filteredDirectoryForms = computed(() => {
  if (!searchQuery.value) return savedForms.value
  const q = searchQuery.value.toLowerCase()
  return savedForms.value.filter(f => f.title && f.title.toLowerCase().includes(q))
})

const openViewModal = (form) => {
  viewFormModal.value = form
}

const closeViewModal = () => {
  viewFormModal.value = null
}

const getShareLink = (form) => {
  return window.location.origin + '/f/' + (form.id || form._aid)
}

const duplicateForm = (form) => {
  const copy = JSON.parse(JSON.stringify(form))
  delete copy.id
  delete copy._id
  copy._aid = 'form_' + Date.now().toString(36)
  copy.title = `Copy of ${copy.title}`
  // Assign stable field IDs if missing
  copy.sections?.forEach(sec => sec.fields?.forEach(f => { if (!f._fid) f._fid = _genFid() }))
  
  viewFormModal.value = null // Close modal
  generatedForm.value = copy

  currentTab.value = 'create'
}

// สถานะการแก้ไขฟิลด์ (Inline Editor)
const showEditModal = ref(false)
const editingField = ref(null) // { sIdx, fIdx }
const editModalLabel = ref('')
const editModalPlaceholder = ref('')
const editModalType = ref('text')
const editModalOptionsText = ref('')
const editModalRequired = ref(false)
const editModalWidth = ref('full')

// สถานะการลากวาง (Drag & Drop)
const dragSource = ref(null) // { sIdx, fIdx }

//  AI Theme Engine State
const themePrompt = ref('')
const themeLoading = ref(false)
const activeTheme = ref(null) // { theme_color, bg_color, card_bg, text_color, ... }

// Conditional Logic fields in Edit Modal
const editModalConditionField = ref('')
const editModalConditionValue = ref('')

const editModalMasterCategory = ref('provinces')

// ==========================================
//  Responses Viewer State (Live Data)
// ==========================================
const liveResponses = ref([])

const fetchDashboardResponses = async () => {
  try {
    let url = '/api/v1/responses/all'
    if (selectedDashboardFormId.value !== 'all') {
      url = `/api/v1/forms/${selectedDashboardFormId.value}/responses`
    }
    const res = await fetch(url)
    const data = await res.json()
    if (data.status === 'success') {
      liveResponses.value = data.data
    }
  } catch (e) {
    console.error('Failed to fetch responses:', e)
    liveResponses.value = []
  }
}

const selectedDashboardFormId = ref('all')

const dashboardFormOptions = computed(() => {
  // Use savedForms to create options instead of liveResponses to show all available forms
  return savedForms.value.map(f => ({
    id: f.id || f._aid,
    title: f.title
  }))
})

// Export to Excel logic
const exportToExcel = () => {
  let url = '/api/v1/responses/export-excel'
  if (selectedDashboardFormId.value && selectedDashboardFormId.value !== 'all') {
    url += `?form_id=${selectedDashboardFormId.value}`
  }
  window.open(url, '_blank')
}

const filteredResponses = computed(() => {
  return liveResponses.value
})

watch(selectedDashboardFormId, () => {
  fetchDashboardResponses()
})

const getFormName = (formId) => {
  const match = savedForms.value.find(f => f.id === formId || f._aid === formId)
  return match ? match.title : formId
}

//  Backend / MongoDB (dashboard)
const mongoDbStatus = ref('checking') // 'checking' | 'connected' | 'error'
const totalFormsInDb = ref(0)

const chatMessages = ref([
  {
    sender: 'ai',
    text: 'สวัสดีครับ! กรุณาเลือกฟังก์ชันที่ต้องการจากเมนูด้านซ้าย แนบไฟล์ และพิมพ์คำสั่งตรงกลางนี้ได้เลยครับ ฝั่งขวาจะแสดงผลฟอร์มหลังจากที่ผมประมวลผลเสร็จแล้ว ✨'
  }
])

const inputTypes = [
  { value: 'text_prompt', label: '1. Text Prompt Only', icon: '✏️', hint: 'สั่งงานด้วยข้อความภาษาธรรมชาติโดยตรง' },
  { value: 'physical_paper', label: '2. Physical Paper (OCR)', icon: '📄', hint: 'อัปโหลดรูปถ่ายฟอร์มเอกสารใบเสร็จ/ใบสมัคร' },
  { value: 'handwritten_sketch', label: '3. Handwritten Sketch', icon: '🖊️', hint: 'รูปภาพฟอร์มที่ร่างด้วยลายมือ' },
  { value: 'voice', label: '4. Voice Instruction', icon: '🎤', hint: 'ไฟล์เสียงพูดสั่งงานหรือคำอธิบาย' },
  { value: 'markdown', label: '5. Markdown (.md)', icon: '📝', hint: 'โครงสร้างเอกสาร Text รูปแบบ Markdown' },
  { value: 'digital_pdf', label: '6. Digital PDF Extractor', icon: '📄', hint: 'เอกสารประเภท PDF ฟอร์มดิจิทัล' },
  { value: 'spreadsheet', label: '7. Legacy Spreadsheet', icon: '📊', hint: 'ไฟล์ตาราง Excel, Google Sheets หรือ CSV' },
  { value: 'ui_screenshot', label: '8. UI Screenshot', icon: '🖼️', hint: 'ภาพแคปหน้าจอ UI ของเว็บไซต์เก่า' },
  { value: 'json_config', label: '9. JSON Configuration', icon: '⚙️', hint: 'ไฟล์โครงสร้าง JSON Schema' },
  { value: 'scanned_image', label: '10. Scanned Image', icon: '🖨️', hint: 'ภาพสแกน PDF/TIFF ความละเอียดสูง' }
]

const activeFunction = computed(() => {
  return inputTypes.find(t => t.value === selectedInputType.value)
})

const resetChat = () => {
  if (confirm("Are you sure you want to reset the chat? This will clear the chat history and the current form on the canvas.")) {
    chatMessages.value = []
    generatedForm.value = null
    formHistory.value = []
    historyIndex.value = -1
    formResponses.value = {}
    textPrompt.value = ''
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  }
}

const selectFunction = (val) => {
  if (selectedInputType.value === val) return  // ถ้าคลิก function  
  selectedInputType.value = val
  // ล้างไฟล์เสมอเมื่อสลับ function เพื่อป้องกันไฟล์ผิดประเภทไปยัง backend
  clearFile()
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) selectedFile.value = file
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

//  [] ฟังก์ชันสำหรับเคลียร์ค่าที่ผู้ใช้กรอกในฟอร์ม
const clearFormResponses = () => {
  if (!formResponses.value || !generatedForm.value || !generatedForm.value.sections) return
  generatedForm.value.sections.forEach(section => {
    if (section.fields) {
      section.fields.forEach(field => {
        const fieldKey = field.name || field.key || field.label
        if (fieldKey) {
          formResponses.value[fieldKey] = field.type === 'checkbox' ? [] : 'คำสั่งจำลอง'
        }
      })
    }
  })
}

// ----------------------------------------------------
// 2. ฟังก์ชันส่งคำสั่งไปหา Backend ( API )
// ----------------------------------------------------
const sendCombinedCommand = async (autoRetryPrompt = null, isAutoRetry = false) => {
  if (autoRetryPrompt instanceof Event) autoRetryPrompt = null
  
  if (!isAutoRetry && !textPrompt.value.trim() && !selectedFile.value) return
  if (!isAutoRetry && loading.value) return

  const userInstruction = isAutoRetry ? autoRetryPrompt : textPrompt.value
  const attachedFileName = selectedFile.value ? selectedFile.value.name : null

  if (!isAutoRetry) {
    chatMessages.value.push({
      sender: 'user',
      text: userInstruction || '(ส่งไฟล์เพื่อทำการวิเคราะห์รูปภาพ)',
      fileName: attachedFileName,
      functionLabel: activeFunction.value.label
    })
    textPrompt.value = ''
  }

  loading.value = true
  
  const existingForm = generatedForm.value
  if (!existingForm) {
    generatedForm.value = null
    formResponses.value = {}  
  }

  try {
    const formData = new FormData()
    formData.append('input_type', selectedInputType.value)
    
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }
    
    if (userInstruction) {
      formData.append('prompt', userInstruction)
    }

    // Intercept if form is already loaded (Edit mode)
    if (existingForm && !selectedFile.value) {
      const editRes = await fetch('/api/v1/forms/edit-schema', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: userInstruction,
          current_schema: existingForm
        })
      })
      if (!editRes.ok) throw new Error(`Backend Error: ${editRes.status}`)
      const editData = await editRes.json()
      chatMessages.value.push({ sender: 'ai', text: " ฟอร์มของคุณถูกอัปเดตเรียบร้อยแล้ว!" })
      generatedForm.value = editData.form
      return // End here for edit mode
    }

    const response = await fetch('/api/v1/forms/generate', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error("QUOTA_EXCEEDED")
      }
      const errText = await response.text().catch(() => '')
      if (errText.includes("QUOTA_EXCEEDED")) {
        throw new Error("QUOTA_EXCEEDED")
      }
      let detail = ''
      try {
        const errJson = JSON.parse(errText)
        detail = errJson.detail || errText
      } catch (e) {
        detail = errText
      }
      const err = new Error(`เกิดข้อผิดพลาดจากเซิร์ฟเวอร์: ${response.status}`)
      err.response = { status: response.status, data: { detail } }
      throw err
    }

    const data = await response.json()
    
    if (data.reply) {
      chatMessages.value.push({ sender: 'ai', text: data.reply })
    } else {
      chatMessages.value.push({ sender: 'ai', text: `  "${activeFunction.value.label}" !` })
    }

    let formPayload = data.form || data
    
    if (!formPayload.sections && formPayload.fields) {
      formPayload.sections = [
        {
          title: 'General Information',
          description: 'ข้อมูลที่ระบบดึงออกมาได้',
          fields: formPayload.fields
        }
      ]
    }

    // Assign stable analytics IDs to each field and the form itself
    if (!formPayload._aid) formPayload._aid = formPayload.id || ('form_' + Date.now().toString(36))
    if (formPayload.sections) {
      formPayload.sections.forEach(sec => {
        if (sec.fields) sec.fields.forEach(f => { if (!f._fid) f._fid = _genFid() })
      })
    }
    generatedForm.value = formPayload


    formResponses.value = {}
    if (formPayload.sections) {
      formPayload.sections.forEach(section => {
        if (section.fields) {
          section.fields.forEach(field => {
            const fieldKey = field.name || field.key || field.label
            formResponses.value[fieldKey] = field.type === 'checkbox' ? [] : 'คำสั่งจำลอง'
          })
        }
      })
    }

  } catch (error) {
    console.error("Backend Error:", error)
    if (error.message === "QUOTA_EXCEEDED" || error.message.includes("QUOTA_EXCEEDED") || error.message.includes("429")) {
      chatMessages.value.push({ 
        sender: 'ai', 
        text: 'ขออภัยครับ โควตาการใช้งาน AI (Token Exhausted) รบกวนรอสักครู่แล้วลองใหม่อีกครั้งครับ 🙏' 
      })
    } else if (error.response && error.response.status === 400) {
      const detailMsg = error.response.data?.detail || error.message
      
      if ((detailMsg.includes("Scanned Image") || detailMsg.includes("10. Scanned Image")) && selectedInputType.value !== 'scanned_image') {
        chatMessages.value.push({
          sender: 'ai',
          text: `🤖 ตรวจพบเอกสารแบบ Scanned PDF ระบบกำลังสลับไปใช้ฟังก์ชัน '10. Scanned Image' และทำการประมวลผลให้ใหม่โดยอัตโนมัติ...`
        })
        selectedInputType.value = 'scanned_image'
        await sendCombinedCommand(userInstruction, true)
        return
      } else {
        chatMessages.value.push({
          sender: 'ai',
          text: `🚨 [ข้อผิดพลาด] ${detailMsg}`
        })
      }
    } else if (error.response && error.response.status === 500) {
      const detailMsg = error.response.data?.detail || error.message
      chatMessages.value.push({
        sender: 'ai',
        text: `🚨 [ข้อผิดพลาด] ${detailMsg}`
      })
    } else {
      chatMessages.value.push({ 
        sender: 'ai', 
        text: `🚨 [ข้อผิดพลาด] ไม่สามารถเชื่อมต่อกับ Backend ได้ หรือ Backend เกิด Error ระบบจึงจำลองฟอร์มขึ้นมาแทนครับ (Detail: ${error.message || error})` 
      })
      
      const sandboxAid = 'sandbox_' + Date.now().toString(36)
      generatedForm.value = {
        _aid: sandboxAid,
        title: `⚠️ Sandbox Mode (${activeFunction.value.label})`,
        sections: [
          {
            title: '',
            description: attachedFileName ? `วิเคราะห์จากไฟล์จำลอง: ${attachedFileName}` : 'คำสั่งจำลอง',
            fields: [
              { label: 'Mock Field 1', name: 'mock_1', _fid: _genFid(), type: 'text', placeholder: '...' },
              { label: '', name: 'notes', _fid: _genFid(), type: 'textarea', placeholder: 'ทดสอบกล่องข้อความ...' }
            ]
          }
        ]
      }

      formResponses.value = { mock_1: '', notes: '' }
    }
  } finally {
    loading.value = false
  }
}

// ----------------------------------------------------
// 3. ฟังก์ชันส่งข้อมูลฟอร์มที่ผู้ใช้กรอก  MongoDB 
// ----------------------------------------------------
const deployForm = async () => {
  if (!generatedForm.value || deploying.value) return

  const rawId = generatedForm.value.id || generatedForm.value._id
  const formId = (typeof rawId === 'object' && rawId !== null && rawId.$oid) ? rawId.$oid : rawId

  deploying.value = true

  try {
    const payload = generatedForm.value

    const isNewForm = !formId
    const url = isNewForm 
      ? '/api/v1/forms' 
      : `/api/v1/forms/${formId}`
    const method = isNewForm ? 'POST' : 'PUT'

    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`เซิร์ฟเวอร์ปฏิเสธการบันทึกข้อมูล: ${response.status}`)
    }

    const result = await response.json()
    
    // ถ้าเป็นฟอร์มใหม่ ให้อัปเดต ID กลับเข้าสู่ generatedForm
    if (isNewForm && result.form && result.form.id) {
      generatedForm.value.id = result.form.id
    }

    alert(isNewForm ? ' บันทึกฟอร์มใหม่สำเร็จ!' : ' 🚀')
    
    chatMessages.value.push({
      sender: 'ai',
      text: ` 🎉 อัปเดตโครงสร้างฟอร์มดิจิทัล "${generatedForm.value.title}" ลงในระบบ MongoDB ของคุณเรียบร้อยแล้วครับ!`
    })

  } catch (error) {
    console.error("Deploy MongoDB Error:", error)
    alert(` เกิดข้อผิดพลาดในการบันทึก: ${error.message}`)
  } finally {
    deploying.value = false
  }
}

// ----------------------------------------------------
// 4. ฟังก์ชันสำหรับการ Export โครงสร้างฟอร์มออกมาเป็นไฟล์ Vue Component (.vue)
// ----------------------------------------------------
const exportVueComponent = (formToExport = null) => {
  // กรอง PointerEvent หรือ Event ของเบราว์เซอร์ออก เพื่อใช้ค่าจาก generatedForm.value 
  const isEvent = formToExport && (formToExport instanceof Event || formToExport.target);
  const form = (formToExport && !isEvent) ? formToExport : generatedForm.value
  if (!form) return
  const title = (form.title || 'Generated Form').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  const formDescription = form.description || ''
  const themeColor = form.theme_color || '#4f46e5'

  //  unique safeKey สำหรับแต่ละ field เพื่อป้องกัน key ชนกัน (โดยเฉพาะชื่อภาษาไทย)
  const allFieldKeys = []
  const usedKeys = new Set()
  if (form.sections) {
    form.sections.forEach((section, sIdx) => {
      if (section.fields) {
        section.fields.forEach((field, fIdx) => {
          const rawKey = field.name || field.key || field.label || ''
          let safeKey = rawKey.replace(/[^a-zA-Z0-9_]/g, '_').replace(/^_+|_+$/g, '') || `field`
          // ป้องกัน key ซ้ำกัน
          let uniqueKey = safeKey
          let counter = 2
          while (usedKeys.has(uniqueKey)) {
            uniqueKey = `${safeKey}_${counter}`
            counter++
          }
          usedKeys.add(uniqueKey)
          allFieldKeys.push({ field, safeKey: uniqueKey, sIdx, fIdx })
        })
      }
    })
  }

  // Map original names to safeKeys for conditional logic checking
  const originalToSafeKeyMap = new Map()
  allFieldKeys.forEach(({ field, safeKey }) => {
    const rawKey = field.name || field.key || field.label || ''
    originalToSafeKeyMap.set(rawKey, safeKey)
  })

  // Check if we have any conditional fields
  const hasConditions = allFieldKeys.some(({ field }) => field.condition_field && field.condition_value)

  // 1.  <script setup>  Vue Component 
  let scriptContent = `<script setup>
import { ref${hasConditions ? ', watch' : 'คำสั่งจำลอง'} } from 'vue'

const formResponses = ref({
`
  allFieldKeys.forEach(({ field, safeKey }) => {
    // If field is checkbox, initialize as array
    if (field.type === 'checkbox') {
      scriptContent += `  ${safeKey}: [],\n`
    } else {
      scriptContent += `  ${safeKey}: '',\n`
    }
  })
  scriptContent += `})

const isSubmitting = ref(false)

const handleSubmit = () => {
  isSubmitting.value = true
  console.log('Form Data Submitted:', formResponses.value)
  setTimeout(() => {
    isSubmitting.value = false
    alert('บันทึกข้อมูลสำเร็จ! 🚀')
  }, 1000)
}
`

  // Add watch block for conditional logic reset in exported component
  if (hasConditions) {
    scriptContent += `
// เคลียร์ค่าฟิลด์ที่ถูกซ่อนโดย Conditional Logic 
watch(formResponses, (newResponses) => {
`
    allFieldKeys.forEach(({ field, safeKey }) => {
      if (field.condition_field && field.condition_value) {
        const srcSafeKey = originalToSafeKeyMap.get(field.condition_field)
        if (srcSafeKey) {
          const srcFieldObj = allFieldKeys.find(k => (k.field.name || k.field.key || k.field.label) === field.condition_field)?.field
          const isSrcCheckbox = srcFieldObj && srcFieldObj.type === 'checkbox'
          
          let conditionExpr = ''
          if (isSrcCheckbox) {
            conditionExpr = `newResponses.${srcSafeKey}.includes('${field.condition_value.replace(/'/g, "\\'")}')`
          } else {
            conditionExpr = `newResponses.${srcSafeKey} === '${field.condition_value.replace(/'/g, "\\'")}'`
          }
          
          scriptContent += `  if (!(${conditionExpr})) {\n`
          scriptContent += `    if (Array.isArray(newResponses.${safeKey})) {\n`
          scriptContent += `      if (newResponses.${safeKey}.length > 0) newResponses.${safeKey} = []\n`
          scriptContent += `    } else if (newResponses.${safeKey} !== '') {\n`
          scriptContent += `      newResponses.${safeKey} = ''\n`
          scriptContent += `    }\n`
          scriptContent += `  }\n`
        }
      }
    })
    scriptContent += `}, { deep: true })\n`
  }

  scriptContent += `<\/script>\n`

  // 2.  <template>  Vue Component
  const descriptionHtml = formDescription
    ? `      <p class="form-description">${formDescription.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>\n`
    : 'คำสั่งจำลอง'

  //  style binding  container  Dynamic Theme
  let containerStyles = `style="--theme-color: ${themeColor}`
  if (form.theme) {
    const t = form.theme
    containerStyles += `; --bg-color: ${t.bg_color || '#f8fafc'}`
    containerStyles += `; --card-bg: ${t.card_bg || '#ffffff'}`
    containerStyles += `; --text-color: ${t.text_color || '#0f172a'}`
    containerStyles += `; --border-color: ${t.border_color || '#e2e8f0'}`
    containerStyles += `; --input-bg: ${t.input_bg || '#f8fafc'}`
    containerStyles += `; --input-text: ${t.input_text || '#334155'}`
    containerStyles += `; --border-radius: ${t.border_radius || '8px'}`
    containerStyles += `; --label-color: ${t.label_color || '#334155'}`
  }
  containerStyles += `"`

  let templateContent = `<template>
  <div class="form-container" ${containerStyles}>
    <div class="form-card animate-fade">
      <header class="form-header">
        <h1 class="form-title">${title}</h1>
${descriptionHtml}      </header>

      <form @submit.prevent="handleSubmit" class="form-element">
`

  //  lookup map: (sIdx, fIdx) => safeKey จาก allFieldKeys ที่ pre-compute ไว้แล้ว
  const fieldKeyMap = new Map()
  allFieldKeys.forEach(({ safeKey, sIdx, fIdx }) => {
    fieldKeyMap.set(`${sIdx}-${fIdx}`, safeKey)
  })

  if (form.sections) {
    form.sections.forEach((section, sIdx) => {
      const sectionDescHtml = section.description
        ? `          <p class="section-desc">${(section.description || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>\n`
        : 'คำสั่งจำลอง'
      templateContent += `        <!-- Section: ${(section.title || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')} -->\n        <fieldset class="form-section">\n          <legend class="section-legend">${(section.title || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</legend>\n${sectionDescHtml}\n          <div class="fields-grid">\n`
      if (section.fields) {
        section.fields.forEach((field, fIdx) => {
          const safeKey = fieldKeyMap.get(`${sIdx}-${fIdx}`) || `field_${sIdx}_${fIdx}`
          const isRequired = field.required ? 'required' : 'คำสั่งจำลอง'
          const requiredMark = field.required ? ' <span class="required-star">*</span>' : 'คำสั่งจำลอง'
          const labelText = (field.label || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          const placeholder = (field.placeholder || '').replace(/"/g, '&quot;')

          //  visibility directive (v-show)  conditional logic
          let visibilityDirective = ''
          if (field.condition_field && field.condition_value) {
            const srcSafeKey = originalToSafeKeyMap.get(field.condition_field)
            if (srcSafeKey) {
              const srcFieldObj = allFieldKeys.find(k => (k.field.name || k.field.key || k.field.label) === field.condition_field)?.field
              const isSrcCheckbox = srcFieldObj && srcFieldObj.type === 'checkbox'
              
              if (isSrcCheckbox) {
                visibilityDirective = ` v-show="formResponses.${srcSafeKey}.includes('${field.condition_value.replace(/'/g, "\\'")}')"`
              } else {
                visibilityDirective = ` v-show="formResponses.${srcSafeKey} === '${field.condition_value.replace(/'/g, "\\'")}'"`
              }
            }
          }

          const widthStyle = field.width === 'half' ? 'style="grid-column: span 1;"' : 'style="grid-column: span 2;"'
          templateContent += `            <div class="field-group" ${widthStyle}${visibilityDirective}>\n`
          templateContent += `              <label class="field-label" for="${safeKey}">${labelText}${requiredMark}</label>\n`

          if (field.type === 'select') {
            templateContent += `              <select id="${safeKey}" v-model="formResponses['${safeKey}']" class="field-input select-input" ${isRequired}>\n`
            templateContent += `                <option value="" disabled selected>${placeholder || 'โปรดเลือกข้อมูล...'}</option>\n`
            if (field.options && Array.isArray(field.options)) {
              field.options.forEach(opt => {
                const optText = String(opt).replace(/</g, '&lt;').replace(/>/g, '&gt;')
                templateContent += `                <option value="${optText}">${optText}</option>\n`
              })
            }
            templateContent += `              </select>\n`
          } else if (field.type === 'textarea') {
            templateContent += `              <textarea id="${safeKey}" v-model="formResponses['${safeKey}']" placeholder="${placeholder}" class="field-input textarea-input" ${isRequired}></textarea>\n`
          } else if (field.type === 'checkbox') {
            templateContent += `              <div class="checkbox-group">\n`
            if (field.options && Array.isArray(field.options)) {
              field.options.forEach(opt => {
                const optText = String(opt).replace(/</g, '&lt;').replace(/>/g, '&gt;')
                templateContent += `                <label class="checkbox-option-label">\n`
                templateContent += `                  <input type="checkbox" v-model="formResponses['${safeKey}']" value="${optText}" /> ${optText}\n`
                templateContent += `                </label>\n`
              })
            } else {
              templateContent += `                <label class="checkbox-option-label">\n`
              templateContent += `                  <input type="checkbox" v-model="formResponses['${safeKey}']" /> \n`
              templateContent += `                </label>\n`
            }
            templateContent += `              </div>\n`
          } else if (field.type === 'radio') {
            templateContent += `              <div class="radio-group">\n`
            if (field.options && Array.isArray(field.options)) {
              field.options.forEach(opt => {
                const optText = String(opt).replace(/</g, '&lt;').replace(/>/g, '&gt;')
                templateContent += `                <label class="radio-option-label">\n`
                templateContent += `                  <input type="radio" v-model="formResponses['${safeKey}']" value="${optText}" ${isRequired} /> ${optText}\n`
                templateContent += `                </label>\n`
              })
            }
            templateContent += `              </div>\n`
          } else {
            const inputType = field.type || 'text'
            templateContent += `              <input id="${safeKey}" type="${inputType}" v-model="formResponses['${safeKey}']" placeholder="${placeholder}" class="field-input text-input" ${isRequired} />\n`
          }

          templateContent += `            </div>\n`
        })
      }

      templateContent += `          </div>\n        </fieldset>\n`
    })
  }

  templateContent += `        <div class="form-actions">
          <button type="submit" :disabled="isSubmitting" class="submit-btn">
            {{ isSubmitting ? 'กำลังบันทึก...' : ' ' }}
          </button>
        </div>
      </form>
    </div>
    <!-- AI Quick Tweaker Modal -->
    <div v-if="showEditModal" class="editor-modal-overlay animate-fade">
      <div class="editor-modal-card">
        <div class="modal-header">
          <h3> AI Quick Tweaker</h3>
          <button class="btn-close-modal" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-input-group">
            <label>Field Label</label>
            <input type="text" v-model="editModalLabel" class="field-input" />
          </div>
          <div class="modal-input-group">
            <label>Placeholder / Hint</label>
            <input type="text" v-model="editModalPlaceholder" class="field-input" />
          </div>
          
          <div class="modal-input-group-row">
            <div class="modal-input-group" style="flex:1">
              <label>Input Type</label>
              <select v-model="editModalType" class="field-input">
                <option value="text">📝 Text (Short)</option>
                <option value="textarea">📝 Textarea (Long)</option>
                <option value="number"> Number</option>
                <option value="email"> Email</option>
                <option value="date"> Date</option>
                <option value="select"> Dropdown (Select)</option>
                <option value="radio"> Radio Options</option>
                <option value="checkbox"> Checkbox Options</option>
                <option value="file">📎 File Upload</option>
                <option value="master_data"> Master Data Dropdown</option>
              </select>
            </div>
            <div class="modal-input-group" style="flex:1">
              <label>Width</label>
              <select v-model="editModalWidth" class="field-input">
                <option value="full">Full Width (100%)</option>
                <option value="half">Half Width (50%)</option>
              </select>
            </div>
          </div>
          
          <div v-if="editModalType === 'master_data'" class="modal-input-group">
            <label>Master Data Category</label>
            <select v-model="editModalMasterCategory" class="field-input">
              <option value="title_names"> (, , , etc.)</option>
              <option value="provinces"> (Provinces)</option>
              <option value="faculties"> (Faculties)</option>
            </select>
          </div>

          <div v-if="['select', 'radio', 'checkbox'].includes(editModalType)" class="modal-input-group">
            <label>Options (comma separated)</label>
            <input type="text" v-model="editModalOptionsText" class="field-input" placeholder="e.g. Option A, Option B, Option C" />
          </div>

          <div class="modal-input-group-row" style="align-items: center; gap: 12px; margin-top: 12px;">
            <input type="checkbox" id="req-check" v-model="editModalRequired" style="width: 18px; height: 18px; cursor:pointer;" />
            <label for="req-check" style="cursor:pointer; font-weight: 600;">Required Field (*)</label>
          </div>
          
          <div class="modal-conditional-zone" style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 8px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 8px; display: block;">Conditional Logic (Show if)</label>
            <div class="modal-input-group-row">
              <input type="text" v-model="editModalConditionField" class="field-input" placeholder="Depends on Field Name" style="flex:1" />
              <input type="text" v-model="editModalConditionValue" class="field-input" placeholder="Equals Value" style="flex:1" />
            </div>
          </div>

        </div>
        <div class="modal-footer-clean">
          <button class="btn-save-pill" @click="saveFieldEdit">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            Save Changes
          </button>
        </div>
      </div>
    </div>

    <!--  Phase 4: Share & Embed Modal -->
    <Transition name="share-modal">
      <div v-if="isShareModalOpen" class="share-modal-overlay" @click.self="closeShareModal">
        <div class="share-modal-card">

          <!-- Modal Header -->
          <div class="share-modal-header">
            <div class="share-modal-title-group">
              <div class="share-modal-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
              </div>
              <div>
                <h3 class="share-modal-title">Share Form</h3>
                <p class="share-modal-sub">{{ generatedForm?.title }}</p>
              </div>
            </div>
            <button class="share-modal-close" @click="closeShareModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- Tab Switcher -->
          <div class="share-tab-row">
            <button
              class="share-tab-btn"
              :class="{ 'share-tab-active': shareActiveTab === 'link' }"
              @click="shareActiveTab = 'link'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              Direct Link
            </button>
            <button
              class="share-tab-btn"
              :class="{ 'share-tab-active': shareActiveTab === 'embed' }"
              @click="shareActiveTab = 'embed'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              Embed Code
            </button>
          </div>

          <!-- Tab: Direct Link -->
          <div v-if="shareActiveTab === 'link'" class="share-section">
            <p class="share-section-desc">Anyone with this link can view and fill your form.</p>
            <div class="share-copy-row">
              <div class="share-url-display">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="share-url-icon"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                <span class="share-url-text">{{ shareFormUrl }}</span>
              </div>
              <button
                class="btn-copy"
                :class="{ 'btn-copy-success': copyLinkStatus === 'copied' }"
                @click="copyToClipboard(shareFormUrl, 'link')"
              >
                <svg v-if="copyLinkStatus === 'idle'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                {{ copyLinkStatus === 'copied' ? 'Copied!' : 'Copy' }}
              </button>
            </div>
            <div class="share-info-row">
              <div class="share-info-chip">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                This is a preview link. Deploy the form to MongoDB first to activate it.
              </div>
            </div>
          </div>

          <!-- Tab: Embed Code -->
          <div v-if="shareActiveTab === 'embed'" class="share-section">
            <p class="share-section-desc">Paste this snippet into any website to embed the form.</p>
            <div class="share-embed-box">
              <pre class="share-embed-code">{{ shareEmbedCode }}</pre>
            </div>
            <button
              class="btn-copy btn-copy-full"
              :class="{ 'btn-copy-success': copyEmbedStatus === 'copied' }"
              @click="copyToClipboard(shareEmbedCode, 'embed')"
            >
              <svg v-if="copyEmbedStatus === 'idle'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              {{ copyEmbedStatus === 'copied' ? 'Copied to Clipboard! ' : 'Copy Embed Code' }}
            </button>
            <div class="share-info-row">
              <div class="share-info-chip">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                Form must be deployed to MongoDB before embedding on a live site.
              </div>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </div>
</template>
`
  let styleContent = `<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
}
.form-container { padding: 40px 20px; background: var(--bg-color, #f8fafc); min-height: 100vh; display: flex; justify-content: center; }
.form-card { width: 100%; max-width: 680px; background: var(--card-bg, #ffffff); border-radius: var(--border-radius, 20px); padding: 36px; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.06); border: 1px solid var(--border-color, #e2e8f0); }
.form-header { margin-bottom: 28px;  }
.form-title { font-size: 1.75rem; font-weight: 800; color: var(--text-color, #0f172a); margin-bottom: 8px; }
.form-description { font-size: 0.95rem; color: var(--text-color, #64748b); opacity: 0.85; line-height: 1.6; }
.form-element { display: flex; flex-direction: column; gap: 24px; }
.form-section { border: 1px solid var(--border-color, #e2e8f0); border-radius: var(--border-radius, 16px); padding: 24px; background-color: var(--card-bg, #ffffff); margin-bottom: 16px; }
.section-legend { font-weight: 700; color: var(--theme-color, #4f46e5); font-size: 1.15rem; padding: 0 8px; margin-bottom: 8px; }
.section-desc { font-size: 0.9rem; color: var(--text-color, #64748b); opacity: 0.8; margin-bottom: 16px; padding: 0 8px; }
.fields-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 0.9rem; font-weight: 600; color: var(--label-color, #475569); display: flex; align-items: center; }
.required-star { color: #ef4444; margin-left: 2px; }
.field-input { width: 100%; padding: 10px 14px; border: 1.5px solid var(--border-color, #cbd5e1); border-radius: var(--border-radius, 10px); font-size: 0.95rem; color: var(--input-text, #334155); background-color: var(--input-bg, #f8fafc); outline: none; }
.textarea-input { min-height: 100px; resize: vertical; }
.checkbox-group, .radio-group { display: flex; flex-wrap: wrap; gap: 16px; padding: 8px 0; }
.checkbox-option-label, .radio-option-label { display: flex; align-items: center; gap: 8px; font-size: 0.95rem; color: var(--text-color, #475569); cursor: pointer; }
.form-actions { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-color, #e2e8f0); text-align: center; }
.submit-btn { padding: 12px 28px; background: var(--theme-color, #4f46e5); color: #ffffff; border: none; border-radius: 12px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: all 0.2s; }
.submit-btn:hover { filter: brightness(1.1); transform: translateY(-2px); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-fullscreen-toggle {
  background: transparent;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 1rem;
  cursor: pointer;
  color: var(--text-color, #475569);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-left: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-fullscreen-toggle:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}
.fullscreen-mode {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9999 !important;
  width: 100vw !important;
  height: 100vh !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: var(--bg-color, #f8fafc);
  display: flex;
  flex-direction: column;
}
.fullscreen-mode .canvas-preview-wrapper {
  flex: 1;
  border-radius: 0;
  max-width: 100%;
}
.fullscreen-mode .form-card {
  max-width: 800px;
  margin: 0 auto;
}


.btn-delete-danger {
  background: #fef2f2 !important;
  color: #ef4444 !important;
  border: 1px solid #fca5a5 !important;
}
.btn-delete-danger:hover {
  background: #fee2e2 !important;
  transform: translateY(-1px);
}
.btn-insert {
  background: #f0fdf4 !important;
  color: #16a34a !important;
  border: 1px solid #bbf7d0 !important;
}
.btn-insert:hover {
  background: #dcfce7 !important;
  transform: translateY(-1px);
}
.editor-modal-card label {
  font-family: 'Poppins', 'Plus Jakarta Sans', sans-serif;
  font-weight: 600 !important;
  color: #334155;
}
.modal-conditional-zone label {
  font-weight: 500 !important;
  color: #64748b;
}

.field-toolbar {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  gap: 4px;
}
.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: 'Poppins', 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  color: var(--text-color, #475569);
  transition: all 0.2s ease;
}
.toolbar-btn:hover {
  background: #f1f5f9;
}
.toolbar-btn.btn-edit:hover {
  color: #3b82f6;
  background: #eff6ff;
}
.toolbar-btn.btn-add:hover {
  color: #10b981;
  background: #ecfdf5;
}
.toolbar-btn.btn-delete-inline:hover {
  color: #ef4444;
  background: #fef2f2;
}

/*  Fix #2: Form Selector Row  */
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

/*  Fix #3: Removed field row & badge  */
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

/*  Phase 4: Share & Embed Modal  */
.btn-share {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.btn-share:hover:not(:disabled) {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.btn-share:disabled { opacity: 0.4; cursor: not-allowed; }

/* Modal Overlay */
.share-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* Modal Card */
.share-modal-card {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0,0,0,0.04);
  overflow: hidden;
}

/* Modal Header */
.share-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 0;
}
.share-modal-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}
.share-modal-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}
.share-modal-title {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 2px;
  letter-spacing: -0.02em;
}
.share-modal-sub {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}
.share-modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}
.share-modal-close:hover { background: #f8fafc; color: #475569; }

/* Tab Row */
.share-tab-row {
  display: flex;
  gap: 4px;
  padding: 20px 28px 0;
  border-bottom: 1px solid #f1f5f9;
}
.share-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 14px;
  border-radius: 8px 8px 0 0;
  border: none;
  background: transparent;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  bottom: -1px;
}
.share-tab-btn:hover { color: #475569; background: #f8fafc; }
.share-tab-active {
  color: #6366f1 !important;
  background: #ffffff !important;
  border: 1px solid #f1f5f9;
  border-bottom: 1px solid #ffffff !important;
}

/* Share Sections */
.share-section { padding: 24px 28px 28px; }
.share-section-desc { font-size: 0.84rem; color: #64748b; margin: 0 0 16px; }

/* Copy Row */
.share-copy-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.share-url-display {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  min-width: 0;
}
.share-url-icon { color: #94a3b8; flex-shrink: 0; }
.share-url-text {
  font-size: 0.8rem;
  color: #475569;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Embed Box */
.share-embed-box {
  background: #0f172a;
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 12px;
  overflow: hidden;
}
.share-embed-code {
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 0.75rem;
  color: #7dd3fc;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  line-height: 1.6;
}

/* Copy Buttons */
.btn-copy {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  flex-shrink: 0;
}
.btn-copy:hover { background: #f1f5f9; color: #0f172a; }
.btn-copy-success {
  background: #f0fdf4 !important;
  border-color: #86efac !important;
  color: #16a34a !important;
}
.btn-copy-full { width: 100%; justify-content: center; margin-bottom: 12px; }

/* Info Chip */
.share-info-row { margin-top: 4px; }
.share-info-chip {
  display: inline-flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.5;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  width: 100%;
}
.share-info-chip svg { flex-shrink: 0; margin-top: 2px; }

/* Vue Transition for Share Modal */
.share-modal-enter-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.share-modal-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}
.share-modal-enter-from {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}
.share-modal-leave-to {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}
.share-modal-enter-from .share-modal-card,
.share-modal-leave-to .share-modal-card {
  transform: translateY(16px);
}
@media (prefers-reduced-motion: reduce) {
  .share-modal-enter-active,
  .share-modal-leave-active { transition: opacity 0.15s; }
  .share-modal-enter-from,
  .share-modal-leave-to { transform: none; }
}
</style>

`

  const blob = new Blob([scriptContent, '\n', templateContent, '\n', styleContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Form_${Date.now()}.vue`
  a.click()
  URL.revokeObjectURL(url)
}

//  AI Theme Engine Call
const requestAiTheme = async () => {
  if (!themePrompt.value.trim() || !generatedForm.value) return;
  themeLoading.value = true;
  try {
    const response = await fetch('/api/v1/ai/theme', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: themePrompt.value })
    });
    
    if (!response.ok) {
      if (response.status === 429) {
        throw new Error("QUOTA_EXCEEDED");
      }
      const errText = await response.text().catch(() => '');
      if (errText.includes("QUOTA_EXCEEDED")) {
        throw new Error("QUOTA_EXCEEDED");
      }
      throw new Error(`Server Error: ${response.status}`);
    }
    const data = await response.json();
    if (data.theme) {
      activeTheme.value = data.theme;
      if (!generatedForm.value.theme) {
        generatedForm.value.theme = {};
      }
      Object.assign(generatedForm.value.theme, data.theme);
      if (data.theme.theme_color) {
        generatedForm.value.theme_color = data.theme.theme_color;
      }
    }
  } catch (error) {
    console.error("Theme Error:", error);
    if (error.message === "QUOTA_EXCEEDED" || error.message.includes("QUOTA_EXCEEDED")) {
      chatMessages.value.push({ 
        sender: 'ai', 
        text: 'ขออภัยครับ โควตาการใช้งาน AI (Token Exhausted) รบกวนรอสักครู่แล้วลองใหม่อีกครั้งครับ 🙏' 
      });
    } else {
      alert("Error generating theme: " + error.message);
    }
  } finally {
    themeLoading.value = false;
  }
};

const isFullscreen = ref(false)
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

// ==========================================
//  Core Logic: Fetch, Load, Delete Forms
// ==========================================
const fetchForms = async () => {
  loadingDirectory.value = true
  try {
    const res = await fetch('/api/v1/forms')
    const data = await res.json()
    if (data.status === 'success') {
      savedForms.value = data.forms
      totalFormsInDb.value = data.forms.length
      mongoDbStatus.value = 'connected'
    } else {
      mongoDbStatus.value = 'error'
    }
  } catch (err) {
    console.error('Fetch Forms Error:', err)
    mongoDbStatus.value = 'error'
  } finally {
    loadingDirectory.value = false
  }
}

const deleteSavedForm = async (id) => {
  if (!confirm('ยืนยันการลบฟอร์มนี้? ข้อมูล Response จะถูกลบไปด้วย')) return
  try {
    const res = await fetch(`/api/v1/forms/${id}`, { method: 'DELETE' })
    if (res.ok) {
      await fetchForms()
      if (generatedForm.value && generatedForm.value.id === id) {
         generatedForm.value = null
      }
    } else {
      alert('')
    }
  } catch (err) {
    console.error(err)
  }
}

const loadSavedForm = (form) => {
  const copy = JSON.parse(JSON.stringify(form))
  // Assign stable form analytics ID
  if (!copy._aid) copy._aid = copy.id || ('form_' + Date.now().toString(36))
  // Assign stable field IDs if missing
  copy.sections?.forEach(sec => sec.fields?.forEach(f => { if (!f._fid) f._fid = _genFid() }))
  generatedForm.value = copy

  currentTab.value = 'create'
}

// --- Phase 3: Templates Logic ---
const savedTemplates = ref([])
const loadingTemplates = ref(false)
const templateSearchQuery = ref('')

// Dynamic icon + color theme mapping based on template title / input_type_used
const getTemplateTheme = (template) => {
  const title = (template.title || '').toLowerCase()
  const type  = (template.input_type_used || '').toLowerCase()

  // --- keyword → theme map ---
  if (title.includes('patient') || title.includes('medical') || title.includes('health') || title.includes('intake')) {
    return {
      bgFrom: '#f3e8ff', bgTo: '#ede9fe',
      iconColor: '#7c3aed',
      pillBg: 'bg-purple-100', pillText: 'text-purple-600',
      // Shield with cross SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.955 11.955 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.25-8.25-3.286Z"/>`,
      viewBox: '0 0 24 24'
    }
  }
  if (title.includes('job') || title.includes('application') || title.includes('career') || title.includes('recruit') || type.includes('job')) {
    return {
      bgFrom: '#dbeafe', bgTo: '#ede9fe',
      iconColor: '#2563eb',
      pillBg: 'bg-blue-100', pillText: 'text-blue-600',
      // Briefcase SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0"/>`,
      viewBox: '0 0 24 24'
    }
  }
  if (title.includes('rsvp') || title.includes('event') || title.includes('party') || title.includes('celebration') || title.includes('wedding')) {
    return {
      bgFrom: '#fee2e2', bgTo: '#fce7f3',
      iconColor: '#e11d48',
      pillBg: 'bg-red-100', pillText: 'text-red-500',
      // Sparkles SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"/>`,
      viewBox: '0 0 24 24'
    }
  }
  if (title.includes('quiz') || title.includes('survey') || title.includes('review') || title.includes('feedback') || title.includes('assessment') || type.includes('quiz')) {
    return {
      bgFrom: '#d1fae5', bgTo: '#a7f3d0',
      iconColor: '#059669',
      pillBg: 'bg-green-100', pillText: 'text-green-600',
      // Question mark / chat bubble SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z"/>`,
      viewBox: '0 0 24 24'
    }
  }
  if (title.includes('order') || title.includes('product') || title.includes('shop') || title.includes('ecommerce') || title.includes('purchase')) {
    return {
      bgFrom: '#fef3c7', bgTo: '#fde68a',
      iconColor: '#d97706',
      pillBg: 'bg-amber-100', pillText: 'text-amber-600',
      // Shopping bag SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>`,
      viewBox: '0 0 24 24'
    }
  }
  if (type.includes('voice')) {
    return {
      bgFrom: '#fce7f3', bgTo: '#ffe4e6',
      iconColor: '#db2777',
      pillBg: 'bg-pink-100', pillText: 'text-pink-600',
      // Microphone SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"/>`,
      viewBox: '0 0 24 24'
    }
  }
  if (type.includes('scanned') || title.includes('scan') || title.includes('document')) {
    return {
      bgFrom: '#e0f2fe', bgTo: '#bae6fd',
      iconColor: '#0284c7',
      pillBg: 'bg-sky-100', pillText: 'text-sky-600',
      // Document scan SVG
      svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>`,
      viewBox: '0 0 24 24'
    }
  }
  // Default / text_prompt / manual
  return {
    bgFrom: '#ede9fe', bgTo: '#e0e7ff',
    iconColor: '#6366f1',
    pillBg: 'bg-indigo-100', pillText: 'text-indigo-600',
    // Text / form SVG
    svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z"/>`,
    viewBox: '0 0 24 24'
  }
}

const fetchTemplates = async () => {
  loadingTemplates.value = true
  try {
    const res = await fetch('/api/v1/templates')
    const data = await res.json()
    if (data.status === 'success') {
      savedTemplates.value = data.templates
    }
  } catch (err) {
    console.error(err)
  } finally {
    loadingTemplates.value = false
  }
}

const saveAsTemplate = async () => {
  if (!generatedForm.value) return
  try {
    const res = await fetch('/api/v1/templates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(generatedForm.value)
    })
    const data = await res.json()
    if (data.status === 'success') {
      showToast("Template saved successfully!", "success")
    } else {
      showToast("Failed to save template: " + data.detail, "error")
    }
  } catch (err) {
    console.error(err)
    alert("Error saving template")
  }
}

const deleteTemplate = async (id) => {
  if (!confirm("Are you sure you want to delete this template?")) return
  try {
    const res = await fetch(`/api/v1/templates/${id}`, { method: 'DELETE' })
    if (res.ok) {
      savedTemplates.value = savedTemplates.value.filter(t => t.id !== id)
    }
  } catch (err) {
    console.error(err)
  }
}

const useTemplate = (template) => {
  if (generatedForm.value && !confirm("Warning: You have an active form on the canvas. Loading a template will overwrite your current work. Proceed?")) {
    return
  }
  
  // Constraint 2: Deep copy, strip _id, and regenerate _fid
  const copy = JSON.parse(JSON.stringify(template))
  delete copy.id
  delete copy._id
  
  if (copy.sections && Array.isArray(copy.sections)) {
    copy.sections.forEach(sec => {
      if (sec.fields && Array.isArray(sec.fields)) {
        sec.fields.forEach(f => {
          f._fid = _genFid()
        })
      }
    })
  }
  
  // Constraint 1: Clear Undo/Redo history
  formHistory.value = []
  historyIndex.value = -1
  
  generatedForm.value = copy
  currentTab.value = 'create'
  
  chatMessages.value.push({
    role: 'system',
    content: `Template "${template.title}" has been loaded onto the canvas.`
  })
}

watch(currentTab, (newTab) => {
  if (newTab === 'directory' || newTab === 'dashboard') {
    fetchForms()
  }
  if (newTab === 'dashboard') {
    fetchDashboardResponses()
  }
  if (newTab === 'templates') {
    fetchTemplates()
  }
})

onMounted(() => {
  fetchForms()
})

// ==========================================
//  AI Quick Tweaker: Edit Form Logic
// ==========================================
const openEditModal = (sIdx, fIdx, field) => {
  editingField.value = { sIdx, fIdx }
  editModalLabel.value = field.label || ''
  editModalPlaceholder.value = field.placeholder || ''
  editModalType.value = field.type || 'text'
  editModalOptionsText.value = (field.options || []).join(', ')
  editModalRequired.value = field.required || false
  editModalWidth.value = field.width || 'full'
  editModalConditionField.value = field.condition_field || ''
  editModalConditionValue.value = field.condition_value || ''
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingField.value = null
}

const saveFieldEdit = async () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const field = generatedForm.value.sections[sIdx].fields[fIdx]
  
  field.label = editModalLabel.value
  field.placeholder = editModalPlaceholder.value
  
  if (editModalType.value === 'master_data') {
    field.type = 'select'
    try {
      const res = await fetch(`/api/v1/master-data/${editModalMasterCategory.value}`)
      const data = await res.json()
      if (data.status === 'success') {
        field.options = data.data
      }
    } catch (e) {
      console.error("Failed to fetch master data", e)
    }
  } else {
    field.type = editModalType.value
    if (['select', 'radio', 'checkbox'].includes(field.type)) {
      field.options = editModalOptionsText.value.split(',').map(s => s.trim()).filter(s => s)
    }
  }
  
  field.required = editModalRequired.value
  field.width = editModalWidth.value
  field.condition_field = editModalConditionField.value || null
  field.condition_value = editModalConditionValue.value || null
  
  closeEditModal()
}


const addFieldBefore = () => {
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
}

const formatDate = (dateString) => {
  if (!dateString) return '';
  const d = new Date(dateString);
  const datePart = d.toLocaleDateString('en-US');
  const timePart = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }).replace(':', '.');
  return ` ${datePart}  ${timePart}`;
}

const addFieldAfterInline = (sIdx, fIdx) => {
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
}

const deleteFieldInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  if (!confirm('ยืนยันการลบ Field นี้?')) return;
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1);
}

const deleteField = () => {
  if (!editingField.value || !generatedForm.value) return
  if (!confirm('Are you sure you want to delete this field?')) return
  const { sIdx, fIdx } = editingField.value
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1)
  closeEditModal()
}


// ==========================================
//  Phase 4: Share & Embed System
// ==========================================
const isShareModalOpen = ref(false)
const shareActiveTab = ref('link')  // 'link' | 'embed'
const copyLinkStatus = ref('idle')   // 'idle' | 'copied'
const copyEmbedStatus = ref('idle')  // 'idle' | 'copied'

const shareFormUrl = computed(() => {
  if (!generatedForm.value) return ''
  const id = generatedForm.value.id || generatedForm.value._aid || 'preview'
  return `${window.location.origin}/f/${id}`
})

const shareEmbedCode = computed(() => {
  const url = shareFormUrl.value
  return `<iframe src="${url}" width="100%" height="600px" style="border:none; border-radius:12px;" loading="lazy" title="${generatedForm.value?.title || 'Form'}"></iframe>`
})

const openShareModal = () => {
  if (!generatedForm.value) return
  shareActiveTab.value = 'link'
  copyLinkStatus.value = 'idle'
  copyEmbedStatus.value = 'idle'
  isShareModalOpen.value = true
}

const closeShareModal = () => {
  isShareModalOpen.value = false
}

const copyToClipboard = async (text, type) => {
  try {
    await navigator.clipboard.writeText(text)
    if (type === 'link') {
      copyLinkStatus.value = 'copied'
      setTimeout(() => { copyLinkStatus.value = 'idle' }, 2000)
    } else {
      copyEmbedStatus.value = 'copied'
      setTimeout(() => { copyEmbedStatus.value = 'idle' }, 2000)
    }
  } catch (err) {
    // Fallback for older browsers
    const el = document.createElement('textarea')
    el.value = text
    el.style.position = 'fixed'
    el.style.opacity = '0'
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
    if (type === 'link') {
      copyLinkStatus.value = 'copied'
      setTimeout(() => { copyLinkStatus.value = 'idle' }, 2000)
    } else {
      copyEmbedStatus.value = 'copied'
      setTimeout(() => { copyEmbedStatus.value = 'idle' }, 2000)
    }
  }
}

</script>

<template>
  <div class="app-layout">
    <aside class="sidebar-nav">
      <div class="brand-zone">
        <div class="brand-logo ai-glow">✨</div>
        <div>
          <h2 class="brand-title gradient-text">Dynamic Form</h2>
          <div class="brand-sub">AI Generator</div>
        </div>
      </div>
      <div class="menu-label">MENU</div>
      <nav class="nav-links">
        <a href="#" class="nav-item" :class="{ active: currentTab === 'create' }" @click.prevent="currentTab = 'create'">
          <span class="nav-icon">✨</span> Create Form
        </a>
        <a href="#" class="nav-item" :class="{ active: currentTab === 'directory' }" @click.prevent="currentTab = 'directory'">
          <span class="nav-icon">📁</span> Directory
        </a>
        <a href="#" class="nav-item" :class="{ active: currentTab === 'templates' }" @click.prevent="currentTab = 'templates'">
          <span class="nav-icon">📂</span> Templates
        </a>
        <a href="#" class="nav-item" :class="{ active: currentTab === 'dashboard' }" @click.prevent="currentTab = 'dashboard'">
          <span class="nav-icon">📊</span> Dashboard
        </a>
      </nav>
    </aside>

    <main class="workspace-container">
      <header class="global-header">
        <div class="breadcrumb">
          <span class="path-parent">Workspace</span> / 
          <span class="path-current">{{ currentTab === 'create' ? 'Create Form' : (currentTab === 'directory' ? 'Form Directory' : (currentTab === 'templates' ? 'Templates Library' : 'Dashboard')) }}</span>
        </div>
      </header>
      
      <!-- CREATE FORM TAB: Premium 3-Column Layout -->
      <div class="workspace-grid create-premium-layout" v-show="currentTab === 'create'">

        <!-- ======== LEFT: Input Methods Panel ======== -->
        <div class="create-panel-card custom-scrollbar">
          <div class="create-panel-header">
            <div class="create-panel-title">
              <div class="create-panel-icon-wrap">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="6" height="6" rx="1"/><rect x="9" y="3" width="6" height="6" rx="1"/><rect x="16" y="3" width="6" height="6" rx="1"/><rect x="2" y="10" width="6" height="6" rx="1"/><rect x="9" y="10" width="6" height="6" rx="1"/><rect x="16" y="10" width="6" height="6" rx="1"/></svg>
              </div>
              <span>Input Methods</span>
            </div>
            <p class="create-panel-sub">Choose how to generate your form</p>
          </div>

          <!-- 2-Column 3D Grid of all Input Methods -->
          <div class="input-methods-grid">
            <div
              v-for="type in inputTypes"
              :key="type.value"
              class="input-method-card"
              :class="{ 'input-method-card--active': selectedInputType === type.value }"
              @click="selectFunction(type.value)"
            >
              <div class="input-method-icon-wrap">
                <span class="input-method-icon">{{ type.icon }}</span>
              </div>
              <span class="input-method-label">{{ type.label }}</span>
              <div v-if="selectedInputType === type.value" class="input-method-check">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </div>
          </div>
        </div>

        <!-- ======== MIDDLE: Chat / Control Panel ======== -->
        <div class="create-panel-card create-chat-panel">
          <!-- Active Mode Banner -->
          <div class="create-active-banner">
            <div class="create-active-left">
              <span class="create-pulse-dot"></span>
              <span class="create-active-text">Active: <strong>{{ activeFunction?.label }}</strong></span>
            </div>
            <div class="create-banner-actions">
              <button @click="undoHistory" :disabled="historyIndex <= 0" class="create-btn-ghost" :style="{ opacity: historyIndex <= 0 ? 0.4 : 1 }" title="Undo">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
                Undo
              </button>
              <button @click="redoHistory" :disabled="historyIndex >= formHistory.length - 1" class="create-btn-ghost" :style="{ opacity: historyIndex >= formHistory.length - 1 ? 0.4 : 1 }" title="Redo">
                Redo
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13"/></svg>
              </button>
              <button @click="resetChat" class="create-btn-ghost create-btn-ghost--danger" title="Clear">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                Reset
              </button>
            </div>
          </div>

          <!-- Chat Feed -->
          <div class="create-chat-feed custom-scrollbar">
            <div v-if="chatMessages.length === 0" class="create-chat-empty">
              <div class="create-chat-empty-icon">✨</div>
              <p>Start generating your form by selecting an input method and typing a prompt below.</p>
            </div>
            <div v-for="(msg, i) in chatMessages" :key="i" class="create-msg-row" :class="'create-msg-row--' + msg.sender">
              <div class="create-msg-avatar">{{ msg.sender === 'ai' ? '🤖' : '👤' }}</div>
              <div class="create-msg-body">
                <div v-if="msg.fileName || msg.functionLabel" class="create-msg-meta">
                  <span v-if="msg.functionLabel" class="create-meta-tag create-meta-tag--fn">{{ msg.functionLabel }}</span>
                  <span v-if="msg.fileName" class="create-meta-tag create-meta-tag--file">📎 {{ msg.fileName }}</span>
                </div>
                <div class="create-msg-text">{{ msg.text }}</div>
              </div>
            </div>
            <div v-if="loading" class="create-msg-row create-msg-row--ai">
              <div class="create-msg-avatar create-msg-avatar--sparkle">✨</div>
              <div class="create-msg-body">
                <div class="create-msg-text create-msg-thinking">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Cockpit -->
          <div class="create-input-cockpit">
            <!-- File Upload Tray -->
            <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" class="create-upload-tray">
              <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
              <div v-if="!selectedFile" class="create-dropzone" @click="$refs.fileInput.click()">
                <span class="create-dropzone-icon">📤</span>
                <span class="create-dropzone-text">Click to upload <strong>{{ activeFunction.hint }}</strong></span>
              </div>
              <div v-else class="create-file-badge">
                <span class="create-file-icon">📎</span>
                <div class="create-file-meta">
                  <div class="create-file-name">{{ selectedFile.name }}</div>
                  <div class="create-file-size">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                </div>
                <button class="create-file-remove" @click="clearFile">×</button>
              </div>
            </div>

            <!-- Prompt Textarea -->
            <textarea
              v-model="textPrompt"
              :disabled="loading"
              class="create-textarea custom-scrollbar"
              placeholder="Describe your form in detail... (Ctrl+Enter to send)"
              @keyup.ctrl.enter="sendCombinedCommand"
            ></textarea>

            <!-- Footer Actions -->
            <div class="create-cockpit-footer">
              <span class="create-keyboard-tip">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M8 2v4M16 2v4"/></svg>
                Ctrl + Enter to send
              </span>
              <div class="create-footer-btns">
                <input type="file" ref="chatFileInput" @change="handleChatFile" accept="image/*" hidden />
                <button class="create-btn-attach" @click="chatFileInput.click()" :disabled="loading" title="Attach Image">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                </button>
                <button class="create-btn-send" :disabled="loading" @click="sendCombinedCommand">
                  <span v-if="!loading" style="display:flex;align-items:center;gap:6px;">
                    Send
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                  </span>
                  <span v-else style="display:flex;align-items:center;gap:6px;">
                    <svg class="create-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                    Generating...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>


        <div class="preview-canvas-column" :class="{ 'fullscreen-mode': isFullscreen }">
          <div class="canvas-header-panel">
            <div class="canvas-badge-row">
              <div style="display: flex; gap: 12px; align-items: center;">
                <div class="canvas-badge">
                  <span>🎨</span> AI Canvas
                </div>
                <div class="device-toggles" style="display: flex; gap: 4px; background: #f1f5f9; padding: 4px; border-radius: 8px;">
                  <button @click="deviceMode = 'desktop'" :style="deviceMode === 'desktop' ? 'background: white; box-shadow: 0 1px 2px rgba(0,0,0,0.1); color: #0f172a;' : 'color: #64748b;'" style="border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; transition: all 0.2s;" title="Desktop View">🖥️</button>
                  <button @click="deviceMode = 'tablet'" :style="deviceMode === 'tablet' ? 'background: white; box-shadow: 0 1px 2px rgba(0,0,0,0.1); color: #0f172a;' : 'color: #64748b;'" style="border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; transition: all 0.2s;" title="Tablet View">📱</button>
                  <button @click="deviceMode = 'mobile'" :style="deviceMode === 'mobile' ? 'background: white; box-shadow: 0 1px 2px rgba(0,0,0,0.1); color: #0f172a;' : 'color: #64748b;'" style="border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; transition: all 0.2s;" title="Mobile View">📱</button>
                </div>
              </div>
              <div style="display: flex; gap: 8px;">
                <button class="btn-fullscreen-toggle" @click="toggleFullscreen" :title="isFullscreen ? 'Exit Full Screen' : 'Full Screen'">
                  {{ isFullscreen ? '🗗' : '🖵' }}
                </button>
                <button class="btn-export-vue" :disabled="!generatedForm" @click="exportVueComponent()">Export .vue</button>
                <button class="btn-share" :disabled="!generatedForm" @click="openShareModal">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                  Share
                </button>
              </div>
            </div>
            <div class="theme-prompt-box">
              <div class="theme-prompt-row">
                <input type="text" v-model="themePrompt" class="theme-prompt-input" placeholder="e.g. Cyberpunk, Minimalist Light, Ocean Blue" @keyup.enter="requestAiTheme" />
                <button class="btn-theme-generate" :disabled="themeLoading || !generatedForm" @click="requestAiTheme">
                  {{ themeLoading ? 'Styling...' : '✨ Style' }}
                </button>
              </div>
            </div>
          </div>

          <div class="canvas-preview-wrapper custom-scrollbar" :style="generatedForm?.theme?.bg_color ? `background-color: ${generatedForm.theme.bg_color}` : ''">
            <!-- Premium Animated Empty State -->
            <div v-if="!generatedForm" class="create-empty-state">
              <!-- Animated background blobs -->
              <div class="create-blob create-blob--purple"></div>
              <div class="create-blob create-blob--indigo"></div>
              <div class="create-blob create-blob--violet"></div>
              <!-- Empty state card -->
              <div class="create-empty-card">
                <div class="create-empty-icon-wrap">
                  <div class="create-empty-icon-float">
                    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="url(#grad1)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
                      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                      <line x1="10" y1="9" x2="8" y2="9"/>
                    </svg>
                  </div>
                </div>
                <h3 class="create-empty-title">No Form Generated Yet</h3>
                <p class="create-empty-sub">Select an input method on the left, then describe your form below to let AI generate it for you.</p>
                <div class="create-empty-steps">
                  <div class="create-empty-step">
                    <div class="create-empty-step-num">1</div>
                    <span>Choose an input method</span>
                  </div>
                  <div class="create-empty-step-divider"></div>
                  <div class="create-empty-step">
                    <div class="create-empty-step-num">2</div>
                    <span>Describe your form</span>
                  </div>
                  <div class="create-empty-step-divider"></div>
                  <div class="create-empty-step">
                    <div class="create-empty-step-num">3</div>
                    <span>AI generates it ✨</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="form-card animate-fade" :style="[
              `--bg-color: ${generatedForm?.theme?.bg_color || '#f8fafc'}; --card-bg: ${generatedForm?.theme?.card_bg || '#ffffff'}; --text-color: ${generatedForm?.theme?.text_color || '#0f172a'}; --theme-color: ${generatedForm?.theme_color || '#4f46e5'}; --border-color: ${generatedForm?.theme?.border_color || '#e2e8f0'}; --border-radius: ${generatedForm?.theme?.border_radius || '20px'}; --input-bg: ${generatedForm?.theme?.input_bg || '#f8fafc'}; --input-text: ${generatedForm?.theme?.input_text || '#334155'}; --label-color: ${generatedForm?.theme?.label_color || '#475569'}`,
              {
                margin: '0 auto',
                transition: 'max-width 0.3s ease',
                maxWidth: deviceMode === 'desktop' ? '100%' : (deviceMode === 'tablet' ? '768px' : '375px')
              }
            ]">
                            <div class="form-header-container" style="position: relative; display: flex; flex-direction: column; gap: 16px; min-height: 120px;" :class="{ 'dragging': isDraggingLogo }">
                
                <!-- Drop Zones Indicators (visible when dragging) -->
                <div v-if="isDraggingLogo" class="drop-zone top-zone" :class="{ active: hoverZone === 'top' }" style="position: absolute; top: -10px; left: 0; right: 0; height: 80px; border: 2px dashed #60a5fa; box-shadow: 0 0 10px rgba(96, 165, 250, 0.2); background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>
                <div v-if="isDraggingLogo" class="drop-zone left-zone" :class="{ active: hoverZone === 'left' }" style="position: absolute; top: 60px; left: -10px; width: 140px; bottom: -10px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>
                <div v-if="isDraggingLogo" class="drop-zone right-zone" :class="{ active: hoverZone === 'right' }" style="position: absolute; top: 60px; right: -10px; width: 140px; bottom: -10px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>

                <!-- Ghost Logo (Follows cursor) -->
                <div v-if="isDraggingLogo" class="form-logo-ghost" :style="{ position: 'fixed', left: ghostPos.x + 'px', top: ghostPos.y + 'px', zIndex: 9999, opacity: 0.8, pointerEvents: 'none', width: logoSize + 'px', height: logoSize + 'px', border: '2px dashed #38bdf8', borderRadius: '12px', background: '#f8fafc' }">
                   <div style="display: flex; height: 100%; align-items: center; justify-content: center; color: #38bdf8;">
                     <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Moving
                   </div>
                </div>

                <!-- Top Logo Area -->
                <div v-show="logoLayout === 'top'" class="logo-area-top" :style="{ opacity: isDraggingLogo ? 0.3 : 1, display: 'flex', justifyContent: logoAlign === 'center' ? 'center' : 'flex-start', width: '100%', position: 'relative' }">
                  <!-- Toolbar -->
                  <div class="logo-toolbar" v-if="generatedForm?.theme?.logo_url" style="position: absolute; top: -45px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); display: flex; gap: 4px; padding: 4px; z-index: 50; transition: opacity 0.2s;" :style="{ opacity: showLogoToolbar ? 1 : 0, pointerEvents: showLogoToolbar ? 'auto' : 'none', left: logoAlign === 'center' ? '50%' : '0', transform: logoAlign === 'center' ? 'translateX(-50%)' : 'none' }">
                    <button @click="logoAlign = 'left'" :style="logoAlign === 'left' ? 'background: #f1f5f9; color: #0f172a;' : 'color: #64748b;'" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer;" title="Align Left"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="21" y1="6" x2="3" y2="6"/><line x1="15" y1="12" x2="3" y2="12"/><line x1="17" y1="18" x2="3" y2="18"/></svg></button>
                    <button @click="logoAlign = 'center'" :style="logoAlign === 'center' ? 'background: #f1f5f9; color: #0f172a;' : 'color: #64748b;'" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer;" title="Align Center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="21" y1="6" x2="3" y2="6"/><line x1="19" y1="12" x2="5" y2="12"/><line x1="21" y1="18" x2="3" y2="18"/></svg></button>
                    <div style="width: 1px; background: #e2e8f0; margin: 4px;"></div>
                    <button @click="removeLogo" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer; color: #ef4444;" title="Remove Logo"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
                  </div>
                  
                  <div class="form-logo-widget" @mouseenter="showLogoToolbar = true" @mouseleave="showLogoToolbar = false" @mousedown="startLogoDrag" :style="{ width: logoSize + 'px', height: logoSize + 'px' }" style="position: relative; border: 2px dashed transparent; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0; transition: border-color 0.2s;" onmouseover="this.style.borderColor='#cbd5e1'" onmouseout="this.style.borderColor='transparent'">
                    
                    <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px; pointer-events: none;" />
                    
                    <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; pointer-events: none; border: 2px dashed #cbd5e1; border-radius: 12px; width: 100%; height: 100%; justify-content: center; background: #f8fafc;">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      <span style="font-size: 11px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload Logo</span>
                    </div>
                    
                    <!-- Upload overlay triggers on click -->
                    <div v-if="!generatedForm?.theme?.logo_url" class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; cursor: pointer; z-index: 15;"></div>
                    <div v-else class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white; z-index: 15; border-radius: 12px;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                    </div>

                    <!-- Custom Resize Handle -->
                    <div @mousedown="startLogoResize" style="position: absolute; bottom: 0; right: 0; width: 16px; height: 16px; cursor: nwse-resize; z-index: 20; display: flex; align-items: flex-end; justify-content: flex-end; padding: 4px; background: transparent;" title="Resize logo">
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="3" stroke-linecap="round"><polyline points="21 15 21 21 15 21"/><line x1="21" y1="21" x2="15" y2="15"/><polyline points="9 21 3 21 3 15"/><line x1="3" y1="21" x2="9" y2="15"/></svg>
                    </div>
                  </div>
                </div>

                <header class="form-header" :style="{ display: 'flex', flexDirection: logoLayout === 'right' ? 'row-reverse' : 'row', alignItems: 'flex-start', gap: '24px', position: 'relative', textAlign: 'left', width: '100%', opacity: isDraggingLogo ? 0.5 : 1 }">
                  <!-- Side Logo Area -->
                  <div v-show="logoLayout === 'left' || logoLayout === 'right'" :style="{ opacity: isDraggingLogo ? 0.3 : 1 }" class="logo-area-side" style="position: relative;">
                    <!-- Toolbar -->
                    <div class="logo-toolbar" v-if="generatedForm?.theme?.logo_url" style="position: absolute; top: -45px; left: 50%; transform: translateX(-50%); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); display: flex; gap: 4px; padding: 4px; z-index: 50; transition: opacity 0.2s;" :style="{ opacity: showLogoToolbar ? 1 : 0, pointerEvents: showLogoToolbar ? 'auto' : 'none' }">
                      <button @click="removeLogo" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer; color: #ef4444;" title="Remove Logo"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
                    </div>

                    <div class="form-logo-widget" @mouseenter="showLogoToolbar = true" @mouseleave="showLogoToolbar = false" @mousedown="startLogoDrag" :style="{ width: logoSize + 'px', height: logoSize + 'px' }" style="position: relative; border: 2px dashed transparent; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0; transition: border-color 0.2s;" onmouseover="this.style.borderColor='#cbd5e1'" onmouseout="this.style.borderColor='transparent'">
                      
                      <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px; pointer-events: none;" />
                      
                      <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; pointer-events: none; border: 2px dashed #cbd5e1; border-radius: 12px; width: 100%; height: 100%; justify-content: center; background: #f8fafc;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                        <span style="font-size: 11px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload Logo</span>
                      </div>
                      
                      <div v-if="!generatedForm?.theme?.logo_url" class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; cursor: pointer; z-index: 15;"></div>
                      <div v-else class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white; z-index: 15; border-radius: 12px;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      </div>

                      <!-- Custom Resize Handle -->
                      <div @mousedown="startLogoResize" style="position: absolute; bottom: 0; right: 0; width: 16px; height: 16px; cursor: nwse-resize; z-index: 20; display: flex; align-items: flex-end; justify-content: flex-end; padding: 4px; background: transparent;" title="Resize logo">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="3" stroke-linecap="round"><polyline points="21 15 21 21 15 21"/><line x1="21" y1="21" x2="15" y2="15"/><polyline points="9 21 3 21 3 15"/><line x1="3" y1="21" x2="9" y2="15"/></svg>
                      </div>
                    </div>
                  </div>
                  
                  <input type="file" ref="logoFileInput" @change="handleLogoUpload" accept="image/*" hidden />
                  
                  <div class="form-title-section" style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
                    <input v-model="generatedForm.title" class="form-title-input" placeholder="Form Title" style="text-align: left; font-size: 28px; padding-left: 0; width: 100%; box-sizing: border-box;" />
                    <textarea v-model="generatedForm.description" class="form-description-input" placeholder="Form Description" style="text-align: left; min-height: 60px; padding-left: 0; width: 100%; box-sizing: border-box;"></textarea>
                  </div>
                </header>
              </div>
              <div class="form-element">
                <draggable v-model="generatedForm.sections" handle=".section-drag-handle" item-key="title" animation="200">
                  <template #item="{ element: section, index: sIdx }">
                    <fieldset class="form-section">
                      <legend class="section-legend" style="display: flex; align-items: center; gap: 8px;">
                        <span class="section-drag-handle" style="cursor: grab; color: #cbd5e1; display: inline-flex; padding: 4px;" title="Drag to reorder section">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                        </span>
                        {{ section.title }}
                      </legend>
                      <p v-if="section.description" class="section-desc">{{ section.description }}</p>
                      
                      <draggable v-model="section.fields" handle=".field-drag-handle" item-key="label" class="fields-grid" animation="200">
                        <template #item="{ element: field, index: fIdx }">
                          <div class="field-item-box" :style="field.width === 'half' ? 'grid-column: span 1' : 'grid-column: span 2'">
                            <div class="field-actions-overlay">
                              <div class="field-toolbar">
                                <button class="toolbar-btn field-drag-handle" style="cursor: grab;" title="Drag to reorder field">
                                  <span class="icon">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                                  </span>
                                </button>
                                <button class="toolbar-btn btn-edit" @click.stop="openEditModal(sIdx, fIdx, field)" title="Edit Field">
                                  <span class="icon">✏️</span> <span class="lbl">แก้ไข</span>
                                </button>
                                <button class="toolbar-btn btn-add" @click.stop="addFieldAfterInline(sIdx, fIdx)" title="Add Field Below">
                                  <span class="icon">✏️</span> <span class="lbl">แก้ไข</span>
                                </button>
                                <button class="toolbar-btn btn-delete-inline" @click.stop="deleteFieldInline(sIdx, fIdx)" title="Delete Field">
                                  <span class="icon">🗑️</span> <span class="lbl">ลบ</span>
                                </button>
                              </div>
                            </div>
                            <label class="field-label">{{ field.label }}<span v-if="field.required" class="required-star">*</span></label>
                            <input v-if="!['select', 'textarea', 'checkbox', 'radio'].includes(field.type)" :type="field.type || 'text'" class="field-input" :placeholder="field.placeholder" @focus="sendAnalyticsLog(field._fid, 'focus', field.label)" @blur="sendAnalyticsLog(field._fid, 'blur', field.label, $event.target.value)" />
                            <textarea v-else-if="field.type === 'textarea'" class="field-input textarea-input" :placeholder="field.placeholder" @focus="sendAnalyticsLog(field._fid, 'focus', field.label)" @blur="sendAnalyticsLog(field._fid, 'blur', field.label, $event.target.value)"></textarea>
                            <select v-else-if="field.type === 'select'" class="field-input" @focus="sendAnalyticsLog(field._fid, 'focus', field.label)" @change="sendAnalyticsLog(field._fid, 'blur', field.label, $event.target.value)">
                              <option value="">{{ field.placeholder || 'Select...' }}</option>
                              <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                            </select>
                            <div v-else-if="['checkbox', 'radio'].includes(field.type)" class="checkbox-group">
                              <label v-for="opt in field.options" :key="opt" class="checkbox-option-label">
                                <input :type="field.type" @change="sendAnalyticsLog(field._fid, 'blur', field.label, opt)" /> {{ opt }}
                              </label>
                            </div>
                          </div>
                        </template>
                      </draggable>
                    </fieldset>
                  </template>
                </draggable>
              </div>
            </div>
          </div>

          <div class="canvas-action-footer">
            <div class="form-action-buttons-row">
              <button class="btn-clear-form" :disabled="!generatedForm" @click="clearFormResponses">Clear Form</button>
              <button class="btn-clear-form" style="color: #6366f1; border-color: #cbd5e1;" :disabled="!generatedForm" @click="saveAsTemplate">Save as Template</button>
              <button class="btn-deploy-form" :disabled="!generatedForm || deploying" @click="deployForm">
                {{ deploying ? 'Deploying...' : 'Deploy to MongoDB' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Phase 3: Templates Tab -->
      <!-- TEMPLATES GALLERY — Stitch Premium Layout -->
      <div class="templates-view-container" v-show="currentTab === 'templates'">
        <div class="tpl-main">
          <div class="tpl-content-wrapper">

            <!-- Header & AI Search -->
            <header class="tpl-header">
              <div>
                <h1 class="tpl-title">Template Gallery</h1>
                <p class="tpl-subtitle">Start with a pre-built structure or tell FormAI exactly what you need.</p>
              </div>
              <!-- AI Search Bar -->
              <div class="tpl-search-bar">
                <span class="material-symbols-outlined tpl-search-icon">auto_awesome</span>
                <input v-model="templateSearchQuery" class="tpl-search-input" placeholder="Search templates by type, industry, or use case..." type="text" />
              </div>
              <!-- Category Pills -->
              <div class="tpl-categories scrollbar-hide">
                <button class="tpl-cat-pill tpl-cat-pill--active">All Templates</button>
                <button class="tpl-cat-pill">Feedback</button>
                <button class="tpl-cat-pill">Registration</button>
                <button class="tpl-cat-pill">Quizzes</button>
                <button class="tpl-cat-pill">E-commerce</button>
              </div>
            </header>

            <!-- Loading -->
            <div v-if="loadingTemplates" class="tpl-state-center">
              <svg class="dir-spinner" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              Loading templates...
            </div>

            <!-- Empty State -->
            <div v-else-if="savedTemplates.length === 0" class="tpl-state-center">
              <div class="tpl-empty-icon">
                <span class="material-symbols-outlined" style="font-size: 32px; text-transform: none;">folder_open</span>
              </div>
              <p class="tpl-empty-text">No templates saved yet.</p>
              <p class="tpl-empty-sub">Generate a form and click "Save as Template" to get started.</p>
            </div>

            <!-- Template Grid -->
            <section v-else class="tpl-grid">
              <div
                v-for="template in savedTemplates"
                :key="template.id"
                class="glass-card rounded-[1.5rem] overflow-hidden group transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl cursor-pointer"
              >
                <!-- Card Hero: Dimensional Colored Icon Area -->
                <div
                  class="tpl-card-hero"
                  :style="{ background: `linear-gradient(135deg, ${getTemplateTheme(template).bgFrom}, ${getTemplateTheme(template).bgTo})` }"
                >
                  <!-- Dimensional Icon Container -->
                  <div class="tpl-card-icon-wrap" :style="{ background: 'rgba(255,255,255,0.65)', boxShadow: `0 8px 24px -4px ${getTemplateTheme(template).iconColor}30` }">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      :viewBox="getTemplateTheme(template).viewBox"
                      stroke-width="1.5"
                      :stroke="getTemplateTheme(template).iconColor"
                      class="w-8 h-8"
                      v-html="getTemplateTheme(template).svg"
                    ></svg>
                  </div>
                  <!-- Hover Overlay -->
                  <div class="tpl-overlay">
                    <button class="tpl-overlay-btn btn-glow" @click.stop="useTemplate(template)">
                      Use this Template
                      <span class="material-symbols-outlined" style="font-size: 18px; text-transform: none;">arrow_forward</span>
                    </button>
                  </div>
                </div>

                <!-- Card Body -->
                <div class="tpl-card-body">
                  <div class="tpl-card-top">
                    <h3 class="tpl-card-title group-hover:text-indigo-700 transition-colors">{{ template.title }}</h3>
                    <span
                      class="tpl-card-badge"
                      :class="[getTemplateTheme(template).pillBg, getTemplateTheme(template).pillText]"
                      style="border: none;"
                    >
                      {{ template.input_type_used ? template.input_type_used.replace('_', ' ') : 'Template' }}
                    </span>
                  </div>
                  <p class="tpl-card-desc">{{ template.description || 'No description provided.' }}</p>
                  <div class="tpl-card-footer">
                    <span class="tpl-card-date">
                      <span class="material-symbols-outlined" style="font-size: 13px; text-transform: none; opacity: 0.6;">schedule</span>
                      {{ formatDate(template.created_at) }}
                    </span>
                    <button class="tpl-delete-btn" @click.stop="deleteTemplate(template.id)" title="Delete template">
                      <span class="material-symbols-outlined" style="font-size: 18px; text-transform: none;">delete</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Blank Canvas CTA Card -->
              <div class="glass-card tpl-blank-card rounded-[1.5rem] group" @click="currentTab = 'create'">
                <div class="tpl-blank-icon-wrap group-hover:bg-indigo-50/80 transition-colors">
                  <span class="material-symbols-outlined tpl-blank-icon group-hover:text-indigo-600 transition-colors">add</span>
                </div>
                <h3 class="tpl-blank-title group-hover:text-indigo-700 transition-colors">Blank Canvas</h3>
                <p class="tpl-blank-sub">Start from scratch and use AI to build exactly what you need block by block.</p>
              </div>
            </section>

          </div>
        </div>
      </div>

      <!-- FORM DIRECTORY — Stitch Premium Grid -->
      <div class="directory-view-container" v-show="currentTab === 'directory'">
        <div class="dir-main">
          <div class="dir-content-wrapper">

            <!-- Page Header & Actions -->
            <div class="dir-header-row">
              <div>
                <h1 class="dir-title">Form Directory</h1>
                <p class="dir-subtitle">Manage and organize all your AI-generated and manual forms.</p>
              </div>

              <div class="dir-header-actions">
                <!-- Search Bar -->
                <div class="dir-search-bar">
                  <svg class="dir-search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                  <input type="text" v-model="searchQuery" placeholder="Search forms..." class="dir-search-input" />
                </div>
                <!-- Glow CTA -->
                <button class="dir-cta-btn btn-glow" @click="currentTab = 'templates'">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Create New Form
                </button>
              </div>
            </div>

            <!-- Filter Pills -->
            <div class="dir-filter-row scrollbar-hide">
              <button class="dir-filter-pill dir-filter-pill--active">All ({{ filteredDirectoryForms.length }})</button>
            </div>

            <!-- Loading -->
            <div v-if="loadingDirectory" class="dir-state-center">
              <svg class="dir-spinner" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span>Loading forms...</span>
            </div>

            <!-- Empty State -->
            <div v-else-if="filteredDirectoryForms.length === 0" class="dir-state-center">
              <div class="dir-empty-icon">
                <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
              </div>
              <p class="dir-empty-text">No forms found. Create your first form!</p>
            </div>

            <!-- Form Grid -->
            <div v-else class="dir-grid">
              <FormCard
                v-for="form in filteredDirectoryForms"
                :key="form._id"
                :form="form"
                @edit="() => openViewModal(form)"
                @duplicate="() => duplicateForm(form)"
                @delete="deleteSavedForm"
              />
            </div>

          </div>
        </div>
      </div>

      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
        <!-- Dashboard Header -->
        <div class="db-header">
          <div>
            <h2 class="db-title">Responses Viewer</h2>
            <p class="db-sub">View and manage form submissions</p>
          </div>
          <div class="db-status-badge" :class="mongoDbStatus === 'connected' ? 'db-ok' : 'db-err'">
            <span class="db-status-dot"></span>
            MongoDB {{ mongoDbStatus === 'connected' ? 'Connected' : 'Error' }}
          </div>
        </div>

        <!-- Form Selector -->
        <div v-if="dashboardFormOptions.length > 0" class="form-selector-row" style="margin-bottom: 24px; display: flex; align-items: center; gap: 12px; background: #ffffff; padding: 16px 24px; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <label class="form-selector-label" style="font-weight: 600; color: #475569; font-size: 0.95rem;"> Viewing responses for:</label>
          <select v-model="selectedDashboardFormId" class="form-selector-dropdown" style="padding: 10px 16px; border-radius: 10px; border: 1px solid #e2e8f0; outline: none; font-family: inherit; font-weight: 500; color: #0f172a; min-width: 250px; background-color: #f8fafc; cursor: pointer;">
            <option value="all">All Forms</option>
            <option v-for="opt in dashboardFormOptions" :key="opt.id" :value="opt.id">
              {{ opt.title }}
            </option>
          </select>
          <div style="flex: 1"></div>
          <button @click="exportToExcel" style="background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px;">
             Export to Excel
          </button>
        </div>

        <!-- KPI Row -->
        <div class="kpi-row">
          <div class="kpi-card kpi-accent-indigo">
            <div class="kpi-icon">📄</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ filteredResponses.length }}</div>
              <div class="kpi-label">Total Submissions</div>
            </div>
          </div>
          <div class="kpi-card kpi-accent-emerald">
            <div class="kpi-icon">✅</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ filteredResponses.filter(r => r.status === 'completed').length }}</div>
              <div class="kpi-label">Completed</div>
            </div>
          </div>
          <div class="kpi-card kpi-accent-amber">
            <div class="kpi-icon">⏳</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ filteredResponses.filter(r => r.status === 'partial').length }}</div>
              <div class="kpi-label">Partial</div>
            </div>
          </div>
        </div>

        <!-- Responses Table Panel -->
        <div class="analytics-panel responses-panel">
          <div class="panel-header">
            <div class="panel-title">
              <span class="panel-icon">📋</span>
              Recent Submissions
            </div>
            <p class="panel-sub">Showing latest mocked data before MongoDB integration</p>
          </div>

          <div v-if="filteredResponses.length === 0" class="analytics-empty">
            <div class="analytics-empty-icon">Inbox</div>
            <p class="analytics-empty-title">No submissions found</p>
            <p class="analytics-empty-sub">Share your form to start collecting responses.</p>
          </div>

          <div v-else class="responses-table-container">
            <table class="responses-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Respondent</th>
                  <th v-if="selectedDashboardFormId === 'all'">Form Details</th>
                  <th>Status</th>
                  <th>Answers Snapshot</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="res in filteredResponses" :key="res.id || res._id" class="response-row">
                  <td class="res-date">{{ new Date(res.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}</td>
                  <td class="res-email">{{ res.respondent_info?.email || res.respondent || 'Anonymous' }}</td>
                  <td v-if="selectedDashboardFormId === 'all'" class="res-form-id"><span class="badge-form">{{ res.form_title || getFormName(res.form_id) }} <span style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">| ID: {{ res.form_id }}</span></span></td>
                  <td>
                    <span class="status-pill status-completed">
                      {{ res.status || 'Completed' }}
                    </span>
                  </td>
                  <td class="res-answers">
                    <div class="answers-preview">
                      <span v-for="(val, key) in res.answers" :key="key" class="answer-chip">
                        <strong>{{ key }}:</strong> {{ val }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- View Form Modal -->
    <Transition name="fade">
      <div v-if="viewFormModal" class="editor-modal-overlay animate-fade" @click.self="closeViewModal">
        <div class="editor-modal-card" style="max-width: 420px; border-radius: 28px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); background: #ffffff;">
          <!-- Top Accent Bar -->
          <div :style="`height: 6px; width: 100%; background: ${viewFormModal.theme_color || '#6366f1'};`"></div>
          
          <div class="modal-header" style="border-bottom: none; padding: 24px 24px 0 24px; display: flex; justify-content: space-between; align-items: center;">
            <div style="width: 48px; height: 48px; border-radius: 16px; display: flex; align-items: center; justify-content: center;" :style="`background: ${(viewFormModal.theme_color || '#6366f1')}15; color: ${viewFormModal.theme_color || '#6366f1'}`">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <button class="btn-close-modal" @click="closeViewModal" style="background: #f1f5f9; border: none; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 1.2rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#e2e8f0'; this.style.color='#0f172a'" onmouseout="this.style.background='#f1f5f9'; this.style.color='#64748b'">×</button>
          </div>

          <div class="modal-body" style="padding: 20px 24px 32px 24px; text-align: left;">
            <h2 style="font-size: 1.4rem; color: #0f172a; margin-bottom: 32px; font-weight: 800; line-height: 1.35; letter-spacing: -0.01em;">{{ viewFormModal.title }}</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
              <!-- Open Fullscreen -->
              <a :href="`/f/${viewFormModal.id || viewFormModal._aid}`" target="_blank" style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 20px; padding: 20px 16px; text-decoration: none; color: #334155; font-weight: 600; font-size: 0.9rem; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.background='#f1f5f9'; this.style.borderColor='#cbd5e1'; this.style.transform='translateY(-2px)'" onmouseout="this.style.background='#f8fafc'; this.style.borderColor='#e2e8f0'; this.style.transform='translateY(0)'">
                <div style="background: #ffffff; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                </div>
                Open Live Form
              </a>

              <!-- Share Link -->
              <button @click="copyToClipboard(getShareLink(viewFormModal), 'link')" style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 20px; padding: 20px 16px; text-decoration: none; color: #334155; font-weight: 600; font-size: 0.9rem; transition: all 0.2s; cursor: pointer; font-family: inherit;" onmouseover="this.style.background='#f1f5f9'; this.style.borderColor='#cbd5e1'; this.style.transform='translateY(-2px)'" onmouseout="this.style.background='#f8fafc'; this.style.borderColor='#e2e8f0'; this.style.transform='translateY(0)'">
                <div style="background: #ffffff; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                </div>
                Copy Share Link
              </button>

              <!-- Duplicate Form -->
              <button @click="duplicateForm(viewFormModal)" style="grid-column: span 2; display: flex; align-items: center; justify-content: center; gap: 10px; background: #0f172a; color: #ffffff; border: none; border-radius: 20px; padding: 18px; font-weight: 600; font-size: 1rem; transition: all 0.2s; cursor: pointer; font-family: inherit; margin-top: 8px; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);" onmouseover="this.style.background='#1e293b'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 15px 30px -5px rgba(15, 23, 42, 0.3)'" onmouseout="this.style.background='#0f172a'; this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 25px -5px rgba(15, 23, 42, 0.25)'">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                Duplicate Form
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <!-- AI Quick Tweaker Modal -->
    <div v-if="showEditModal" class="editor-modal-overlay animate-fade">
      <div class="editor-modal-card">
        <div class="modal-header">
          <h3> AI Quick Tweaker</h3>
          <button class="btn-close-modal" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-input-group">
            <label>Field Label</label>
            <input type="text" v-model="editModalLabel" class="field-input" />
          </div>
          <div class="modal-input-group">
            <label>Placeholder / Hint</label>
            <input type="text" v-model="editModalPlaceholder" class="field-input" />
          </div>
          
          <div class="modal-input-group-row">
            <div class="modal-input-group" style="flex:1">
              <label>Input Type</label>
              <select v-model="editModalType" class="field-input">
                <option value="text">📝 Text (Short)</option>
                <option value="textarea">📝 Textarea (Long)</option>
                <option value="number"> Number</option>
                <option value="email"> Email</option>
                <option value="date"> Date</option>
                <option value="select"> Dropdown (Select)</option>
                <option value="radio"> Radio Options</option>
                <option value="checkbox">☑️ Checkbox Options</option>
                <option value="file">📎 File Upload</option>
              </select>
            </div>
            <div class="modal-input-group" style="flex:1">
              <label>Width</label>
              <select v-model="editModalWidth" class="field-input">
                <option value="full">Full Width (100%)</option>
                <option value="half">Half Width (50%)</option>
              </select>
            </div>
          </div>

          <div v-if="['select', 'radio', 'checkbox'].includes(editModalType)" class="modal-input-group">
            <label>Options (comma separated)</label>
            <input type="text" v-model="editModalOptionsText" class="field-input" placeholder="e.g. Option A, Option B, Option C" />
          </div>

          <div class="modal-input-group-row" style="align-items: center; gap: 12px; margin-top: 12px;">
            <input type="checkbox" id="req-check" v-model="editModalRequired" style="width: 18px; height: 18px; cursor:pointer;" />
            <label for="req-check" style="cursor:pointer; font-weight: 600;">Required Field (*)</label>
          </div>
          
          <div class="modal-conditional-zone" style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 8px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 8px; display: block;">Conditional Logic (Show if)</label>
            <div class="modal-input-group-row">
              <input type="text" v-model="editModalConditionField" class="field-input" placeholder="Depends on Field Name" style="flex:1" />
              <input type="text" v-model="editModalConditionValue" class="field-input" placeholder="Equals Value" style="flex:1" />
            </div>
          </div>
        </div>

        <div class="modal-footer-clean">
          <button class="btn-save-pill" @click="saveFieldEdit">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            Save Changes
          </button>
        </div>
      </div>
    </div>

    <!--  Phase 4: Share & Embed Modal -->
    <Transition name="share-modal">
      <div v-if="isShareModalOpen" class="share-modal-overlay" @click.self="closeShareModal">
        <div class="share-modal-card">

          <!-- Modal Header -->
          <div class="share-modal-header">
            <div class="share-modal-title-group">
              <div class="share-modal-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
              </div>
              <div>
                <h3 class="share-modal-title">Share Form</h3>
                <p class="share-modal-sub">{{ generatedForm?.title }}</p>
              </div>
            </div>
            <button class="share-modal-close" @click="closeShareModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- Tab Switcher -->
          <div class="share-tab-row">
            <button
              class="share-tab-btn"
              :class="{ 'share-tab-active': shareActiveTab === 'link' }"
              @click="shareActiveTab = 'link'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              Direct Link
            </button>
            <button
              class="share-tab-btn"
              :class="{ 'share-tab-active': shareActiveTab === 'embed' }"
              @click="shareActiveTab = 'embed'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              Embed Code
            </button>
          </div>

          <!-- Tab: Direct Link -->
          <div v-if="shareActiveTab === 'link'" class="share-section">
            <p class="share-section-desc">Anyone with this link can view and fill your form.</p>
            <div class="share-copy-row">
              <div class="share-url-display">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="share-url-icon"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                <span class="share-url-text">{{ shareFormUrl }}</span>
              </div>
              <button
                class="btn-copy"
                :class="{ 'btn-copy-success': copyLinkStatus === 'copied' }"
                @click="copyToClipboard(shareFormUrl, 'link')"
              >
                <svg v-if="copyLinkStatus === 'idle'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                {{ copyLinkStatus === 'copied' ? 'Copied!' : 'Copy' }}
              </button>
              <a :href="shareFormUrl" target="_blank" class="btn-copy" style="text-decoration: none; display: inline-flex; justify-content: center;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                Open 
              </a>
            </div>
            <div class="share-info-row">
              <div class="share-info-chip">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                This is a preview link. Deploy the form to MongoDB first to activate it.
              </div>
            </div>
          </div>

          <!-- Tab: Embed Code -->
          <div v-if="shareActiveTab === 'embed'" class="share-section">
            <p class="share-section-desc">Paste this snippet into any website to embed the form.</p>
            <div class="share-embed-box">
              <pre class="share-embed-code">{{ shareEmbedCode }}</pre>
            </div>
            <button
              class="btn-copy btn-copy-full"
              :class="{ 'btn-copy-success': copyEmbedStatus === 'copied' }"
              @click="copyToClipboard(shareEmbedCode, 'embed')"
            >
              <svg v-if="copyEmbedStatus === 'idle'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              {{ copyEmbedStatus === 'copied' ? 'Copied to Clipboard! ' : 'Copy Embed Code' }}
            </button>
            <div class="share-info-row">
              <div class="share-info-chip">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                Form must be deployed to MongoDB before embedding on a live site.
              </div>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-layout {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
  color: #0f172a;
}

.sidebar-nav {
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #f1f5f9;
  padding: 32px 24px;
  position: fixed;
  height: 100vh;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.brand-zone {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 36px;
  padding: 0 4px;
}

.brand-logo.ai-glow {
  background: linear-gradient(135deg, #4f46e5 0%, #c026d3 100%);
  color: #ffffff;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 20px;
  box-shadow: 0 4px 15px rgba(192, 38, 211, 0.25);
  transition: transform 0.2s ease;
}

.brand-logo.ai-glow:hover {
  transform: scale(1.05);
}

.brand-title.gradient-text {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -0.5px;
}

.brand-sub {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.menu-label {
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 700;
  color: #94a3b8;
  margin-bottom: 12px;
  letter-spacing: 1px;
  padding-left: 8px;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-item {
  padding: 12px 16px;
  color: #475569;
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-item:hover {
  background: #f8fafc;
  color: #0f172a;
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
  color: #4f46e5;
  font-weight: 700;
}

.workspace-container {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  min-height: 100vh;
}

.global-header {
  height: 72px;
  background: #ffffff;
  border-bottom: 1px solid #f1f5f9;
  padding: 0 32px;
  display: flex;
  align-items: center;
}

.breadcrumb {
  font-size: 13.5px;
  font-weight: 600;
  color: #64748b;
}

.path-parent {
  color: #64748b;
}

.path-current {
  color: #0f172a;
  font-weight: 700;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 280px 450px 1fr;
  gap: 24px;
  padding: 24px;
  height: calc(100vh - 72px);
  align-items: stretch;
}

/* 1. Functions Menu Column */
.functions-menu-column {
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.01);
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.column-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.column-header-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.column-header-sub {
  font-size: 12px;
  color: #64748b;
}

.functions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.function-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  background: #f8fafc;
}

.function-item:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}

.function-item.active {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.06) 0%, rgba(99, 102, 241, 0.06) 100%);
  border-color: rgba(79, 70, 229, 0.15);
  color: #4f46e5;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.04);
}

.func-icon {
  font-size: 16px;
}

.func-label {
  font-size: 13px;
}

/* 2. Unified Chat Column */
.unified-chat-column {
  background: #ffffff;
  border-radius: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.01);
}

.active-mode-banner {
  padding: 16px 20px;
  background: #ffffff;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.pulse-indicator {
  width: 8px;
  height: 8px;
  background: #4f46e5;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.mode-text {
  font-size: 12.5px;
  color: #475569;
}

.chat-display-feed {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #f8fafc;
}

.message-bubble-row {
  display: flex;
  gap: 12px;
  max-width: 90%;
  align-items: flex-start;
}

.message-bubble-row.ai {
  align-self: flex-start;
}

.message-bubble-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.sender-avatar {
  width: 32px;
  height: 32px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  flex-shrink: 0;
}

.message-bubble-row.user .sender-avatar {
  background: #e0f2fe;
  border-color: #bae6fd;
}

.message-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-text-body {
  background: #ffffff;
  border: 1px solid #f1f5f9;
  padding: 12px 16px;
  border-radius: 16px;
  border-top-left-radius: 2px;
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.message-bubble-row.user .message-text-body {
  background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
  color: #ffffff;
  border: none;
  border-radius: 16px;
  border-top-right-radius: 2px;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
}

.message-attachment-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 2px;
}

.meta-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 8px;
}

.function-tag {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.file-tag {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.thinking-state {
  color: #64748b;
  font-style: normal;
  background: #f1f5f9;
  border-color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sparkle-icon {
  animation: spin 2s linear infinite;
  display: inline-block;
}

.unified-input-cockpit {
  padding: 20px;
  background: #ffffff;
  border-top: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
}

.integrated-upload-tray {
  background: #f8fafc;
  border: 1.5px dashed #e2e8f0;
  border-radius: 12px;
  padding: 8px 12px;
  transition: all 0.2s ease;
}

.mini-dropzone {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  justify-content: center;
  height: 38px;
}

.mini-upload-icon {
  font-size: 18px;
}

.mini-upload-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.integrated-upload-tray:hover {
  border-color: #4f46e5;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.02) 0%, rgba(59, 130, 246, 0.02) 100%);
}

.attached-file-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border: 1.5px solid #bfdbfe;
  padding: 8px 12px;
  border-radius: 10px;
}

.file-preview-icon {
  font-size: 16px;
}

.file-meta-info {
  flex: 1;
  overflow: hidden;
}

.file-name-string {
  font-size: 12px;
  font-weight: 700;
  color: #1e3a8a;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.file-size-string {
  font-size: 10px;
  color: #64748b;
}

.remove-file-action {
  background: none;
  border: none;
  color: #ef4444;
  font-weight: bold;
  cursor: pointer;
  padding: 0 4px;
  font-size: 14px;
}

.embedded-textarea {
  width: 100%;
  height: 72px;
  padding: 12px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13.5px;
  outline: none;
  resize: none;
  transition: all 0.2s ease;
  background: #f8fafc;
  color: #0f172a;
}

.embedded-textarea:focus {
  border-color: #4f46e5;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.05);
}

.cockpit-footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.keyboard-tip {
  font-size: 11.5px;
  color: #94a3b8;
}

.submit-combined-btn {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #ffffff;
  border: none;
  height: 42px;
  padding: 0 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
}

.submit-combined-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(15, 23, 42, 0.25);
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.submit-combined-btn:disabled {
  background: #cbd5e1;
  color: #94a3b8;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 3. Preview Canvas Column */
.preview-canvas-column {
  background: var(--bg-color, #f8fafc);
  border-radius: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.01);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.canvas-header-panel {
  padding: 20px 24px;
  background: var(--card-bg, #ffffff);
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.canvas-badge-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.canvas-badge {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  color: #38bdf8 !important;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 1px;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-export-vue {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
  transition: all 0.2s ease;
}

.btn-export-vue:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3) !important;
}

.theme-prompt-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
}

.theme-prompt-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.theme-prompt-input {
  flex: 1;
  height: 38px;
  padding: 0 12px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 12.5px;
  color: #334155;
  background-color: #ffffff;
  outline: none;
  transition: all 0.2s ease;
}

.theme-prompt-input:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.btn-theme-generate {
  background: linear-gradient(135deg, #4f46e5 0%, #c026d3 100%);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  padding: 0 16px;
  height: 38px;
  font-size: 12.5px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-theme-generate:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(79, 70, 229, 0.3);
}

.btn-theme-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-theme-reset {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-theme-reset:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.theme-preview-swatch {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
}

.swatch-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  display: inline-block;
}

.canvas-preview-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
  background-color: var(--bg-color, #f8fafc);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  transition: background-color 0.3s ease;
}

.empty-canvas-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px;
  height: 100%;
}

.empty-icon-box {
  width: 64px;
  height: 64px;
  background: #ffffff;
  border-radius: 20px;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  border: 1.5px dashed #e2e8f0;
}

.empty-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.empty-sub {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  max-width: 320px;
}

.form-card {
  width: 100%;
  max-width: 680px;
  background: var(--card-bg, #ffffff);
  border-radius: var(--border-radius, 20px);
  padding: 36px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color, #e2e8f0);
  transition: all 0.3s ease;
}

.form-header {
  margin-bottom: 28px;
  
}

.form-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-color, #0f172a);
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.form-title-input {
  width: 100%;
  text-align: center;
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-color, #0f172a);
  margin-bottom: 8px;
  background: transparent;
  border: 1px dashed transparent;
  outline: none;
  font-family: inherit;
  transition: all 0.2s;
  border-radius: 8px;
  padding: 4px;
}
.form-title-input:hover, .form-title-input:focus {
  border-color: rgba(0,0,0,0.1);
  background: rgba(255,255,255,0.3);
}

.form-description {
  font-size: 0.95rem;
  color: var(--text-color, #64748b);
  opacity: 0.85;
  line-height: 1.6;
  transition: all 0.3s ease;
}

.form-description-input {
  width: 100%;
  text-align: center;
  font-size: 0.95rem;
  color: var(--text-color, #64748b);
  opacity: 0.85;
  line-height: 1.6;
  background: transparent;
  border: 1px dashed transparent;
  outline: none;
  font-family: inherit;
  resize: vertical;
  min-height: 50px;
  transition: all 0.2s;
  border-radius: 8px;
  padding: 4px;
}
.form-description-input:hover, .form-description-input:focus {
  border-color: rgba(0,0,0,0.1);
  background: rgba(255,255,255,0.3);
}

.form-element {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--border-radius, 16px);
  padding: 24px;
  background-color: var(--card-bg, #ffffff);
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.section-legend {
  font-weight: 700;
  color: var(--theme-color, #4f46e5);
  font-size: 1.15rem;
  padding: 0 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.section-desc {
  font-size: 0.9rem;
  color: var(--text-color, #64748b);
  opacity: 0.8;
  margin-bottom: 16px;
  padding: 0 8px;
  transition: all 0.3s ease;
}

.fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.field-item-box {
  position: relative;
  border: 1.5px dashed transparent;
  border-radius: 12px;
  padding: 12px;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-item-box:hover {
  border-color: var(--theme-color, #4f46e5);
  background-color: rgba(79, 70, 229, 0.02);
}

.field-item-box:nth-child(odd):last-child {
  grid-column: span 2;
}

.field-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--label-color, #475569);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.required-star {
  color: #ef4444;
  margin-left: 2px;
}

.field-input {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid var(--border-color, #cbd5e1);
  border-radius: var(--border-radius, 10px);
  font-size: 0.95rem;
  color: var(--input-text, #334155);
  background-color: var(--input-bg, #f8fafc);
  transition: all 0.2s ease;
  outline: none;
}

.field-input:focus {
  background-color: var(--card-bg, #ffffff);
  border-color: var(--theme-color, #4f46e5);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.textarea-input {
  min-height: 100px;
  resize: vertical;
}

.checkbox-group, .radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 8px 0;
}

.checkbox-option-label, .radio-option-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  color: var(--text-color, #475569);
  cursor: pointer;
  transition: all 0.3s ease;
}

.checkbox-option-label input, .radio-option-label input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.field-actions-overlay {
  display: none;
  position: absolute;
  top: -12px;
  right: 12px;
  gap: 6px;
  z-index: 10;
}

.field-item-box:hover .field-actions-overlay {
  display: flex;
}

.btn-action-edit, .btn-action-delete {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
}

.btn-action-edit:hover {
  background: #eff6ff;
  border-color: #3b82f6;
  transform: scale(1.1);
}

.btn-action-delete:hover {
  background: #fee2e2;
  border-color: #ef4444;
  transform: scale(1.1);
}

.add-field-action-row {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #f1f5f9;
}

.btn-add-field {
  width: 100%;
  background: #ffffff;
  color: #4f46e5;
  border: 1.5px dashed #cbd5e1;
  border-radius: 12px;
  padding: 12px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-add-field:hover {
  background: #eff6ff;
  border-color: #4f46e5;
  color: #3730a3;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.canvas-action-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color, #e2e8f0);
}

.form-action-buttons-row {
  display: flex;
  gap: 12px;
}

.btn-clear-form {
  background: #ffffff !important;
  color: #475569 !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 12px !important;
  font-weight: 700;
  cursor: pointer;
  font-size: 13.5px;
  padding: 0 20px;
  height: 46px;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.btn-clear-form:hover {
  background: #f1f5f9 !important;
  color: #0f172a !important;
}

.btn-clear-form:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-deploy-form {
  flex: 1;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  color: #ffffff !important;
  height: 46px;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-size: 13.5px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn-deploy-form:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
  box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3) !important;
}

.btn-deploy-form:disabled {
  background: #cbd5e1 !important;
  color: #94a3b8 !important;
  cursor: not-allowed;
  box-shadow: none !important;
}

/* 4. Directory & Dashboard Workspaces */
.directory-view-container, .dashboard-view-container {
  padding: 40px 32px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.view-header {
  margin-bottom: 32px;
}

.view-title {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
}

.view-sub {
  font-size: 14px;
  color: #64748b;
}

.forms-grid-directory {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

/*  Directory Card — Premium Redesign  */
.directory-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.directory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -8px rgba(0, 0, 0, 0.09), 0 4px 8px -2px rgba(0, 0, 0, 0.04);
}

/* Thin accent stripe at top keyed to form theme colour */
.dir-card-accent {
  height: 4px;
  width: 100%;
  flex-shrink: 0;
}

.dir-card-inner {
  padding: 20px 22px 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 16px;
}

/* Content row: icon + title/desc */
.dir-card-content {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.dir-card-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.dir-card-text { min-width: 0; }

.dir-card-title {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dir-card-desc {
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.55;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Meta row */
.dir-card-meta { display: flex; align-items: center; gap: 8px; }

.dir-meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  font-weight: 500;
  color: #94a3b8;
  padding: 4px 10px;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 100px;
}

/* Action buttons row */
.dir-card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto;
}

.dir-btn-load {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 9px 16px;
  border-radius: 10px;
  border: none;
  background: #6366f1;
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  letter-spacing: 0.01em;
}

.dir-btn-load:hover {
  background: #4f46e5;
  transform: translateY(-1px);
}

.dir-btn-delete {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid #fee2e2;
  background: #fff5f5;
  color: #ef4444;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, transform 0.15s;
  flex-shrink: 0;
}

.dir-btn-delete:hover {
  background: #fee2e2;
  border-color: #ef4444;
  transform: translateY(-1px);
}

.directory-empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
}

/*  Dashboard: Premium Analytics Studio  */
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

/* Responses Table */
.responses-panel {
  padding: 0;
  overflow: hidden;
}
.panel-header {
  padding: 28px 28px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.responses-table-container {
  width: 100%;
  overflow-x: auto;
}
.responses-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  color: #334155;
}
.responses-table th {
  text-align: left;
  padding: 14px 28px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.responses-table td {
  padding: 16px 28px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: top;
}
.response-row {
  transition: all 0.2s ease;
}
.response-row:hover {
  background: #f8fafc;
}
.res-date {
  color: #64748b;
  font-size: 0.85rem;
  white-space: nowrap;
}
.res-email {
  font-weight: 600;
  color: #0f172a;
}
.badge-form {
  font-size: 0.75rem;
  font-family: monospace;
  background: #eff6ff;
  color: #3b82f6;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #bfdbfe;
}
.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
}
.status-completed {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}
.status-partial {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}
.answers-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.answer-chip {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #475569;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.answer-chip strong {
  color: #0f172a;
  margin-right: 4px;
}

/* Legacy classes kept for compat */
.dashboard-stats-grid { display: none; }

.stat-icon-wrapper.purple {
  background: #faf5ff;
  color: #9333ea;
}

.stat-icon-wrapper.green {
  background: #ecfdf5;
  color: #059669;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  margin-top: 6px;
}

.dashboard-chart-card {
  background: #ffffff;
  border: none;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.01);
}

.chart-title-row {
  margin-bottom: 28px;
}

.chart-title {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

.chart-sub {
  font-size: 13px;
  color: #64748b;
  margin-top: 6px;
}

.css-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.chart-bar-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.bar-label-col {
  width: 220px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  flex-shrink: 0;
}

.bar-track-col {
  flex: 1;
  height: 14px;
  background: #f1f5f9;
  border-radius: 9999px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, #4f46e5, #818cf8);
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-value-col {
  width: 80px;
  text-align: right;
  font-size: 13.5px;
  font-weight: 700;
  color: #0f172a;
  flex-shrink: 0;
}

/* 5. In-line Editor Modal */
.editor-modal-overlay {
  background: rgba(15, 23, 42, 0.45) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.editor-modal-card {
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: none;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s ease;
}

.btn-close-modal:hover {
  color: #0f172a;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: calc(85vh - 140px);
  overflow-y: auto;
}

.modal-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.modal-label {
  font-size: 12.5px;
  font-weight: 700;
  color: #475569;
}

.modal-input, .modal-select {
  width: 100%;
  height: 42px;
  padding: 0 14px;
  border: 1.5px solid #cbd5e1;
  border-radius: 10px;
  font-size: 13.5px;
  color: #334155;
  background-color: #ffffff;
  outline: none;
  transition: all 0.2s ease;
}

.modal-input:focus, .modal-select:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.mock-checkbox-group, .mock-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}

.mock-option-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  color: var(--text-color, #475569);
  cursor: default;
}

/*  Modal Footer: Single Save Pill  */
.modal-footer-clean {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px 20px;
  border-top: 1px solid #f1f5f9;
}

.btn-save-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: 100px;
  border: none;
  background: linear-gradient(135deg, #6366f1, #7c3aed);
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  cursor: pointer;
  letter-spacing: 0.01em;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-save-pill:hover {
  background: linear-gradient(135deg, #4f46e5, #6d28d9);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
  transform: translateY(-1px);
}

.btn-save-pill:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.modal-footer {
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-modal-cancel {
  padding: 10px 20px;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-modal-cancel:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-modal-save {
  padding: 10px 22px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
  color: #ffffff;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
  transition: all 0.2s ease;
}

.btn-modal-save:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(79, 70, 229, 0.25);
}

.drag-handle {
  display: inline-block;
  cursor: grab;
  margin-right: 8px;
  color: #94a3b8;
  user-select: none;
  font-weight: normal;
}

.drag-handle:active {
  cursor: grabbing;
}

.modal-input-group-row {
  display: flex;
  gap: 16px;
}

.modal-input-group.half {
  flex: 1;
}

.modal-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
}

.modal-section-divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0 10px 0;
}

.modal-section-divider::before,
.modal-section-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #f1f5f9;
}

.modal-section-divider:not(:empty)::before {
  margin-right: .5em;
}

.modal-section-divider:not(:empty)::after {
  margin-left: .5em;
}

.divider-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  background: #ffffff;
  padding: 0 8px;
}

.field-mock-input {
  width: 100%;
  height: 38px;
  padding: 0 12px;
  border: 1.5px solid var(--border-color, #cbd5e1);
  border-radius: var(--border-radius, 8px);
  font-size: 13px;
  color: var(--input-text, #334155);
  background: var(--input-bg, #f8fafc);
  outline: none;
}

.textarea-mock {
  height: 72px;
  padding: 8px 12px;
  resize: none;
}

/* Scrollbars & Keyframes */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.animate-fade {
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.5; }
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .fields-grid {
    grid-template-columns: 1fr;
  }
  .field-group {
    grid-column: span 1 !important;
  }
  .form-card {
    padding: 24px;
  }
}

.btn-fullscreen-toggle {
  background: transparent;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 1rem;
  cursor: pointer;
  color: var(--text-color, #475569);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-left: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-fullscreen-toggle:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}
.fullscreen-mode {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9999 !important;
  width: 100vw !important;
  height: 100vh !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: var(--bg-color, #f8fafc);
  display: flex;
  flex-direction: column;
}
.fullscreen-mode .canvas-preview-wrapper {
  flex: 1;
  border-radius: 0;
  max-width: 100%;
}
.fullscreen-mode .form-card {
  max-width: 800px;
  margin: 0 auto;
}


.btn-delete-danger {
  background: #fef2f2 !important;
  color: #ef4444 !important;
  border: 1px solid #fca5a5 !important;
}
.btn-delete-danger:hover {
  background: #fee2e2 !important;
  transform: translateY(-1px);
}
.btn-insert {
  background: #f0fdf4 !important;
  color: #16a34a !important;
  border: 1px solid #bbf7d0 !important;
}
.btn-insert:hover {
  background: #dcfce7 !important;
  transform: translateY(-1px);
}
.editor-modal-card label {
  font-family: 'Poppins', 'Plus Jakarta Sans', sans-serif;
  font-weight: 600 !important;
  color: #334155;
}
.modal-conditional-zone label {
  font-weight: 500 !important;
  color: #64748b;
}

.field-toolbar {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  gap: 4px;
}
.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: 'Poppins', 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  color: var(--text-color, #475569);
  transition: all 0.2s ease;
}
.toolbar-btn:hover {
  background: #f1f5f9;
}
.toolbar-btn.btn-edit:hover {
  color: #3b82f6;
  background: #eff6ff;
}
.toolbar-btn.btn-add:hover {
  color: #10b981;
  background: #ecfdf5;
}
.toolbar-btn.btn-delete-inline:hover {
  color: #ef4444;
  background: #fef2f2;
}

/*  Fix #2: Form Selector Row  */
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

/*  Fix #3: Removed field row & badge  */
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

/*  Phase 4: Share & Embed Modal  */
.btn-share {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.btn-share:hover:not(:disabled) {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.btn-share:disabled { opacity: 0.4; cursor: not-allowed; }

/* Modal Overlay */
.share-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* Modal Card */
.share-modal-card {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0,0,0,0.04);
  overflow: hidden;
}

/* Modal Header */
.share-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 0;
}
.share-modal-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}
.share-modal-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}
.share-modal-title {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 2px;
  letter-spacing: -0.02em;
}
.share-modal-sub {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}
.share-modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}
.share-modal-close:hover { background: #f8fafc; color: #475569; }

/* Tab Row */
.share-tab-row {
  display: flex;
  gap: 4px;
  padding: 20px 28px 0;
  border-bottom: 1px solid #f1f5f9;
}
.share-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 14px;
  border-radius: 8px 8px 0 0;
  border: none;
  background: transparent;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  bottom: -1px;
}
.share-tab-btn:hover { color: #475569; background: #f8fafc; }
.share-tab-active {
  color: #6366f1 !important;
  background: #ffffff !important;
  border: 1px solid #f1f5f9;
  border-bottom: 1px solid #ffffff !important;
}

/* Share Sections */
.share-section { padding: 24px 28px 28px; }
.share-section-desc { font-size: 0.84rem; color: #64748b; margin: 0 0 16px; }

/* Copy Row */
.share-copy-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.share-url-display {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  min-width: 0;
}
.share-url-icon { color: #94a3b8; flex-shrink: 0; }
.share-url-text {
  font-size: 0.8rem;
  color: #475569;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Embed Box */
.share-embed-box {
  background: #0f172a;
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 12px;
  overflow: hidden;
}
.share-embed-code {
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 0.75rem;
  color: #7dd3fc;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  line-height: 1.6;
}

/* Copy Buttons */
.btn-copy {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  flex-shrink: 0;
}
.btn-copy:hover { background: #f1f5f9; color: #0f172a; }
.btn-copy-success {
  background: #f0fdf4 !important;
  border-color: #86efac !important;
  color: #16a34a !important;
}
.btn-copy-full { width: 100%; justify-content: center; margin-bottom: 12px; }

/* Info Chip */
.share-info-row { margin-top: 4px; }
.share-info-chip {
  display: inline-flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.5;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  width: 100%;
}
.share-info-chip svg { flex-shrink: 0; margin-top: 2px; }

/* Vue Transition for Share Modal */
.share-modal-enter-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.share-modal-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}
.share-modal-enter-from {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}
.share-modal-leave-to {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}
.share-modal-enter-from .share-modal-card,
.share-modal-leave-to .share-modal-card {
  transform: translateY(16px);
}
@media (prefers-reduced-motion: reduce) {
  .share-modal-enter-active,
  .share-modal-leave-active { transition: opacity 0.15s; }
  .share-modal-enter-from,
  .share-modal-leave-to { transform: none; }
}

.form-logo-container {
  position: relative;
  text-align: center;
  margin-bottom: 24px;
  min-height: 80px;
  border-radius: 12px;
  overflow: hidden;
}
.form-logo-image {
  max-height: 120px;
  max-width: 100%;
  object-fit: contain;
  display: inline-block;
}
.form-logo-placeholder {
  height: 80px;
  background: #f1f5f9;
  border: 2px dashed #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-weight: 500;
  border-radius: 12px;
}
.form-logo-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
  border-radius: 12px;
}

.form-logo-widget:hover .form-logo-overlay {
  opacity: 1 !important;
}



/* ==============================================
   FORM DIRECTORY - Glassmorphism Reskin
   ============================================== */

.dir-glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.50);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.70);
  border-radius: 24px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04), 0 10px 20px -5px rgba(0,0,0,0.04);
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.28s cubic-bezier(0.4, 0, 0.2, 1), background 0.28s;
  min-height: 220px;
}

.dir-glass-card:hover {
  transform: translateY(-5px) scale(1.01);
  background: rgba(255, 255, 255, 0.70);
  border-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 20px 30px -8px rgba(99, 102, 241, 0.12), 0 8px 10px -5px rgba(99, 102, 241, 0.06);
}

@media (min-width: 1024px) {
  .dir-card-wide {
    grid-column: span 2;
  }
}

.dir-blob-tr {
  position: absolute;
  top: 0; right: 0;
  width: 120px; height: 120px;
  border-bottom-left-radius: 100%;
  pointer-events: none;
}

.dir-blob-bl {
  position: absolute;
  bottom: -24px; left: -24px;
  width: 100px; height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.dir-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.dir-more-btn {
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 50%;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: #64748b;
  opacity: 0;
  transition: opacity 0.2s, background 0.2s, color 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.dir-glass-card:hover .dir-more-btn {
  opacity: 1;
}

.dir-more-btn:hover {
  background: white;
  color: #6366f1;
}

.dir-card-title-new {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
  letter-spacing: -0.01em;
  transition: color 0.2s;
}

.dir-glass-card:hover .dir-card-title-new {
  color: #4f46e5;
}

.dir-btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.75);
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  white-space: nowrap;
}

.dir-btn-edit:hover {
  background: white;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

.dir-btn-del-new {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.2s, background 0.2s, border-color 0.2s;
  opacity: 0;
}

.dir-glass-card:hover .dir-btn-del-new {
  opacity: 1;
}

.dir-btn-del-new:hover {
  color: #ef4444;
  background: rgba(254, 226, 226, 0.8);
  border-color: rgba(252, 165, 165, 0.5);
}

.dir-mesh-orb {
  position: absolute;
  border-radius: 50%;
  opacity: 0.45;
  filter: blur(40px);
  pointer-events: none;
}

.dir-orb-1 {
  width: 320px; height: 320px;
  background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
  top: -80px; left: -80px;
  animation: orbDrift1 18s ease-in-out infinite;
}

.dir-orb-2 {
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(139,92,246,0.20) 0%, transparent 70%);
  top: 40%; right: -60px;
  animation: orbDrift2 22s ease-in-out infinite;
}

.dir-orb-3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%);
  bottom: 0; left: 30%;
  animation: orbDrift3 16s ease-in-out infinite;
}

@keyframes orbDrift1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(40px, 30px); }
}
@keyframes orbDrift2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, 20px); }
}
@keyframes orbDrift3 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -25px); }
}

/* =============================================
   DIRECTORY PAGE — Premium Grid Layout
   ============================================= */
.directory-view-container {
  background: #eff4ff;
  min-height: 100vh;
}
.dir-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
}
.dir-content-wrapper {
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.dir-header-row {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
@media (min-width: 768px) {
  .dir-header-row {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
.dir-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1e1b4b;
  margin: 0 0 8px;
  letter-spacing: -0.03em;
}
.dir-subtitle {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
  max-width: 440px;
}
.dir-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.dir-search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 9999px;
  padding: 10px 20px;
  min-width: 240px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s, border-color 0.2s;
}
.dir-search-bar:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.12);
}
.dir-search-icon {
  width: 16px;
  height: 16px;
  color: #9ca3af;
  flex-shrink: 0;
}
.dir-search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.875rem;
  color: #111827;
  width: 100%;
}
.dir-search-input::placeholder { color: #9ca3af; }
.dir-cta-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #7c3aed);
  color: #fff;
  font-weight: 700;
  font-size: 0.875rem;
  padding: 12px 24px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.2);
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.2s, box-shadow 0.2s;
}
.dir-cta-btn:hover {
  transform: translateY(-2px);
}
.btn-glow {
  box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.45);
}
.btn-glow:hover {
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.6);
}
.dir-filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.dir-filter-pill {
  padding: 8px 20px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.7);
  color: #6b7280;
}
.dir-filter-pill:hover {
  background: rgba(255,255,255,0.8);
  color: #6366f1;
}
.dir-filter-pill--active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.dir-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
}
@media (min-width: 640px) { .dir-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .dir-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1280px) { .dir-grid { grid-template-columns: repeat(4, 1fr); } }
.dir-state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 0;
  color: #6b7280;
  font-size: 0.9rem;
}
.dir-empty-icon {
  width: 64px;
  height: 64px;
  background: #eef2ff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}
.dir-empty-text { color: #6b7280; }
.dir-spinner {
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

/* =============================================
   TEMPLATE GALLERY — Stitch Glassmorphism
   ============================================= */

/* Glassmorphism Card */
.glass-card {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.glass-card:hover {
  transform: translateY(-4px) scale(1.02);
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.2);
}

/* Layout */
.templates-view-container {
  background: transparent;
  min-height: 100vh;
}
.tpl-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
}
.tpl-content-wrapper {
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  gap: 36px;
}

/* Header */
.tpl-header {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.tpl-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #1e1b4b;
  margin: 0 0 8px;
  letter-spacing: -0.03em;
}
.tpl-subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
  max-width: 540px;
}

/* AI Search Bar */
.tpl-search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 14px 20px;
  max-width: 720px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  transition: box-shadow 0.3s, border-color 0.3s, background 0.3s;
}
.tpl-search-bar:focus-within {
  box-shadow: 0 0 0 3px rgba(99,102,241,0.2), 0 8px 24px rgba(99,102,241,0.12);
  border-color: rgba(99,102,241,0.6);
  background: rgba(255, 255, 255, 0.75);
}
.tpl-search-icon {
  color: #6366f1;
  font-size: 22px;
  text-transform: none;
  flex-shrink: 0;
  font-family: 'Material Symbols Outlined', sans-serif;
  font-variation-settings: 'FILL' 0;
}
.tpl-search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.9375rem;
  color: #1e1b4b;
}
.tpl-search-input::placeholder { color: #9ca3af; }

/* Category Pills */
.tpl-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tpl-cat-pill {
  padding: 9px 22px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  background: rgba(255,255,255,0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.5);
  color: #6b7280;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.tpl-cat-pill:hover {
  background: rgba(255,255,255,0.7);
  color: #6366f1;
}
.tpl-cat-pill--active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(99,102,241,0.35);
}

/* Grid */
.tpl-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
}
@media (min-width: 768px) { .tpl-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .tpl-grid { grid-template-columns: repeat(3, 1fr); } }

/* Card: Hero Image Area */
.tpl-card-hero {
  height: 180px;
  width: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255,255,255,0.2);
  transition: all 0.35s ease;
}
.glass-card:hover .tpl-card-hero {
  filter: brightness(1.04);
}
.tpl-card-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.8);
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.glass-card:hover .tpl-card-icon-wrap {
  transform: scale(1.1) rotate(-3deg);
}

/* Hover Overlay */
.tpl-overlay {
  opacity: 0;
  position: absolute;
  inset: 0;
  background: rgba(30, 27, 75, 0.45);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s ease;
}
.glass-card:hover .tpl-overlay { opacity: 1; }
.tpl-overlay-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 700;
  font-size: 0.875rem;
  padding: 12px 24px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.2);
  cursor: pointer;
  transition: transform 0.2s;
}
.tpl-overlay-btn:hover { transform: scale(1.05); }

/* Card Body */
.tpl-card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(255,255,255,0.4);
}
.tpl-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}
.tpl-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0;
  line-height: 1.3;
}
.tpl-card-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 8px;
  border: 1px solid;
  white-space: nowrap;
  flex-shrink: 0;
  capitalize: first-letter;
}
.tpl-card-desc {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tpl-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}
.tpl-card-date {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
}
.tpl-delete-btn {
  color: #9ca3af;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
  display: flex;
  align-items: center;
}
.tpl-delete-btn:hover {
  color: #ef4444;
  background: rgba(239,68,68,0.08);
}

/* Blank Canvas Card */
.tpl-blank-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  min-height: 280px;
  background: rgba(255,255,255,0.25) !important;
}
.tpl-blank-card:hover {
  background: rgba(255,255,255,0.5) !important;
  border-color: rgba(99,102,241,0.4) !important;
}
.tpl-blank-icon-wrap {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: rgba(255,255,255,0.55);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.tpl-blank-icon {
  font-size: 28px;
  font-family: 'Material Symbols Outlined', sans-serif;
  text-transform: none;
  color: #6b7280;
}
.tpl-blank-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 8px;
}
.tpl-blank-sub {
  font-size: 0.82rem;
  color: #9ca3af;
  margin: 0;
  max-width: 220px;
  line-height: 1.5;
}

/* State Messages */
.tpl-state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 0;
  color: #6b7280;
  font-size: 0.9rem;
  text-align: center;
}
.tpl-empty-icon {
  width: 64px;
  height: 64px;
  background: #eef2ff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}
.tpl-empty-text { font-weight: 600; color: #374151; margin: 0; }
.tpl-empty-sub { color: #9ca3af; font-size: 0.82rem; margin: 0; }

/* =============================================
   CREATE FORM TAB — Premium UI Overhaul
   ============================================= */

/* Layout override for new premium structure */
.create-premium-layout {
  display: grid;
  grid-template-columns: 260px 1fr 1.6fr;
  gap: 20px;
  height: calc(100vh - 130px);
  min-height: 0;
}

/* Panel Card (Glassmorphism) */
.create-panel-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.08), 0 2px 8px rgba(0,0,0,0.04);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}
.create-panel-card:hover {
  box-shadow: 0 12px 40px rgba(99, 102, 241, 0.12), 0 2px 8px rgba(0,0,0,0.04);
}

/* Panel Header */
.create-panel-header {
  padding: 20px 20px 12px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}
.create-panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e1b4b;
  margin-bottom: 4px;
}
.create-panel-icon-wrap {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}
.create-panel-sub {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
  padding-left: 2px;
}

/* Input Methods 2-Col 3D Grid */
.input-methods-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 14px;
  overflow-y: auto;
  flex: 1;
}
.input-method-card {
  position: relative;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  overflow: hidden;
}
.input-method-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  opacity: 0;
  transition: opacity 0.25s ease;
  border-radius: inherit;
}
.input-method-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 16px 32px -8px rgba(99, 102, 241, 0.35);
  border-color: #a5b4fc;
  z-index: 2;
}
.input-method-card--active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: transparent;
  box-shadow: 0 12px 28px -6px rgba(99, 102, 241, 0.45);
  transform: translateY(-2px);
}
.input-method-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.25s;
  position: relative;
  z-index: 1;
}
.input-method-card--active .input-method-icon-wrap {
  background: rgba(255, 255, 255, 0.2);
}
.input-method-icon {
  font-size: 1.25rem;
  position: relative;
  z-index: 1;
}
.input-method-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #475569;
  text-align: center;
  line-height: 1.3;
  position: relative;
  z-index: 1;
}
.input-method-card--active .input-method-label {
  color: rgba(255, 255, 255, 0.92);
}
.input-method-check {
  position: absolute;
  top: 7px;
  right: 7px;
  width: 18px;
  height: 18px;
  background: rgba(255,255,255,0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

/* Chat Panel */
.create-chat-panel {
  min-height: 0;
}

/* Active Banner */
.create-active-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  background: rgba(248, 249, 255, 0.5);
  flex-shrink: 0;
}
.create-active-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: #475569;
}
.create-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5);
  animation: pulse-green 2s infinite;
  flex-shrink: 0;
}
@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5); }
  70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}
.create-active-text strong { color: #6366f1; }
.create-banner-actions {
  display: flex;
  gap: 6px;
}
.create-btn-ghost {
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.create-btn-ghost:hover { background: #f8fafc; border-color: #cbd5e1; color: #334155; }
.create-btn-ghost:disabled { cursor: not-allowed; }
.create-btn-ghost--danger:hover { background: #fef2f2; border-color: #fecaca; color: #ef4444; }

/* Chat Feed */
.create-chat-feed {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}
.create-chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
  color: #94a3b8;
  text-align: center;
  font-size: 0.85rem;
  padding: 20px;
}
.create-chat-empty-icon { font-size: 2rem; }
.create-msg-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.create-msg-row--user { flex-direction: row-reverse; }
.create-msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
  border: 2px solid #e2e8f0;
}
.create-msg-avatar--sparkle { background: linear-gradient(135deg, #fef3c7, #fde68a); }
.create-msg-body { max-width: 85%; }
.create-msg-row--user .create-msg-body { align-items: flex-end; display: flex; flex-direction: column; }
.create-msg-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 5px; }
.create-meta-tag {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
}
.create-meta-tag--fn { background: #ede9fe; color: #6d28d9; }
.create-meta-tag--file { background: #e0f2fe; color: #0369a1; }
.create-msg-text {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 10px 14px;
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.6;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.create-msg-row--ai .create-msg-text {
  background: linear-gradient(135deg, rgba(238,242,255,0.8), rgba(245,243,255,0.8));
  border-color: #c7d2fe;
}
.create-msg-row--user .create-msg-text { background: #1e1b4b; color: #e0e7ff; border-color: transparent; }

/* Thinking Animation */
.create-msg-thinking {
  display: flex !important;
  align-items: center;
  gap: 5px;
  padding: 14px 18px !important;
}
.create-msg-thinking span {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #6366f1;
  animation: think-bounce 1.2s ease-in-out infinite;
}
.create-msg-thinking span:nth-child(2) { animation-delay: 0.2s; }
.create-msg-thinking span:nth-child(3) { animation-delay: 0.4s; }
@keyframes think-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* Input Cockpit */
.create-input-cockpit {
  border-top: 1px solid rgba(226, 232, 240, 0.6);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(248, 249, 255, 0.4);
  flex-shrink: 0;
}

/* Upload Tray */
.create-upload-tray { }
.create-dropzone {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 2px dashed #c7d2fe;
  background: rgba(238, 242, 255, 0.5);
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.82rem;
  color: #6366f1;
}
.create-dropzone:hover { background: rgba(238, 242, 255, 0.85); border-color: #818cf8; }
.create-dropzone-icon { font-size: 1.1rem; }
.create-dropzone-text { color: #475569; font-size: 0.8rem; }
.create-file-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 8px 12px;
}
.create-file-icon { font-size: 1.2rem; }
.create-file-meta { flex: 1; min-width: 0; }
.create-file-name { font-size: 0.8rem; font-weight: 600; color: #166534; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.create-file-size { font-size: 0.7rem; color: #4ade80; }
.create-file-remove {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
  line-height: 1;
  transition: color 0.2s;
}
.create-file-remove:hover { color: #ef4444; }

/* Prompt Textarea */
.create-textarea {
  width: 100%;
  min-height: 72px;
  max-height: 140px;
  resize: none;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 0.875rem;
  color: #334155;
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
  line-height: 1.6;
  box-sizing: border-box;
}
.create-textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}
.create-textarea:disabled { opacity: 0.6; cursor: not-allowed; }
.create-textarea::placeholder { color: #94a3b8; }

/* Cockpit Footer */
.create-cockpit-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.create-keyboard-tip {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  color: #94a3b8;
}
.create-footer-btns {
  display: flex;
  align-items: center;
  gap: 8px;
}
.create-btn-attach {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: white;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.create-btn-attach:hover { background: #f8fafc; border-color: #a5b4fc; color: #6366f1; }
.create-btn-attach:disabled { opacity: 0.5; cursor: not-allowed; }
.create-btn-send {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 9px 22px;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}
.create-btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(99, 102, 241, 0.55);
}
.create-btn-send:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
.create-spin { animation: spin-anim 0.8s linear infinite; }
@keyframes spin-anim { to { transform: rotate(360deg); } }

/* ======== CANVAS EMPTY STATE ======== */
.create-empty-state {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-height: 320px;
}
/* Animated Blobs */
.create-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  animation: blob-float 8s ease-in-out infinite;
  pointer-events: none;
}
.create-blob--purple {
  width: 220px; height: 220px;
  background: rgba(168, 85, 247, 0.18);
  top: -30px; left: -30px;
  animation-delay: 0s;
}
.create-blob--indigo {
  width: 180px; height: 180px;
  background: rgba(99, 102, 241, 0.16);
  bottom: -20px; right: -20px;
  animation-delay: -3s;
}
.create-blob--violet {
  width: 140px; height: 140px;
  background: rgba(139, 92, 246, 0.14);
  bottom: 20px; left: 30%;
  animation-delay: -5s;
}
@keyframes blob-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(15px, -20px) scale(1.05); }
  66% { transform: translate(-10px, 10px) scale(0.97); }
}
/* Empty State Card */
.create-empty-card {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  border: 2px dashed rgba(99, 102, 241, 0.3);
  border-radius: 28px;
  padding: 40px 36px;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(99, 102, 241, 0.08);
}
.create-empty-icon-wrap {
  margin-bottom: 20px;
}
.create-empty-icon-float {
  width: 72px;
  height: 72px;
  margin: 0 auto;
  background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.12));
  border: 1.5px solid rgba(99,102,241,0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: icon-float 3.5s ease-in-out infinite;
}
@keyframes icon-float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}
.create-empty-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: #1e1b4b;
  margin: 0 0 10px;
  letter-spacing: -0.02em;
}
.create-empty-sub {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0 0 24px;
  line-height: 1.6;
}
/* Step indicators */
.create-empty-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.create-empty-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  color: #6b7280;
  font-weight: 500;
}
.create-empty-step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 0.72rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}
.create-empty-step-divider {
  width: 24px;
  height: 1.5px;
  background: linear-gradient(to right, #a5b4fc, #c4b5fd);
  border-radius: 1px;
  margin-bottom: 20px;
}

</style>

