#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all known code issues in PPCU TestBench."""
import os
BASE = r"E:\Codex Workspace\02_Projects\PPCU_TestBench"

def fix_file(path, old, new):
    fpath = os.path.join(BASE, path)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] {path}")
    else:
        print(f"[WARN] Not found in {path}: {repr(old[:60])}")

if __name__ == "__main__":
    print("=== Fix 1: Remove orphaned _tabs property ===")
    fpath = os.path.join(BASE, "src/ui/main_window.py")
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    skip = False
    for line in lines:
        if 'def tabs(self):' in line:
            skip = True
            continue
        if skip and ('@property' in line or 'return' in line or line.strip() == ''):
            continue
        skip = False
        # Fix 3-space indent back to 4-space
        if line.startswith('   ') and not line.startswith('    '):
            line = ' ' + line
        new_lines.append(line)
    with open(fpath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("[OK] main_window.py - removed _tabs property")
    
    print("\n=== Fix 2: needed_bytes double-counting in packet.py ===")
    fix_file("src/core/hardware/packet.py",
        "if byte_offset + needed_bytes > len(data):",
        "if needed_bytes > len(data):")
    fix_file("src/core/hardware/packet.py",
        'f"Data too short: need {byte_offset + needed_bytes}B, have {len(data)}B"',
        'f"Data too short: need {needed_bytes}B, have {len(data)}B"')
    
    print("\n=== Done ===")
