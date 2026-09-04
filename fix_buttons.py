import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace button class for "View Details"
# It looks something like: <button class="btn-premium-primary" ...> <svg ...> View Details </button>
# Let's find exactly how they are structured
m = re.findall(r'<button class=\"([^\"]+)\"[^>]*>(?:\s*<svg[^>]*>.*?</svg>)?\s*View Details\s*</button>', text, re.IGNORECASE)
print('Classes found for View Details:', m)

# Let's just do a blanket replace if it's easy:
text = re.sub(
    r'(<button class=\")btn-premium-primary(\"[^>]*>(?:\s*<[^>]+>)*\s*View Details\s*</button>)',
    r'\g<1>btn-premium-coral\g<2>',
    text,
    flags=re.IGNORECASE | re.DOTALL
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced buttons')
