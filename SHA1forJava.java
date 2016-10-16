import java.security.MessageDigest;



public static String SHA1(String inputText) {
	byte arr[] = null;

	try{
		MessageDigest m = MessageDigest.getInstance("SHA-1");  
		m.update(inputText.getBytes("UTF8"));  
		arr = m.digest();
	} catch (Exception e){
	}
		
	StringBuffer sb = new StringBuffer();  
	for (int i = 0; i < arr.length; ++i) {  
		sb.append(Integer.toHexString((arr[i] & 0xFF) | 0x100).substring(1,3));  
	}  
	return sb.toString();  
}