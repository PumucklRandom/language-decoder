@REM set environment variables for proxy
@REM set http_proxy=http://localhost:3128
@REM set https_proxy=http://localhost:3128

@REM change working directory to script folder
cd /d "%~dp0"

@REM run python main script
@REM start .\python\python.exe .\__main__.py
start .\python\pythonw.exe .\__main__.py