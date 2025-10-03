#!/usr/bin/env python3
"""
Configuration Module
Handles application configuration and settings.
"""

import os
from typing import Dict, Any

class Config:
    def __init__(self):
        """Initialize configuration with default values."""
        self.settings = {
            # Network scanning settings
            'scan_timeout': 1.0,
            'scan_threads': 50,
            'arp_timeout': 5,
            
            # Port scanning settings
            'port_scan_timeout': 1.0,
            'port_scan_threads': 100,
            'common_ports_only': False,
            
            # Metasploit settings
            'msf_path': 'msfconsole',
            'msf_timeout': 30,
            
            # Output settings
            'save_results': True,
            'output_directory': './results',
            
            # Logging settings
            'enable_logging': True,
            'log_level': 'INFO',
            'log_file': 'security_toolkit.log'
        }
        
        # Load configuration from environment variables if available
        self._load_from_env()
        
        # Create output directory if needed
        self._create_output_directory()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mapping = {
            'SCAN_TIMEOUT': 'scan_timeout',
            'SCAN_THREADS': 'scan_threads',
            'PORT_SCAN_TIMEOUT': 'port_scan_timeout',
            'PORT_SCAN_THREADS': 'port_scan_threads',
            'MSF_PATH': 'msf_path',
            'OUTPUT_DIRECTORY': 'output_directory'
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert to appropriate type
                if config_key.endswith('_timeout') or config_key.endswith('_threads'):
                    try:
                        self.settings[config_key] = float(value)
                    except ValueError:
                        pass  # Keep default value
                else:
                    self.settings[config_key] = value
    
    def _create_output_directory(self):
        """Create output directory if it doesn't exist."""
        output_dir = self.settings['output_directory']
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception:
                # If we can't create the directory, use current directory
                self.settings['output_directory'] = '.'
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.settings[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration settings.
        
        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()
    
    def update(self, updates: Dict[str, Any]):
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.settings.update(updates)
    
    def save_to_file(self, filepath: str):
        """
        Save configuration to a file.
        
        Args:
            filepath: Path to save configuration file
        """
        try:
            import json
            with open(filepath, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    def load_from_file(self, filepath: str):
        """
        Load configuration from a file.
        
        Args:
            filepath: Path to configuration file
        """
        try:
            import json
            with open(filepath, 'r') as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {e}")

# Global configuration instance
config = Config()