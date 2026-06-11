#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Chinese mojibake and code issues."""
import os, sys
BASE = r"E:\Codex Workspace\02_Projects\PPCU_TestBench"

def fix_file(path, replacements):
    fpath = os.path.join(BASE, path)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  OK {path}")
        else:
            print(f"  NOT FOUND in {path}")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

def fix_file(path, replacements):
def fix_file_and_remove(path, replacements, remove_lines_with=None):
    """Read file, apply replacements, optionally remove lines, write back."""
    fpath = os.path.join(BASE, path)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  OK {path}: {repr(new[:40])}")
        else:
            print(f"  NOT FOUND in {path}: {repr(old[:40])}")
    
    if remove_lines_with:
        new_lines = []
        for line in content.split('\n'):
            if any(x in line for x in remove_lines_with):
                print(f"  REMOVED in {path}: {line.strip()[:50]}")
                continue
            new_lines.append(line)
        content = '\n'.join(new_lines)
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

def fix_full_file(path, old_lines_text, new_lines_text):
    """Replace exact multi-line block in file."""
    fpath = os.path.join(BASE, path)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if old_lines_text in content:
        content = content.replace(old_lines_text, new_lines_text)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK {path}")
    else:
        print(f"  NOT FOUND in {path}")

if __name__ == "__main__":
    print("=== Fixing encoding and code issues ===")
    
    # Remove orphaned _tabs property + fix indentation
    OLD = '''    @property
    def conn_bar(self):
        return self._conn_bar

    @property
    def tabs(self):
        return self._tabs
'''
    NEW = '''    @property
    def conn_bar(self):
        return self._conn_bar
'''
    fix_full_file("src/ui/main_window.py", OLD, NEW)
    
    print("\n=== Done ===")
