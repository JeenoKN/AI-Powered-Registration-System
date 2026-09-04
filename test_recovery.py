import re

def recover_char_by_char(match):
    seq = match.group(0)
    recovered_bytes = bytearray()
    for char in seq:
        try:
            b = char.encode('cp1252')
            recovered_bytes.extend(b)
        except Exception:
            # If it's a replacement char or unmappable, we skip
            pass
    try:
        return recovered_bytes.decode('utf-8')
    except Exception:
        # If UTF-8 decode fails (incomplete bytes), return original
        return seq

with open('leftover_mojibake.txt', 'r', encoding='utf-8') as f:
    leftover = f.read()

fixed_leftover = re.sub(r'[^\x00-\x7F]+', recover_char_by_char, leftover)

with open('leftover_mojibake_fixed.txt', 'w', encoding='utf-8') as f:
    f.write(fixed_leftover)

print('Test run on leftover_mojibake.txt done.')
