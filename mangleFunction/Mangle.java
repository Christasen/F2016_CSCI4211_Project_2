import java.io.*;
import java.net.*;
import java.util.*;

class Mangle{
	public static void main(String[] args) throws Exception {
		String packet = "";
		for (int i = 0; i < 512; i++){
			packet = packet + "a";
		} // Make a packet.
		
		while(true){
			String mangledPacket = replace(packet, 2, 20, 20);
			System.out.println(mangledPacket);
		}
	}

	public static String replace(String packet, int delay, int drop, int mangle){
		try{
			Thread thread = Thread.currentThread();
  			thread.sleep(delay * 1000);
		} catch (Exception e) {

		}
	
		String result = "";

		if (packet.length() < 512) return result;

		Random rand = new Random();
        int prob = rand.nextInt(100);

		if (prob < drop + mangle){
			if (prob < drop) {
				return result;
			} else {
				for (int i = 0; i < 512; i++){
					int charInt = rand.nextInt(94) + 32;
					char[] character = Character.toChars(charInt);
					String temp = Character.toString(character[0]);
					result = result + temp;
				}
				return result;
			}
		} else {
			return packet;
		}
	}
}
