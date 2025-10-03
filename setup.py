#!/usr/bin/env python3
"""
Setup Script for Network Security Toolkit
Automatically installs all required dependencies for the toolkit.
"""

import os
import sys
import platform
import subprocess

def print_header(text):
    """Print a formatted header."""
    width = max(len(text) + 4, 50)
    print("\n" + "=" * width)
    print(f"{text.upper():^{width}}")
    print("=" * width)

def print_info(text):
    """Print informational message."""
    print(f"[*] {text}")

def print_success(text):
    """Print success message."""
    print(f"[+] {text}")

def print_error(text):
    """Print error message."""
    print(f"[-] {text}")

def print_warning(text):
    """Print warning message."""
    print(f"[!] {text}")

def detect_termux():
    """Detect if running on Termux."""
    return os.path.exists("/data/data/com.termux/files/usr")

def setup_termux():
    """Setup dependencies for Termux environment."""
    print_info("Setting up dependencies for Termux...")
    
    try:
        # Update package list
        print_info("Updating package list...")
        os.system("pkg update -y")
        
        # Install required packages
        packages = [
            "python",
            "nmap",
            "net-tools",
            "curl",
            "wget"
        ]
        
        print_info("Installing packages...")
        for package in packages:
            print_info(f"Installing {package}...")
            os.system(f"pkg install {package} -y")
        
        # Install Python packages
        python_packages = [
            "netifaces"
        ]
        
        print_info("Installing Python packages...")
        for package in python_packages:
            print_info(f"Installing Python package {package}...")
            os.system(f"pip install {package}")
        
        print_success("Termux setup completed!")
        return True
        
    except Exception as e:
        print_error(f"Error during Termux setup: {e}")
        return False

def setup_windows():
    """Setup dependencies for Windows environment."""
    print_info("Setting up dependencies for Windows...")
    
    try:
        # Check if Chocolatey is installed
        try:
            result = subprocess.run(["choco", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print_info("Chocolatey detected")
                use_choco = True
            else:
                use_choco = False
        except FileNotFoundError:
            use_choco = False
        
        if use_choco:
            # Install packages using Chocolatey
            packages = [
                "python",
                "nmap",
                "curl"
            ]
            
            print_info("Installing packages with Chocolatey...")
            for package in packages:
                print_info(f"Installing {package}...")
                os.system(f"choco install {package} -y")
        else:
            print_warning("Chocolatey not found. Please install packages manually:")
            print_info("  - Python 3.6+")
            print_info("  - Nmap")
            print_info("  - Git (optional)")
            print_info("You can install Chocolatey from: https://chocolatey.org/install")
        
        # Install Python packages
        python_packages = [
            "netifaces"
        ]
        
        print_info("Installing Python packages...")
        for package in python_packages:
            print_info(f"Installing Python package {package}...")
            os.system(f"pip install {package}")
        
        print_success("Windows setup completed!")
        return True
        
    except Exception as e:
        print_error(f"Error during Windows setup: {e}")
        return False

def setup_linux():
    """Setup dependencies for Linux environment."""
    print_info("Setting up dependencies for Linux...")
    
    try:
        # Detect package manager
        package_manager = None
        
        try:
            subprocess.run(["apt", "--version"], capture_output=True)
            package_manager = "apt"
        except FileNotFoundError:
            try:
                subprocess.run(["yum", "--version"], capture_output=True)
                package_manager = "yum"
            except FileNotFoundError:
                try:
                    subprocess.run(["dnf", "--version"], capture_output=True)
                    package_manager = "dnf"
                except FileNotFoundError:
                    try:
                        subprocess.run(["pacman", "--version"], capture_output=True)
                        package_manager = "pacman"
                    except FileNotFoundError:
                        package_manager = None
        
        if package_manager == "apt":
            # Debian/Ubuntu
            print_info("Using apt package manager")
            os.system("sudo apt update")
            packages = [
                "python3",
                "python3-pip",
                "nmap",
                "net-tools",
                "curl"
            ]
            for package in packages:
                print_info(f"Installing {package}...")
                os.system(f"sudo apt install {package} -y")
        elif package_manager == "yum":
            # RHEL/CentOS
            print_info("Using yum package manager")
            os.system("sudo yum update -y")
            packages = [
                "python3",
                "python3-pip",
                "nmap",
                "net-tools",
                "curl"
            ]
            for package in packages:
                print_info(f"Installing {package}...")
                os.system(f"sudo yum install {package} -y")
        elif package_manager == "dnf":
            # Fedora
            print_info("Using dnf package manager")
            os.system("sudo dnf update -y")
            packages = [
                "python3",
                "python3-pip",
                "nmap",
                "net-tools",
                "curl"
            ]
            for package in packages:
                print_info(f"Installing {package}...")
                os.system(f"sudo dnf install {package} -y")
        elif package_manager == "pacman":
            # Arch Linux
            print_info("Using pacman package manager")
            os.system("sudo pacman -Syu --noconfirm")
            packages = [
                "python3",
                "python-pip",
                "nmap",
                "net-tools",
                "curl"
            ]
            for package in packages:
                print_info(f"Installing {package}...")
                os.system(f"sudo pacman -S {package} --noconfirm")
        else:
            print_warning("Unsupported package manager. Please install packages manually:")
            print_info("  - Python 3.6+")
            print_info("  - pip")
            print_info("  - nmap")
            print_info("  - net-tools")
            print_info("  - curl")
            return False
        
        # Install Python packages
        python_packages = [
            "netifaces"
        ]
        
        print_info("Installing Python packages...")
        for package in python_packages:
            print_info(f"Installing Python package {package}...")
            os.system("pip3 install " + package)
        
        print_success("Linux setup completed!")
        return True
        
    except Exception as e:
        print_error(f"Error during Linux setup: {e}")
        return False

def setup_macos():
    """Setup dependencies for macOS environment."""
    print_info("Setting up dependencies for macOS...")
    
    try:
        # Check if Homebrew is installed
        try:
            result = subprocess.run(["brew", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print_info("Homebrew detected")
                use_brew = True
            else:
                use_brew = False
        except FileNotFoundError:
            use_brew = False
        
        if use_brew:
            # Install packages using Homebrew
            packages = [
                "python3",
                "nmap",
                "curl"
            ]
            
            print_info("Installing packages with Homebrew...")
            for package in packages:
                print_info(f"Installing {package}...")
                os.system(f"brew install {package}")
        else:
            print_warning("Homebrew not found. Please install it first:")
            print_info("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print_info("Then run this setup again.")
            return False
        
        # Install Python packages
        python_packages = [
            "netifaces"
        ]
        
        print_info("Installing Python packages...")
        for package in python_packages:
            print_info(f"Installing Python package {package}...")
            os.system("pip3 install " + package)
        
        print_success("macOS setup completed!")
        return True
        
    except Exception as e:
        print_error(f"Error during macOS setup: {e}")
        return False

def main():
    """Main setup function."""
    print_header("NETWORK SECURITY TOOLKIT SETUP")
    
    try:
        # Detect the operating system
        system = platform.system().lower()
        print_info(f"Detected OS: {system}")
        
        # Check if running on Termux
        is_termux = detect_termux()
        
        if is_termux:
            print_info("Running on Termux")
            success = setup_termux()
        elif system == "windows":
            print_info("Running on Windows")
            success = setup_windows()
        elif system == "linux":
            print_info("Running on Linux")
            success = setup_linux()
        elif system == "darwin":
            print_info("Running on macOS")
            success = setup_macos()
        else:
            print_error(f"Unsupported operating system: {system}")
            return False
        
        if success:
            print_success("Setup completed successfully!")
            print_info("You can now run the toolkit with: python main.py")
        else:
            print_error("Setup completed with errors.")
        
        return success
        
    except Exception as e:
        print_error(f"Error during setup: {e}")
        return False

if __name__ == "__main__":
    main()