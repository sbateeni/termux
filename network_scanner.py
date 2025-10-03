#!/usr/bin/env python3
"""
Network Scanner Module
Discovers devices on the local network and retrieves their IP and MAC addresses.
"""

import subprocess
import socket
import struct
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import re
from typing import List, Dict, Tuple, Optional

class NetworkScanner:
    def __init__(self):
        self.devices = []
        self.local_ip = self._get_local_ip()
        self.network_range = self._get_network_range()
    
    def _get_local_ip(self) -> str:
        """Get the local IP address of the machine."""
        try:
            # Try multiple methods to get local IP
            # Method 1: Connect to external server
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            try:
                # Method 2: Use hostname resolution
                import subprocess
                if os.name == 'nt':  # Windows
                    result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'IPv4' in line and '192.168.' in line:
                            ip = line.split(':')[-1].strip()
                            return ip
                else:  # Unix/Linux/Mac
                    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout.strip().split()[0]
            except Exception:
                pass
        return "192.168.1.1"  # Fallback
    
    def _get_network_range(self) -> str:
        """Calculate network range based on local IP."""
        ip_parts = self.local_ip.split('.')
        return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
    
    def _ping_host(self, ip: str) -> bool:
        """Ping a single host to check if it's alive."""
        try:
            # Check if running on Termux
            is_termux = "com.termux" in os.environ.get("PREFIX", "")
            
            if is_termux:
                # Use ping command appropriate for Termux
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            elif os.name == 'nt':  # Windows
                # Use ping command appropriate for Windows
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", ip],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            else:  # Unix/Linux/Mac
                # Use ping command appropriate for Unix/Linux/Mac
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_mac_address(self, ip: str) -> Optional[str]:
        """Get MAC address for a given IP using ARP table or other methods."""
        try:
            # Check if running on Termux
            is_termux = "com.termux" in os.environ.get("PREFIX", "")
            
            if is_termux:
                # For Termux, try different approaches
                try:
                    # Try using ip neighbor command first
                    result = subprocess.run(
                        ["ip", "neighbor", "show", ip],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        # Parse output for MAC address
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ip in line and 'lladdr' in line:
                                # Extract MAC address
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part == 'lladdr' and i + 1 < len(parts):
                                        mac = parts[i + 1]
                                        return mac.upper()
                except Exception:
                    pass
                
                # Try arp command if ip neighbor didn't work
                try:
                    result = subprocess.run(
                        ["arp", ip],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        # Parse ARP output for MAC address
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ip in line:
                                # Look for MAC address pattern (xx:xx:xx:xx:xx:xx)
                                mac_match = re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', line)
                                if mac_match:
                                    return mac_match.group(0).upper()
                except Exception:
                    pass
                    
                return None
            
            # Method 1: Use arp command to get MAC address (non-Termux)
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ["arp", "-a", ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:  # Unix/Linux/Mac
                result = subprocess.run(
                    ["arp", ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            if result.returncode == 0:
                # Parse ARP output for MAC address
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ip in line:
                        # Look for MAC address pattern (xx-xx-xx-xx-xx-xx)
                        mac_match = re.search(r'([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}', line)
                        if mac_match:
                            return mac_match.group(0).replace('-', ':').upper()
            
            # Method 2: Try alternative approach for Windows
            if os.name == 'nt':
                try:
                    result = subprocess.run(
                        ["getmac", "/v"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ip in line:
                                # Look for MAC address pattern
                                mac_match = re.search(r'([0-9a-fA-F]{2}[-]){5}[0-9a-fA-F]{2}', line)
                                if mac_match:
                                    return mac_match.group(0).replace('-', ':').upper()
                except Exception:
                    pass
            
            return None
        except Exception:
            return None
    
    def _get_hostname(self, ip: str) -> str:
        """Get hostname for a given IP address."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return "Unknown"
    
    def _scan_single_ip(self, ip: str) -> Optional[Dict]:
        """Scan a single IP address and return device info if alive."""
        if self._ping_host(ip):
            print(f"[+] Found device: {ip}")
            
            # Get MAC address (might take a moment)
            mac = self._get_mac_address(ip)
            hostname = self._get_hostname(ip)
            
            return {
                'ip': ip,
                'mac': mac or 'Unknown',
                'hostname': hostname,
                'status': 'alive'
            }
        return None
    
    def scan_network(self, max_threads: int = 50) -> List[Dict]:
        """
        Scan the entire network range for alive devices.
        
        Args:
            max_threads: Maximum number of concurrent threads
            
        Returns:
            List of dictionaries containing device information
        """
        print(f"[*] Scanning network range: {self.network_range}")
        print(f"[*] Local IP: {self.local_ip}")
        print("[*] Starting network scan...")
        
        # Check if running on Termux
        is_termux = "com.termux" in os.environ.get("PREFIX", "")
        if is_termux:
            print("[*] Detected Termux environment - using alternative scanning method...")
            return self._scan_network_termux()
        
        # Generate IP range
        base_ip = self.local_ip.rsplit('.', 1)[0]
        ip_list = [f"{base_ip}.{i}" for i in range(1, 255)]
        
        self.devices = []
        
        # Use ThreadPoolExecutor for concurrent scanning
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit all IP scanning tasks
            future_to_ip = {executor.submit(self._scan_single_ip, ip): ip for ip in ip_list}
            
            # Collect results as they complete
            for future in as_completed(future_to_ip):
                result = future.result()
                if result:
                    self.devices.append(result)
        
        # Sort devices by IP
        self.devices.sort(key=lambda x: socket.inet_aton(x['ip']))
        
        print(f"[+] Scan complete! Found {len(self.devices)} devices")
        return self.devices
    
    def _scan_network_termux(self) -> List[Dict]:
        """Alternative network scanning method for Termux."""
        self.devices = []
        
        try:
            # Use nmap for scanning in Termux as it's more reliable
            print("[*] Using nmap for scanning in Termux...")
            
            # Check if nmap is installed
            nmap_installed = shutil.which("nmap") is not None
            if not nmap_installed:
                print("[-] nmap is not installed. Please install it with: pkg install nmap")
                print("[-] Falling back to basic ping scan...")
                return self._basic_ping_scan()
            
            # Run nmap scan
            result = subprocess.run(
                ["nmap", "-sn", self.network_range],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse nmap output
                lines = result.stdout.strip().split('\n')
                current_ip = None
                
                for line in lines:
                    # Look for IP addresses
                    ip_match = re.search(r'Nmap scan report for ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', line)
                    if ip_match:
                        current_ip = ip_match.group(1)
                        continue
                    
                    # Look for MAC addresses
                    if current_ip and 'MAC Address:' in line:
                        mac_match = re.search(r'MAC Address: ([0-9A-F:]+)', line)
                        if mac_match:
                            mac = mac_match.group(1)
                            hostname = "Unknown"  # nmap doesn't always provide hostname in this format
                            
                            # Try to get hostname
                            try:
                                hostname = socket.gethostbyaddr(current_ip)[0]
                            except Exception:
                                pass
                            
                            self.devices.append({
                                'ip': current_ip,
                                'mac': mac,
                                'hostname': hostname,
                                'status': 'alive'
                            })
                            current_ip = None
            
            # Sort devices by IP
            self.devices.sort(key=lambda x: socket.inet_aton(x['ip']))
            
            print(f"[+] Scan complete! Found {len(self.devices)} devices")
            return self.devices
            
        except Exception as e:
            print(f"[-] Error during nmap scan: {e}")
            print("[-] Falling back to basic ping scan...")
            return self._basic_ping_scan()
    
    def _basic_ping_scan(self) -> List[Dict]:
        """Basic ping scan as fallback method."""
        print("[*] Using basic ping scan...")
        
        # Generate IP range
        base_ip = self.local_ip.rsplit('.', 1)[0]
        ip_list = [f"{base_ip}.{i}" for i in range(1, 255)]
        
        # Try to ping each IP sequentially (slower but more compatible)
        for ip in ip_list:
            if self._ping_host(ip):
                print(f"[+] Found device: {ip}")
                mac = self._get_mac_address(ip)
                hostname = self._get_hostname(ip)
                
                self.devices.append({
                    'ip': ip,
                    'mac': mac or 'Unknown',
                    'hostname': hostname,
                    'status': 'alive'
                })
        
        # Sort devices by IP
        self.devices.sort(key=lambda x: socket.inet_aton(x['ip']))
        
        print(f"[+] Scan complete! Found {len(self.devices)} devices")
        return self.devices
    
    def display_devices(self) -> None:
        """Display discovered devices in a formatted table."""
        if not self.devices:
            print("[-] No devices found")
            return
        
        print("\n" + "="*80)
        print("DISCOVERED NETWORK DEVICES")
        print("="*80)
        print(f"{'#':<3} {'IP Address':<15} {'MAC Address':<18} {'Hostname':<25} {'Status'}")
        print("-"*80)
        
        for i, device in enumerate(self.devices, 1):
            print(f"{i:<3} {device['ip']:<15} {device['mac']:<18} {device['hostname']:<25} {device['status']}")
        
        print("-"*80)
        print(f"Total devices found: {len(self.devices)}")
    
    def get_devices(self) -> List[Dict]:
        """Return the list of discovered devices."""
        return self.devices
    
    def save_results(self, filename: str = "network_scan_results.txt") -> None:
        """Save scan results to a file."""
        try:
            with open(filename, 'w') as f:
                f.write("Network Scan Results\n")
                f.write("===================\n")
                f.write(f"Scan Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Network Range: {self.network_range}\n")
                f.write(f"Local IP: {self.local_ip}\n\n")
                
                for device in self.devices:
                    f.write(f"IP: {device['ip']}\n")
                    f.write(f"MAC: {device['mac']}\n")
                    f.write(f"Hostname: {device['hostname']}\n")
                    f.write(f"Status: {device['status']}\n")
                    f.write("-" * 30 + "\n")
            
            print(f"[+] Results saved to {filename}")
        except Exception as e:
            print(f"[-] Error saving results: {e}")

def main():
    """Test the network scanner module."""
    scanner = NetworkScanner()
    
    print("Network Scanner Test")
    print("===================")
    
    # Perform network scan
    devices = scanner.scan_network()
    
    # Display results
    scanner.display_devices()
    
    # Save results
    scanner.save_results()

if __name__ == "__main__":
    main()