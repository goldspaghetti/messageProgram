#!/usr/bin/env python3
#not secure, client and server chatting program on the terminal
#changes from v6: Admin added, changes with usernames
import argparse, socket, threading, queue, datetime, sys, secrets
bufsize = 4096
def clientSend(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(b'send')
    usernameOpen = False
    while usernameOpen == False:
        username = input('enter username > ')
        dataUsername = username.encode('ascii')
        sock.sendall(dataUsername)
        usernameTaken = sock.recv(bufsize)
        if usernameTaken == b'0':
            print('username taken')
        else:
            usernameOpen = True
            print('username Open')
    while True:
        message = input()
        #sys.stdout.write("\033[F")
        message = message.encode('ascii')
        sock.sendall(message)
        if message == b'!disconnect':
            sock.close()
            break

def clientReceive(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(b'receive')
    adminIdent = sock.recv(bufsize)
    adminIdent = adminIdent.decode('ascii')
    identLen = len(adminIdent)
    while True:
        message = sock.recv(bufsize)
        message = message.decode('ascii')
        if message[0:identLen] == adminIdent:
            message = message[identLen:]
            print(f"\033[91m{message}\033[00m")
        else:
            print(message)

if __name__ == '__main__':
    choices = {'send':clientSend, 'receive':clientReceive}
    parser = argparse.ArgumentParser(description='client for chatting program')
    parser.add_argument('role', choices=choices, help='send or recieve messages')
    parser.add_argument('ip', help='ip address to connect to')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port to connect to')
    args = parser.parse_args()
    choices[args.role](args.ip, args.p)
    
