import java.io.*;
import java.net.*;
import java.util.*;

class Server {
	public static void main(String[] args) throws Exception {
		int port = 8888;
		ServerSocket welcomeSock = null;

		try {
			welcomeSock = new ServerSocket(port);
		} catch (Exception e) {
			System.out.println("Error: cannot open socket");
			System.exit(1); // Handle exceptions.
		}

		System.out.println("Server is listening on port 8888...");

            Socket sSock = welcomeSock.accept();
		try{
            	BufferedReader inFromClient = new BufferedReader(new InputStreamReader(sSock.getInputStream()));
            	PrintWriter sendOut = new PrintWriter(sSock.getOutputStream(), true);
            	
                  while(true){
                        String data = inFromClient.readLine();
                        
                        Random rand = new Random();
                        int pm = rand.nextInt(100);

                        if(pm<=50){
                              System.out.println("ACK is lost on the way.");
                        } else {
                              System.out.println("ACK is transmitted.");
                              sendOut.println("ACK");
                        }

                  }

            } catch(Exception e){
                  // Do nothing here.
            }

	}
}