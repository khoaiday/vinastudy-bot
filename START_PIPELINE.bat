@echo off
title VInaStudy Auto-Pipeline
color 0A
cls
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   VInaStudy Auto-Pipeline Daemon                ║
echo  ║   Claude Code commit → Test → Deploy → Verify  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: Đi đến thư mục pipeline
cd /d "%~dp0"

:: Kiểm tra Node.js
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js chua duoc cai dat!
    echo Download: https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js san sang
echo [OK] Bat dau watch dev branch...
echo [INFO] Log: pipeline\pipeline_log.md
echo [INFO] Alert: PIPELINE_ALERT.md (chi xuat hien khi co van de)
echo.
echo      Giu cua so nay mo de pipeline chay...
echo      Dong cua so nay de dung pipeline.
echo.

:: Chạy daemon
node pipeline\pipeline.js

pause
