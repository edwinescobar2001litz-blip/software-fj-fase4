@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   SOFTWARE FJ - MODO INTERACTIVO
echo ============================================
echo.
py menu.py
echo.
echo Presione cualquier tecla para salir...
pause >nul
