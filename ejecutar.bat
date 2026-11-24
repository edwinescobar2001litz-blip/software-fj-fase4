@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   SOFTWARE FJ - FASE 4 (SIMULACION)
echo ============================================
echo.
py main.py
echo.
echo Presione cualquier tecla para salir...
pause >nul
