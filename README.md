# CSCI4211_Project_2

Name: Tiannan Zhou

ID: 5232494

Email: zhou0745@umn.edu

## Usage

Server:
```
python3 program.py [-n HOST] [-p PORT]
```
The default values of Host and Port are `localhost` and `5001` for a server.

Client:
```
python3 program.py [-n HOST] [-p PORT] -f FILENAME
```
As a client, the name of file is required. The default values of Host and Port are `localhost` and `5002` for a client.

For more information about arguments, please enter
```
python3 program.py -h
```

## Logic of my program
* I used ArgumentParser library to parse the arguments. If the filename is left empty, the program would be started as a server. Otherwise, it would be started as a client.
* I am using TCP three-way-handshakes to establish the connection. The ACK (the third handshake) packet from the client would attach the filename. After receiving the ACK packet for the filename packet mentioned above, the client would start to send the file content.
* After sending all the content, the client would send a FIN packet to ask the server to close the file and the client would close itself when it receives a FINACK packet. The server would close itself when it receives the ACK packet for the FINACK packet it sent or receives nothing.
* I used SHA-1 to verify the packet. Retransmitting would happen when the previous sending packet is timeout or the packet received is invalid.

## Packet Structure
* 40-byte checksum
* 1-byte sequence number
* 3-byte total size of the actual data
* 1-byte signifying if the packet is last
* 467-byte of data
