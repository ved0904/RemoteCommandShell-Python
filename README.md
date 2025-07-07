# Remote Command Shell - Python

A Python-based remote administration tool that allows secure command execution on client machines from a central server.

## Features

- Single server to multiple client connections
- Cross-platform command execution
- Secure socket communication
- AWS EC2 instance support
- Real-time command feedback

### Upcoming Features
- Multiple client management interface
- Simultaneous command execution across all clients
- Encrypted communication channels
- Client activity monitoring

## Prerequisites

- Python 3.6+
- AWS EC2 instance (for server deployment)
- Putty (for Windows clients)
- Basic firewall configuration (port 9999 open)

## Installation
### For Server (Admin Side):
1. **Set up your server machine**:
   - AWS EC2: Launch a Ubuntu instance and note its public IP
   - Local machine: Ensure Python 3.6+ is installed

2. **Install dependencies**:
   ```bash
   pip install socket subprocess os

3.Clone the repository:
git clone https://github.com/ved0904/RemoteCommandShell-Python.git
cd Reverse_Shell

4.Run the server:
python server.py
(Keep this terminal open)

###For Client (Target Machine):
1.Install Python 3.6+ if not already installed

2.Edit client.py:

3.eplace "YOUR_SERVER_IP" with your server's actual IP (line 5)

4.Save the file

5.Run the client:

6.Run - python client.py
(Runs silently in background)

Port Configuration:
Ensure port 9999 is open on server's firewall/security group

For AWS EC2: Add TCP rule for port 9999 in Security Groups


### Server Setup (AWS EC2)
1. Launch an EC2 instance (Ubuntu recommended)
2. Configure security groups to allow TCP on port 9999
3. SSH into instance using Putty
4. Clone this repository:
   ```bash
   git clone https://github.com/ved0904/RemoteCommandShell-Python.git
