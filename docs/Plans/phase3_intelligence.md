# Phase 3: UI Precision & Analytics Integration

This phase updates the time-tracking formatting, improves field-level interactions, and prepares the behavioral analytics engine.

## 1. UI Precision & Smart Timing

### 🕒 Directory & Dashboard: Precise Timestamps
- Update the form card metadata to display a specific, localized timestamp.
- **Format Required**: "ทำเมื่อวัน [MM/DD/YYYY] เวลา [HH.mm]" (Example: ทำเมื่อวัน 6/16/2026 เวลา 13.27)
- Use standard JavaScript Date methods to parse the updated/created time dynamically.

### 🛠️ Canvas: Precision Hover Toolbar
- **Functional Requirement**: When a user hovers over any generated field in the Preview Canvas, a unified control toolbar must appear right next to the active field or the Edit Field button.
- **Buttons Grouping**: The toolbar must combine 3 essential actions side-by-side:
  1. `[Edit]` (To update the current field)
  2. `[Add Field]` (To quickly insert a new field right next to/after this one)
  3. `[Delete]` (To instantly remove this specific field)
- **UI Design Liberty**: The AI should determine the best visual layout, icons, spacing, and hover effects that seamlessly blend with the existing Premium Minimalist UI and attached Skills. Avoid awkward floating text; make it look like a professional SaaS component.

---

## 2. Behavioral Analytics Strategy

### 📊 Backend (FastAPI + MongoDB)
- Prepare schemas to log `form_id`, `field_id`, and `interaction_type` (focus, blur, duration).
- Track where users drop off before submission.

---

## Verification Plan
1. Open Directory -> Check if the timestamp matches the exact format "ทำเมื่อวัน 6/16/2026 เวลา 13.27".
2. Hover over a field in Preview -> Ensure [Edit | Add | Delete] appear side-by-side as a clean button group.