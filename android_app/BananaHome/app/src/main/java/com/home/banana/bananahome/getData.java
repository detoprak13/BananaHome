package com.home.banana.bananahome;

import android.app.Activity;
import android.content.Context;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.os.AsyncTask;
import android.util.Base64;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.HttpURLConnection;
import java.net.URL;

 class getData extends AsyncTask<Void, Void, String> {
        private Context mContext;

     public getData(){

     }

    @Override
    protected String doInBackground(Void... params) {
        // These two need to be declared outside the try/catch
        // so that they can be closed in the finally block.
        HttpURLConnection urlConnection = null;
        Reader reader;

        // Will contain the raw JSON response as a string.
        String forecastJsonStr;

        try {

            URL url = new URL("http://34.201.239.10/Thingworx/Things/exampleThing/Properties");

            // Create the request to OpenWeatherMap, and open the connection
            urlConnection = (HttpURLConnection) url.openConnection();
            urlConnection.setRequestMethod("GET");
            urlConnection.setRequestProperty("Accept", "application/json");
            urlConnection.setRequestProperty("Content-Type", "application/json");
            urlConnection.setRequestProperty("appKey", "8a5a6287-93e0-4729-ad49-0311913fb389");
            urlConnection.connect();

            // Read the input stream into a String
            InputStream inputStream = urlConnection.getInputStream();
            StringBuffer buffer = new StringBuffer();

            if (inputStream == null) {
                // Nothing to do.
                return null;
            }
          //  reader = new BufferedReader(new InputStreamReader(inputStream));
            reader = new InputStreamReader(inputStream);
            final char[] buf = new char[16384];
            int read;
            while ((read = reader.read(buf)) >0) {

                buffer.append(buf,0,read);
            }

            if (buffer.length() == 0) {
                // Stream was empty.  No point in parsing.
                return null;
            }
            forecastJsonStr = buffer.toString();
           inputStream.close();
            return forecastJsonStr;
        } catch (IOException e) {
            // If the code didn't successfully get the weather data, there's no point in attemping
            // to parse it.
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
            int temperature = 0;
            int humidity = 0;
            String image = "";
            String duman = "";
            for(int i = 0; i<inputs.length();i++){
                JSONObject temp = inputs.getJSONObject(i);
                temperature = temp.getInt("temperature");
                humidity = temp.getInt("humidity");
                image = temp.getString("ImagePhoto");
                duman = temp.getString("smoke");
            }
            byte[] imageAsBytes = Base64.decode(image.getBytes(), Base64.DEFAULT);
           status_fragment.humidity.setText(String.valueOf(humidity));
            status_fragment.temperature.setText(String.valueOf(temperature));
           status_fragment.status.setText(String.valueOf(duman));


           MainActivity.status.humidity.setText(String.valueOf(humidity)+"%");
            MainActivity.status.temperature.setText(String.valueOf(String.valueOf(temperature)+"°C"));
            if(String.valueOf(duman).equals("var")){
                MainActivity.status.status.setText("!!!ALERT!!!");
                MainActivity.status.status.setTextColor(Color.RED);
            }else{
                MainActivity.status.status.setText("OK");
                MainActivity.status.status.setTextColor(Color.BLACK);
            }
            MainActivity.photo.photo.setImageBitmap(BitmapFactory.decodeByteArray(imageAsBytes, 0, imageAsBytes.length));
            photoFragment.photo.setImageBitmap(BitmapFactory.decodeByteArray(imageAsBytes,0,imageAsBytes.length));
        }
        catch (Exception e){

        }
    }


}
