@echo off
title STANDALONE DJ CROSSFADE ENGINE (PC SPEAKERS)
color 0B
echo =========================================================================
echo   STARTING STANDALONE DJ CROSSFADE ENGINE (REALTEK PC SPEAKERS LOCKED)
echo =========================================================================
cd /d "%~dp0"
"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" standalone_dj_engine.py
pause
