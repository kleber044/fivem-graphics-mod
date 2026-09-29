@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Instalar-FGM.ps1" -Command uninstall
if errorlevel 1 pause
