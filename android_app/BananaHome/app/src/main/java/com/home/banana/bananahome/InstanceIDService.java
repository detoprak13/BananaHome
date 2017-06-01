package com.home.banana.bananahome;


import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.FirebaseInstanceIdService;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;

public class InstanceIDService extends FirebaseInstanceIdService {

    @Override
    public void onTokenRefresh() {
        String token = FirebaseInstanceId.getInstance().getToken();

        sendToServer(token);
    }

    private void sendToServer(String token) {
        try {
            BufferedReader reader = null;
            URL url = new URL("http://34.201.239.10/Thingworx/Things/exampleThing/Properties/*");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("PUT");
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            JSONObject tokenjson = new JSONObject();
            tokenjson.put("token",token);
            String toWrite = tokenjson.toString();
            OutputStreamWriter osw = new OutputStreamWriter(connection.getOutputStream());
            osw.write(toWrite);
            osw.flush();
            osw.close();
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }

}



