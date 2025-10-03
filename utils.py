#!/usr/bin/env python3
"""
Utility Module
Provides common utility functions for the security toolkit.
"""

import os
import sys
import platform
from typing import List, Dict, Any

def clear_screen():
    """Clear the terminal screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_header(text: str):
    """
    Print a formatted header.
    
    Args:
        text: Header text to display
    """
    width = max(len(text) + 4, 50)
    print("\n" + "=" * width)
    print(f"{text.upper():^{width}}")
    print("=" * width)

def print_info(text: str):
    """
    Print informational message.
    
    Args:
        text: Information text to display
    """
    print(f"[*] {text}")

def print_success(text: str):
    """
    Print success message.
    
    Args:
        text: Success text to display
    """
    print(f"[+] {text}")

def print_error(text: str):
    """
    Print error message.
    
    Args:
        text: Error text to display
    """
    print(f"[-] {text}")

def print_warning(text: str):
    """
    Print warning message.
    
    Args:
        text: Warning text to display
    """
    print(f"[!] {text}")

def is_valid_ip(ip: str) -> bool:
    """
    Validate IP address format.
    
    Args:
        ip: IP address string to validate
        
    Returns:
        True if valid IP format, False otherwise
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            num = int(part)
            if not 0 <= num <= 255:
                return False
        return True
    except ValueError:
        return False

def is_valid_port(port: int) -> bool:
    """
    Validate port number.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid port (1-65535), False otherwise
    """
    return isinstance(port, int) and 1 <= port <= 65535

def format_time(seconds: float) -> str:
    """
    Format time duration in a human-readable format.
    
    Args:
        seconds: Time duration in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"

def get_local_ip() -> str:
    """
    Get the local IP address of the machine.
    
    Returns:
        Local IP address string
    """
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def get_network_interfaces() -> List[Dict[str, str]]:
    """
    Get network interface information.
    
    Returns:
        List of dictionaries containing interface information
    """
    interfaces = []
    
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    interfaces.append({
                        'name': interface,
                        'ip': addr_info.get('addr', 'Unknown'),
                        'netmask': addr_info.get('netmask', 'Unknown')
                    })
    except ImportError:
        # Fallback if netifaces is not available
        interfaces.append({
            'name': 'local',
            'ip': get_local_ip(),
            'netmask': '255.255.255.0'
        })
    
    return interfaces

def save_to_file(data: Any, filename: str, format: str = 'json') -> bool:
    """
    Save data to a file in specified format.
    
    Args:
        data: Data to save
        filename: Output filename
        format: Output format ('json', 'txt', 'csv')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if format.lower() == 'json':
            import json
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        elif format.lower() == 'txt':
            with open(filename, 'w') as f:
                f.write(str(data))
        elif format.lower() == 'csv':
            import csv
            if isinstance(data, list) and data:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header if data is list of dicts
                    if isinstance(data[0], dict):
                        writer.writerow(data[0].keys())
                        for row in data:
                            writer.writerow(row.values())
                    else:
                        for row in data:
                            writer.writerow([row] if not isinstance(row, (list, tuple)) else row)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return True
    except Exception as e:
        print_error(f"Error saving to file: {e}")
        return False

def load_from_file(filename: str, format: str = 'json') -> Any:
    """
    Load data from a file.
    
    Args:
        filename: Input filename
        format: Input format ('json', 'txt')
        
    Returns:
        Loaded data or None if failed
    """
    try:
        if not os.path.exists(filename):
            print_error(f"File not found: {filename}")
            return None
            
        if format.lower() == 'json':
            import json
            with open(filename, 'r') as f:
                return json.load(f)
        elif format.lower() == 'txt':
            with open(filename, 'r') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        print_error(f"Error loading from file: {e}")
        return None

def check_admin_privileges() -> bool:
    """
    Check if the script is running with administrative privileges.
    
    Returns:
        True if running as admin, False otherwise
    """
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def get_system_info() -> Dict[str, str]:
    """
    Get system information.
    
    Returns:
        Dictionary with system information
    """
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }

# Example usage
if __name__ == "__main__":
    print_header("Utility Module Test")
    
    # Test functions
    print_info("Testing utility functions...")
    print_success("Local IP: " + get_local_ip())
    print_success("Valid IP (192.168.1.1): " + str(is_valid_ip("192.168.1.1")))
    print_success("Valid Port (80): " + str(is_valid_port(80)))
    print_success("Formatted time (125.5s): " + format_time(125.5))
    
    # Test system info
    sys_info = get_system_info()
    print_info("System Information:")
    for key, value in sys_info.items():
        print(f"  {key}: {value}")