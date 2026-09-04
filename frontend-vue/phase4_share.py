filepath = r"e:\NewSystem\frontend-vue\src\App.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# ===========================================================
# 1. ADD Share State & Logic right before </script>
# ===========================================================
JS_TO_ADD = """
// ==========================================
// 🔗 Phase 4: Share & Embed System
// ==========================================
const isShareModalOpen = ref(false)
const shareActiveTab = ref('link')  // 'link' | 'embed'
const copyLinkStatus = ref('idle')   // 'idle' | 'copied'
const copyEmbedStatus = ref('idle')  // 'idle' | 'copied'

const shareFormUrl = computed(() => {
  if (!generatedForm.value) return ''
  const id = generatedForm.value.id || generatedForm.value._aid || 'preview'
  return `https://dynamic-form.ai/f/${id}`
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
"""

content = content.replace("</script>", JS_TO_ADD + "\n</script>", 1)

# ===========================================================
# 2. ADD Share button in the Canvas Header (next to Export .vue)
# ===========================================================
OLD_HEADER_BTNS = """              <button class="btn-export-vue" :disabled="!generatedForm" @click="exportVueComponent()">Export .vue</button>"""
NEW_HEADER_BTNS = """              <button class="btn-export-vue" :disabled="!generatedForm" @click="exportVueComponent()">Export .vue</button>
              <button class="btn-share" :disabled="!generatedForm" @click="openShareModal">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                Share
              </button>"""
content = content.replace(OLD_HEADER_BTNS, NEW_HEADER_BTNS)

# ===========================================================
# 3. ADD Share Modal HTML before the closing </div></template>
# ===========================================================
SHARE_MODAL_HTML = """
    <!-- ✨ Phase 4: Share & Embed Modal -->
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
              {{ copyEmbedStatus === 'copied' ? 'Copied to Clipboard! ✅' : 'Copy Embed Code' }}
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
</template>"""

content = content.replace("  </div>\n</template>", SHARE_MODAL_HTML)

# ===========================================================
# 4. ADD Premium CSS for Share Modal
# ===========================================================
SHARE_CSS = """
/* ─── Phase 4: Share & Embed Modal ─── */
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
</style>"""

content = content.replace("</style>", SHARE_CSS)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Phase 4 Share & Embed applied successfully.")
