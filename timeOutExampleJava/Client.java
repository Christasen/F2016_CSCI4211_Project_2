import java.io.*;
import java.net.*;

class Client {
	public static void main(String[] args) throws Exception {
		String host = "localhost"; // Remote hostname. It can be changed to anything you desire.
		int port = 8888; // Port number.
		String sentence; // Store user input.
		String data; // Store the server's feedback.

		Socket cSock = null;
		DataOutputStream sendOut = null;
		BufferedReader readFrom = null;

		try{
			cSock = new Socket(host, port); // Initialize the socket.
			sendOut = new DataOutputStream(cSock.getOutputStream()); // The output stream to server.
			readFrom = new BufferedReader(new InputStreamReader(cSock.getInputStream())); // The input stream from server.
		} catch (Exception e) {
			System.out.println("Error: cannot open socket");
			System.exit(1); // Handle exceptions.
		}


		/* Following part is how to handle timeout event. Please pay attention! */

		while(true){
			sendOut.writeBytes("Test" + "\n");
			cSock.setSoTimeout(5000); // Set the time out in milliseconds.
			try{
				data = readFrom.readLine();
				System.out.println(data);
			} catch (SocketTimeoutException e) {
				System.out.println("Timeout! Retransmitting...");
			}
		}
	}
}