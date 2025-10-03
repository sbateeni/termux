# PowerShell script to install Metasploit on Windows
# Run this script as Administrator

Write-Host "Metasploit Windows Installer" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[-] This script must be run as Administrator" -ForegroundColor Red
    Write-Host "[*] Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Configuration
$DownloadURL = "https://windows.metasploit.com/metasploitframework-latest.msi"
$DownloadLocation = "$env:TEMP\Metasploit"
$InstallLocation = "C:\metasploit-framework"
$LogLocation = "$DownloadLocation\install.log"

Write-Host "[*] Creating download directory: $DownloadLocation" -ForegroundColor Cyan
if (!(Test-Path $DownloadLocation)) {
    New-Item -Path $DownloadLocation -ItemType Directory | Out-Null
}

Write-Host "[*] Creating installation directory: $InstallLocation" -ForegroundColor Cyan
if (!(Test-Path $InstallLocation)) {
    New-Item -Path $InstallLocation -ItemType Directory | Out-Null
}

$Installer = "$DownloadLocation\metasploit.msi"

Write-Host "[*] Downloading Metasploit installer from $DownloadURL" -ForegroundColor Cyan
try {
    Invoke-WebRequest -UseBasicParsing -Uri $DownloadURL -OutFile $Installer -ErrorAction Stop
    Write-Host "[+] Download completed successfully" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to download Metasploit installer: $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[*] Installing Metasploit to $InstallLocation" -ForegroundColor Cyan
try {
    $process = Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", "$Installer", "/qn", "/norestart", "INSTALLLOCATION=$InstallLocation", "/l*v", "$LogLocation" -Wait -PassThru -ErrorAction Stop
    if ($process.ExitCode -eq 0) {
        Write-Host "[+] Metasploit installed successfully" -ForegroundColor Green
    } else {
        Write-Host "[-] Installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "[*] Check the log file for details: $LogLocation" -ForegroundColor Yellow
        pause
        exit 1
    }
} catch {
    Write-Host "[-] Failed to install Metasploit: $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

# Add to PATH
Write-Host "[*] Adding Metasploit to system PATH" -ForegroundColor Cyan
try {
    $path = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::Machine)
    if ($path -notlike "*$InstallLocation\bin*") {
        $newPath = "$path;$InstallLocation\bin"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::Machine)
        Write-Host "[+] Metasploit added to system PATH" -ForegroundColor Green
    } else {
        Write-Host "[*] Metasploit is already in system PATH" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[-] Failed to add Metasploit to PATH: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[*] You may need to manually add $InstallLocation\bin to your system PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[+] Installation completed successfully!" -ForegroundColor Green
Write-Host "[*] Please restart your terminal/command prompt to use Metasploit" -ForegroundColor Yellow
Write-Host "[*] You can then test with: msfconsole --version" -ForegroundColor Yellow

pause