<template>
  <!-- เปลี่ยน p-6 เป็น p-7 เพื่อขยายระยะห่างขอบด้านใน (Padding) -->
  <div class="bg-white rounded-[24px] p-7 flex flex-col justify-between group relative overflow-hidden h-full shadow-sm border border-slate-100/80 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.08)] hover:-translate-y-1.5 cursor-pointer" @click="$emit('edit', form._id)">
    
    <!-- Organic Blob -->
    <div class="absolute -right-10 -top-10 w-48 h-48 rounded-full mix-blend-multiply filter blur-[40px] opacity-40 transition-all duration-700 ease-out group-hover:scale-150 group-hover:opacity-70 pointer-events-none" :class="theme.blobColor"></div>
    
    <!-- เพิ่ม pl-1 ตรงนี้เพื่อสร้างระยะห่างจากขอบซ้าย -->
    <div class="flex flex-col gap-4 relative z-10 pl-1">
      <!-- Top Row: Badge -->
      <div class="flex justify-start items-start">
        <div class="px-3 py-1.5 rounded-full font-label-sm text-[12px] font-bold flex items-center gap-1.5 w-max shadow-sm transition-transform duration-300 group-hover:scale-105" :class="theme.badge">
          <span class="material-symbols-outlined !text-[16px] lowercase" style="font-variation-settings: 'FILL' 1;">{{ theme.icon }}</span>
          <span class="capitalize tracking-wide">{{ form.input_type_used ? form.input_type_used.replace('_', ' ') : 'Manual' }}</span>
        </div>
      </div>

      <!-- Middle Row: Text Content -->
      <div class="mt-1">
        <h3 class="text-[18px] text-slate-800 font-bold line-clamp-2 leading-snug tracking-tight group-hover:text-indigo-600 transition-colors duration-300">
          {{ form.title || 'Untitled Form' }}
        </h3>
        <p class="text-[13px] text-slate-500 flex items-start gap-1.5 mt-2.5 font-medium leading-relaxed">
          <span class="material-symbols-outlined !text-[16px] opacity-70 mt-0.5">schedule</span>
          <span class="line-clamp-2">{{ form.description || 'Updated recently' }}</span>
        </p>
      </div>
    </div>

    <!-- Bottom Row: Actions -->
    <div class="flex justify-between items-center pt-4 mt-4 border-t border-slate-50 relative z-10">
      <!-- Edit Button: เอา -ml-2 ออกเพื่อให้ชิดซ้ายตรงกับ Text ด้านบน -->
      <button @click.stop="$emit('edit', form._id)" class="px-3 py-2 rounded-xl text-[13px] font-bold flex items-center gap-2 transition-all duration-300 hover:bg-slate-50" :class="theme.text">
        <span class="material-symbols-outlined !text-[18px]" style="font-variation-settings: 'FILL' 1;">edit</span> Edit Form
      </button>
      
      <!-- Action Icons -->
      <div class="flex items-center gap-1">
        <button @click.stop="$emit('duplicate', form._id)" class="text-slate-400 hover:text-indigo-600 transition-all duration-300 p-2 rounded-xl hover:bg-indigo-50" title="Duplicate">
          <span class="material-symbols-outlined !text-[18px]">content_copy</span>
        </button>
        <button @click.stop="$emit('delete', form._id)" class="text-slate-400 hover:text-rose-500 transition-all duration-300 p-2 rounded-xl hover:bg-rose-50" title="Delete">
          <span class="material-symbols-outlined !text-[18px]">delete</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  form: { type: Object, required: true }
})
defineEmits(['edit', 'duplicate', 'delete'])

// Update Theme Mapping: เพิ่มสี blobColor สำหรับ Organic Background
const theme = computed(() => {
  const typeMap = {
    text_prompt: {
      blobColor: 'bg-indigo-300',
      badge: 'bg-indigo-50 text-indigo-700 border border-indigo-100/50',
      text: 'text-indigo-700',
      icon: 'edit_square'
    },
    voice: {
      blobColor: 'bg-rose-300',
      badge: 'bg-rose-50 text-rose-700 border border-rose-100/50',
      text: 'text-rose-700',
      icon: 'mic'
    },
    scanned_image: {
      blobColor: 'bg-sky-300',
      badge: 'bg-sky-50 text-sky-700 border border-sky-100/50',
      text: 'text-sky-700',
      icon: 'document_scanner'
    },
    manual: {
      blobColor: 'bg-slate-300',
      badge: 'bg-slate-50 text-slate-700 border border-slate-100/50',
      text: 'text-slate-700',
      icon: 'build'
    }
  }
  return typeMap[props.form.input_type_used] || typeMap.manual
})
</script>

<style scoped>
/* ใช้ Tailwind Utility Classes ทั้งหมดเพื่อให้จัดการง่ายและประสิทธิภาพสูง */
.material-symbols-outlined {
  /* ป้องกัน Tailwind capitalize/uppercase ทำลาย Ligature ไว้ใน scoped เผื่อฉุกเฉิน */
  font-family: 'Material Symbols Outlined', sans-serif;
  font-weight: normal;
  font-style: normal;
  display: inline-block;
  line-height: 1;
  text-transform: none;
  letter-spacing: normal;
  word-wrap: normal;
  white-space: nowrap;
  direction: ltr;
  -webkit-font-smoothing: antialiased;
}
</style>