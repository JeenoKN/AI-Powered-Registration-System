import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

# Update workspace grid background
vue = vue.replace(
    '<div class="workspace-grid" v-show="currentTab === \'create\'">',
    '<div class="workspace-grid h-full w-full bg-[#F9F8F6] rounded-r-[32px] overflow-hidden" v-show="currentTab === \'create\'">'
)

# Refactor function items
vue = vue.replace(
    '<div class="function-item"',
    '<div class="function-item bg-white rounded-2xl shadow-sm border border-gray-100 text-gray-700 hover:-translate-y-1 hover:shadow-md hover:shadow-indigo-500/10 transition-all duration-300 cursor-pointer p-4 flex items-center gap-3"'
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

# Remove old function-item CSS
with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = re.sub(r'\.function-item\s*\{[^}]*\}', '', css)
css = re.sub(r'\.function-item:hover\s*\{[^}]*\}', '', css)
css = re.sub(r'\.function-item\.active\s*\{[^}]*\}', '', css)

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated AI creator background and function items.")
