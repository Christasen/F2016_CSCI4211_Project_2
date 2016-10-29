import sys, os, random, threading, hashlib, select

from socket import *
from datetime import datetime
from argparse import ArgumentParser

BUFSIZE = 512
TIMEOUT = 10 # Wait for three seconds.
SYN = "SYN"
ACK = "ACK"
SYNACK = "SYNACK"
RST = "RST"
# ORI_DATA = hashlib.sha1(('00030RST' + ('\0' * 464)).encode()).hexdigest() + '00030RST' + ('\0' * 464)

def validate_packet(data):
    content = data[40:]
    pkt_key = data[:40]
    local_key = hashlib.sha1(content.encode()).hexdigest()
    return pkt_key == local_key

def create_packet(seq_num, content, lastsign):
    packet = str(seq_num) + "%03d"%(len(content)) + str(lastsign) + content
    packet += '\0' * (467 - len(content))
    our_key = hashlib.sha1(packet.encode()).hexdigest()
    return our_key + packet

def TCP_SWP_server(connectedSock, addr):
    recv_filename = ""
    sSock = connectedSock
    exp_seq = 0
    data_sending = ""
    SYNed = False
    ACKed = False
    while True:
        ready = select.select([sSock], [], [], TIMEOUT)
        if ready[0]:
            data = sSock.recv(BUFSIZE).decode()
            print("Packet received:")
            print(data)
        else:
            # timeout, re-sent data
            if len(data_sending) != 0:
                print("Timeout! Retransmitting...")
                print("Packet sent:")
                print(data_sending)
                sSock.send(data_sending.encode())
            continue
        # validate packet
        if not validate_packet(data):
            # invalid packet, discard the packet
            continue
        #parse the packet
        seq_num = int(data[40])
        pkt_size = int(data[41:44])
        lastsign = int(data[44])
        content = data[45:]
        if exp_seq != seq_num:
            # wrong sequence num, discard the packet
            continue
        exp_seq = (exp_seq + 1) % 10
        # check SYN
        if not SYNed:
            if content[:3] == SYN:
                # SYN successfully, send SYNACK
                SYNed = True
                data_sending = create_packet(seq_num, SYNACK, 0)
                print("Packet sent:")
                print(data_sending)
                sSock.send(data_sending.encode())
                continue
            else:
                # not a valid SYN message, close the connection
                data_sending = create_packet(0, RST, 1)
                print("RST packet sent")
                print(data_sending)
                sSock.send(data_sending.encode())
                break
        # check ACK
        if not ACKed:
            if content[:3] == ACK:
                # ACK successfully, start to receive the filename, send ACK
                ACKed = True
                recv_filename = content[3:pkt_size]
                fd = open(recv_filename, "w")
                data_sending = create_packet(seq_num, ACK, 0)
                print("Packet sent:")
                print(data_sending)
                sSock.send(data_sending.encode())
                continue
            else:
                # not a valid ACK message, close the connection
                data_sending = create_packet(0, RST, 1)
                print("RST packet sent")
                print(data_sending)
                sSock.send(data_sending.encode())
                break
        # if SYNed and ACKed, store the content sent from the client
        # and send ACK to the client
        fd.write(content[:pkt_size])
        data_sending = create_packet(seq_num, ACK, lastsign)
        print("Packet sent:")
        print(data_sending)
        sSock.send(data_sending.encode())
        # close the connection if this is the last packet
        if lastsign == 1:
            fd.close()
            print("Transfer completed.")
            break
    # close the socket if the connection is closed
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
    # Monitor the exit commands
    monitor = threading.Thread(target = monitorQuit, args = [sSock])
    monitor.start()
    print("Server is listening...")
    while True:
        connectedSock, addr = sSock.accept()
        server = threading.Thread(target = TCP_SWP_server, args=[connectedSock, addr[0]])
        server.start()


def TCP_client(hostname, portnum, filename):
    # try to open the file
    try:
        fd = open(filename, 'r')
        file_content = fd.read()
        fd.close()
        file_len = len(file_content)
        file_p = 0
    except error as msg:
        print(msg)
        return -1
    # start to establish connection
    print("Client starts to establish connection to {}:{}".format(hostname, portnum))
    try:
        cSock = socket(AF_INET, SOCK_STREAM)
        cSock.connect((hostname, portnum))
    except error as msg:
        print(msg)
        return -1
    # initialize all variables host
    SYNed = False
    seq_num = 0
    data_sending = create_packet(seq_num, SYN, 0)
    cSock.send(data_sending.encode())
    while True:
        ready = select.select([cSock], [], [], TIMEOUT)
        if ready[0]:
            data = cSock.recv(BUFSIZE).decode()
            print('Packet received:')
            print(data)
        else:
            print("Timeout! Retransmitting...")
            print("Packet sent:")
            print(data_sending)
            cSock.send(data_sending.encode())
            continue
        # validate data received
        if not validate_packet(data):
            # invalid packet, discard the packet
            continue
        # parse the packet
        rep_seq_num = int(data[40])
        pkt_size = int(data[41:44])
        lastsign = int(data[44])
        content = data[45:]
        if lastsign == 1:
            if content[:3] == ACK:
                # last packet sent successfully, close the connection
                print("Client: transferring completed")
            elif content[:3] == RST:
                # reset connection
                print("Client: connection is reseted")
            break
        # compare seq_num with the seq_num received
        if seq_num != rep_seq_num:
            # wrong sequence number, discard the packet
            continue
        # start to send a new packet
        seq_num += 1
        # check SYNed
        if not SYNed:
            if content[:6] == SYNACK:
                # SYN successfully
                SYNed = True
                # send ACK and the name of file would be transferred
                data_sending = create_packet(seq_num, ACK + filename, 0)
                print("Packet sent:")
                print(data_sending)
                cSock.send(data_sending.encode())
                continue
            else:
                # invliad SYNACK message
                continue
        # check whether connection should be closed:
        # check whether the last packet is ACKed
        if content[:3] == ACK:
            # send the content of the file
            end_this_time = min(file_p + 467, file_len)
            content_sending = file_content[file_p:end_this_time]
            file_p = end_this_time
            if len(content_sending) == 0:
                end_signal = 1
            else:
                end_signal = 0
            data_sending = create_packet(seq_num, content_sending, end_signal)
            print("Packet sent:")
            print(data_sending)
            cSock.send(data_sending.encode())
        else:
            # not ACKed
            continue
    cSock.close()



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
    parser.add_argument('-n', '--host', type = str, default = 'localhost',
                        help = "specify a host to send and listen (default: localhost)")
    parser.add_argument('-p', '--port', type = int, default = -1,
                        help = "specify a port to send and listen (default: 5001 for server, 5002 for client)")
    parser.add_argument('-f', '--filename', type = str, default = '',
                        help = "specify a file which will be transferred to the server. Leaving this arg empty means this program will be a server")
    args = parser.parse_args()
    return (args.host, args.port, args.filename)

def monitorQuit(genSock):
    while True:
        sentence = input()
        if sentence == "exit":
            genSock.shutdown(1)
            genSock.close()
            os.kill(os.getpid(), 9)

# print(validate_packet(ORI_DATA))
main()
