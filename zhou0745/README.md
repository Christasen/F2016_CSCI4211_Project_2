# CSCI4211_Project_2

Name: Tiannan Zhou

ID: 5232494

Email: zhou0745@umn.edu

## Usage

As a Server:
```
python3 program.py [-n HOST] [-p PORT]
```
Hostname and Port # are optional arguments. The default values of Host and Port are `localhost` and `5001` for a server.

As a Client:
```
python3 program.py [-n HOST] [-p PORT] -f FILENAME
```
As a client, the name of file which would be transferred to the server side is required. Hostname and Port # are optional arguments. The default values of Host and Port are `localhost` and `5002` for a client.

For more information about arguments, please enter
```
python3 program.py -h
```

## Logic of my program
* I used ArgumentParser library to parse the arguments from the commands lines. If the filename is left empty, the program would be started as a server. Otherwise, it would be started as a client to transfer file.
* Firstly, I am using TCP three-way handshakes to establish the connection. The ACK (the third handshake) packet from the client to the server would attach the filename. After receiving the ACK packet for the filename packet mentioned above, the client would start to send the file content.
* After sending all the content, the client would send a FIN packet to ask the server close the file and the client would close itself when it receives a FINACK packet from the server. The server would close itself when it receives the ACK packet for the FINACK packet it sent.
* I used SHA-1 to verify the packet. Retransmitting would happen when the previous sending packet is timeout or the packet received is invalid.

## Packet Structure
* 40-byte checksum
* 1-byte sequence number
* 3-byte total size of the actual data
* 1-byte signifying if the packet is last
* 467-byte of data
