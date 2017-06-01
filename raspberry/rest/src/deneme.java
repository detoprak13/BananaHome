import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONArray;
import org.json.JSONObject;

public class deneme {

	public static void main(String[] args) {

		try{
			
			if(args[0].equals("send")){
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
			
				  a.put("humidity", Integer.valueOf(args[1]));
				  a.put("temperature", Integer.valueOf(args[2]));
				  
				  String payload = a.toString();
			
			
				 System.out.println(a);
				 
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
				
					  
					}
			
			else if(args[0].equals("get")){
				
				
				  String url = "http://34.201.239.10/Thingworx/Things/exampleThing/Properties";
					  URL obj = new URL(url);
					  HttpURLConnection con = (HttpURLConnection) obj.openConnection();
					 
					  //add request header
					  con.setRequestMethod("GET");
					  con.setRequestProperty("Accept", "application/json");
					  
					  con.setRequestProperty("Content-Type", "application/json");
					  con.setRequestProperty("appKey", "8a5a6287-93e0-4729-ad49-0311913fb389");
				  con.setUseCaches(false);
				  con.setDoOutput(true);
				  
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
					  //print result
					  JSONObject responseJson = new JSONObject(response.toString());
					  
					   JSONArray inputs = responseJson.getJSONArray("rows");
					   int temperature = 0;
					   
					   for(int i = 0; i<inputs.length();i++){
						   JSONObject temp = inputs.getJSONObject(i);
						   temperature = temp.getInt("temperature");
					   }
					   System.out.println(temperature);
				
			}
			else{
						System.out.println("ERROR");
				}
			

			  
			  
			  
		
	}
	
	catch(Exception e){
		e.printStackTrace();
	}
		
		
	}
}
	