#!/usr/bin/env python3
"""
Test script to check if Metasploit is properly installed and accessible
"""

import subprocess
import shutil
import os
import platform

def test_metasploit():
    """Test if Metasploit is installed and accessible"""
    print("Testing Metasploit installation...")
    
    # Determine the correct executable name based on OS
    if platform.system().lower() == 'windows':
        msfconsole_name = 'msfconsole.bat'
    else:
        msfconsole_name = 'msfconsole'
    
    # First check if it's in PATH
    msfconsole_path = shutil.which(msfconsole_name)
    if msfconsole_path:
        print(f"[+] Metasploit found in PATH: {msfconsole_path}")
        
        # Try to get version
        try:
            result = subprocess.run(
                [msfconsole_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"[+] Metasploit version: {result.stdout.strip()}")
                return True
            else:
                print(f"[-] Error getting Metasploit version: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[-] Timeout while getting Metasploit version")
        except Exception as e:
            print(f"[-] Error testing Metasploit: {e}")
    else:
        print("[-] Metasploit not found in PATH")
    
    # Try common installation paths
    system = platform.system().lower()
    if system == 'windows':
        # Check common Windows installation paths
        common_paths = [
            'C:\\metasploit-framework\\bin\\msfconsole.bat',
            'C:\\Program Files\\metasploit-framework\\bin\\msfconsole.bat',
            'C:\\Program Files (x86)\\metasploit-framework\\bin\\msfconsole.bat',
            'C:\\Tools\\metasploit-framework\\bin\\msfconsole.bat'
        ]
    else:
        common_paths = [
            '/usr/bin/msfconsole',
            '/opt/metasploit-framework/bin/msfconsole',
            '/usr/local/bin/msfconsole'
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"[+] Metasploit found at: {path}")
            
            # Try to get version
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"[+] Metasploit version: {result.stdout.strip()}")
                    return True
                else:
                    print(f"[-] Error getting Metasploit version: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("[-] Timeout while getting Metasploit version")
            except Exception as e:
                print(f"[-] Error testing Metasploit: {e}")
    
    print("[-] Metasploit is not properly installed or accessible")
    print("\nTo install Metasploit:")
    if system == 'windows':
        print("1. Run the setup again with administrator privileges")
        print("2. Or manually install from: https://www.metasploit.com/download/")
        print("3. Make sure to add Metasploit to your system PATH")
    elif system == 'darwin':  # macOS
        print("1. Install via Homebrew: brew install metasploit")
    else:  # Linux
        print("1. Follow the official installation guide at: https://docs.metasploit.com/docs/using-metasploit/getting-started/setup.html")
    
    return False

if __name__ == "__main__":
    test_metasploit()