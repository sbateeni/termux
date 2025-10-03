#!/usr/bin/env python3
"""
Port Scanner Module
Scans open ports on a target IP address.
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict, Tuple, Optional

class PortScanner:
    def __init__(self, target_ip: str):
        """
        Initialize port scanner with target IP.
        
        Args:
            target_ip: IP address to scan for open ports
        """
        self.target_ip = target_ip
        self.open_ports = []
        self.scan_results = {}
        self.scan_start_time = None
        self.scan_end_time = None
    
    def scan_port(self, port: int, timeout: float = 1.0) -> Tuple[int, bool]:
        """
        Scan a single port on the target IP using multiple methods.
        
        Args:
            port: Port number to scan
            timeout: Connection timeout in seconds
            
        Returns:
            Tuple of (port, is_open)
        """
        # Method 1: TCP Connect scan
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Attempt connection
            result = sock.connect_ex((self.target_ip, port))
            sock.close()
            
            # Check if connection was successful
            is_open = (result == 0)
            if is_open:
                return (port, True)
        except Exception:
            pass
        
        # Method 2: Try with different socket options
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            result = sock.connect_ex((self.target_ip, port))
            sock.close()
            
            is_open = (result == 0)
            return (port, is_open)
        except Exception:
            pass
        
        return (port, False)
    
    def scan_port_range(self, start_port: int, end_port: int, 
                       max_threads: int = 100, timeout: float = 1.0) -> List[int]:
        """
        Scan a range of ports for open connections.
        
        Args:
            start_port: Starting port number
            end_port: Ending port number
            max_threads: Maximum number of concurrent threads
            timeout: Connection timeout in seconds
            
        Returns:
            List of open port numbers
        """
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError("Invalid port range. Ports must be between 1-65535")
        
        print(f"[*] Scanning ports {start_port}-{end_port} on {self.target_ip}")
        print(f"[*] Using {max_threads} threads with {timeout}s timeout")
        
        self.scan_start_time = time.time()
        self.open_ports = []
        self.scan_results = {}
        
        # Generate port list
        port_list = list(range(start_port, end_port + 1))
        
        # Use ThreadPoolExecutor for concurrent scanning
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit all port scanning tasks
            future_to_port = {
                executor.submit(self.scan_port, port, timeout): port 
                for port in port_list
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_port):
                port, is_open = future.result()
                self.scan_results[port] = is_open
                
                if is_open:
                    self.open_ports.append(port)
                    print(f"[+] Port {port} is OPEN")
        
        self.scan_end_time = time.time()
        self.open_ports.sort()
        
        print(f"[+] Scan complete! Found {len(self.open_ports)} open ports")
        return self.open_ports
    
    def scan_common_ports(self, max_threads: int = 50, timeout: float = 1.0) -> List[int]:
        """
        Scan common ports that are frequently used by services.
        
        Args:
            max_threads: Maximum number of concurrent threads
            timeout: Connection timeout in seconds
            
        Returns:
            List of open port numbers
        """
        # Common ports list
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
            1723, 3306, 3389, 5900, 8080, 8443
        ]
        
        print(f"[*] Scanning common ports on {self.target_ip}")
        return self.scan_port_range(
            min(common_ports), 
            max(common_ports), 
            max_threads, 
            timeout
        )
    
    def get_service_name(self, port: int) -> str:
        """
        Get service name for a given port number.
        
        Args:
            port: Port number
            
        Returns:
            Service name string
        """
        service_map = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            111: "RPCBind",
            135: "MS RPC",
            139: "NetBIOS",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            1723: "PPTP",
            3306: "MySQL",
            3389: "RDP",
            5900: "VNC",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt"
        }
        
        return service_map.get(port, "Unknown")
    
    def display_results(self) -> None:
        """Display scan results in a formatted table."""
        if not self.open_ports:
            print("[-] No open ports found")
            return
        
        scan_duration = 0
        if self.scan_start_time and self.scan_end_time:
            scan_duration = self.scan_end_time - self.scan_start_time
        
        print("\n" + "="*70)
        print("PORT SCAN RESULTS")
        print("="*70)
        print(f"Target IP: {self.target_ip}")
        print(f"Scan Duration: {scan_duration:.2f} seconds")
        print(f"Open Ports Found: {len(self.open_ports)}")
        print("-"*70)
        print(f"{'Port':<8} {'Service':<15} {'Status'}")
        print("-"*70)
        
        for port in self.open_ports:
            service = self.get_service_name(port)
            print(f"{port:<8} {service:<15} OPEN")
        
        print("-"*70)
    
    def get_open_ports(self) -> List[int]:
        """Return list of open ports."""
        return self.open_ports
    
    def get_scan_summary(self) -> Dict:
        """
        Get summary of port scan results.
        
        Returns:
            Dictionary with scan summary information
        """
        scan_duration = 0
        if self.scan_start_time and self.scan_end_time:
            scan_duration = self.scan_end_time - self.scan_start_time
        
        return {
            'target_ip': self.target_ip,
            'open_ports': self.open_ports,
            'scan_duration': scan_duration,
            'total_ports_scanned': len(self.scan_results),
            'open_port_details': [
                {
                    'port': port,
                    'service': self.get_service_name(port)
                }
                for port in self.open_ports
            ]
        }
    
    def save_results(self, filename: Optional[str] = None) -> None:
        """
        Save scan results to a file.
        
        Args:
            filename: Output filename (defaults to target_ip_ports.txt)
        """
        if not filename:
            filename = f"{self.target_ip.replace('.', '_')}_ports.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("Port Scan Results\n")
                f.write("================\n")
                f.write(f"Target IP: {self.target_ip}\n")
                f.write(f"Scan Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if self.scan_start_time and self.scan_end_time:
                    scan_duration = self.scan_end_time - self.scan_start_time
                    f.write(f"Scan Duration: {scan_duration:.2f} seconds\n")
                
                f.write(f"\nOpen Ports ({len(self.open_ports)}):\n")
                f.write("-" * 30 + "\n")
                
                for port in self.open_ports:
                    service = self.get_service_name(port)
                    f.write(f"Port {port}: {service} (OPEN)\n")
            
            print(f"[+] Results saved to {filename}")
        except Exception as e:
            print(f"[-] Error saving results: {e}")

def main():
    """Test the port scanner module."""
    # Test with localhost
    scanner = PortScanner("127.0.0.1")
    
    print("Port Scanner Test")
    print("================")
    
    # Scan common ports
    open_ports = scanner.scan_common_ports(max_threads=20, timeout=0.5)
    
    # Display results
    scanner.display_results()
    
    # Save results
    scanner.save_results()

if __name__ == "__main__":
    main()