package firebaseNotification;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import javax.net.ssl.HttpsURLConnection;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
 
 
/**
 * @author athakur
 */
public class FCMMessageSender {
     
    public static final String FCM_URL = "https://fcm.googleapis.com/fcm/send";
    public static final String FCM_SERVER_API_KEY    = "AAAA11u5iWo:APA91bE61edj7Utad1Z5Px3X-rzqasHiUC_EZaf-I-wkBH4rLJQGZ0QI5fxVH_Y2KzrDKbzV2iwqekkrRYFmxV_46ZNh2ge6R0gY5KOgz_zTYg5cUy82hFpixKX_EQeLFu7BNIhqkgff";
  //  private static final String deviceRegistrationId =  "e0ONw_ejb_s:APA91bH7MNwyPjPPoMny2fOFkQgEm1PVv4QZjM-_LxRCzcWAc23PHv4ui84al9QvD-oERkiFqV_OehXgU00DCaKlnqvVLJAr8mgoYRpk8_B9Hkxqekhs49TLChv5MtiFowXg1eRQqRug";
 
    public static void main(String args[])
    {
    	   try{
    	 
    	 String authKey = FCM_SERVER_API_KEY; // You FCM AUTH key
         String FMCurl = FCM_URL; 
      
         URL url2 = new URL(FMCurl);
         HttpURLConnection conn = (HttpURLConnection) url2.openConnection();

         conn.setUseCaches(false);
         conn.setDoInput(true);
         conn.setDoOutput(true);

         conn.setRequestMethod("POST");
         conn.setRequestProperty("Authorization","key="+authKey);
         conn.setRequestProperty("Content-Type","application/json");
         JSONObject json = new JSONObject();
         
         json.put("to","fZDCEMndvYY:APA91bEO6Tu-MGOgrNyjGgG7QANIJOV4y6pEdAl2rJk6nTkV75iezvYaenCQNTjofmng7qqLNUszdJU2UUGor6aHN_bX0b8OIO9cqcbWI5ECm2IiJuITBEN1WIFVJT5G3FrIwQ9sOU2p");
         JSONObject info = new JSONObject();
         info.put("title", "Kenkim Home"); // Notification title
         info.put("body", "NABER"); // Notification body
         info.put("sound", "default");
         json.put("data", info);

         OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
         wr.write(json.toString());
         wr.flush();
         conn.getInputStream();
		 
	
			  BufferedReader in2 = new BufferedReader(new InputStreamReader(conn.getInputStream()));
			  String inputLine2;
			  StringBuilder response2 = new StringBuilder();
			 
			  while((inputLine2 = in2.readLine()) != null) {
			  response2.append(inputLine2);
			  }
			  
			 
			  in2.close();	
			  System.out.println(response2.toString());
         }
         catch(Exception e){
        	e.printStackTrace();
         }
   
}
    
   

    
}

