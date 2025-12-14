# Remote Command Shell - Python

A Python-based reverse shell for remote command execution and system administration. This is an educational tool that demonstrates socket programming, client-server communication, and network security concepts.

**IMPORTANT:** This tool is intended for educational purposes and authorized security testing only. Only use on systems you own or have explicit permission to access. Unauthorized access to computer systems is illegal.

## What This Does

This project lets you remotely access another computer's terminal from your laptop. You type commands on your machine, they execute on the remote computer, and you see the results in real-time.

Think of it like TeamViewer or Remote Desktop, but instead of seeing their screen, you're directly accessing their command prompt. It's like sitting at that computer and typing commands, but you're doing it from your own laptop.

## Features

Current features:
- Remote command execution on client machines
- Cross-platform support (Windows, Linux, macOS)
- Error handling and activity logging
- Configuration file support for easy setup
- Real-time command output
- Directory navigation with cd command
- Automatic activity logging for debugging

Planned features:
- Multi-client support to handle multiple connections simultaneously
- Auto-reconnect mechanism if connection drops
- File upload and download capabilities
- Encrypted communication using SSL/TLS
- Web-based dashboard for managing clients
- Session management and command history

## Requirements

- Python 3.6 or higher (tested on Python 3.8+)
- Network connectivity between server and client
- Port 9999 open on the server (or whatever port you configure)
- Basic understanding of networking concepts

## Installation

First, clone the repository:

```bash
git clone https://github.com/ved0904/RemoteCommandShell-Python.git
cd Reverse_Shell
```

Next, configure your settings by editing `Reverse_Shell/config.json`:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 9999,
        "log_file": "server.log"
    },
    "client": {
        "server_ip": "YOUR_SERVER_IP_HERE",
        "server_port": 9999,
        "log_file": "client.log"
    }
}
```

Make sure to replace `YOUR_SERVER_IP_HERE` with your actual server IP address.

There are no external dependencies to install. Everything uses Python's standard library (socket, subprocess, json, datetime).

## How to Use

### Running the Server

On your computer (the one you'll be typing commands on):

```bash
cd Reverse_Shell/Reverse_Shell
python server.py
```

You should see something like this:

```
[2025-12-14 14:41:22] [INFO] ==================================================
[2025-12-14 14:41:22] [INFO] Reverse Shell Server Starting...
[2025-12-14 14:41:22] [INFO] Socket created successfully on port 9999
[2025-12-14 14:41:22] [INFO] Waiting for incoming connections...
```

The server is now listening for client connections.

### Running the Client

On the remote computer (the one you want to control):

Make sure the config.json file has the correct server IP, then run:

```bash
python client.py
```

The client will connect automatically and wait for commands.

### Executing Commands

Once a client connects, you can type commands on the server terminal. Here are some examples:

```bash
dir                    # List files (Windows)
ls -la                 # List files (Linux/Mac)
cd Documents           # Change directory
ipconfig               # Network info (Windows)
ifconfig               # Network info (Linux/Mac)
whoami                 # Current user
systeminfo             # System information (Windows)
quit                   # Close connection and exit
```

## Project Structure

```
Reverse_Shell/
├── Reverse_Shell/
│   ├── server.py           # Server-side code (your computer)
│   ├── client.py           # Client-side code (remote computer)
│   ├── config.json         # Configuration file
│   ├── server.log          # Server activity log (auto-generated)
│   └── client.log          # Client activity log (auto-generated)
└── README.md               # This file
```

## Configuration

### Server Settings

In the config.json file under "server":
- **host**: Set to "0.0.0.0" to listen on all network interfaces
- **port**: The port to listen on (default is 9999, change if needed)
- **log_file**: Where to save server logs

### Client Settings

In the config.json file under "client":
- **server_ip**: Your server's IP address (find using ipconfig or ifconfig)
- **server_port**: Must match the port your server is listening on
- **log_file**: Where to save client logs

## Network Setup

### Local Network (Same WiFi)

To find your server's IP:
- On Windows: Run `ipconfig` and look for IPv4 Address
- On Linux/Mac: Run `ifconfig` or `ip addr`

Update the client's config.json with this IP address, and make sure your firewall allows connections on port 9999.

### AWS EC2 Deployment

If you want to host the server on AWS:

1. Launch an EC2 instance (Ubuntu is recommended)
2. Configure the Security Group to allow inbound TCP traffic on port 9999
3. SSH into your instance:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```
4. Install Python if needed:
   ```bash
   sudo apt update
   sudo apt install python3
   ```
5. Clone the repository and run as described above

## Log Files

Both the server and client create log files automatically. These are helpful for debugging issues.

Example server.log:
```
[2025-12-14 14:41:22] [INFO] Configuration loaded from config.json
[2025-12-14 14:41:22] [INFO] Socket created successfully on port 9999
[2025-12-14 14:41:30] [INFO] Connection established! IP: 192.168.1.105 | Port: 54321
[2025-12-14 14:41:35] [INFO] Command sent to 192.168.1.105: dir
```

Example client.log:
```
[2025-12-14 14:41:30] [INFO] Reverse Shell Client Starting...
[2025-12-14 14:41:30] [INFO] Connected successfully to 192.168.1.100:9999
[2025-12-14 14:41:35] [INFO] Executing command: dir
```

## Troubleshooting

**Connection Refused Error**
- Make sure the server is actually running
- Double-check the server IP in the client's config.json
- Verify that port 9999 is open in your firewall
- Ensure both machines can reach each other on the network

**Config File Not Found**
- The program will use default values if config.json is missing
- Check the log files for warning messages
- Make sure config.json is in the same directory as the Python scripts

**Commands Not Executing**
- Some commands might require administrator or sudo privileges
- Try using full paths for executables if needed
- Check the client.log file for error messages

## Security Notes

This is an educational tool, so please use it responsibly.

Current limitations:
- Communication is not encrypted (this is planned for a future update)
- No authentication mechanism (also planned for the future)
- Configure your firewall to only allow connections from trusted IP addresses
- Only use this on systems you own or have permission to access
- Never use this for malicious purposes

## What You'll Learn

By working with this project, you'll gain experience with:
- TCP socket programming and client-server architecture
- Remote process execution using subprocess
- Proper error handling and exception management
- Configuration files and JSON parsing
- File I/O and logging systems
- Network security concepts and reverse shells
- Remote system administration techniques

## Author

Parived Arora
GitHub: @ved0904

Repository: https://github.com/ved0904/RemoteCommandShell-Python
