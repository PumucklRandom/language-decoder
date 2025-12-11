@echo off
REM set http_proxy=http://localhost:3128
REM set https_proxy=http://localhost:3128

cd /d "%~dp0"
start "" /B .\python\pythonw.exe .\__main__.py
exit