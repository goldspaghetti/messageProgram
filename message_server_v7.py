#!/usr/bin/env python3
#not secure, client and server chatting program on the terminal
#unreliable due to nature of recv (packet loss)
#changes from v6: Admin added, changes with usernames
import argparse, socket, threading, queue, datetime, time, random, secrets, sys
bufsize = 4096
messageQueue = queue.Queue()
usernames = {}
adminIdent = secrets.randbits(64)
#chat commands
def dance(threadNum):
    for i in range(threadNum):
        messageQueue.put(b':D-<')
    time.sleep(0.6)
    for i in range(threadNum):
        messageQueue.put(b':D|-<')
    time.sleep(0.6)
    for i in range(threadNum):
        messageQueue.put(b':D/-<')

def flip(threadNum):
    outcome = random.randint(0, 1)
    if outcome == 0:
        for i in range(threadNum):
            messageQueue.put(b'tails')
    else:
        for i in range(threadNum):
            messageQueue.put(b'heads')

#admin chat
def adminSend(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(b'admin')
    while True:
        message = input()
        message = message.encode('ascii')
        sock.sendall(message)
        if message == b'!disconnect':
            sock.close()
            break
        if message == b'!terminate':
            sock.close()
            break

#server
def getUsername(sock, peerName):
    usernameOpen = True
    retry = True
    while retry == True:
        usernameOpen = True
        username = sock.recv(bufsize)
        for i in usernames:
            if usernames[i] == username:
                usernameOpen = False
                sock.sendall(b'0')
        if usernameOpen == True:
            sock.sendall(b'1')
            retry = False
    usernames[peerName] = username
    
def manageAdmin(sock):
    threadNum = 0
    print('amount: ' + str(threadNum))
    dataAdminIdent = str(adminIdent).encode('ascii')
    while True:
        message = sock.recv(bufsize)
        threadNum = 0
        for threads in threading.enumerate():
            if threads.getName() == 'message':
                threadNum += 1
        for i in range(threadNum):
            messageQueue.put(dataAdminIdent + b'admin: ' + message)
        print('admin: ' + message.decode('ascii'))
        if message == b'!terminate':
            sock.close()
            break
        if message == b'!dictionary':
            print(usernames)
        
def manageMessage(sock):
    lock = threading.Lock()
    sock.sendall(str(adminIdent).encode('ascii'))
    while True:
        lock.acquire()
        message = messageQueue.get()
        sock.sendall(message)
        lock.release()
        time.sleep(0.2)

def manageClient(sock, sockname):
    getUsername(sock, sockname)
    userInfo = sock.getpeername()
    while True:
        data = sock.recv(bufsize)
        username = usernames.get(userInfo)
        text = username + b': ' + data
        #threadNum is local in order to prevent 2 messages sent at the same time messing it up
        threadNum = 0
        for threads in threading.enumerate():
            if threads.getName() == 'message':
                threadNum += 1
        print('amount: ' + str(threadNum))
        print(text.decode('ascii'))
        for i in range(threadNum):
            messageQueue.put(text)
        if data == b'!dance':
            dance(threadNum)
        if data == b'!flip':
            flip(threadNum)
        if data == b'!disconnect':
            sock.close()
            for threads in range(threadNum):
                messageQueue.put(username + b' has disconnected')
            del usernames[sockname]
            break
        
        
def server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(0)
    print('server set up at', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        print('new user at: ', sc.getpeername())
        role = sc.recv(bufsize)
        if role == b'send':
            messageThread = threading.Thread(target=manageClient,
                                         args=[sc, sockname]).start()
        if role == b'receive':
            sendThread = threading.Thread(target=manageMessage,
                                      args=[sc], name='message').start()
        if role == b'admin':
            adminThread = threading.Thread(target=manageAdmin, args=[sc]).start()

if __name__ == '__main__':
    choices = {'server':server, 'admin':adminSend}
    parser = argparse.ArgumentParser(description='server for chatting program')
    parser.add_argument('role', choices=choices, help='Set up server or send messages as admin')
    parser.add_argument('ip', help='ip address to set up server')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port to set up server(default 1060)')
    args = parser.parse_args()
    choices[args.role](args.ip, args.p)

#possible features to add:
# more secure, get rid of accepting false requests
#sending time (do this for client, as timezones exist)
#
    
    
