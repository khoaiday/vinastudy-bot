@echo off
echo.
echo  ██████╗  █████╗ ██╗    ██╗██╗███████╗████████╗
echo  ██╔══██╗██╔══██╗██║    ██║██║██╔════╝╚══██╔══╝
echo  ██║  ██║███████║██║ █╗ ██║██║█████╗     ██║   
echo  ██║  ██║██╔══██║██║███╗██║██║██╔══╝     ██║   
echo  ██████╔╝██║  ██║╚███╔███╔╝██║███████╗   ██║   
echo  ╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚══════╝   ╚═╝  
echo.
echo  ASSET GENERATION PIPELINE
echo  Leonardo.ai + Tripo3D → Game Assets Auto-Generator
echo  =====================================================
echo.

cd /d "%~dp0"

:MENU
echo  Chon loai asset can generate:
echo.
echo  [1] Tower Icons 2D (9 icons - Leonardo.ai)
echo  [2] UI Backgrounds (HUD, Banner, Victory, Defeat - Leonardo.ai)
echo  [3] Enemy Sprites (Scout, Heavy, Boss - Leonardo.ai)
echo  [4] Tower Models 3D (4 towers - Tripo3D)
echo  [5] TAT CA (tat ca asset chua co)
echo  [6] Liet ke trang thai assets
echo  [0] Thoat
echo.
set /p choice="  Nhap lua chon: "

if "%choice%"=="1" (
  echo.
  echo  Generating Tower Icons...
  node tools\asset_gen\asset_gen.js --type towers_2d
  goto END
)
if "%choice%"=="2" (
  echo.
  echo  Generating UI Assets...
  node tools\asset_gen\asset_gen.js --type ui_2d
  goto END
)
if "%choice%"=="3" (
  echo.
  echo  Generating Enemy Sprites...
  node tools\asset_gen\asset_gen.js --type enemies_2d
  goto END
)
if "%choice%"=="4" (
  echo.
  echo  Generating 3D Tower Models (Tripo3D)...
  node tools\asset_gen\asset_gen.js --type towers_3d
  goto END
)
if "%choice%"=="5" (
  echo.
  echo  Generating ALL assets...
  node tools\asset_gen\asset_gen.js
  goto END
)
if "%choice%"=="6" (
  echo.
  node tools\asset_gen\asset_gen.js --list
  echo.
  goto MENU
)
if "%choice%"=="0" exit

:END
echo.
echo  Xong! Assets da duoc luu vao thu muc game.
echo  Chay git push de deploy len Railway.
echo.
pause
