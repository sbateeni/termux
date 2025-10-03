# Network Security Testing Toolkit

## ⚠️ IMPORTANT DISCLAIMER

This toolkit is for **educational and authorized security testing purposes only**. 
Only use on networks you own or have explicit permission to test. Unauthorized 
network scanning or penetration testing may be illegal.

**WARNING**: This toolkit performs real network scans and genuine exploit testing 
using the Metasploit Framework. It can potentially disrupt target systems or 
networks. Ensure you understand the implications and have proper authorization 
before use.

## Overview

A comprehensive Python-based network security testing toolkit that provides the following capabilities:

1. **Network Discovery**: Scan local network to discover connected devices and retrieve their IP and MAC addresses
2. **Target Selection**: Interactive interface to select target devices from discovered network devices
3. **Port Scanning**: Scan open ports on selected targets to identify running services
4. **Exploit Search**: Search for potential exploits matching discovered services using Metasploit integration
5. **Exploit Testing**: Run vulnerability checks and generate exploit scripts

## Features

- Modular design for easy maintenance and extension
- Multi-threaded scanning for improved performance
- Interactive command-line interface
- Detailed reporting and result saving
- **Real Metasploit Framework integration** for genuine exploit testing
- **Enhanced network scanning** using multiple detection methods
- **Automated exploit testing** - tries all exploits until one succeeds
- **Detailed exploit information** retrieval from Metasploit
- **Real exploit execution** with safety confirmation prompts
- **Organized exploit script management** in dedicated exploit directory
- **Automatic selection** of most recent exploit script
- **Cross-platform automatic setup** for all environments (Windows, Linux, macOS, Termux)
- **Standalone setup script** for easy deployment
- Configurable settings

## Requirements

- Python 3.6 or higher
- **Metasploit Framework (REQUIRED for exploit functionality)**
  - Install from: https://github.com/rapid7/metasploit-framework
  - Follow the official installation guide for your platform
- Windows, macOS, or Linux operating system (including Termux on Android)
- Administrative privileges for network scanning

## Automatic Setup

The toolkit includes an automatic setup feature that can install all required dependencies:

- **Option 8** in the main menu
- **Standalone setup script**: `python setup.py`
- Supports Windows, Linux, macOS, and Termux environments
- Automatically detects package managers (Chocolatey, Homebrew, apt, yum, dnf, pacman)

## Installation

1. Clone or download this repository:
   ```
   git clone <repository-url>
   cd termux
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. (Optional) Install Metasploit Framework for full exploit functionality:
   - Visit https://www.metasploit.com/ for installation instructions

## Usage

Run the main toolkit:
```
python main.py
```

Follow the interactive menu to:
1. Discover network devices
2. Select a target
3. Scan target ports
4. Search for exploits
5. Run exploit checks

## Modules

- `main.py` - Main controller orchestrating all modules
- `network_scanner.py` - Network device discovery
- `target_selector.py` - Target selection interface
- `port_scanner.py` - Port scanning functionality
- `metasploit_interface.py` - Metasploit integration
- `config.py` - Configuration management
- `utils.py` - Utility functions
- `requirements.txt` - Python package dependencies

## Legal Notice

This toolkit is provided for educational purposes only. The authors are not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before testing any network or system.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests with improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.