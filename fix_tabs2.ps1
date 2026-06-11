$path = "E:\Codex Workspace\02_Projects\PPCU_TestBench\src\ui\main_window.py"
$tmp = $path + ".tmp"
$content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
$old = "  @property`r`n  def conn_bar(self):`r`n      return self._conn_bar`r`n`r`n  @property`r`n  def tabs(self):`r`n      return self._tabs"
$new = "    @property`r`n    def conn_bar(self):`r`n        return self._conn_bar"
$content = $content.Replace($old, $new)
[System.IO.File]::WriteAllText($tmp, $content, [System.Text.Encoding]::UTF8)
Move-Item -LiteralPath $tmp -Destination $path -Force
Write-Host "Done"
