with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: dir-blob-tr broken :style
text = text.replace(
    r'<div class="dir-blob-tr" :style="\background: linear-gradient(to bottom-left, 44, transparent)"></div>',
    "<div class=\"dir-blob-tr\" :style=\"{ background: 'linear-gradient(to bottom-left, ' + (form.theme_color || '#6366f1') + '44, transparent)' }\"></div>"
)

# Fix 2: dir-badge broken :style
text = text.replace(
    r'<span class="dir-badge" :style="\background: 18; color: ; border: 1px solid 30;">',
    "<span class=\"dir-badge\" :style=\"{ background: (form.theme_color || '#6366f1') + '18', color: form.theme_color || '#6366f1', border: '1px solid ' + (form.theme_color || '#6366f1') + '30' }\">"
)

# Fix 3: dir-btn-edit broken :style
text = text.replace(
    r'<button class="dir-btn-edit" @click="openViewModal(form)" :style="\color: ; border: 1px solid 30;">',
    "<button class=\"dir-btn-edit\" @click=\"openViewModal(form)\" :style=\"{ color: form.theme_color || '#6366f1', border: '1px solid ' + (form.theme_color || '#6366f1') + '30' }\">"
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)
print("Fixed template bindings")
