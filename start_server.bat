@echo off
cd /d "%~dp0"
echo === VInaStudy Web Server ===
echo.

REM Kiem tra .env
if not exist .env (
    echo [LOI] Chua co file .env !
    echo Chay lenh: copy .env.example .env
    echo Sau do dien DATABASE_URL vao file .env
    pause
    exit /b 1
)

echo Dang khoi dong server tai http://localhost:8080
echo Nhan Ctrl+C de dung server
echo.
python web_server.py
pause
