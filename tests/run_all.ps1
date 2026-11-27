# Windows 版：在 repo 根目錄執行  powershell -ExecutionPolicy Bypass -File tests\run_all.ps1
# 需要：Python 3、pip install playwright pillow、python -m playwright install chromium
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py -or $py -like '*WindowsApps*') { $py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" }
$env:PYTHONIOENCODING = 'utf-8'
$srv = Start-Process -FilePath $py -ArgumentList '-m','http.server','8765' -WorkingDirectory $root -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 2
try {
  Get-ChildItem (Join-Path $PSScriptRoot 'test_*.py') | Sort-Object Name | ForEach-Object {
    Write-Output "===== tests/$($_.Name)"
    Push-Location $root
    & $py $_.FullName 2>&1 | Select-Object -Last 25 | ForEach-Object { "$_" }
    Pop-Location
  }
} finally {
  Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
}
