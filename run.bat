@echo off
chcp 65001 > nul
color 0A
title Автосалон на Python Flask

echo.
echo ========================================
echo   Автосалон на Python Flask
echo ========================================
echo.
echo Запуск приложения...
echo.

REM Get the directory of the script
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Run Python app
if exist ".venv\Scripts\python.exe" (
    echo Используется виртуальное окружение...
    .venv\Scripts\python.exe app.py
) else (
    echo Используется глобальный Python...
    python app.py
)

pause
