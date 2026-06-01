@echo off
cd /d "%~dp0"
echo.
echo === DAI VIET DEFENSE — Asset Generation ===
echo.

echo [1/3] Checking asset status...
node tools/asset_gen/asset_gen.js --list
echo.

echo [2/3] Generating missing tower icons (2D)...
node tools/asset_gen/asset_gen.js --type towers_2d
echo.

echo [3/3] Done! Check daiviet_defense/assets/icons/
echo.
pause
