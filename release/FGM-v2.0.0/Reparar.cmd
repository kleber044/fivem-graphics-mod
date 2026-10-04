@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Instalar-FGM.ps1" -Command repair
if errorlevel 1 pause
