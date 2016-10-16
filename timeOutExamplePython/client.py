import sys, socket, threading, select

def main():
	PORT = 8888

	cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cSock.connect(("localhost", PORT))

	timeOut = 10 # Wait for three seconds.

	while True:
		cSock.send(b"Test")

		#Following part is how to handle timeout event. Please pay attention!

		ready = select.select([cSock], [], [], timeOut) 
		if ready[0]:
			data = cSock.recv(512).decode()
			print(data)
		else:
			print("Timeout! Retransmitting...")
main()