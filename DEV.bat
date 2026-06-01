@echo off
cd /d "%~dp0"
echo Starting local dev server...
start "" http://localhost:8080/daiviet_defense/index_3d.html
node scratch/serve.js
