import sys, os, random, threading, hashlib

from socket import *
from datetime import datetime
from argparse import ArgumentParser
from select import *

BUFSIZE = 512

def get_digest_in_char(hexkey):
    charkey = str()

def TCP_SWP_server(connectedSock, addr):
    sSock = connectedSock
    data = sSock.recv(BUFSIZE)
    checksum = data[:20]
    pktnum = data[20]
    pktsize = data[21:24]
    lastsign = data[24]
    pktdata = data[25:].decode().strip('\0')
    seqid = 0


    if hashres == checksum:
        # match
    else:
        # data lost, discard the packet

    sSock.close()



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

    print("Server is listening...")
    while True:
        connectedSock, addr = sSock.accept()
        server = threading.Thread(target = TCP_SWP_server, args=[connectedSock, addr[0]])
        server.start()


def TCP_client(hostname, portnum, filename):
    try:
        fd = open(filename, 'r')
    except error as msg:
        print(msg)
        return -1
    print("Client starts to establish connection to {}:{}".format(hostname, portnum))
    while True:
        try:
            cSock = socket(AF_INET, SOCK_STREAM)
            cSock.connect((hostnamem, portnum))
        except error as msg:
            print(msg)
            return -1


def main():
    (host, port, filename) = parse_args()
    if filename == '':
        if port < 0:
            port = 5001
        return TCP_server(host, port)
    else:
        if port < 0:
            port = 5002
        return TCP_client(host, port, filename)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--host', type = str, default = 'localhost',
                        help = "specify a host to send and listen (default: localhost)")
    parser.add_argument('-p', '--port', type = int, default = -1,
                        help = "specify a port to send and listen (default: 5001 for server, 5002 for client)")
    parser.add_argument('-f', '--file', type = str, default = '',
                        help = "specify a file which will be transferred to the server. Leaving this arg empty means this program will be a server")
    args = parser.parse_args()
    return (args.host, args.port, args.file)

def monitorQuit(genSock):
    while True:
        sentence = input()
        if sentence == "exit":
            genSock.shutdown(1)
            genSock.close()
            os.kill(os.getpid(), 9)

main()
