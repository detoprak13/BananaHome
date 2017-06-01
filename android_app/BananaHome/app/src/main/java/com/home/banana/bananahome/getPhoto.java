package com.home.banana.bananahome;

import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.util.Base64;
import android.widget.ImageView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.logging.Level;
import java.util.logging.Logger;


class getPhoto extends AsyncTask<Void, Void, String> {
    ImageView photo;

     public getPhoto(){

     }

    @Override
    protected String doInBackground(Void... params) {
        HttpURLConnection urlConnection = null;
        Reader reader;
        String forecastJsonStr;
        try {
            URL url = new URL("http://34.201.239.10/Thingworx/Things/exampleThing/Properties");
            urlConnection = (HttpURLConnection) url.openConnection();
            urlConnection.setRequestMethod("GET");
            urlConnection.setRequestProperty("Accept", "application/json");
            urlConnection.setRequestProperty("Content-Type", "application/json");
            urlConnection.setRequestProperty("appKey", "8a5a6287-93e0-4729-ad49-0311913fb389");
            urlConnection.connect();

            InputStream inputStream = urlConnection.getInputStream();

            StringBuffer buffer = new StringBuffer();
            if (inputStream == null) {
                return null;
            }
           // reader = new BufferedReader(new InputStreamReader(inputStream));
            reader = new InputStreamReader(inputStream);
            final char[] buf = new char[16384];
            int read;

            while ((read = reader.read(buf)) >0) {

                buffer.append(buf,0,read);
            }

            if (buffer.length() == 0) {
                return null;
            }
            forecastJsonStr = buffer.toString();
            inputStream.close();
            return  forecastJsonStr;
        }catch (Exception e){
            e.printStackTrace();
            return null;
        }
        finally {
            urlConnection.disconnect();
        }
    }

    @Override
    protected void onPostExecute(String s) {
        super.onPostExecute(s);
        try {
            JSONObject response = new JSONObject(s);
            JSONArray inputs = response.getJSONArray("rows");

            String image = "";

            for (int i = 0; i < inputs.length(); i++) {
                JSONObject temp = inputs.getJSONObject(i);
                image = temp.getString("ImagePhoto");

            }

            byte[] imageAsBytes = Base64.decode(image.getBytes(), Base64.DEFAULT);

            photo.setImageBitmap(BitmapFactory.decodeByteArray(imageAsBytes, 0, imageAsBytes.length));
            photo.setImageBitmap(BitmapFactory.decodeByteArray(imageAsBytes, 0, imageAsBytes.length));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }



}
