package voiceCommandParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONArray;
import org.json.JSONObject;

public class Main {
	private static boolean alreadyPlayed = false;
	public static void main(String[] args) {
		while(true){
		try{
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
		   String voiceCommand = "";
		   for(int i = 0; i<inputs.length();i++){
			   JSONObject temp = inputs.getJSONObject(i);
			   voiceCommand = temp.getString("voiceCommand");
		   }
	
		   if(voiceCommand.equals("")){
			   
		   }
		   else{
		  
		    if(voiceCommand.toLowerCase().substring(0,4).equals("play")){
			   if(alreadyPlayed){
				   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/stopmusic.sh");
				   Process p = pb.start();
				   playMusic(voiceCommand.substring(11, voiceCommand.length()));
			   }
			   else{
				   alreadyPlayed = true;
			   playMusic(voiceCommand.substring(11, voiceCommand.length()));
}
		   }
		   else if(voiceCommand.toLowerCase().equals("pause music")){
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/pausemusic.sh");
			   Process p = pb.start();
		   }
		   else if(voiceCommand.toLowerCase().equals("volume down")){
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/volumedown.sh");
			   Process p = pb.start();
		   }
		   else if(voiceCommand.toLowerCase().equals("volume up")){
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/volumeup.sh");
			   Process p = pb.start();
		   }
		   else if(voiceCommand.toLowerCase().equals("forward")){
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/seekplus5.sh");
			   Process p = pb.start();
		   }
		   else if(voiceCommand.toLowerCase().equals("backward")){
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/seekminus5.sh");
			   Process p = pb.start();
		   }
		   else if(voiceCommand.toLowerCase().equals("quit music")){
			   	clearMusic();
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/stopmusic.sh");
			   Process p = pb.start();
			   
		   }
		   else if(voiceCommand.toLowerCase().equals("mute")){
			   ProcessBuilder pb = new ProcessBuilder("sh","/home/pi/Desktop/mute.sh");
			   Process p = pb.start();
		   }
		    
		   else if(voiceCommand.toLowerCase().equals("lights on")){
			   ProcessBuilder pb = new ProcessBuilder("python","/home/pi/Desktop/led/ledon.py");
			   Process p = pb.start();
		   }
		   else if(voiceCommand.toLowerCase().equals("lights off")){
			   ProcessBuilder pb = new ProcessBuilder("python","/home/pi/Desktop/led/ledoff.py");
			   Process p = pb.start();
			   
		   }
		    
		    
		   else{
		   }
		   
		   resetVoice();
		   }
		   
		}
		catch(Exception e){
			e.printStackTrace();
		}
		
		}
	}
	
	public static void resetVoice(){
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

	  a.put("voiceCommand", String.valueOf(""));
	  
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
	
	
	public static void playMusic(String music){
		   try{
			    PrintWriter writer = new PrintWriter("/home/pi/Desktop/test.txt", "UTF-8");
			    writer.println("search "+music);
			    writer.close();
			} catch (IOException e) {
			   // do something
			}
	}
	

	public static void clearMusic(){
		   try{   
			    PrintWriter writer = new PrintWriter("/home/pi/Desktop/test.txt", "UTF-8");
			    writer.println("");
			    writer.close();
			} catch (IOException e) {
			   // do something
			}
	}

}
