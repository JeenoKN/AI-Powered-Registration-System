import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

targets = ['app-shell-layout', 'sidebar-nav', 'workspace-container', 'workspace-inner-card', 'workspace-grid', 'unified-chat-column', 'unified-input-cockpit', 'functions-menu-column', 'preview-canvas-column', 'directory-view-container']

for i, line in enumerate(lines):
    for t in targets:
        if t in line and ('class="' + t in line or "class='" + t in line):
            print(f'{i+1}: {line.rstrip()}')
            break
