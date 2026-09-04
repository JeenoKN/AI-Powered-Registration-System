with open(r'e:\NewSystem\backend-python\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if '@app.post' in line or '@app.get' in line or '@app.put' in line:
        print(f'{i+1}: {line.rstrip()}')
