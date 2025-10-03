#!/usr/bin/env python3
"""
Network Security Testing Toolkit
Main controller script that integrates all modules
"""

import os
import sys
import importlib.util
import subprocess

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
try:
    from network_scanner import NetworkScanner
    from target_selector import TargetSelector
    from port_scanner import PortScanner
    from metasploit_interface import MetasploitInterface
    from config import config  # Import the global config instance
    from utils import print_header, print_info, print_success, print_warning, print_error
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run setup.py first to install dependencies")
    sys.exit(1)

class NetworkSecurityToolkit:
    def __init__(self):
        self.scanner = NetworkScanner()
        self.selector = None  # Will be initialized after scanning
        self.port_scanner = None  # Will be initialized with target IP
        self.metasploit = MetasploitInterface()
        self.devices = []
        self.selected_target = None

    def is_admin(self):
        """Check if the script is running with administrator privileges"""
        try:
            # Unix/Linux/macOS
            return os.getuid() == 0
        except AttributeError:
            # Windows - use a more robust method
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                # Fallback method for Windows
                try:
                    return os.system("net session >nul 2>&1") == 0
                except Exception:
                    return False

    def setup_dependencies(self):
        """Setup all required dependencies"""
        print_header("SETUP DEPENDENCIES")
        
        # Detect OS
        import platform
        import shutil
        
        os_name = platform.system().lower()
        print_info(f"Detected OS: {os_name}")
        
        if os_name == "windows":
            print_info("Running on Windows")
            print_info("Setting up dependencies for Windows...")
            
            try:
                # Check if running as administrator
                if not self.is_admin():
                    print_warning("This toolkit requires administrator privileges on Windows for some operations.")
                    print_info("Some features may not work properly without admin rights.")
                    print_info("Please run this script as Administrator for full functionality.")
                    input("Press Enter to continue anyway (some features may not work)...")
                
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
                
                if choco_installed:
                    # Install/update Nmap
                    print_info("Installing/Updating Nmap...")
                    try:
                        result = subprocess.run(
                            ["choco", "install", "nmap", "-y"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            print_success("Nmap installed/updated successfully")
                        else:
                            print_warning(f"Nmap installation/update may have issues: {result.stdout}")
                    except Exception as e:
                        print_error(f"Error with Nmap: {e}")
                    
                    # Install/update Metasploit automatically
                    print_info("Installing/Updating Metasploit...")
                    try:
                        # First, try to install via Chocolatey
                        result = subprocess.run(
                            ["choco", "install", "metasploit", "-y"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            print_success("Metasploit installed/updated successfully via Chocolatey")
                        else:
                            print_warning("Chocolatey installation failed, trying alternative method...")
                            # Alternative method: Download and install Metasploit directly
                            self._install_metasploit_windows()
                    except Exception as e:
                        print_error(f"Error with Metasploit installation: {e}")
                        print_info("Trying alternative installation method...")
                        self._install_metasploit_windows()
                else:
                    print_warning("Chocolatey not available. Please install Nmap and Metasploit manually.")
                    self._install_metasploit_windows()
                    
            except Exception as e:
                print_error(f"Error during Windows setup: {e}")
                
        elif os_name == "linux":
            print_info("Running on Linux")
            # Check if running on Termux
            if "com.termux" in os.environ.get("PREFIX", ""):
                print_info("Running on Termux")
                try:
                    # Update package list
                    print_info("Updating package lists...")
                    subprocess.run(["pkg", "update", "-y"], check=True)
                    
                    # Install basic network tools
                    print_info("Installing network tools...")
                    subprocess.run(["pkg", "install", "inetutils", "traceroute", "net-tools", "-y"], check=True)
                    
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
                            self._install_metasploit_termux()
                    except Exception as e:
                        print_warning(f"Automated installation failed: {e}")
                        print_info("Trying manual installation...")
                        self._install_metasploit_termux()
                        
                except subprocess.CalledProcessError as e:
                    print_error(f"Error installing packages in Termux: {e}")
                    print_info("Try manually installing Metasploit with:")
                    print_info("curl -fsSL https://kutt.it/msf | bash")
                except Exception as e:
                    print_error(f"Unexpected error in Termux setup: {e}")
            else:
                print_info("Running on standard Linux")
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
                
                if pkg_manager:
                    print_info(f"Detected package manager: {pkg_manager}")
                    try:
                        update_cmd, install_cmd = package_managers[pkg_manager]
                        
                        # Update package lists
                        print_info("Updating package lists...")
                        subprocess.run(update_cmd, shell=True, check=True)
                        print_success("Package lists updated")
                        
                        # Install packages based on package manager
                        packages = {
                            "apt": ["nmap", "metasploit-framework"],
                            "yum": ["nmap", "metasploit"],
                            "dnf": ["nmap", "metasploit"],
                            "pacman": ["nmap", "metasploit"]
                        }
                        
                        for package in packages.get(pkg_manager, ["nmap", "metasploit"]):
                            print_info(f"Installing {package}...")
                            subprocess.run(f"{install_cmd} {package}", shell=True, check=True)
                            print_success(f"{package} installed successfully")
                            
                    except subprocess.CalledProcessError as e:
                        print_error(f"Error with package manager: {e}")
                    except Exception as e:
                        print_error(f"Unexpected error in Linux setup: {e}")
                else:
                    print_error("No supported package manager found")
                    
        elif os_name == "darwin":
            print_info("Running on macOS")
            try:
                # Check if Homebrew is installed
                if shutil.which("brew") is None:
                    print_info("Installing Homebrew...")
                    brew_install_cmd = (
                        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/'
                        'Homebrew/install/HEAD/install.sh)"'
                    )
                    subprocess.run(brew_install_cmd, shell=True, check=True)
                    print_success("Homebrew installed successfully")
                
                # Update Homebrew
                print_info("Updating Homebrew...")
                subprocess.run("brew update", shell=True, check=True)
                print_success("Homebrew updated")
                
                # Install packages
                packages = ["nmap", "metasploit"]
                for package in packages:
                    print_info(f"Installing {package}...")
                    subprocess.run(f"brew install {package}", shell=True, check=True)
                    print_success(f"{package} installed successfully")
                    
            except subprocess.CalledProcessError as e:
                print_error(f"Error in macOS setup: {e}")
            except Exception as e:
                print_error(f"Unexpected error in macOS setup: {e}")
        else:
            print_error(f"Unsupported OS: {os_name}")
            return
        
        # Install Python packages
        print_info("Installing Python dependencies...")
        try:
            python_packages = ["scapy", "python-nmap", "requests"]
            for package in python_packages:
                print_info(f"Installing {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print_success(f"{package} installed successfully")
                
        except subprocess.CalledProcessError as e:
            print_error(f"Error installing Python packages: {e}")
        except Exception as e:
            print_error(f"Unexpected error installing Python packages: {e}")
            
        print_success("Dependency setup completed!")
        input("Press Enter to continue...")

    def _install_metasploit_windows(self):
        """Install Metasploit on Windows using the official installer"""
        try:
            import platform
            import urllib.request
            import tempfile
            import os
            
            print_info("Attempting to download and install Metasploit automatically...")
            
            # Check system architecture
            arch = platform.machine().lower()
            is_64bit = arch in ['amd64', 'x86_64', 'arm64']
            
            # For Windows, we'll try to download the official installer
            # Note: This is a simplified approach. In practice, you would need to
            # check the official Metasploit website for the latest download link
            print_info("Downloading Metasploit installer...")
            
            # Create a temporary directory for the installation
            with tempfile.TemporaryDirectory() as temp_dir:
                installer_path = os.path.join(temp_dir, "metasploit-installer.exe")
                
                # Try to download the installer (this is a placeholder URL)
                # In a real implementation, you would need to get the actual download link
                print_warning("Automatic download of Metasploit installer is not implemented due to dynamic URLs.")
                print_info("Please download the Metasploit installer manually from:")
                print_info("https://www.metasploit.com/download/")
                print_info("After downloading, run the installer as Administrator.")
                
                # For now, we'll just provide instructions
                print_info("Installation steps:")
                print_info("1. Download the Metasploit installer from the link above")
                print_info("2. Run the installer as Administrator")
                print_info("3. Make sure to add Metasploit to your PATH during installation")
                print_info("4. Restart your command prompt/terminal after installation")
                
        except Exception as e:
            print_error(f"Error during Metasploit installation: {e}")
            print_info("Please install Metasploit manually from: https://www.metasploit.com/download/")

    def _install_metasploit_termux(self):
        """Install Metasploit on Termux using the gushmazuko script"""
        try:
            import os
            
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

    def check_for_updates(self):
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

    def scan_network(self):
        """Scan network for connected devices"""
        print_header("NETWORK SCAN")
        try:
            # Check if running on Termux and handle accordingly
            import platform
            if "com.termux" in os.environ.get("PREFIX", "") and platform.system().lower() == "linux":
                print_info("Running on Termux - using alternative scanning method...")
                print_info("Installing required tools...")
                try:
                    # Install required tools for Termux
                    subprocess.run(["pkg", "install", "nmap", "net-tools", "-y"], check=True)
                    print_success("Required tools installed")
                except Exception as e:
                    print_warning(f"Could not install tools automatically: {e}")
                    print_info("Please manually install: pkg install nmap net-tools")
            
            self.devices = self.scanner.scan_network()
            if self.devices:
                print_success(f"Found {len(self.devices)} devices:")
                for i, device in enumerate(self.devices):
                    print_info(f"{i+1}. IP: {device['ip']} | MAC: {device['mac']}")
            else:
                print_warning("No devices found on network")
                print_info("If you're on Termux, network scanning might be limited.")
                print_info("Try using nmap directly: nmap -sn 192.168.1.0/24")
        except Exception as e:
            print_error(f"Error during network scan: {e}")
            print_info("If you're on Termux, try: nmap -sn your_network_range")
        input("\nPress Enter to continue...")

    def select_target(self):
        """Select target device from scanned devices"""
        if not self.devices:
            print_error("No devices scanned yet. Please scan network first.")
            input("Press Enter to continue...")
            return
            
        print_header("TARGET SELECTION")
        try:
            # Initialize the selector with the scanned devices
            self.selector = TargetSelector(self.devices)
            self.selected_target = self.selector.select_target_interactive()
            if self.selected_target:
                print_success(f"Selected target: {self.selected_target['ip']}")
            else:
                print_info("No target selected")
        except Exception as e:
            print_error(f"Error during target selection: {e}")
        input("Press Enter to continue...")

    def scan_ports(self):
        """Scan ports on selected target"""
        if not self.selected_target:
            print_error("No target selected. Please select a target first.")
            input("Press Enter to continue...")
            return
            
        print_header("PORT SCAN")
        try:
            target_ip = self.selected_target['ip']
            # Initialize the port scanner with the target IP
            self.port_scanner = PortScanner(target_ip)
            print_info(f"Scanning ports on {target_ip}...")
            
            # Scan common ports
            open_ports = self.port_scanner.scan_common_ports()
            
            if open_ports:
                print_success(f"Found {len(open_ports)} open ports:")
                for port in self.port_scanner.get_open_ports():
                    service = self.port_scanner.get_service_name(port)
                    print_info(f"Port {port}/tcp: {service}")
            else:
                print_warning("No open ports found")
        except Exception as e:
            print_error(f"Error during port scan: {e}")
        input("Press Enter to continue...")

    def run_exploits(self):
        """Run Metasploit exploits on selected target"""
        if not self.selected_target:
            print_error("No target selected. Please select a target first.")
            input("Press Enter to continue...")
            return
            
        print_header("METASPLOIT EXPLOITATION")
        try:
            target_ip = self.selected_target['ip']
            print_info(f"Running exploits on {target_ip}...")
            
            # First check if Metasploit is installed
            if not self.metasploit.check_metasploit_installed():
                print_error("Metasploit is not installed or not in PATH")
                print_info("Please install Metasploit and ensure it's in your system PATH")
                print_info("On Termux, use: curl -fsSL https://kutt.it/msf | bash")
                input("Press Enter to continue...")
                return
            
            # If we don't have port scan results, scan common ports first
            if self.port_scanner is None:
                print_info("Scanning common ports first...")
                self.port_scanner = PortScanner(target_ip)
                self.port_scanner.scan_common_ports()
            
            open_ports = self.port_scanner.get_open_ports()
            
            # Search for exploits
            exploits = self.metasploit.search_exploits(target_ip, open_ports)
            
            if not exploits:
                print_warning("No exploits found for target")
                input("Press Enter to continue...")
                return
            
            # Display found exploits
            self.metasploit.display_exploits(exploits)
            
            # Try exploits until one succeeds
            success = False
            for exploit in exploits:
                print_info(f"Trying exploit: {exploit['exploit_name']}")
                
                # Check if target is vulnerable to this exploit
                check_result = self.metasploit.run_exploit_check(
                    target_ip,
                    exploit['exploit_name'],
                    exploit['port']
                )
                
                if check_result.get('vulnerable', False):
                    print_success(f"Target is vulnerable to {exploit['exploit_name']}")
                    
                    # Generate payload
                    payload = self.metasploit.generate_payload()
                    
                    # Create exploit script
                    script_path = self.metasploit.create_exploit_script(
                        target_ip,
                        exploit['port'],
                        exploit['exploit_name'],
                        payload
                    )
                    
                    if script_path:
                        print_info(f"Created exploit script: {script_path}")
                        print_warning("Exploit script created. You can run it manually with option 5.")
                        success = True
                        break
                    else:
                        print_error("Failed to create exploit script")
                else:
                    print_info(f"Target not vulnerable to {exploit['exploit_name']}")
            
            if success:
                print_success("Exploitation completed successfully!")
            else:
                print_warning("Exploitation attempts completed with no successful exploits")
                
        except Exception as e:
            print_error(f"Error during exploitation: {e}")
        input("Press Enter to continue...")

    def run_single_exploit(self):
        """Run a single Metasploit exploit"""
        if not self.selected_target:
            print_error("No target selected. Please select a target first.")
            input("Press Enter to continue...")
            return
            
        print_header("SINGLE EXPLOIT EXECUTION")
        try:
            target_ip = self.selected_target['ip']
            print_info(f"Running single exploit on {target_ip}...")
            
            # Check if Metasploit is installed
            if not self.metasploit.check_metasploit_installed():
                print_error("Metasploit is not installed or not in PATH")
                print_info("Please install Metasploit and ensure it's in your system PATH")
                print_info("On Termux, use: curl -fsSL https://kutt.it/msf | bash")
                input("Press Enter to continue...")
                return
            
            # List available exploit scripts
            exploit_dir = os.path.join(os.path.dirname(__file__), "exploit")
            if not os.path.exists(exploit_dir):
                print_error("Exploit directory not found")
                input("Press Enter to continue...")
                return
                
            exploit_files = [f for f in os.listdir(exploit_dir) if f.endswith('.rc')]
            
            if not exploit_files:
                print_error("No exploit scripts found")
                input("Press Enter to continue...")
                return
                
            print_info("Available exploit scripts:")
            for i, filename in enumerate(exploit_files):
                print_info(f"{i+1}. {filename}")
                
            try:
                choice = int(input("\nSelect exploit script (number): ")) - 1
                if 0 <= choice < len(exploit_files):
                    selected_script = os.path.join(exploit_dir, exploit_files[choice])
                    print_info(f"Running exploit: {exploit_files[choice]}")
                    
                    # Confirm execution
                    confirm = input("\n[!] WARNING: This will execute a real exploit. Continue? (y/N): ").strip().lower()
                    if confirm != 'y':
                        print_info("Exploit execution cancelled")
                        input("Press Enter to continue...")
                        return
                    
                    # Execute the exploit using the Metasploit interface method
                    success = self.metasploit.run_exploit_script(selected_script)
                    
                    if success:
                        print_success("Exploit executed successfully!")
                    else:
                        print_error("Exploit execution failed")
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Invalid input")
                
        except Exception as e:
            print_error(f"Error during single exploit execution: {e}")
        input("Press Enter to continue...")

    def show_menu(self):
        """Display main menu"""
        print_header("NETWORK SECURITY TESTING TOOLKIT")
        print("1. Scan Network")
        print("2. Select Target")
        print("3. Scan Ports")
        print("4. Run Automated Exploits")
        print("5. Run Single Exploit")
        print("6. Show Selected Target")
        print("7. Rescan Network")
        print("8. Setup Dependencies")
        print("9. Check for Updates")
        print("0. Exit")

    def show_selected_target(self):
        """Show currently selected target"""
        print_header("SELECTED TARGET")
        if self.selected_target:
            print_info(f"IP Address: {self.selected_target['ip']}")
            print_info(f"MAC Address: {self.selected_target['mac']}")
        else:
            print_info("No target selected")
        input("Press Enter to continue...")

    def rescan_network(self):
        """Rescan network for devices"""
        print_header("NETWORK RESCAN")
        try:
            print_info("Rescanning network...")
            self.devices = self.scanner.scan_network()
            if self.devices:
                print_success(f"Found {len(self.devices)} devices:")
                for i, device in enumerate(self.devices):
                    print_info(f"{i+1}. IP: {device['ip']} | MAC: {device['mac']}")
                    
                # Auto-select if only one device found
                if len(self.devices) == 1:
                    self.selector = TargetSelector(self.devices)
                    self.selected_target = self.devices[0]
                    print_success(f"Auto-selected only device: {self.selected_target['ip']}")
            else:
                print_warning("No devices found on network")
                print_info("If you're on Termux, network scanning might be limited.")
                print_info("Try using nmap directly: nmap -sn 192.168.1.0/24")
        except Exception as e:
            print_error(f"Error during network rescan: {e}")
            print_info("If you're on Termux, try: nmap -sn your_network_range")
        input("Press Enter to continue...")

    def run(self):
        """Main application loop"""
        # Check if running on Termux and provide guidance
        import platform
        if "com.termux" in os.environ.get("PREFIX", "") and platform.system().lower() == "linux":
            print_warning("Running on Termux")
            print_info("Some features may be limited on Android.")
            print_info("Make sure you have installed all required packages.")
        
        while True:
            self.show_menu()
            try:
                choice = input("\n[?] Select option: ").strip()
                
                if choice == "1":
                    self.scan_network()
                elif choice == "2":
                    self.select_target()
                elif choice == "3":
                    self.scan_ports()
                elif choice == "4":
                    self.run_exploits()
                elif choice == "5":
                    self.run_single_exploit()
                elif choice == "6":
                    self.show_selected_target()
                elif choice == "7":
                    self.rescan_network()
                elif choice == "8":
                    self.setup_dependencies()
                elif choice == "9":
                    self.check_for_updates()
                elif choice == "0":
                    print_info("Exiting Network Security Toolkit...")
                    break
                else:
                    print_error("Invalid option. Please try again.")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n[i] Interrupted by user")
                print_info("Exiting Network Security Toolkit...")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")
                input("Press Enter to continue...")

def main():
    """Entry point"""
    try:
        toolkit = NetworkSecurityToolkit()
        toolkit.run()
    except Exception as e:
        print_error(f"Failed to start toolkit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()