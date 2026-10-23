$ErrorActionPreference = "Stop"

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $python = $pythonCommand.Source
} else {
    $python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python314\python.exe"
}

if (-not (Test-Path $python)) {
    throw "Python was not found. Install Python or select the project's Python interpreter in VS Code."
}

Push-Location $PSScriptRoot
try {
    & $python -c "import flask"
    if ($LASTEXITCODE -ne 0) {
        throw "Flask is not installed in $python. Install Flask in the selected project interpreter, then try again."
    }
} finally {
    Pop-Location
}

$listener = Get-NetTCPConnection -LocalAddress "127.0.0.1" -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($listener) {
    $expectedAppPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "app.py"))
    $allProcesses = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
    $projectProcesses = @(
        $allProcesses |
            Where-Object {
                $_.Name -match '^python(w)?\.exe$' -and
                ([string]$_.CommandLine).Replace('/', '\').IndexOf($expectedAppPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
            }
    )
    $processesToStop = @($projectProcesses)
    $response = $null

    if ($processesToStop.Count -eq 0) {
        $listenerProcess = $allProcesses |
            Where-Object { $_.ProcessId -eq $listener.OwningProcess } |
            Select-Object -First 1
        if ($listenerProcess -and $listenerProcess.Name -match '^python(w)?\.exe$' -and
            ([string]$listenerProcess.CommandLine -match '(?i)(?:^|\s|")app\.py(?:["\s]|$)')) {
            $response = Read-Host "A Python process running app.py owns port 5000 (PID $($listener.OwningProcess)), but its command line does not identify the project folder. If this is this project's Flask app, stop it and continue? (Y/N)"
            if ($response -notmatch '(?i)^y(?:es)?$') {
                throw "The existing server was left running. Stop it, then run .\run_with_email.ps1 again."
            }

            $processIdsToStop = New-Object 'System.Collections.Generic.List[int]'
            $processIdsToStop.Add([int]$listener.OwningProcess)
            $foundChild = $true
            while ($foundChild) {
                $foundChild = $false
                foreach ($process in $allProcesses) {
                    if ($process.Name -match '^python(w)?\.exe$' -and
                        $processIdsToStop.Contains([int]$process.ParentProcessId) -and
                        -not $processIdsToStop.Contains([int]$process.ProcessId)) {
                        $processIdsToStop.Add([int]$process.ProcessId)
                        $foundChild = $true
                    }
                }
            }

            $processesToStop = @(
                foreach ($processId in $processIdsToStop) {
                    $allProcesses | Where-Object { $_.ProcessId -eq $processId } | Select-Object -First 1
                }
            )
        } else {
            throw "A different process is listening on 127.0.0.1:5000 (PID $($listener.OwningProcess)). Stop it before starting this Flask app."
        }
    }

    if ($processesToStop.Count -gt 0) {
        if (-not $response) {
            $projectProcessIds = ($processesToStop | ForEach-Object { $_.ProcessId }) -join ", "
            $response = Read-Host "The Flask app from this project is already running (PID $projectProcessIds). Stop it and continue? (Y/N)"
            if ($response -notmatch '(?i)^y(?:es)?$') {
                throw "The existing Flask server was left running. Stop it, then run .\run_with_email.ps1 again."
            }
        }

        foreach ($process in ($processesToStop | Sort-Object { $_.ParentProcessId -ne $listener.OwningProcess })) {
            Stop-Process -Id $process.ProcessId -ErrorAction Stop
        }

        for ($attempt = 0; $attempt -lt 40; $attempt++) {
            Start-Sleep -Milliseconds 250
            $listener = Get-NetTCPConnection -LocalAddress "127.0.0.1" -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if (-not $listener) {
                break
            }
        }

        if ($listener) {
            throw "The existing Flask server (PID $($listener.OwningProcess)) did not release port 5000. Stop it manually, then try again."
        }
    }
}

Write-Host "Email settings will be loaded from .env. Keep this terminal open."

Push-Location $PSScriptRoot
try {
    & $python app.py
} finally {
    Pop-Location
}
