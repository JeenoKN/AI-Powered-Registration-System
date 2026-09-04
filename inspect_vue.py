import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find the main app shell layout
match = re.search(r'<div class="app-shell-layout">.*?</aside>', text, re.DOTALL)
if match:
    print('APP SHELL & SIDEBAR:')
    try:
        print(match.group(0)[:500] + '...\n')
    except Exception as e:
        print(f"Error printing sidebar: {e}")

# Let's find the AI creator view
match2 = re.search(r'<div class="ai-creator-container"[^>]*>.*?<div class="directory-view-container"', text, re.DOTALL)
if match2:
    print('AI CREATOR VIEW:')
    try:
        print(match2.group(0)[:1500] + '...\n')
    except Exception as e:
        print(f"Error printing ai creator view: {e}")
