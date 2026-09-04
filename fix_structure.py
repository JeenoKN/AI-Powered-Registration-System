with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the Templates section and remove the incorrectly placed bento grid from it
# The templates section starts at: <div class="templates-view-container directory-view-container" v-show="currentTab === 'templates'">
# Currently it has the bento grid for filteredDirectoryForms inside it - WRONG

templates_start = text.find('<div class="templates-view-container directory-view-container" v-show="currentTab === \'templates\'">')
dashboard_start = text.find('<div class="dashboard-view-container" v-show="currentTab === \'dashboard\'">')

if templates_start == -1 or dashboard_start == -1:
    print("Could not find section boundaries")
    print("templates_start:", templates_start)
    print("dashboard_start:", dashboard_start)
else:
    print(f"Templates section: {templates_start}")
    print(f"Dashboard section: {dashboard_start}")
    
    # Extract current templates section (the broken one)
    current_templates = text[templates_start:dashboard_start]
    print("Current templates section length:", len(current_templates))
    print("First 300 chars:", current_templates[:300])
