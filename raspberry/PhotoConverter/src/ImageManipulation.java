import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import org.apache.commons.io.IOUtils;
import org.json.JSONObject;
import java.util.Base64;

public class ImageManipulation {

	public static void main(String[] args) {

		File file = new File("/home/pi/Desktop/image.jpg");

		
		
		try {			
			FileInputStream imageInFile = new FileInputStream(file);
			byte[] imageBytes = IOUtils.toByteArray(imageInFile);
			String base64 = Base64.getEncoder().encodeToString(imageBytes);
			System.out.println(base64);
			System.out.println("Image Successfully Manipulated!");
		
		
			 String url = "http://34.201.239.10/Thingworx/Things/exampleThing/Properties/*";
			  URL obj = new URL(url);
			  HttpURLConnection con = (HttpURLConnection) obj.openConnection();
			 
			  con.setRequestMethod("PUT");
			  con.setRequestProperty("Accept", "application/json");
			  
			  con.setRequestProperty("Content-Type", "application/json");
		  con.setRequestProperty("appKey", "8a5a6287-93e0-4729-ad49-0311913fb389");
		  con.setUseCaches(false);
		  con.setDoOutput(true);
		  

		  JSONObject a = new JSONObject();
	
		  a.put("ImagePhoto",base64);
	
		  
	String payload = a.toString();
	  OutputStreamWriter out = new OutputStreamWriter(
			    con.getOutputStream());
 
		  		out.write(payload);
				out.flush();
			out.close();	 
				  
		  int responseCode = con.getResponseCode();
			 
		  System.out.println("\nSending 'POST' request to URL : " + url);
		  System.out.println("Response Code : " + responseCode);
	
			  BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
			  String inputLine;
			  StringBuilder response = new StringBuilder();
			 
			  while((inputLine = in.readLine()) != null) {
			  response.append(inputLine);
			  }
			  
			 
			  in.close();	
			  System.out.println(response.toString());
			
		} catch (FileNotFoundException e) {
			System.out.println("Image not found" + e);
		} catch (IOException ioe) {
			System.out.println("Exception while reading the Image " + ioe);
		}
	}



}