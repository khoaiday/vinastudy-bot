@echo off
:: Quản lý VInaStudy Pipeline
:: Dùng khi cần tắt tạm hoặc kiểm tra trạng thái

cls
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   VInaStudy Pipeline Manager                    ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  [1] Xem trạng thái pipeline
echo  [2] Chạy pipeline ngay
echo  [3] Dừng pipeline
echo  [4] Xóa khỏi auto-start (gỡ cài đặt)
echo  [5] Xem log gần nhất
echo  [0] Thoát
echo.
set /p CHOICE=  Chọn: 

if "%CHOICE%"=="1" goto :status
if "%CHOICE%"=="2" goto :start
if "%CHOICE%"=="3" goto :stop
if "%CHOICE%"=="4" goto :uninstall
if "%CHOICE%"=="5" goto :log
goto :exit

:status
echo.
schtasks /query /tn "VInaStudy-AutoPipeline" /fo LIST 2>nul
if %ERRORLEVEL% NEQ 0 echo  Pipeline chưa được đăng ký. Chạy SETUP_AUTOSTART.bat trước.
echo.

:: Kiểm tra process đang chạy
tasklist /fi "IMAGENAME eq node.exe" /fo LIST 2>nul | findstr /i "node" >nul
if %ERRORLEVEL% EQU 0 (
    echo  ✅ Pipeline đang chạy (node.exe active)
) else (
    echo  ⏹  Pipeline không chạy hiện tại
)
echo.
goto :end

:start
echo.
schtasks /run /tn "VInaStudy-AutoPipeline" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  ✅ Pipeline đã khởi động!
    echo  Log: pipeline\pipeline_log.md
) else (
    echo  Chạy trực tiếp...
    start /min cmd /c "node pipeline\pipeline.js"
    echo  ✅ Pipeline đang chạy trong background
)
echo.
goto :end

:stop
echo.
taskkill /f /im node.exe /fi "WINDOWTITLE eq VInaStudy*" >nul 2>&1
:: Kill tất cả node (cẩn thận nếu có node khác)
echo  Dừng node processes...
for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq node.exe" /fo csv ^| findstr node') do (
    taskkill /pid %%i /f >nul 2>&1
)
echo  ✅ Đã dừng pipeline
echo.
goto :end

:uninstall
echo.
echo  Xóa khỏi auto-start...
schtasks /delete /tn "VInaStudy-AutoPipeline" /f >nul 2>&1
echo  ✅ Đã gỡ. Pipeline sẽ không tự chạy nữa.
echo  (Chạy SETUP_AUTOSTART.bat để cài lại)
echo.
goto :end

:log
echo.
if exist "pipeline\pipeline_log.md" (
    echo  === Log gần nhất ===
    :: Hiển thị 30 dòng cuối của log
    powershell -Command "Get-Content 'pipeline\pipeline_log.md' | Select-Object -First 50"
) else (
    echo  Chưa có log. Pipeline chưa chạy lần nào.
)
echo.
goto :end

:end
pause
:exit
