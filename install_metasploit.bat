@echo off
:: Batch file to install Metasploit on Windows
:: This script will run the PowerShell installer with administrator privileges

title Metasploit Installer

echo Metasploit Windows Installer
echo ========================
echo.

:: Check if script is running with admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Running with administrator privileges
    echo ====================================
) else (
    echo [-] This installer requires administrator privileges
    echo ================================================
    echo [*] Requesting administrator privileges...
    :: Re-run the script with admin privileges
    PowerShell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0install_metasploit.ps1\"' -Verb RunAs"
    exit /b
)

:: Change to the script directory
cd /d "%~dp0"

:: Run the PowerShell script
echo [*] Running Metasploit installation script...
PowerShell -ExecutionPolicy Bypass -File "%~dp0install_metasploit.ps1"

:: Pause to keep window open after execution
pause