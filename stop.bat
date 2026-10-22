@echo off
title AI Agent Master Stopper
color 0C
echo ===================================================
echo   STOPPING ALL AI SERVERS, AGENTS AND CLOSING WINDOWS
echo ===================================================

echo [1/5] Stopping Ollama and LLM Engines...
taskkill /F /IM "ollama app.exe" /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1
taskkill /F /IM llama-server.exe /T >nul 2>&1
powershell -NoProfile -Command "Stop-Process -Name 'ollama', 'ollama app', 'llama-server' -Force -ErrorAction SilentlyContinue" >nul 2>&1

echo [2/5] Stopping Docker Desktop...
taskkill /F /IM "Docker Desktop.exe" /T >nul 2>&1
taskkill /F /IM "com.docker.backend.exe" /T >nul 2>&1
taskkill /F /IM "com.docker.proxy.exe" /T >nul 2>&1

echo [3/5] Closing UI Cockpit Windows...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '--app=http://(127\.0\.0\.1|localhost):5000' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1

echo [4/5] Closing all service CMD windows and Python processes...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -match '^cmd\.exe$' -and $_.CommandLine -match 'skills_api|telegram_service|app\.py|ollama serve|network_sentinel|cyber_honeypot|power_sentinel|standalone_dj_engine|voice_master_sentinel') -or ($_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -match 'skills_api\.py|telegram_service\.py|app\.py|network_sentinel\.py|cyber_honeypot\.py|power_sentinel\.py|standalone_dj_engine\.py|voice_master_sentinel\.py') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1

echo [5/5] Enforcing Window Title cleanup...
taskkill /F /FI "WINDOWTITLE eq *Ollama Server*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *AI Skills Brain API*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *Telegram AI Bot*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *Main AI Agent*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *Deep - 3D AI Workstation*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *Local AI Cockpit*" /T >nul 2>&1

echo.
echo All AI services, processes, and windows have been completely closed.
echo.
exit /b 0
