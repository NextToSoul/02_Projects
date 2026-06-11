# Experience Notes - 2026-06-11
## Toolchain Issues Found and Fixed

### 1. Chinese Characters Display (Non-Issue)
PowerShell Get-Content displays UTF-8 Chinese characters as mojibake.
The actual files are correct UTF-8. Verify with Python, not PowerShell.

### 2. apply_patch Indentation Bug
When using Update File with space-prefixed context lines,
apply_patch strips one leading space per line.
Fix: Use only delete and add lines for indent-sensitive code.

### 3. CRLF Line Endings in apply_patch
Files with Windows CRLF line endings cause apply_patch matching failures.
Fix: Ensure target files use Unix LF line endings.

### 4. PowerShell Heredoc Restriction
PowerShell @'...'@ heredoc terminates early if markers appear in content.
Fix: Use apply_patch to create files; avoid PowerShell heredocs for scripts.

### 5. BOM from Out-File -Encoding utf8
PowerShell Out-File -Encoding utf8 adds UTF-8 BOM, breaking Python 3.12.
Fix: Use apply_patch with Add File to create clean UTF-8 files.

### Known Code Issues (Fixed)
- main_window.py: Removed orphaned self._tabs property (QTabWidget to QSplitter migration)
- packet.py: Fixed needed_bytes double-counting in _extract_bits() validation check
- ui/__init__.py: Removed BOM that caused syntax error
- Global syntax check: 34/34 source files pass compilation
