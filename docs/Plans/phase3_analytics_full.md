# Phase 3: Analytics Logic Specification

This document defines the data structures and event triggers for form analytics. Please implement the logic while using your full creative freedom for the UI/UX.

## 1. Event Tracking Requirements (`App.vue`)
- Must capture user interactions dynamically rendered fields.
- Use appropriate Vue events (`@blur`, `@focus`, etc.) to track when a user enters and leaves a field.
- Create a function `sendAnalyticsLog(fieldId, actionType)` to handle data.

## 2. Dashboard Logic
- Compute the "Drop-off Rate" based on the logic: (Times Focused - Times Filled).
- Prepare the data objects so they are ready to be visualized.

## 3. UI/UX Independence
- **Visual Design**: The UI for the Dashboard Analytics is entirely up to you. Utilize the attached Skill folders (Impeccable, Minimalist) to design the charts, metric cards, and layout. Make it look like a high-end SaaS product.