@echo off
cd /d "%~dp0"
del .git\HEAD.lock 2>nul
del .git\index.lock 2>nul
git add -A
git commit -m "chore: auto-push %date% %time%"
git push origin dev:main
echo.
echo === DONE ===
timeout /t 2
