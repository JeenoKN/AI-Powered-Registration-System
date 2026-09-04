# UI Refinement Specs: Form Directory & AI Quick Tweaker Cleanup

This document outlines strict UI/UX updates to improve visual hierarchy, clean up redundant controls, and ensure elite SaaS aesthetics.

## 1. AI Quick Tweaker Modal Cleanup (`App.vue`)
- **Button Removal**: Completely remove the following action elements from the modal's bottom section:
  - `Delete` button
  - `Add Before` / `Add After` button groups
  - `Cancel` text button
- **Remaining Action**: Keep ONLY the `Save Changes` button in the bottom right.
- **Button Aesthetics**: Design the `Save Changes` button to be a premium, rounded pill-shaped button with a smooth active/hover transition (e.g., elegant color shift or subtle scaling).
- **Dismissal Interaction**: Clicking the top-right `×` (Close Icon) must strictly handle the modal dismissal (Cancel/Close action) safely without throwing state errors.

## 2. Form Directory Premium Makeover (`App.vue`)
- **Card Interactivity**: Apply premium hover states to the individual form cards (`.form-card`). On hover, cards should lift slightly (`translateY(-4px)`) and drop a rich, diffused ambient shadow (`box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.05)`).
- **Modernized Controls**: Replace the raw browser-native `[Load & Edit]` and `[Delete]` buttons with sleek, modern UI component styling:
  - Use clear text hierarchy or high-end micro-buttons.
  - Buttons must feature premium styling: rounded corners, micro-paddings, subtle borders, and harmonious typography matching the font layout.
- **Layout & Spacing**: Refine padding, gap sizes, and metadata layout (e.g., date formatting and calendar icon row) to ensure a perfectly clean grid.