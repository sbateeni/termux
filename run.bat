@echo off
:: Batch file to run the Network Security Toolkit with administrator privileges
:: This helps with installation of dependencies that require elevated permissions

title Network Security Toolkit

:: Check if script is running with admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
    echo ====================================
) else (
    echo Requesting administrator privileges...
    echo ====================================
    :: Re-run the script with admin privileges
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: Change to the script directory
cd /d "%~dp0"

:: Check if Python is installed (try multiple methods)
set PYTHON_FOUND=0

:: Try 'python' command
python --version >nul 2>&1
if %errorLevel% == 0 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    echo Python is installed ^(as python^)
    goto :python_found
)

:: Try 'py' command (Windows Python Launcher)
py --version >nul 2>&1
if %errorLevel% == 0 (
    set PYTHON_CMD=py
    set PYTHON_FOUND=1
    echo Python is installed ^(as py^)
    goto :python_found
)

:: Try 'python3' command
python3 --version >nul 2>&1
if %errorLevel% == 0 (
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    echo Python is installed ^(as python3^)
    goto :python_found
)

:: If we get here, Python is not found
echo Python is not installed or not in PATH
echo Please install Python 3.6 or later
echo Download from: https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b

:python_found
:: Check if main.py exists
if exist "main.py" (
    echo Starting Network Security Toolkit...
    echo ====================================
    %PYTHON_CMD% main.py
) else (
    echo Error: main.py not found!
    echo Please make sure you are in the correct directory
    pause
    exit /b
)

:: Pause to keep window open after execution
pause