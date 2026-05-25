param(
  [ValidateSet("status", "start", "stop", "restart", "logs")]
  [string]$Action = "status",
  [string]$Hermes = "",
  [string]$WorkDir = "",
  [string]$RuntimeDir = ""
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if (-not $Hermes) {
  $Hermes = Join-Path $env:LOCALAPPDATA "hermes\hermes-agent\venv\Scripts\hermes.exe"
}
if (-not $WorkDir) {
  $WorkDir = (Get-Location).Path
}
if (-not $RuntimeDir) {
  $RuntimeDir = Join-Path $env:USERPROFILE ".hermes\gateway-runtime"
}

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

function Get-GatewayProcesses {
  $escaped = [regex]::Escape($Hermes)
  Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -in @("hermes.exe", "python.exe")) -and
    ($_.CommandLine -match $escaped) -and
    ($_.CommandLine -match "gateway run")
  }
}

function Stop-Gateway {
  & $Hermes gateway stop | Out-String | Write-Output
  Start-Sleep -Seconds 2
  Get-GatewayProcesses | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }
}

function Start-Gateway {
  $env:HERMES_ACCEPT_HOOKS = "1"
  $stdout = Join-Path $RuntimeDir "stdout.log"
  $stderr = Join-Path $RuntimeDir "stderr.log"
  $p = Start-Process -FilePath $Hermes `
    -ArgumentList @("gateway", "run", "--replace") `
    -WorkingDirectory $WorkDir `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru `
    -WindowStyle Hidden
  $p.Id | Set-Content -LiteralPath (Join-Path $RuntimeDir "pid.txt") -Encoding ascii
  Start-Sleep -Seconds 7
}

switch ($Action) {
  "status" {
    & $Hermes gateway status 2>&1 | Out-String | Write-Output
    Get-GatewayProcesses | Select-Object ProcessId, ParentProcessId, Name, CommandLine | Format-List
  }
  "start" {
    Start-Gateway
    & $Hermes gateway status 2>&1 | Out-String | Write-Output
  }
  "stop" {
    Stop-Gateway
  }
  "restart" {
    Stop-Gateway
    Start-Gateway
    & $Hermes gateway status 2>&1 | Out-String | Write-Output
  }
  "logs" {
    foreach ($file in @("stderr.log", "stdout.log")) {
      $path = Join-Path $RuntimeDir $file
      if (Test-Path $path) {
        "--- $file ---"
        Get-Content -LiteralPath $path -Encoding UTF8 -Tail 120
      } else {
        "--- $file missing ---"
      }
    }
  }
}
