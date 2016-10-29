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

## Packet Structure
* 40-byte checksum
* 1-byte sequence number
* 3-byte total size of the actual data
* 1-byte signifying if the packet is last
* 467-byte of data
