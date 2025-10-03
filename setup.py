#!/usr/bin/env python3
"""
Network Security Toolkit Setup Script
Provides automated setup for all required dependencies across multiple platforms.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header text"""
    print("\n" + "="*60)
    print(f"{text:^60}")
    print("="*60)

def print_info(text):
    """Print informational text"""
    print(f"[i] {text}")

def print_success(text):
    """Print success text"""
    print(f"[+] {text}")

def print_warning(text):
    """Print warning text"""
    print(f"[!] {text}")

def print_error(text):
    """Print error text"""
    print(f"[-] {text}")

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def check_package_installed(package_name, check_command):
    """Check if a package is already installed"""
    try:
        subprocess.run(check_command, shell=True, check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def setup_windows():
    """Setup dependencies on Windows"""
    print_header("WINDOWS SETUP")
    
    # Check if running as administrator
    if not is_admin():
        print_warning("This script needs administrator privileges to install some packages.")
        print_info("Please run this script as Administrator for full functionality.")
        input("Press Enter to continue anyway (some features may not work)...")
    
    try:
        # Check if Chocolatey is installed
        choco_installed = shutil.which("choco") is not None
        
        if not choco_installed:
            print_info("Installing Chocolatey...")
            try:
                choco_install_cmd = (
                    'Set-ExecutionPolicy Bypass -Scope Process -Force; '
                    '[System.Net.ServicePointManager]::SecurityProtocol = '
                    '[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
                    'iex ((New-Object System.Net.WebClient).DownloadString('
                    '\'https://community.chocolatey.org/install.ps1\'))'
                )
                result = subprocess.run(
                    ["powershell", "-Command", choco_install_cmd],
                    capture_output=True, text=True, shell=True
                )
                if result.returncode == 0:
                    print_success("Chocolatey installed successfully")
                    choco_installed = True
                else:
                    print_error(f"Failed to install Chocolatey: {result.stderr}")
            except Exception as e:
                print_error(f"Error installing Chocolatey: {e}")
        
        packages = [
            ("Nmap", "choco install nmap -y", "nmap --version"),
            ("Metasploit", "choco install metasploit -y", "msfconsole --version")
        ]
        
        for name, install_cmd, check_cmd in packages:
            print_info(f"Checking {name}...")
            if check_package_installed(name, check_cmd):
                print_success(f"{name} is already installed")
            else:
                print_info(f"Installing {name}...")
                try:
                    result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        print_success(f"{name} installed successfully")
                    else:
                        print_error(f"Failed to install {name}: {result.stderr}")
                        if name == "Metasploit":
                            print_info("Trying alternative installation method...")
                            _install_metasploit_windows()
                except Exception as e:
                    print_error(f"Error installing {name}: {e}")
                    if name == "Metasploit":
                        print_info("Trying alternative installation method...")
                        _install_metasploit_windows()
    except Exception as e:
        print_error(f"Error during Windows setup: {e}")

def _install_metasploit_windows():
    """Install Metasploit on Windows using alternative method"""
    try:
        print_info("Attempting alternative Metasploit installation...")
        print_warning("Automatic download of Metasploit installer is not implemented due to dynamic URLs.")
        print_info("Please download the Metasploit installer manually from:")
        print_info("https://www.metasploit.com/download/")
        print_info("After downloading, run the installer as Administrator.")
        print_info("Make sure to add Metasploit to your PATH during installation.")
    except Exception as e:
        print_error(f"Error during Metasploit installation: {e}")

def setup_linux():
    """Setup dependencies on Linux"""
    print_header("LINUX SETUP")
    
    # Detect package manager
    package_managers = {
        "apt": ("apt update", "apt install -y"),
        "yum": ("yum check-update", "yum install -y"),
        "dnf": ("dnf check-update", "dnf install -y"),
        "pacman": ("pacman -Sy", "pacman -S --noconfirm")
    }
    
    pkg_manager = None
    for pm, _ in package_managers.items():
        if shutil.which(pm):
            pkg_manager = pm
            break
    
    if not pkg_manager:
        print_error("No supported package manager found")
        return
    
    print_info(f"Detected package manager: {pkg_manager}")
    
    # Define packages for each manager
    packages = {
        "apt": [("nmap", "nmap"), ("metasploit-framework", "msfconsole")],
        "yum": [("nmap", "nmap"), ("metasploit", "msfconsole")],
        "dnf": [("nmap", "nmap"), ("metasploit", "msfconsole")],
        "pacman": [("nmap", "nmap"), ("metasploit", "msfconsole")]
    }
    
    update_cmd, install_cmd = package_managers[pkg_manager]
    
    # Update package lists
    print_info("Updating package lists...")
    try:
        subprocess.run(update_cmd, shell=True, check=True)
        print_success("Package lists updated")
    except subprocess.CalledProcessError:
        print_warning("Failed to update package lists")
    
    # Install packages
    for pkg_name, check_cmd in packages.get(pkg_manager, []):
        print_info(f"Checking {pkg_name}...")
        if check_package_installed(pkg_name, f"which {check_cmd}"):
            print_success(f"{pkg_name} is already installed")
        else:
            print_info(f"Installing {pkg_name}...")
            try:
                result = subprocess.run(f"{install_cmd} {pkg_name}", 
                                      shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print_success(f"{pkg_name} installed successfully")
                else:
                    print_error(f"Failed to install {pkg_name}: {result.stderr}")
            except Exception as e:
                print_error(f"Error installing {pkg_name}: {e}")

def setup_macos():
    """Setup dependencies on macOS"""
    print_header("MACOS SETUP")
    
    # Check if Homebrew is installed
    if not shutil.which("brew"):
        print_info("Installing Homebrew...")
        try:
            brew_install_cmd = (
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/'
                'Homebrew/install/HEAD/install.sh)"'
            )
            subprocess.run(brew_install_cmd, shell=True, check=True)
            print_success("Homebrew installed successfully")
        except subprocess.CalledProcessError:
            print_error("Failed to install Homebrew")
            return
    
    packages = [
        ("nmap", "nmap"),
        ("metasploit", "msfconsole")
    ]
    
    # Update Homebrew
    print_info("Updating Homebrew...")
    try:
        subprocess.run("brew update", shell=True, check=True)
        print_success("Homebrew updated")
    except subprocess.CalledProcessError:
        print_warning("Failed to update Homebrew")
    
    # Install packages
    for pkg_name, check_cmd in packages:
        print_info(f"Checking {pkg_name}...")
        if check_package_installed(pkg_name, f"which {check_cmd}"):
            print_success(f"{pkg_name} is already installed")
        else:
            print_info(f"Installing {pkg_name}...")
            try:
                result = subprocess.run(f"brew install {pkg_name}", 
                                      shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print_success(f"{pkg_name} installed successfully")
                else:
                    print_error(f"Failed to install {pkg_name}: {result.stderr}")
            except Exception as e:
                print_error(f"Error installing {pkg_name}: {e}")

def setup_termux():
    """Setup dependencies on Termux"""
    print_header("TERMUX SETUP")
    
    try:
        # Update package lists
        print_info("Updating package lists...")
        subprocess.run(["pkg", "update", "-y"], check=True)
        print_success("Package lists updated")
        
        # Install basic network tools
        print_info("Installing network tools...")
        subprocess.run(["pkg", "install", "inetutils", "traceroute", "net-tools", "-y"], check=True)
        print_success("Network tools installed")
        
        # Install Nmap
        print_info("Installing Nmap...")
        subprocess.run(["pkg", "install", "nmap", "-y"], check=True)
        print_success("Nmap installed successfully")
        
        # Install Metasploit Framework using the recommended method
        print_info("Installing Metasploit Framework...")
        print_info("This may take a while. Please be patient...")
        
        # Try the automated curl method first
        try:
            subprocess.run(["pkg", "install", "curl", "-y"], check=True)
            curl_result = subprocess.run(
                ["curl", "-fsSL", "https://kutt.it/msf"],
                capture_output=True, text=True
            )
            if curl_result.returncode == 0:
                # Save the script and execute it
                with open("metasploit_installer.sh", "w") as f:
                    f.write(curl_result.stdout)
                subprocess.run(["chmod", "+x", "metasploit_installer.sh"], check=True)
                subprocess.run(["bash", "metasploit_installer.sh"], check=True)
                print_success("Metasploit Framework installed successfully")
            else:
                # Fallback to manual installation
                _install_metasploit_termux()
        except Exception as e:
            print_warning(f"Automated installation failed: {e}")
            print_info("Trying manual installation...")
            _install_metasploit_termux()
            
    except subprocess.CalledProcessError as e:
        print_error(f"Error installing packages in Termux: {e}")
        print_info("Try manually installing Metasploit with:")
        print_info("curl -fsSL https://kutt.it/msf | bash")
    except Exception as e:
        print_error(f"Unexpected error in Termux setup: {e}")

def _install_metasploit_termux():
    """Install Metasploit on Termux using the gushmazuko script"""
    try:
        print_info("Installing Metasploit using gushmazuko script...")
        
        # Download and run the Metasploit installation script
        msf_install_script = "https://github.com/gushmazuko/metasploit_in_termux/raw/master/metasploit.sh"
        
        # Install required dependencies first
        subprocess.run(["pkg", "install", "wget", "curl", "git", "ruby", "ruby-dev", "libffi-dev", "ncurses-utils", "-y"], check=True)
        
        # Download the script
        subprocess.run(["wget", msf_install_script], check=True)
        subprocess.run(["chmod", "+x", "metasploit.sh"], check=True)
        
        # Run the installation script
        print_info("Running Metasploit installation script. This may take 10-15 minutes...")
        subprocess.run(["./metasploit.sh"], check=True)
        
        print_success("Metasploit Framework installed successfully")
        print_info("To start Metasploit, run: msfconsole")
        
    except subprocess.CalledProcessError as e:
        print_error(f"Error installing Metasploit in Termux: {e}")
        print_info("Try manually installing Metasploit with:")
        print_info("curl -fsSL https://kutt.it/msf | bash")
    except Exception as e:
        print_error(f"Unexpected error installing Metasploit in Termux: {e}")
        print_info("Try manually installing Metasploit with:")
        print_info("curl -fsSL https://kutt.it/msf | bash")

def install_python_packages():
    """Install required Python packages"""
    print_header("PYTHON PACKAGES SETUP")
    
    packages = [
        "scapy",
        "python-nmap",
        "requests"
    ]
    
    for pkg in packages:
        print_info(f"Installing {pkg}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], 
                          check=True, capture_output=True)
            print_success(f"{pkg} installed successfully")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install {pkg}: {e}")

def check_for_updates():
    """Check for updates from the GitHub repository and update if needed."""
    print_header("CHECK FOR UPDATES")
    
    try:
        # GitHub repository information
        repo_owner = "XmaX"
        repo_name = "termux"
        
        print_info(f"Checking for updates from GitHub repository: {repo_owner}/{repo_name}")
        
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("Git is not installed or not available in PATH.")
            print_info("Please install Git to enable update functionality.")
            return
        
        # Get current commit hash
        try:
            current_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            current_hash = current_commit.stdout.strip()
            print_info(f"Current commit: {current_hash[:8]}")
        except subprocess.CalledProcessError:
            print_error("Not a git repository or git repository not initialized.")
            print_info("Please clone the repository using 'git clone' to enable update functionality.")
            return
        
        # Fetch latest changes from remote
        print_info("Fetching latest changes from remote repository...")
        try:
            subprocess.run(["git", "fetch"], check=True)
        except subprocess.CalledProcessError:
            print_error("Failed to fetch updates from remote repository.")
            return
        
        # Get latest commit hash from remote
        try:
            latest_commit = subprocess.run(
                ["git", "rev-parse", f"origin/main"],
                capture_output=True,
                text=True,
                check=True
            )
            latest_hash = latest_commit.stdout.strip()
            print_info(f"Latest commit:  {latest_hash[:8]}")
        except subprocess.CalledProcessError:
            print_error("Failed to get latest commit information.")
            return
        
        # Compare commits
        if current_hash == latest_hash:
            print_success("Your repository is up to date!")
            return
        
        print_warning("Updates are available!")
        print_info(f"Current: {current_hash[:8]}")
        print_info(f"Latest:  {latest_hash[:8]}")
        
        # Ask user if they want to update
        choice = input("\n[?] Do you want to update to the latest version? (y/N): ").strip().lower()
        if choice != 'y':
            print_info("Update cancelled by user.")
            return
        
        # Perform the update
        print_info("Updating repository...")
        try:
            # Stash any local changes
            subprocess.run(["git", "stash"], check=True)
            
            # Pull the latest changes
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            
            # Apply stashed changes if any
            subprocess.run(["git", "stash", "pop"], check=False)
            
            print_success("Repository updated successfully!")
            print_info("Restart the toolkit to use the updated version.")
            
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to update repository: {e}")
            print_info("You may need to manually resolve conflicts.")
            
    except Exception as e:
        print_error(f"Error during update check: {e}")

def main():
    """Main setup function"""
    print_header("NETWORK SECURITY TOOLKIT SETUP")
    
    system = platform.system().lower()
    print_info(f"Detected system: {system}")
    
    # Menu for setup options
    while True:
        print("\nSetup Options:")
        print("1. Full Setup (Install all dependencies)")
        print("2. Install Python Packages Only")
        print("3. Check for Updates")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            if system == "windows":
                setup_windows()
            elif system == "linux":
                # Check if running on Termux
                if "com.termux" in os.environ.get("PREFIX", ""):
                    setup_termux()
                else:
                    setup_linux()
            elif system == "darwin":  # macOS
                setup_macos()
            else:
                print_error(f"Unsupported system: {system}")
            
            install_python_packages()
            print_success("Setup completed!")
            
        elif choice == "2":
            install_python_packages()
            print_success("Python packages installed!")
            
        elif choice == "3":
            check_for_updates()
            
        elif choice == "0":
            print_info("Exiting setup...")
            break
            
        else:
            print_error("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()