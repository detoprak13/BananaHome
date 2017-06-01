package filedeneme;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONObject;

public class deneme {

	public static void main(String[] args) {
		try{
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

	  a.put("smoke",String.valueOf(args[0]));
	
	  
	  String payload = a.toString();

	 
  OutputStreamWriter out = new OutputStreamWriter(
		    con.getOutputStream());

	  		out.write(payload);
			out.flush();
			out.close();	 
		
  
	  
	  int responseCode = con.getResponseCode();
		 

		  BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
		  String inputLine;
		  StringBuilder response = new StringBuilder();
		 
		  while((inputLine = in.readLine()) != null) {
		  response.append(inputLine);
		  }	 
		  in.close();
		  		
		  
		}
	
catch(Exception e){
	e.printStackTrace();
}
}
}

