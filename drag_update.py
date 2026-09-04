import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Inject Reactive Variables & Functions
inject_code = """
const isDraggingLogo = ref(false);
const dragStartX = ref(0);
const dragStartY = ref(0);
const initialLogoPosX = ref(0);
const initialLogoPosY = ref(0);

const startLogoDrag = (e) => {
  if (!generatedForm.value?.theme) return;
  // Initialize default pos if not exist
  if (generatedForm.value.theme.logo_pos_x === undefined) generatedForm.value.theme.logo_pos_x = 50;
  if (generatedForm.value.theme.logo_pos_y === undefined) generatedForm.value.theme.logo_pos_y = 50;
  
  isDraggingLogo.value = true;
  dragStartX.value = e.clientX || (e.touches && e.touches[0].clientX) || 0;
  dragStartY.value = e.clientY || (e.touches && e.touches[0].clientY) || 0;
  initialLogoPosX.value = generatedForm.value.theme.logo_pos_x || 50;
  initialLogoPosY.value = generatedForm.value.theme.logo_pos_y || 50;
  
  if (e.type === 'mousedown') e.preventDefault();
};

const onLogoDrag = (e) => {
  if (!isDraggingLogo.value || !generatedForm.value?.theme) return;
  
  const currentX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
  const currentY = e.clientY || (e.touches && e.touches[0].clientY) || 0;
  
  const deltaX = currentX - dragStartX.value;
  const deltaY = currentY - dragStartY.value;
  
  const deltaPercentX = deltaX * -0.15; 
  const deltaPercentY = deltaY * -0.15;
  
  let newX = initialLogoPosX.value + deltaPercentX;
  let newY = initialLogoPosY.value + deltaPercentY;
  
  newX = Math.max(0, Math.min(100, newX));
  newY = Math.max(0, Math.min(100, newY));
  
  generatedForm.value.theme.logo_pos_x = newX;
  generatedForm.value.theme.logo_pos_y = newY;
};

const endLogoDrag = () => {
  isDraggingLogo.value = false;
};
"""

# Insert near logoFileInput
if 'const logoFileInput =' in text:
    text = text.replace('const logoFileInput = ref(null);', 'const logoFileInput = ref(null);\n' + inject_code)

# 2. Update Image Template
old_img = '<img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" />'
new_img = '''<img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" :class="{ 'is-dragging': isDraggingLogo }" :style="{ objectPosition: ${generatedForm.theme.logo_pos_x || 50}% % }" @mousedown="startLogoDrag" @mousemove="onLogoDrag" @mouseup="endLogoDrag" @mouseleave="endLogoDrag" @touchstart="startLogoDrag" @touchmove="onLogoDrag" @touchend="endLogoDrag" />'''

text = text.replace(old_img, new_img)

# 3. Update CSS
text = re.sub(
    r'\.form-logo-image\s*\{[^}]+\}',
    r'.form-logo-image {\n  max-height: 120px;\n  width: 100%;\n  object-fit: cover;\n  display: block;\n  cursor: grab;\n  user-select: none;\n  -webkit-user-drag: none;\n}\n.form-logo-image.is-dragging {\n  cursor: grabbing;\n}',
    text
)

text = re.sub(
    r'\.form-logo-container\s*\{[^}]+\}',
    r'.form-logo-container {\n  position: relative;\n  text-align: center;\n  margin-bottom: 24px;\n  height: 120px;\n  border-radius: 12px;\n  overflow: hidden;\n  display: flex;\n  align-items: stretch;\n}',
    text
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Drag logic applied!')
