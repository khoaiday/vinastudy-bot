@echo off
:: Đăng ký pipeline tự khởi động cùng Windows
:: Chạy file này 1 LẦN DUY NHẤT với quyền Admin

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   Cài đặt Auto-Start khi mở máy                ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: Kiểm tra quyền Admin
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cần chạy với quyền Administrator!
    echo.
    echo  → Chuột phải vào file này → "Run as administrator"
    pause
    exit /b 1
)

:: Đường dẫn tuyệt đối đến pipeline
set PIPELINE_DIR=%~dp0
set PIPELINE_JS=%PIPELINE_DIR%pipeline\pipeline.js
set NODE_EXE=%APPDATA%\..\Local\Programs\nodejs\node.exe

:: Tìm node.exe
where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('where node') do set NODE_EXE=%%i
    goto :found_node
)

echo [ERROR] Không tìm thấy node.exe!
echo  Cài Node.js từ: https://nodejs.org
pause
exit /b 1

:found_node
echo [OK] Node.js: %NODE_EXE%
echo [OK] Pipeline: %PIPELINE_JS%
echo.

:: Tạo Task Scheduler entry
:: - Chạy ẩn (HIDDEN) khi user đăng nhập
:: - Không hiện cửa sổ CMD
schtasks /create ^
  /tn "VInaStudy-AutoPipeline" ^
  /tr "\"%NODE_EXE%\" \"%PIPELINE_JS%\"" ^
  /sc ONLOGON ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f ^
  /it

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  ✅ Đã đăng ký thành công!
    echo.
    echo  Pipeline sẽ tự chạy mỗi khi bạn mở máy.
    echo  Chạy ngay bây giờ luôn? [Y/N]
    set /p RUN_NOW=  Chọn: 
    if /i "%RUN_NOW%"=="Y" (
        echo.
        echo  Đang khởi động pipeline...
        schtasks /run /tn "VInaStudy-AutoPipeline"
        echo  ✅ Pipeline đang chạy ngầm!
        echo  Log: %PIPELINE_DIR%pipeline\pipeline_log.md
    )
) else (
    echo.
    echo  [ERROR] Đăng ký thất bại. Thử chạy lại với quyền Admin.
)

echo.
pause
