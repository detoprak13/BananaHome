package com.home.banana.bananahome;

import android.os.AsyncTask;
import android.util.Log;
import org.json.JSONObject;


import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.logging.Level;
import java.util.logging.Logger;


class putVoiceCommand extends AsyncTask<Void, Void, String> {
    String comm = "";

     public putVoiceCommand(){
     }
    @Override
    protected String doInBackground(Void... params) {
        HttpURLConnection urlConnection = null;
        try {

            URL url = new URL("http://34.201.239.10/Thingworx/Things/exampleThing/Properties/*");
            urlConnection = (HttpURLConnection) url.openConnection();
            urlConnection.setRequestMethod("PUT");
            urlConnection.setRequestProperty("Accept", "application/json");
            urlConnection.setRequestProperty("Content-Type", "application/json");
            urlConnection.setRequestProperty("appKey", "8a5a6287-93e0-4729-ad49-0311913fb389");
            urlConnection.connect();

            JSONObject cmd = new JSONObject();
            cmd.put("voiceCommand", comm);
            String payload = cmd.toString();
            Log.d("payload ",payload);
            OutputStreamWriter out = new OutputStreamWriter(
                    urlConnection.getOutputStream());

            out.write(payload);
            out.flush();
            out.close();



            return urlConnection.getInputStream().toString();

        } catch (Exception e) {
            Log.e("PlaceholderFragment", "Error ", e);
            return null;

        } finally {
            if (urlConnection != null) {
                urlConnection.disconnect();
            }
        }
    }

    @Override
    protected void onPostExecute(String s) {
        super.onPostExecute(s);

    }
}
