# -*- coding: utf-8 -*-
"""Step 2: Sidebar glass + nav active states"""

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

# Sidebar glass
vue = vue.replace('<aside class="sidebar-nav">', '<aside class="sidebar-nav sidebar-glass">')

# Brand logo: make it use glass
vue = vue.replace('<div class="brand-logo ai-glow">', '<div class="brand-logo aurora-logo">')

# Nav items: remove legacy active class, let CSS handle it
# Update the nav links to use glass-nav-item class
vue = vue.replace(
    '<a href="#" class="nav-item" :class="{ active: currentTab === \'create\' }" @click.prevent="currentTab = \'create\'">',
    '<a href="#" class="glass-nav-item" :class="{ \'glass-nav-active\': currentTab === \'create\' }" @click.prevent="currentTab = \'create\'">'
)
vue = vue.replace(
    '<a href="#" class="nav-item" :class="{ active: currentTab === \'directory\' }" @click.prevent="currentTab = \'directory\'">',
    '<a href="#" class="glass-nav-item" :class="{ \'glass-nav-active\': currentTab === \'directory\' }" @click.prevent="currentTab = \'directory\'">'
)
vue = vue.replace(
    '<a href="#" class="nav-item" :class="{ active: currentTab === \'templates\' }" @click.prevent="currentTab = \'templates\'">',
    '<a href="#" class="glass-nav-item" :class="{ \'glass-nav-active\': currentTab === \'templates\' }" @click.prevent="currentTab = \'templates\'">'
)
vue = vue.replace(
    '<a href="#" class="nav-item" :class="{ active: currentTab === \'dashboard\' }" @click.prevent="currentTab = \'dashboard\'">',
    '<a href="#" class="glass-nav-item" :class="{ \'glass-nav-active\': currentTab === \'dashboard\' }" @click.prevent="currentTab = \'dashboard\'">'
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

print("Step 2 done: Sidebar glass + nav active states updated.")
