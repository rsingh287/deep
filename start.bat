@echo off
title AI Agent Master Starter
color 0A
cd /d %~dp0

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_services.ps1"

exit /b 0
