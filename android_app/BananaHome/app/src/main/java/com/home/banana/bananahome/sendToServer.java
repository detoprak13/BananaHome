package com.home.banana.bananahome;

import android.os.AsyncTask;
import android.util.Log;

import org.json.JSONObject;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.logging.Level;
import java.util.logging.Logger;

class sendToServer extends AsyncTask<Void, Void, String> {
    String token = "";
     HttpURLConnection connection = null;
     public sendToServer(){
     }

    @Override
    protected String doInBackground(Void... params) {
        // These two need to be declared outside the try/catch
        try {
            URL url = new URL("http://34.201.239.10/Thingworx/Things/exampleThing/Properties/*");
            connection  = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("PUT");
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("appKey", "8a5a6287-93e0-4729-ad49-0311913fb389");
            JSONObject tokenjson = new JSONObject();
            tokenjson.put("token",token);
            String toWrite = tokenjson.toString();
            OutputStreamWriter osw = new OutputStreamWriter(connection.getOutputStream());
            osw.write(toWrite);
            osw.flush();
            osw.close();
            int responsecode = connection.getResponseCode();
            Log.d("RESPONSE CODE SERVER: ",""+responsecode);
            return "OK";
        }
        catch (Exception e){
            e.printStackTrace();
            return null;
        }

    }

    @Override
    protected void onPostExecute(String s) {
        super.onPostExecute(s);

    }

}
