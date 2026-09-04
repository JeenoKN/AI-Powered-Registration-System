# Phase 2: Premium UI Polish & Version Control System

This plan covers the visual refinement of the "AI Quick Tweaker" (Edit Modal) and the implementation of the Phase 2 "Version History" feature.

## Phase 1.5: UI/UX Refinement (The "Quick Tweaker")

### 🎨 Visual Overhaul
- **Aesthetic**: Implement a glassmorphism effect (backdrop-blur) for the modal background.
- **Typography**: Use distinct weights for labels and helper text (Poppins/Lato).
- **Icons**: Add icons representing field types (e.g., 🔠 for Text, 🔢 for Number).

### 🛠️ New Inline Actions (Inside Modal)
- **Insert Buttons**: Add "Add Field Before" and "Add Field After" buttons at the bottom of the modal.
  - *Logic*: Clicking these will open a list of basic field types to insert immediately into the `generatedForm.fields` array at the target index.
- **Enhanced Delete**: Make the Delete button more prominent with a "Danger" red accent, but placed safely to avoid accidental clicks.

---

## Phase 2: Version History (The "Time Machine")

### 🔙 Backend Logic (FastAPI + MongoDB)
- **Schema Update**: Update `Form` model to include `history: List[FormSnapshot]`.
- **Snapshot Trigger**: Every time the form is saved or an AI prompt is successfully processed, create a snapshot containing `{ timestamp, form_json, prompt_used }`.
- **API Endpoints**:
  - `GET /api/v1/forms/{id}/history`: Fetch all snapshots.
  - `POST /api/v1/forms/{id}/rollback/{index}`: Replace the current form state with a specific history snapshot.

### 🕒 Frontend UI (Vue 3)
- **Version Drawer**: Add a side-drawer (History Sidebar) that opens from the Directory or Workspace.
- **Timeline UI**: Show a vertical list of snapshots with timestamps and a "Restore" button.
- **Preview Tooltip**: On hovering over a history item, show a small text-summary of what fields were in that version.

---

## Verification Plan
1. Open Edit Modal -> Verify the new Premium look & glassmorphism.
2. Inside Modal -> Click "Add Field After" -> Check if the field is inserted correctly.
3. Edit form -> Check Database -> Verify `history` array is growing.
4. Open History Sidebar -> Click "Rollback" -> Verify the UI updates to the previous state.

---

### 🚀 วิธีรันงาน (Next Step)

1.  แนบไฟล์ Skills ทั้ง 3 ตัว และไฟล์ **`phase2_blueprint.md`** เข้าไปในแชท
2.  ใช้โมเดล **Gemini 3.1 Pro (High)**
3.  ส่ง Prompt สั้นๆ นี้ได้เลยครับ:

> "ฉันได้แนบไฟล์ `phase2_blueprint.md` มาให้แล้ว กรุณาเริ่มทำส่วนที่ 1 (Phase 1.5 UI Refinement) ในไฟล์ `App.vue` ให้เสร็จก่อน โดยเน้นความสวยงามระดับ Premium และเพิ่มปุ่ม Insert/Delete ภายใน Modal ให้สมบูรณ์ เมื่อเสร็จแล้วให้แจ้งฉันเพื่อเตรียมลุยส่วนที่ 2 (Backend History) ต่อไป"

ลุยได้เลยครับ! หน้าตา AI Quick Tweaker รอบนี้จะออกมาสวยเหมือนแอปราคาแพงๆ แน่นอนครับ! 🎨✨

สไลด์สรุปแผนงาน Phase 2 ของคุณพร้อมแล้วครับ! ตรวจสอบดูได้เลยว่าภาพรวมและ Timeline ตรงใจคุณไหมครับ