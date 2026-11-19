@echo off
cd /d "%~dp0"
py -3 hydrate_assets.py
if errorlevel 1 goto end
py -3 check_site.py
if errorlevel 1 goto end
start "" http://localhost:4173/
py -3 -m http.server 4173
:end
pause
