with open(r'E:\Codex Workspace\02_Projects\PPCU_TestBench\src\core\hardware\packet.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''       if needed_bytes > len(data):
           logger.warning(
               f"Data too short: need {needed_bytes}B, have {len(data)}B"
           )
           return 0'''

new = '''        if needed_bytes > len(data):
            logger.warning(
                f"Data too short: need {needed_bytes}B, have {len(data)}B"
            )
            return 0'''

if old in content:
    content = content.replace(old, new)
    with open(r'E:\Codex Workspace\02_Projects\PPCU_TestBench\src\core\hardware\packet.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK - fixed packet.py')
else:
    print('Old block NOT FOUND')
    pos = content.find('needed_bytes = byte_offset + (bit_length + 7) // 8')
    if pos >= 0:
        lines = content[pos:pos+400].split('\n')
        for i, line in enumerate(lines[:8]):
            print(f'  +{i}: {repr(line)}')
