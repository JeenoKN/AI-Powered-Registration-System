with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

templates_start = text.find('<div class="templates-view-container directory-view-container" v-show="currentTab === \'templates\'">')
dashboard_start = text.find('<div class="dashboard-view-container" v-show="currentTab === \'dashboard\'">')

current_templates = text[templates_start:dashboard_start]
print(current_templates)
