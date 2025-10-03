#!/usr/bin/env python3
"""
Test imports for all modules
"""

try:
    from network_scanner import NetworkScanner
    print("NetworkScanner imported successfully")
except Exception as e:
    print(f"Error importing NetworkScanner: {e}")

try:
    from target_selector import TargetSelector
    print("TargetSelector imported successfully")
except Exception as e:
    print(f"Error importing TargetSelector: {e}")

try:
    from port_scanner import PortScanner
    print("PortScanner imported successfully")
except Exception as e:
    print(f"Error importing PortScanner: {e}")

try:
    from metasploit_interface import MetasploitInterface
    print("MetasploitInterface imported successfully")
except Exception as e:
    print(f"Error importing MetasploitInterface: {e}")

try:
    from config import Config
    print("Config imported successfully")
except Exception as e:
    print(f"Error importing Config: {e}")

try:
    from utils import clear_screen
    print("Utils imported successfully")
except Exception as e:
    print(f"Error importing Utils: {e}")

print("Import test completed")