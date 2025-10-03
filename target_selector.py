#!/usr/bin/env python3
"""
Target Selector Module
Provides interface for selecting target IP from discovered network devices.
"""

import sys
from typing import List, Dict, Optional

class TargetSelector:
    def __init__(self, devices: List[Dict]):
        """
        Initialize target selector with list of discovered devices.
        
        Args:
            devices: List of device dictionaries from network scanner
        """
        self.devices = devices
        self.selected_target = None
    
    def display_targets(self) -> None:
        """Display available targets in a formatted table."""
        if not self.devices:
            print("[-] No devices available for selection")
            return
        
        print("\n" + "="*90)
        print("AVAILABLE TARGETS")
        print("="*90)
        print(f"{'#':<3} {'IP Address':<15} {'MAC Address':<18} {'Hostname':<25} {'Description'}")
        print("-"*90)
        
        for i, device in enumerate(self.devices, 1):
            # Add some basic device type detection based on hostname/MAC
            description = self._get_device_description(device)
            print(f"{i:<3} {device['ip']:<15} {device['mac']:<18} {device['hostname']:<25} {description}")
        
        print("-"*90)
        print(f"Total targets available: {len(self.devices)}")
    
    def _get_device_description(self, device: Dict) -> str:
        """
        Attempt to identify device type based on hostname and MAC address.
        
        Args:
            device: Device dictionary containing IP, MAC, hostname
            
        Returns:
            String description of likely device type
        """
        hostname = device['hostname'].lower()
        mac = device['mac'].upper()
        
        # Router detection
        if any(keyword in hostname for keyword in ['router', 'gateway', 'rt-', 'linksys', 'netgear', 'asus']):
            return "Router/Gateway"
        
        # Common device type detection
        if any(keyword in hostname for keyword in ['android', 'iphone', 'samsung', 'mobile']):
            return "Mobile Device"
        elif any(keyword in hostname for keyword in ['laptop', 'desktop', 'pc', 'windows', 'ubuntu']):
            return "Computer"
        elif any(keyword in hostname for keyword in ['printer', 'canon', 'hp', 'epson']):
            return "Printer"
        elif any(keyword in hostname for keyword in ['tv', 'smart', 'roku', 'chromecast']):
            return "Smart TV/Media"
        elif any(keyword in hostname for keyword in ['camera', 'cam', 'security']):
            return "Security Camera"
        
        # MAC address vendor detection (simplified)
        mac_prefix = mac[:8] if len(mac) >= 8 else ""
        vendor_map = {
            "00:50:56": "VMware",
            "08:00:27": "VirtualBox",
            "52:54:00": "QEMU",
            "00:0C:29": "VMware",
            "00:1C:42": "Parallels",
            "B8:27:EB": "Raspberry Pi",
            "DC:A6:32": "Raspberry Pi",
        }
        
        for prefix, vendor in vendor_map.items():
            if mac_prefix == prefix:
                return f"{vendor} Device"
        
        return "Unknown Device"
    
    def select_target_interactive(self) -> Optional[Dict]:
        """
        Interactive target selection via user input.
        
        Returns:
            Selected device dictionary or None if cancelled
        """
        if not self.devices:
            print("[-] No devices available for selection")
            return None
        
        while True:
            self.display_targets()
            print("\n[*] Target Selection Options:")
            print("    Enter device number (1-{})".format(len(self.devices)))
            print("    Enter 'q' to quit")
            print("    Enter 'r' to refresh device list")
            print("    Enter IP address directly")
            
            try:
                choice = input("\n[?] Select target: ").strip()
                
                # Quit option
                if choice.lower() == 'q':
                    print("[*] Target selection cancelled")
                    return None
                
                # Refresh option
                if choice.lower() == 'r':
                    print("[*] Please refresh the device list from main menu")
                    continue
                
                # Check if input is an IP address
                if self._is_valid_ip(choice):
                    target = self._find_device_by_ip(choice)
                    if target:
                        self.selected_target = target
                        print(f"[+] Target selected: {target['ip']} ({target['hostname']})")
                        return target
                    else:
                        print(f"[-] IP {choice} not found in discovered devices")
                        continue
                
                # Check if input is a device number
                device_num = int(choice)
                if 1 <= device_num <= len(self.devices):
                    target = self.devices[device_num - 1]
                    self.selected_target = target
                    print(f"[+] Target selected: {target['ip']} ({target['hostname']})")
                    return target
                else:
                    print(f"[-] Invalid selection. Please enter number between 1 and {len(self.devices)}")
                
            except ValueError:
                print("[-] Invalid input. Please enter a valid number, IP address, or command")
            except KeyboardInterrupt:
                print("\n[*] Target selection cancelled")
                return None
    
    def select_target_by_ip(self, ip: str) -> Optional[Dict]:
        """
        Select target by IP address.
        
        Args:
            ip: IP address string
            
        Returns:
            Selected device dictionary or None if not found
        """
        target = self._find_device_by_ip(ip)
        if target:
            self.selected_target = target
            print(f"[+] Target selected: {target['ip']} ({target['hostname']})")
            return target
        else:
            print(f"[-] IP {ip} not found in discovered devices")
            return None
    
    def select_target_by_index(self, index: int) -> Optional[Dict]:
        """
        Select target by device index.
        
        Args:
            index: Device index (0-based)
            
        Returns:
            Selected device dictionary or None if invalid index
        """
        if 0 <= index < len(self.devices):
            target = self.devices[index]
            self.selected_target = target
            print(f"[+] Target selected: {target['ip']} ({target['hostname']})")
            return target
        else:
            print(f"[-] Invalid index. Please provide index between 0 and {len(self.devices)-1}")
            return None
    
    def _find_device_by_ip(self, ip: str) -> Optional[Dict]:
        """Find device by IP address."""
        for device in self.devices:
            if device['ip'] == ip:
                return device
        return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format."""
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
    
    def get_selected_target(self) -> Optional[Dict]:
        """Return currently selected target."""
        return self.selected_target
    
    def display_selected_target(self) -> None:
        """Display information about currently selected target."""
        if not self.selected_target:
            print("[-] No target currently selected")
            return
        
        target = self.selected_target
        print("\n" + "="*60)
        print("SELECTED TARGET INFORMATION")
        print("="*60)
        print(f"IP Address:    {target['ip']}")
        print(f"MAC Address:   {target['mac']}")
        print(f"Hostname:      {target['hostname']}")
        print(f"Description:   {self._get_device_description(target)}")
        print(f"Status:        {target['status']}")
        print("="*60)
    
    def filter_devices(self, filter_type: str = None) -> List[Dict]:
        """
        Filter devices by type.
        
        Args:
            filter_type: Type to filter by ('router', 'computer', 'mobile', etc.)
            
        Returns:
            Filtered list of devices
        """
        if not filter_type:
            return self.devices
        
        filtered = []
        for device in self.devices:
            description = self._get_device_description(device).lower()
            if filter_type.lower() in description:
                filtered.append(device)
        
        return filtered
    
    def get_target_summary(self) -> Dict:
        """
        Get summary of current target selection.
        
        Returns:
            Dictionary with target summary information
        """
        if not self.selected_target:
            return {'selected': False, 'target': None}
        
        return {
            'selected': True,
            'target': self.selected_target,
            'description': self._get_device_description(self.selected_target)
        }

def main():
    """Test the target selector module."""
    # Sample devices for testing
    sample_devices = [
        {'ip': '192.168.1.1', 'mac': '00:1A:2B:3C:4D:5E', 'hostname': 'router.local', 'status': 'alive'},
        {'ip': '192.168.1.100', 'mac': '08:00:27:12:34:56', 'hostname': 'ubuntu-desktop', 'status': 'alive'},
        {'ip': '192.168.1.150', 'mac': 'B8:27:EB:AA:BB:CC', 'hostname': 'raspberry-pi', 'status': 'alive'},
    ]
    
    print("Target Selector Test")
    print("===================")
    
    selector = TargetSelector(sample_devices)
    
    # Test interactive selection
    target = selector.select_target_interactive()
    
    if target:
        selector.display_selected_target()

if __name__ == "__main__":
    main()