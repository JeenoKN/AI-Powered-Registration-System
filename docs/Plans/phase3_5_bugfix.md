# Phase 3.5: Analytics Architecture Refactoring & Bug Fixes

This phase addresses critical logical bugs and refactors the Analytics implementation based on real-world edge cases.

## 1. Dashboard Data Isolation
- **Issue**: Analytics data is globally mixed for all forms.
- **Fix**: The Dashboard must have a dropdown or selector allowing the user to select *which* form's analytics they want to view. Structure the analytics state to group logs by a specific `formId`.

## 2. Stable Identifiers (The Rename Bug)
- **Issue**: Tracking by field name breaks when the user renames a field via the AI Quick Tweaker.
- **Fix**: Ensure every generated field gets a stable, hidden `id` (e.g., `field_uuid`). Use this `id` as the primary key in the analytics store. Always cache the last known label in the analytics store so the dashboard can render it correctly.

## 3. Smart Purge Logic for Deleted Fields (Anti-Clutter)
- **Issue**: Accidental field creation followed by immediate deletion clutters the Dashboard with empty `[Removed]` field analytics due to accidental focus logs.
- **Fix**: When a field is deleted from the form, apply this condition:
  - If `Times Filled === 0` (Accidental click/No real data): **Completely delete** its analytics entry from the system. Do not show it on the Dashboard.
  - If `Times Filled > 0` (Legacy data exists): Retain the record for accurate funnel totals, but render it on the Dashboard with a subtle grayed-out tag `[Removed]`.

## 4. The Tab-Switch Focus Guard
- **Issue**: Switching browser tabs triggers duplicate `@focus` events on the active input, falsely boosting focus counts.
- **Fix**: Implement a state guard (`currentlyFocusedId`). If a focus event fires on the exact same field that is already marked as active, ignore the event. Only allow a new focus count if a different field or element is selected.