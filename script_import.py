with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Add import FormCard from '../components/FormCard.vue' at the top of <script setup>
script_start = text.find('<script setup>')
if script_start != -1:
    import_statement = "\nimport FormCard from '../components/FormCard.vue'"
    insert_pos = script_start + len('<script setup>')
    text = text[:insert_pos] + import_statement + text[insert_pos:]
    with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Import statement added")
else:
    print("Could not find <script setup>")
