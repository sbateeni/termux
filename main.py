#!/usr/bin/env python3
"""
Main Controller Module
Orchestrates all modules for complete network security testing workflow.
"""

import sys
import time
import os
import subprocess
from typing import List, Dict, Optional

# Import all modules
from network_scanner import NetworkScanner
from target_selector import TargetSelector
from port_scanner import PortScanner
from metasploit_interface import MetasploitInterface
from config import Config
from utils import clear_screen, print_header, print_error, print_success, print_info, print_warning

class SecurityToolkit:
    def __init__(self):
        """Initialize the security toolkit."""
        self.config = Config()
        self.scanner = None
        self.selector = None
        self.port_scanner = None
        self.msf_interface = MetasploitInterface()
        self.current_target = None
        self.open_ports = []
        self.potential_exploits = []
        
    def run(self):
        """Main application loop."""
        clear_screen()
        print_header("NETWORK SECURITY TESTING TOOLKIT")
        print_info("DISCLAIMER: This tool is for educational and authorized security testing only.")
        print_info("Only use on networks you own or have explicit permission to test.\n")
        
        # Check if Metasploit is installed
        msf_available = self.msf_interface.check_metasploit_installed()
        
        if not msf_available:
            print_warning("Metasploit Framework not found!")
            print_info("Exploitation features will be simulated.")
            print_info("To enable real exploit functionality, please install Metasploit Framework.")
            print_info("Run setup (Option 8) for installation guidance.")
        
        while True:
            self.display_menu()
            choice = input("\n[?] Select option: ").strip()
            
            if choice == '1':
                self.discover_network_devices()
            elif choice == '2':
                self.select_target()
            elif choice == '3':
                self.scan_target_ports()
            elif choice == '4':
                self.search_exploits()
            elif choice == '5':
                self.run_exploit_check()
            elif choice == '6':
                self.run_exploit_script()
            elif choice == '7':
                self.show_current_status()
            elif choice == '8':
                self.setup_dependencies()
            elif choice.lower() == 'q':
                print_info("Exiting toolkit. Goodbye!")
                sys.exit(0)
            else:
                print_error("Invalid option. Please try again.")
            
            input("\nPress Enter to continue...")
    
    def display_menu(self):
        """Display the main menu."""
        clear_screen()
        print_header("MAIN MENU")
        print("1. Discover network devices")
        print("2. Select target")
        print("3. Scan target ports")
        print("4. Search for exploits")
        print("5. Run exploit check")
        print("6. Run exploit script (from file)")
        print("7. Show current status")
        print("8. Setup/Install dependencies")
        print("Q. Quit")
    
    def discover_network_devices(self):
        """Discover devices on the network."""
        print_header("NETWORK DISCOVERY")
        
        try:
            self.scanner = NetworkScanner()
            devices = self.scanner.scan_network()
            
            if devices:
                self.scanner.display_devices()
                self.selector = TargetSelector(devices)
                print_success("Network scan completed successfully!")
            else:
                print_error("No devices found on the network.")
        except KeyboardInterrupt:
            print_info("\nScan interrupted by user.")
        except Exception as e:
            print_error(f"Error during network scan: {e}")
    
    def select_target(self):
        """Select target from discovered devices."""
        print_header("TARGET SELECTION")
        
        if not self.selector:
            print_error("No devices discovered yet. Run network discovery first.")
            return
        
        try:
            target = self.selector.select_target_interactive()
            if target:
                self.current_target = target
                self.selector.display_selected_target()
                print_success("Target selected successfully!")
            else:
                print_info("Target selection cancelled.")
        except Exception as e:
            print_error(f"Error during target selection: {e}")
    
    def scan_target_ports(self):
        """Scan open ports on selected target."""
        print_header("PORT SCANNING")
        
        if not self.current_target:
            print_error("No target selected. Please select a target first.")
            return
        
        target_ip = self.current_target['ip']
        print_info(f"Scanning ports on target: {target_ip}")
        
        try:
            # Get scan type from user
            print("\nScan Options:")
            print("1. Common ports (20 most common services)")
            print("2. Custom port range")
            
            choice = input("\n[?] Select scan type (1-2): ").strip()
            
            self.port_scanner = PortScanner(target_ip)
            
            if choice == '1':
                self.open_ports = self.port_scanner.scan_common_ports()
            elif choice == '2':
                try:
                    start_port = int(input("Start port (1-65535): "))
                    end_port = int(input("End port (1-65535): "))
                    self.open_ports = self.port_scanner.scan_port_range(start_port, end_port)
                except ValueError:
                    print_error("Invalid port numbers.")
                    return
            else:
                print_error("Invalid choice. Using common ports scan.")
                self.open_ports = self.port_scanner.scan_common_ports()
            
            # Display results
            self.port_scanner.display_results()
            print_success("Port scan completed successfully!")
            
        except KeyboardInterrupt:
            print_info("\nScan interrupted by user.")
        except Exception as e:
            print_error(f"Error during port scan: {e}")
    
    def search_exploits(self):
        """Search for exploits matching target and open ports."""
        print_header("EXPLOIT SEARCH")
        
        if not self.current_target or not self.open_ports:
            print_error("Target and port scan required first. Please complete steps 1-3.")
            return
        
        if not self.msf_interface:
            print_error("Metasploit interface not initialized.")
            return
        
        target_ip = self.current_target['ip']
        print_info(f"Searching exploits for: {target_ip}")
        print_info(f"Open ports: {self.open_ports}")
        
        try:
            # Search for exploits
            self.potential_exploits = self.msf_interface.search_exploits(target_ip, self.open_ports)
            
            if self.potential_exploits:
                self.msf_interface.display_exploits(self.potential_exploits)
                print_success("Exploit search completed!")
            else:
                print_info("No exploits found for the target configuration.")
                
        except Exception as e:
            print_error(f"Error during exploit search: {e}")
    
    def run_exploit_check(self):
        """Run exploit checks against target."""
        print_header("EXPLOIT CHECKING")
        
        if not self.potential_exploits:
            print_error("No exploits found. Please search for exploits first.")
            return
        
        if not self.msf_interface:
            print_error("Metasploit interface not initialized.")
            return
        
        target_ip = self.current_target['ip'] if self.current_target else "unknown"
        print_info(f"Checking exploits for target: {target_ip}")
        
        try:
            # Display available exploits
            if not self.msf_interface:
                print_error("Metasploit interface not initialized.")
                return
            self.msf_interface.display_exploits(self.potential_exploits)
            
            # Ask user if they want to try all exploits automatically
            auto_choice = input("\n[?] Try all exploits automatically until one succeeds? (y/N): ").strip().lower()
            
            if auto_choice == 'y':
                self._try_all_exploits(target_ip)
                return
            
            # Let user select which exploit to check
            try:
                selection = int(input(f"\n[?] Select exploit to check (1-{len(self.potential_exploits)}): ")) - 1
                if 0 <= selection < len(self.potential_exploits):
                    selected_exploit = self.potential_exploits[selection]
                    
                    # Get detailed exploit information
                    exploit_details = self.msf_interface.get_exploit_details(
                        selected_exploit['exploit_name']
                    )
                    
                    print(f"\nExploit Details:")
                    print(f"  Name: {exploit_details['name']}")
                    print(f"  Description: {exploit_details['description']}")
                    print(f"  Rank: {exploit_details['rank']}")
                    print(f"  Platform: {exploit_details['platform']}")
                    
                    # Run exploit check
                    result = self.msf_interface.run_exploit_check(
                        target_ip,
                        selected_exploit['exploit_name'],
                        selected_exploit['port']
                    )
                    
                    # Display result
                    print("\n" + "="*50)
                    print("EXPLOIT CHECK RESULT")
                    print("="*50)
                    print(f"Target: {result['target']}")
                    print(f"Port: {result['port']}")
                    print(f"Exploit: {result['exploit']}")
                    print(f"Vulnerable: {'YES' if result['vulnerable'] else 'NO'}")
                    print(f"Confidence: {result['confidence']}")
                    print(f"Details: {result['details']}")
                    print("="*50)
                    
                    # Ask if user wants to generate exploit script
                    if result['vulnerable']:
                        choice = input("\n[?] Generate exploit script? (y/N): ").strip().lower()
                        if choice == 'y':
                            payload = self.msf_interface.generate_payload()
                            script_path = self.msf_interface.create_exploit_script(
                                target_ip,
                                selected_exploit['port'],
                                selected_exploit['exploit_name'],
                                payload
                            )
                            
                            if script_path:
                                print_success(f"Exploit script created: {script_path}")
                                print_info("To run the exploit, use: msfconsole -r " + script_path)
                else:
                    print_error("Invalid selection.")
            except ValueError:
                print_error("Invalid input.")
                
        except Exception as e:
            print_error(f"Error during exploit check: {e}")
    
    def _try_all_exploits(self, target_ip: str):
        """Try all potential exploits until one succeeds with detailed reporting."""
        print_info("Trying all exploits automatically...")
        
        if not self.msf_interface:
            print_error("Metasploit interface not initialized.")
            return
        
        successful_exploit = None
        
        for i, exploit in enumerate(self.potential_exploits):
            print_info(f"Trying exploit {i+1}/{len(self.potential_exploits)}: {exploit['exploit_name']} on port {exploit['port']}")
            
            try:
                # Get detailed exploit information
                exploit_details = self.msf_interface.get_exploit_details(exploit['exploit_name'])
                print_info(f"  Description: {exploit_details['description']}")
                print_info(f"  Rank: {exploit_details['rank']}")
                
                result = self.msf_interface.run_exploit_check(
                    target_ip,
                    exploit['exploit_name'],
                    exploit['port']
                )
                
                if result['vulnerable']:
                    successful_exploit = exploit
                    print_success(f"Success! Exploit {exploit['exploit_name']} worked (confidence: {result['confidence']}).")
                    
                    # Show detailed results
                    print_info(f"Exploit Details:")
                    print_info(f"  Target: {result['target']}")
                    print_info(f"  Port: {result['port']}")
                    print_info(f"  Confidence: {result['confidence']}")
                    
                    # Generate exploit script
                    choice = input("\n[?] Generate exploit script? (y/N): ").strip().lower()
                    if choice == 'y':
                        payload = self.msf_interface.generate_payload()
                        script_path = self.msf_interface.create_exploit_script(
                            target_ip,
                            exploit['port'],
                            exploit['exploit_name'],
                            payload
                        )
                        
                        if script_path:
                            print_success(f"Exploit script created: {script_path}")
                            print_info("To run the exploit, use: msfconsole -r " + script_path)
                            print_info("Ensure you have proper authorization before running this script!")
                    
                    break
                else:
                    print_info(f"Exploit {exploit['exploit_name']} did not work (confidence: {result['confidence']}).")
                    
            except Exception as e:
                print_error(f"Error with exploit {exploit['exploit_name']}: {e}")
        
        if not successful_exploit:
            print_error("No exploits were successful.")
        else:
            print_success("Automated exploit testing completed successfully!")
    
    def run_exploit_script(self):
        """Run an exploit script from a file."""
        print_header("RUN EXPLOIT SCRIPT")
        
        if not self.msf_interface:
            print_error("Metasploit interface not initialized.")
            return
        
        try:
            # Ensure exploit directory exists
            exploit_dir = "exploit"
            if not os.path.exists(exploit_dir):
                os.makedirs(exploit_dir)
                print_info(f"Created directory: {exploit_dir}")
            
            # List available .rc files in exploit directory
            import glob
            pattern = os.path.join(exploit_dir, "*.rc")
            rc_files = glob.glob(pattern)
            
            # Sort files by modification time (newest first)
            rc_files.sort(key=os.path.getmtime, reverse=True)
            
            if rc_files:
                print_info("Available exploit script files (newest first):")
                for i, file in enumerate(rc_files, 1):
                    # Show relative path
                    relative_path = os.path.relpath(file, exploit_dir)
                    print(f"  {i}. {relative_path}")
                
                # Automatically select the most recent file
                latest_file = rc_files[0]
                relative_latest = os.path.relpath(latest_file, exploit_dir)
                print_info(f"\nAutomatically selecting most recent file: {relative_latest}")
                
                # Ask user if they want to use the latest file or select another
                choice = input("[?] Use this file? (Y/n): ").strip().lower()
                
                if choice == '' or choice == 'y':
                    script_path = latest_file
                else:
                    # Let user select a file
                    try:
                        file_choice = int(input("[?] Select file number: ")) - 1
                        if 0 <= file_choice < len(rc_files):
                            script_path = rc_files[file_choice]
                        else:
                            print_error("Invalid file selection.")
                            return
                    except ValueError:
                        print_error("Invalid input.")
                        return
            else:
                print_error("No exploit script files found in exploit directory.")
                return
            
            # Show selected file
            print_info(f"Selected file: {script_path}")
            
            # Run the exploit script
            success = self.msf_interface.run_exploit_script(script_path)
            
            if success:
                print_success("Exploit script executed successfully!")
            else:
                print_error("Failed to execute exploit script.")
                print_info("Make sure Metasploit is properly installed and the script file is valid.")
                print_info("You can run the setup (Option 8) to install missing dependencies.")
                
        except Exception as e:
            print_error(f"Error running exploit script: {e}")
    
    def setup_dependencies(self):
        """Setup and install all required dependencies."""
        print_header("SETUP DEPENDENCIES")
        
        try:
            # Detect the operating system
            import platform
            system = platform.system().lower()
            
            print_info(f"Detected OS: {system}")
            
            # Check if running on Termux
            is_termux = os.path.exists("/data/data/com.termux/files/usr") if system == "linux" else False
            
            if is_termux:
                print_info("Running on Termux")
                self._setup_termux()
            elif system == "windows":
                print_info("Running on Windows")
                self._setup_windows()
            elif system == "linux":
                print_info("Running on Linux")
                self._setup_linux()
            elif system == "darwin":
                print_info("Running on macOS")
                self._setup_macos()
            else:
                print_error(f"Unsupported operating system: {system}")
                
        except Exception as e:
            print_error(f"Error during setup: {e}")
    
    def _setup_termux(self):
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
            
            print_info("Checking and installing packages...")
            for package in packages:
                # Check if package is already installed
                try:
                    result = subprocess.run(["dpkg", "-l", package], 
                                          capture_output=True, text=True)
                    if "ii  " + package in result.stdout:
                        print_info(f"{package} is already installed. Skipping...")
                        continue
                except Exception:
                    # If check fails, proceed with installation
                    pass
                
                print_info(f"Installing {package}...")
                os.system(f"pkg install {package} -y")
            
            # Install Python packages
            python_packages = [
                "netifaces"
            ]
            
            print_info("Installing Python packages...")
            for package in python_packages:
                # Check if Python package is already installed
                try:
                    import importlib
                    importlib.import_module(package)
                    print_info(f"Python package {package} is already installed. Skipping...")
                    continue
                except ImportError:
                    pass  # Package not found, proceed with installation
                except Exception:
                    pass  # If check fails, proceed with installation
                
                print_info(f"Installing Python package {package}...")
                os.system(f"pip install {package}")
            
            print_success("Termux setup completed!")
            
        except Exception as e:
            print_error(f"Error during Termux setup: {e}")
    
    def _setup_windows(self):
        """Setup dependencies for Windows environment."""
        print_info("Setting up dependencies for Windows...")
        
        try:
            # Check if running as administrator
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                print_warning("Not running as Administrator. Some installations may fail.")
                print_info("For best results, run this script as Administrator.")
                print_info("Right-click on Command Prompt or PowerShell and select 'Run as Administrator'")
                print_info("")
            
            # Check if Chocolatey is installed
            import subprocess
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
                # Check for lock files and suggest resolution
                lock_file_path = r"C:\ProgramData\chocolatey\lib"
                if os.path.exists(lock_file_path):
                    import glob
                    lock_files = glob.glob(os.path.join(lock_file_path, "*") + "/*lock*")
                    if lock_files:
                        print_warning("Lock files detected. If installation fails, you may need to:")
                        print_info("  1. Close all Chocolatey/PowerShell windows")
                        print_info("  2. Restart your computer")
                        print_info("  3. Run this setup again as Administrator")
                        print_info("")
                
                # Check and install packages using Chocolatey
                packages = [
                    "python",
                    "nmap",
                    "curl"
                ]
                
                print_info("Checking and installing packages with Chocolatey...")
                for package in packages:
                    # Check if package is already installed
                    try:
                        result = subprocess.run(["choco", "list", "--local-only", package], 
                                              capture_output=True, text=True, timeout=30)
                        if package.lower() in result.stdout.lower() and "packages installed" not in result.stdout.lower():
                            print_info(f"{package} is already installed. Skipping...")
                            continue
                    except Exception:
                        # If check fails, proceed with installation
                        pass
                    
                    print_info(f"Installing {package}...")
                    result = os.system(f"choco install {package} -y")
                    if result != 0:
                        print_error(f"Failed to install {package}. Try running as Administrator.")
            else:
                print_warning("Chocolatey not found. Please install packages manually:")
                print_info("  - Python 3.6+ (https://www.python.org/downloads/)")
                print_info("  - Nmap (https://nmap.org/download.html)")
                print_info("  - Git (optional) (https://git-scm.com/download/win)")
                print_info("")
                print_info("To install Chocolatey (recommended):")
                print_info("  1. Run PowerShell as Administrator")
                print_info("  2. Run: Set-ExecutionPolicy Bypass -Scope Process -Force")
                print_info("  3. Run: [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072")
                print_info("  4. Run: iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))")
                print_info("  5. Restart your shell and run this setup again")
                print_info("")
            
            # Install Python packages
            python_packages = [
                "netifaces"
            ]
            
            print_info("Installing Python packages...")
            for package in python_packages:
                print_info(f"Installing Python package {package}...")
                result = os.system(f"pip install {package}")
                if result != 0:
                    print_error(f"Failed to install Python package {package}")
            
            # Provide Metasploit installation instructions
            print_info("")
            print_info("IMPORTANT: Metasploit Framework must be installed separately:")
            print_info("  1. Download Metasploit Framework from: https://github.com/rapid7/metasploit-framework")
            print_info("  2. Or use the official installer: https://www.metasploit.com/download/")
            print_info("  3. Follow the Windows installation guide")
            print_info("  4. Make sure 'msfconsole' is in your PATH after installation")
            print_info("")
            
            print_success("Windows setup completed! Please install Metasploit Framework separately.")
            
        except Exception as e:
            print_error(f"Error during Windows setup: {e}")
    
    def _setup_linux(self):
        """Setup dependencies for Linux environment."""
        print_info("Setting up dependencies for Linux...")
        
        try:
            # Detect package manager
            import subprocess
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
                    # Check if package is already installed
                    check_result = subprocess.run(["dpkg", "-l", package], 
                                                capture_output=True, text=True)
                    if "ii  " + package in check_result.stdout:
                        print_info(f"{package} is already installed. Skipping...")
                        continue
                            
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
                    # Check if package is already installed
                    check_result = subprocess.run(["rpm", "-q", package], 
                                                capture_output=True, text=True)
                    if check_result.returncode == 0:
                        print_info(f"{package} is already installed. Skipping...")
                        continue
                            
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
                    # Check if package is already installed
                    check_result = subprocess.run(["rpm", "-q", package], 
                                                capture_output=True, text=True)
                    if check_result.returncode == 0:
                        print_info(f"{package} is already installed. Skipping...")
                        continue
                            
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
                    # Check if package is already installed
                    check_result = subprocess.run(["pacman", "-Q", package], 
                                                capture_output=True, text=True)
                    if check_result.returncode == 0:
                        print_info(f"{package} is already installed. Skipping...")
                        continue
                            
                    print_info(f"Installing {package}...")
                    os.system(f"sudo pacman -S {package} --noconfirm")
            else:
                print_warning("Unsupported package manager. Please install packages manually:")
                print_info("  - Python 3.6+")
                print_info("  - pip")
                print_info("  - nmap")
                print_info("  - net-tools")
                print_info("  - curl")
            
            # Install Python packages
            python_packages = [
                "netifaces"
            ]
            
            print_info("Installing Python packages...")
            for package in python_packages:
                print_info(f"Installing Python package {package}...")
                os.system("pip3 install " + package)
            
            print_success("Linux setup completed!")
            
        except Exception as e:
            print_error(f"Error during Linux setup: {e}")
    
    def _setup_macos(self):
        """Setup dependencies for macOS environment."""
        print_info("Setting up dependencies for macOS...")
        
        try:
            # Check if Homebrew is installed
            import subprocess
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
                
                print_info("Checking and installing packages with Homebrew...")
                for package in packages:
                    # Check if package is already installed
                    try:
                        result = subprocess.run(["brew", "list", package], 
                                              capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            print_info(f"{package} is already installed. Skipping...")
                            continue
                    except Exception:
                        # If check fails, proceed with installation
                        pass
                    
                    print_info(f"Installing {package}...")
                    os.system(f"brew install {package}")
            else:
                print_warning("Homebrew not found. Please install it first:")
                print_info("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                print_info("Then run this setup again.")
                return
            
            # Install Python packages
            python_packages = [
                "netifaces"
            ]
            
            print_info("Installing Python packages...")
            for package in python_packages:
                print_info(f"Installing Python package {package}...")
                os.system("pip3 install " + package)
            
            print_success("macOS setup completed!")
            
        except Exception as e:
            print_error(f"Error during macOS setup: {e}")
    
    def show_current_status(self):
        """Show current toolkit status."""
        print_header("CURRENT STATUS")
        
        print("Network Discovery:")
        if self.scanner:
            devices = self.scanner.get_devices()
            print(f"  Devices found: {len(devices)}")
        else:
            print("  Not performed")
        
        print("\nTarget Selection:")
        if self.current_target:
            print(f"  Selected target: {self.current_target['ip']} ({self.current_target['hostname']})")
        else:
            print("  No target selected")
        
        print("\nPort Scanning:")
        if self.open_ports:
            print(f"  Open ports found: {len(self.open_ports)}")
            print(f"  Ports: {self.open_ports}")
        else:
            print("  Not performed")
        
        print("\nExploit Search:")
        if self.potential_exploits:
            print(f"  Potential exploits: {len(self.potential_exploits)}")
        else:
            print("  Not performed")
        
        print("\n" + "-"*50)

def main():
    """Main entry point."""
    try:
        toolkit = SecurityToolkit()
        toolkit.run()
    except KeyboardInterrupt:
        print("\n\n[*] Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()