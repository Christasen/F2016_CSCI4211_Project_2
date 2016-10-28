import sys, os, random, threading
from socket import *
from datetime import datetime
from argparse import ArgumentParser
import select

def TCP_server(hostname, portnum):
    print("Server starts to listen to {}:{}".format(hostname, portnum))

    try:
        sSock = socket(AF_INET, SOCK_STREAM)
        sSock.bind((hostname, portnum))
        sSock.listen(20)
    except error as msg:
        print(msg)
        return -1

    monitor = threading.Thread(target = monitorQuit, args = [sSock])
    monitor.start()

    print("Server is running...")

    while True:
        1 + 1

def TCP_client(hostname, portnum):
    print("Client starts to listen to {}:{}".format(hostname, portnum))

    try:
        cSock = socket(AF_INET, SOCK_STREAM)
        cSock.bind((hostname, portnum))
        cSock.listen(20)
    except error as msg:
        print(msg)
        return -1

    monitor = threading.Thread(target = monitorQuit, args = [cSock])
    monitor.start()
    print("Client is running...")

    while True:
        1 + 1

def main():
    (host, port, role) = parse_args()
    if role == "server":
        if port < 0:
            port = 5001
        return TCP_server(host, port)
    elif role == "client":
        if port < 0:
            port = 5002
        return TCP_client(host, port)
    else:
        print("Errors in role name. The role name must be 'server' or 'client'")
        print("Use '-h' for more details\n")
        return 0

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--host', type = str, default = 'localhost',
                        help = "specify a host to send and listen (default: localhost)")
    parser.add_argument('-p', '--port', type = int, default = -1,
                        help = "specify a port to send and listen (default: 5001 for server, 5002 for client)")
    parser.add_argument('-r', '--role', type = str, default = 'server',
                        help = "specify a role for the program ('server' or 'client', default: 'server')")
    args = parser.parse_args()
    return (args.host, args.port, args.role)

def monitorQuit(genSock):
    while True:
        sentence = input()
        if sentence == "exit":
            genSock.shutdown(1)
            genSock.close()
            os.kill(os.getpid(), 9)

main()
