@echo off
title 3D Buddy & Skills Master Suite
color 0A
echo ===================================================
echo   LAUNCHING ANTIGRAVITY AI SUITE
echo ===================================================

echo [1/2] Starting Central Skills API (FastAPI)...
start "AI Skills Brain API" cmd /k "cd C:\Users\User\.gemini\antigravity\scratch\local_ai_gui && python skills_api.py"

echo [2/2] Starting Telegram Bot Service...
start "Telegram AI Bot" cmd /k "cd C:\Users\User\.gemini\antigravity\scratch\local_ai_gui && python telegram_service.py"

echo.
echo All microservices have been launched in separate windows!
echo - Skills API is on port 8000
echo.
pause
