# Network Security Testing Toolkit

A comprehensive Python-based toolkit for network security testing and penetration testing. This toolkit provides functionality for network discovery, port scanning, and Metasploit integration for vulnerability exploitation.

## Features

- **Network Discovery**: Scan and identify devices on your local network with IP and MAC addresses
- **Target Selection**: Interactive target selection with manual IP entry option
- **Port Scanning**: Multi-threaded port scanning with service detection
- **Metasploit Integration**: Full integration with Metasploit Framework for vulnerability exploitation
- **Automated Exploitation**: Automated exploit testing that tries all exploits until one succeeds
- **Cross-Platform**: Works on Windows, Linux, macOS, and Termux (Android)
- **Automatic Setup**: One-click dependency installation across all platforms

## Prerequisites

- Python 3.6 or later
- Administrative privileges (on Windows for full functionality)
- Internet connection for initial setup

## Installation

### Automated Installation (Recommended)

1. Clone or download this repository
2. Run the setup script:
   - **Windows**: Double-click `setup.bat` or run `python setup.py`
   - **Linux/macOS/Termux**: Run `python setup.py`

### Manual Installation

Install required system dependencies:

#### Windows
```bash
# Install via Chocolatey (run as Administrator)
choco install nmap metasploit

# Or download from official sources
# Nmap: https://nmap.org/download.html
# Metasploit: https://www.metasploit.com/download/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install nmap metasploit-framework
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install nmap metasploit
```

#### Termux (Android)
```bash
pkg update
pkg install nmap
curl -fsSL https://kutt.it/msf | bash
```

### Python Dependencies

Install Python packages:
```bash
pip install -r requirements.txt
```

Or run the setup script which will automatically install them.

## Usage

### Quick Start

1. **Run the toolkit**:
   - **Windows**: Double-click `run.bat` or run `python main.py`
   - **Linux/macOS/Termux**: Run `python main.py`

2. **Follow the menu options**:
   - Option 1: Scan network for connected devices
   - Option 2: Select target (with manual IP entry option)
   - Option 3: Scan ports on selected target
   - Option 4: Run automated exploits
   - Option 5: Run single exploit
   - Option 8: Setup/Install dependencies

### Detailed Usage

#### Network Scanning
The toolkit will automatically detect your local network range and scan for connected devices, showing IP addresses, MAC addresses, and hostnames.

#### Target Selection
You can either select from discovered devices or manually enter an IP address:
- Enter device number from the list
- Enter 'm' for manual IP entry
- Enter IP address directly (e.g., 192.168.1.100)

#### Port Scanning
The toolkit scans common ports to identify open services on the target system.

#### Metasploit Exploitation
The toolkit integrates with Metasploit to:
- Search for exploits matching target services
- Check if targets are vulnerable
- Generate and execute exploit scripts
- Run automated exploitation until one succeeds

## Platform-Specific Notes

### Windows
- Must be run as Administrator for full functionality
- Metasploit installation may require manual PATH configuration
- If Metasploit fails to install via setup, use the included `install_metasploit.bat` script

### Termux
- Some network scanning features may be limited due to Android restrictions
- Metasploit installation uses the gushmazuko automated script
- Ensure Termux has storage permissions: `termux-setup-storage`

### Linux/macOS
- Standard installation via package managers
- May require sudo privileges for network scanning

## Troubleshooting

### Metasploit Not Found
If Metasploit is not detected:
1. Ensure it's properly installed
2. Verify it's in your system PATH
3. On Windows, you may need to manually add the Metasploit bin directory to PATH
4. Restart your terminal/command prompt after installation

### Network Scanning Issues
- On Termux, network scanning may be limited
- Try using nmap directly: `nmap -sn your_network_range`
- Ensure you have proper network permissions

### Permission Errors
- Windows: Run as Administrator
- Linux/macOS/Termux: May require sudo privileges

## Security Notice

This toolkit is intended for ethical hacking and security research purposes only. Only use it on systems and networks you own or have explicit permission to test. Unauthorized use may be illegal and could result in serious consequences.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## Acknowledgments

- [Metasploit Framework](https://www.metasploit.com/)
- [Nmap](https://nmap.org/)
- [Scapy](https://scapy.net/)