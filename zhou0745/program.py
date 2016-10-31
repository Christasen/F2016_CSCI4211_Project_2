import sys, os, random, threading, hashlib, select, time

from socket import *
from datetime import datetime
from argparse import ArgumentParser
from datetime import datetime

BUFSIZE = 512
TIMEOUT = 10 # Wait for ten seconds.
SYN = '\x16\x00'
ACK = '\x06\x00'
SYNACK = '\x16\x06'
RST = '\x18\x00'
FIN = '\x19\x00'
ACKFIN = '\x06\x19'

# ORI_DATA = hashlib.sha1(('00030RST' + ('\0' * 464)).encode()).hexdigest() + '00030RST' + ('\0' * 464)

def validate_packet(data):
    content = data[40:]
    pkt_key = data[:40]
    local_key = hashlib.sha1(content.encode()).hexdigest()
    local_key = (40 - len(local_key)) * " " + local_key
    print("len: {}".format(len(data)))
    print("{}\n{}\nseq: {}".format(pkt_key, local_key, data[40]))
    return pkt_key == local_key

def create_packet(seq_num, content, lastsign):
    packet = str(seq_num) + "%03d"%(len(content)) + str(lastsign) + content
    packet += '\x00' * (467 - len(content))
    our_key = hashlib.sha1(packet.encode()).hexdigest()
    our_key = (40 - len(our_key)) * " " + our_key
    return our_key + packet

def TCP_SWP_server(connectedSock, addr):
    print("\n----Incoming transmission from a client.----")
    recv_filename = ""
    sSock = connectedSock
    exp_seq = 0
    seq_num = 0;
    data_sending = ""
    SYNed = False
    ACKed = False
    FINed = False
    while True:
        ready = select.select([sSock], [], [], TIMEOUT)
        print("\nTime: {}".format(str(datetime.now())))
        if ready[0]:
            data = sSock.recv(BUFSIZE).decode()
            print("Packet Receiving: Received a packet from the client.")
        else:
            # timeout, re-sent data
            if len(data_sending) != 0:
                print("Packet Receiving: Timeout! Retransmitting packet[#{}]...".format(seq_num))
                sSock.send(data_sending.encode())
                continue
            else:
                print("Packet Receiving: Did not receive SYN packet.")
                continue
        # validate packet
        if (len(data) < 512):
            print("Server: connection is closed by the client. Quitting...")
            break

        if not validate_packet(data):
            # invalid packet, discard the packet
            print("Packet Receiving: The packet received is invalid, discard it.")
            print("Server: Retransmitting packet[#{}]...".format((exp_seq - 1) % 10))
            sSock.send(data_sending.encode())
            continue
        #parse the packet
        seq_num = int(data[40])
        pkt_size = int(data[41:44])
        lastsign = int(data[44])
        content = data[45:]
        # check SYN
        if exp_seq != seq_num and lastsign == 0:
            # wrong sequence num, discard the packet
            print("Packet Receiving: # of the packet received does not match the exception, discard the packet.")
            print("Server: Retransmitting packet[#{}]...".format((exp_seq - 1) % 10))
            sSock.send(data_sending.encode())
            continue

        if not SYNed:
            if content[:2] == SYN:
                # SYN successfully, send SYNACK
                SYNed = True
                print("Packet Receiving: The packet received is a valid SYN packet.")
                data_sending = create_packet(seq_num, SYNACK, 0)
                print("Packet[#{}] Sending: Sending a SYNACK packet to the client...".format(seq_num))
                sSock.send(data_sending.encode())
                exp_seq = (seq_num + 1) % 10
                continue
            else:
                # not a valid SYN message, close the connection
                data_sending = create_packet(0, RST, 1)
                print("Server Error: Sending a RST message to the client...")
                sSock.send(data_sending.encode())
                break
        # check ACK
        if not ACKed:
            if content[:2] == ACK:
                # ACK successfully, start to receive the filename, send ACK
                ACKed = True
                recv_filename = content[2:pkt_size]
                print("Packet Receiving: the packet received is valid, starting to receive the file '{}'...".format(recv_filename))
                fd = open(recv_filename, "w")
                data_sending = create_packet(seq_num, ACK, 0)
                print("Packet[#{}] Sending: Sending an ACK packet to the client...".format(seq_num))
                sSock.send(data_sending.encode())
                exp_seq = (seq_num + 1) % 10
                continue
            else:
                # not a valid ACK message, close the connection
                data_sending = create_packet(0, RST, 1)
                print("Server Error: Sending a RST message to the client...")
                sSock.send(data_sending.encode())
                break
        # if this is a FIN packet, return ACKFIN packet and close the file
        if (content[:2] == FIN):
            FINed = True
            fd.close()
            print("Packet Receiving: the packet received is a FIN packet, close the file.")
            print("Packet[#{}] Sending: Sending an ACKFIN packet to the client...".format(seq_num))
            data_sending = create_packet(seq_num, ACKFIN, 0)
            sSock.send(data_sending.encode())
            exp_seq = (seq_num + 1) % 10
            continue
        # if this is the last packet, break then close the connection
        if (lastsign == 1):
            print("Packet Receiving: The last packet is received, quitting...")
            break
        # if SYNed and ACKed, also not received FIN, store the content sent from the client
        # and send ACK to the client
        print("Packet Receiving: the packet received is valid, writing the content into local file...")
        fd.write(content[:pkt_size])
        data_sending = create_packet(seq_num, ACK, 0)
        print("Packet[#{}] Sending: Sending an ACK packet to the client...".format(seq_num))
        sSock.send(data_sending.encode())
        exp_seq = (seq_num + 1) % 10
        # close the connection if this is the last packet
    # close the socket if the connection is closed
    print("Connection closed.")
    sSock.shutdown(SHUT_RDWR)
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


def TCP_client(hostname, portnum, full_filedir):
    # try to open the file
    try:
        fd = open(full_filedir, 'r')
        file_content = fd.read()
        fd.close()
        file_len = len(file_content)
        file_p = 0
    except error as msg:
        print(msg)
        return -1
    # complete the steps of reading the file
    # extract the short name of the file
    if '/' in full_filedir:
        # get the last seg of the full path and assign it to filename
        file_dir_splited = full_filedir.split('/')
        filename = file_dir_splited[-1]
    else:
        # if this is a file directory without any '/' symbol, assign the dir to filename directly
        filename = full_filedir
    # start to establish connection
    print("\n----Client starts to establish connection to {}:{}----".format(hostname, portnum))
    try:
        cSock = socket(AF_INET, SOCK_STREAM)
        cSock.connect((hostname, portnum))
    except error as msg:
        print(msg)
        return -1
    # initialize all variables host
    SYNed = False
    first_wave = True
    seq_num = 0
    data_sending = create_packet(seq_num, SYN, 0)
    print("\nTime: {}".format(str(datetime.now())))
    print("Packet[#{}] Sending: Sending a SYN packet to the server...".format(seq_num))
    cSock.send(data_sending.encode())
    while True:
        ready = select.select([cSock], [], [], TIMEOUT)
        print("\nTime: {}".format(str(datetime.now())))
        if ready[0]:
            print("Packet Receiving: Received a packet from the server.")
            data = cSock.recv(BUFSIZE).decode()
        else:
            if (first_wave):
                print("Client: SYN packet is Timeout.")
            print("Packet Receiving: Timeout! Retransmitting packet[#{}]...".format(seq_num))
            cSock.send(data_sending.encode())
            continue
        first_wave = False
        # # validate data received
        if (len(data) < 512):
            print("Client: Connection is closed by the server side. Quitting...")
            break
        if not validate_packet(data):
            # invalid packet, discard the packet
            print("Packet Receiving: The packet received is invalid, discard it.")
            print("Client: Retransmitting packet[#{}]...".format(seq_num))
            cSock.send(data_sending.encode())
            continue
        # parse the packet
        rep_seq_num = int(data[40])
        pkt_size = int(data[41:44])
        lastsign = int(data[44])
        content = data[45:]
        # check whether this is a RST packet
        if (content[:2] == RST):
            print("Client: Connection is reseted by the server side. Quitting...")
            break
        # compare seq_num with the seq_num received while it's not a last packet
        if seq_num != rep_seq_num and lastsign == 0:
            # wrong sequence number, discard the packet
            print("Packet Receiving: # of the packet received is incorrect, discard the packet.")
            print("Client: Retransmitting packet[#{}]...".format(seq_num))
            cSock.send(data_sending.encode())
            continue
        # start to send a new packet
        # check SYNed
        if not SYNed:
            if content[:2] == SYNACK:
                # SYN successfully
                SYNed = True
                print("Packet Receiving: Received a valid SYNACK message from the server.")
                seq_num = (seq_num + 1) % 10
                # send ACK and the name of file would be transferred
                data_sending = create_packet(seq_num, ACK + filename, 0)
                print("Packet[#{}] Sending: Sending a packet contained ACK and the name of file...".format(seq_num))
                cSock.send(data_sending.encode())
                continue
            else:
                # invliad SYNACK message
                print("Packet Receiving: The packet does not contain required SYNACK message, discard the packet.")
                print("Client: Retransmitting packet[#{}]...".format(seq_num))
                cSock.send(data_sending.encode())
                continue
        # check whether this is a ACKFIN packet,
        # if yes, send last packet to the server then close the connection
        if content[:2] == ACKFIN:
            print("Packet Receiving: The packet is an ACKFIN packet.")
            seq_num = (seq_num + 1) % 10
            data_sending = create_packet(seq_num, ACK, 1)
            print("Packet[#{}] Sending: Sending last packet to the server to close the connection...".format(seq_num))
            cSock.send(data_sending.encode())
            break
        # check whether the packet is ACKed
        if content[:2] == ACK:
            # send next packet for the content of the file
            print("Packet Receiving: Received a valid ACK message from the server.")
            seq_num = (seq_num + 1) % 10
            end_this_time = min(file_p + 467, file_len)
            content_sending = file_content[file_p:end_this_time]
            file_p = end_this_time
            if len(content_sending) == 0:
                content_sending = FIN
            data_sending = create_packet(seq_num, content_sending, 0)
            if (content_sending == FIN):
                print("Packet[#{}] Sending: The packet will be sent is a FIN packet.".format(seq_num))
            print("Packet[#{}] Sending: Sending a packet contained the file content to the server...".format(seq_num))
            cSock.send(data_sending.encode())
        else:
            # not ACKed, discard it
            print("Packet Receiving: this is an invalid ACK packe, discard the packet.".format(rep_seq_num))
            print("Client: Retransmitting packet[#{}]...".format(seq_num))
            cSock.send(data_sending.encode())
    print("Connection closed.")
    cSock.shutdown(SHUT_RDWR)
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
            genSock.shutdown(SHUT_RDWR)
            genSock.close()
            os.kill(os.getpid(), 9)

# print(validate_packet(ORI_DATA))
main()
