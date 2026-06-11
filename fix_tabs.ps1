$path = "E:\Codex Workspace\02_Projects\PPCU_TestBench\src\ui\main_window.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
$old = "   @property`r`n   def conn_bar(self):`r`n       return self._conn_bar`r`n`r`n   @property`r`n   def tabs(self):`r`n       return self._tabs"
$new = "    @property`r`n    def conn_bar(self):`r`n        return self._conn_bar"
$content = $content.Replace($old, $new)
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
Write-Host "Fixed main_window.py"
