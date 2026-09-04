# -*- coding: utf-8 -*-
"""Step 1: Wrap outer layout with Aurora orbs background"""

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

# Replace outer app-layout wrapper with aurora shell
vue = vue.replace(
    '<div class="app-layout">',
    '<div class="aurora-shell">\n    <!-- Aurora orbs -->\n    <div class="aurora-orb aurora-orb-indigo" aria-hidden="true"></div>\n    <div class="aurora-orb aurora-orb-fuchsia" aria-hidden="true"></div>\n    <div class="aurora-orb aurora-orb-cyan" aria-hidden="true"></div>\n    <div class="app-layout">'
)

# Close the extra wrapper before </template>
vue = vue.replace('</div>\n\n<!-- Modals', '</div><!-- /app-layout -->\n</div><!-- /aurora-shell -->\n\n<!-- Modals')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

print("Step 1 done: Aurora shell wrapper added.")
