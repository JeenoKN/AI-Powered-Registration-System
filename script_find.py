import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# find openViewModal
match = re.search(r'const openViewModal\s*=\s*\((.*?)\)\s*=>\s*\{', text)
if match:
    print(f"openViewModal params: {match.group(1)}")
else:
    print("openViewModal not found")

# find duplicateForm
match = re.search(r'const duplicateForm\s*=\s*async\s*\((.*?)\)\s*=>\s*\{', text)
if match:
    print(f"duplicateForm params: {match.group(1)}")
else:
    print("duplicateForm not found")

# find FormCard usages
card = re.search(r'<FormCard(.*?)/>', text, re.DOTALL)
if card:
    print(f"FormCard usage: <FormCard{card.group(1)}/>")
else:
    print("FormCard not found")
