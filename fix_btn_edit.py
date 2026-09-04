with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'dir-btn-edit' in line and 'openViewModal' in line:
        print(f"Line {i+1}: {line.rstrip()}")
