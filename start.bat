@echo off
echo ======================================================================
echo   AI-Powered Construction Material Quality Assessment System
echo ======================================================================
echo.
echo Starting application server on http://localhost:8000 ...
echo API Swagger Docs: http://localhost:8000/docs
echo.

set "PYTHON_CMD=python"
if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Python\bin\python.exe"
)

"%PYTHON_CMD%" run_backend.py
pause
