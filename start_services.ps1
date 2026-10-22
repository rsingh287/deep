# DEEP High-Performance AI Master Service Launcher (Native, Docker-Free)
$ErrorActionPreference = "SilentlyContinue"

$workDir = "c:\Users\User\.gemini\antigravity\scratch\local_ai_gui"
$pythonExe = "C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

function Test-PortOpen($port) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect("127.0.0.1", $port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(300, $false)
        if ($wait -and $tcp.Connected) {
            $tcp.EndConnect($iar)
            $tcp.Close()
            return $true
        }
        $tcp.Close()
    } catch {}
    return $false
}

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   INITIALIZING AI SYSTEMS & SERVICES (NATIVE)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# [1/4] Ollama Server
if (Test-PortOpen 11434) {
    Write-Host "[1/4] Ollama Server: Already Active (Port 11434)" -ForegroundColor Green
} else {
    Write-Host "[1/4] Starting Ollama Server (Port 11434)..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
}

# [2/4] Central Skills API (FastAPI)
if (Test-PortOpen 8000) {
    Write-Host "[2/4] Skills Brain API: Already Active (Port 8000)" -ForegroundColor Green
} else {
    Write-Host "[2/4] Starting Skills Brain API (Port 8000)..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonExe -ArgumentList "skills_api.py" -WorkingDirectory $workDir -WindowStyle Hidden
}

# [3/4] Telegram Bot Service
$tgProc = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "telegram_service\.py" }
if ($tgProc) {
    Write-Host "[3/4] Telegram AI Bot: Already Active" -ForegroundColor Green
} else {
    Write-Host "[3/4] Starting Telegram AI Bot..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonExe -ArgumentList "telegram_service.py" -WorkingDirectory $workDir -WindowStyle Hidden
}

# [4/5] Main AI Agent Cockpit (Flask)
if (Test-PortOpen 5000) {
    Write-Host "[4/5] Main AI Agent: Already Active (Port 5000)" -ForegroundColor Green
} else {
    Write-Host "[4/5] Starting Main AI Agent (Port 5000)..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonExe -ArgumentList "app.py" -WorkingDirectory $workDir -WindowStyle Hidden
}

# [5/5] Standalone DJ AutoMix Engine (Port 8765)
if (Test-PortOpen 8765) {
    Write-Host "[5/5] Standalone DJ Engine: Already Active (Port 8765)" -ForegroundColor Green
} else {
    Write-Host "[5/5] Starting Standalone DJ Engine (Port 8765)..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonExe -ArgumentList "standalone_dj_engine.py" -WorkingDirectory $workDir -WindowStyle Hidden
}

# Fast verification loop
$online = $false
for ($i = 0; $i -lt 30; $i++) {
    if (Test-PortOpen 5000) {
        $online = $true
        break
    }
    Start-Sleep -Milliseconds 800
}

Write-Host ""
if ($online) {
    Write-Host ">>> All AI services online! Cockpit ready on http://127.0.0.1:5000" -ForegroundColor Green
} else {
    Write-Host ">>> Services launched in background; initializing..." -ForegroundColor Yellow
}
