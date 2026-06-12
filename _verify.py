import sys, os
sys.path.insert(0, r'E:\Codex Workspace\02_Projects\PPCU_TestBench')
base = r'E:\Codex Workspace\02_Projects\PPCU_TestBench'

# Verify packet.py
with open(os.path.join(base, 'src/core/hardware/packet.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'needed_bytes' in line and '=' in line:
        status = 'OK' if '(bit_length + 7) // 8' in line else 'WRONG'
        print(f'[packet.py:{i}] FORMULA: {line.strip()} -> {status}')
    if 'needed_bytes > len' in line:
        status = 'OK' if 'byte_offset + needed_bytes' in line else 'WRONG'
        print(f'[packet.py:{i}] CHECK: {line.strip()} -> {status}')

# Verify poller.py
with open(os.path.join(base, 'src/core/telemetry/poller.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'header_size' in line:
        status = 'OK' if '8' in line else 'WRONG'
        print(f'[poller.py:{i}] {line.strip()} -> {status}')

# Verify executor.py
with open(os.path.join(base, 'src/core/engine/executor.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'header_size' in line:
        status = 'OK' if '8' in line else 'WRONG'
        print(f'[executor.py:{i}] {line.strip()} -> {status}')

# Verify layout
with open(os.path.join(base, 'src/ui/main_window.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'right_splitter' in line and 'QSplitter' in line:
        print(f'[main_window.py:{i}] LAYOUT right_splitter -> OK')

# Check syntax
errors = []
for root, dirs, files in os.walk(os.path.join(base, 'src')):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                source = fh.read()
            try:
                compile(source, path, 'exec')
            except SyntaxError as e:
                errors.append(f'{os.path.relpath(path, base)}: {e}')
if errors:
    for e in errors:
        print(f'SYNTAX ERROR: {e}')
else:
    print('All source files have valid syntax')
