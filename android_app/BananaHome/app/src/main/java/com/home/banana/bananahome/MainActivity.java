package com.home.banana.bananahome;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.StrictMode;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.support.v4.app.FragmentTransaction;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.LinearLayout;
import com.google.firebase.iid.FirebaseInstanceId;
import java.util.ArrayList;
import java.util.Locale;



public class MainActivity extends AppCompatActivity {

    public static TextToSpeech tts;
    public LinearLayout statusLayout;
    public LinearLayout voiceLinear;
    public LinearLayout musicLayout;
    static music_player muplayer;
     static status_fragment status;
      static photoFragment photo;

    private final  int REQ_CODE_SPEECH_OUTPUT = 143;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        muplayer = new music_player();
        status = new status_fragment();
        photo = new photoFragment();
        tts = new TextToSpeech(getApplicationContext(),new TextToSpeech.OnInitListener(){
            @Override
            public void onInit(int status) {
                if(status != TextToSpeech.ERROR) {
                    tts.setLanguage(Locale.US);
                }
            }
        });

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);
        initListening();
        sendToServer sts = new sendToServer();
        sts.token = FirebaseInstanceId.getInstance().getToken();
        sts.execute();

        statusLayout = (LinearLayout) findViewById(R.id.StatusLinear);
        musicLayout = (LinearLayout) findViewById(R.id.musicLinear);
        voiceLinear = (LinearLayout)findViewById(R.id.voiceLinear);

        statusLayout.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
               ft.replace(R.id.applicationFragment,status);
               ft.addToBackStack(null);
                ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
                ft.commit();
            }
        });

        musicLayout.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
               ft.replace(R.id.applicationFragment,muplayer);
              ft.addToBackStack(null);
                ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
                ft.commit();
            }
        });

        voiceLinear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openMic();
            }
        });


        String act = (String) getIntent().getSerializableExtra("activityToStart");
        if(act != null) {
            if (act.equals("photo")) {
                Log.d("XXXXXXX","YYYYYYY");
                FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
                photo.startedFromNotification = true;
                ft.replace(R.id.applicationFragment, photo);
                ft.addToBackStack(null);
                ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
                ft.commit();
            }
            else{
                status_fragment a;
                if(act.equals("gas")){
                    a = new status_fragment();
                    Log.d("OLDU BACIM","OLDU BACIM");
                    FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
                    ft.replace(R.id.applicationFragment, a);
                    ft.addToBackStack(null);
                    ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
                    ft.commit();
                }
            }
        }else {

                FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
                ft.replace(R.id.applicationFragment, status);
                ft.addToBackStack(null);
                ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
                ft.commit();

        }

    }


        private  void openMic(){
            Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);

            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT,"Hi Speak Now");

            try{
            startActivityForResult(intent,REQ_CODE_SPEECH_OUTPUT);
            }
            catch(ActivityNotFoundException tim){

            }
        }

        @Override
        protected void onActivityResult(int requestCode,int resultCode,Intent data){
                super.onActivityResult(requestCode,resultCode,data);
            switch (requestCode){
                case REQ_CODE_SPEECH_OUTPUT: {
                    if(resultCode == RESULT_OK && null != data){
                        ArrayList<String> voiceInText = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                        Log.d("VOICE: ",voiceInText.get(0));
                       putVoiceCommand vo = new putVoiceCommand();
                        vo.comm = voiceInText.get(0);
                         vo.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                    }
                    break;
                }
            }

        }


        public void initListening(){
           runTimer();
        }


    private void runTimer() {
        final Handler handler = new Handler();
        handler.post(new Runnable() {
            @Override
            public void run() {
                    handler.postDelayed(this, 3000);
                new getData().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            }
        });

    }





    public static void sendMessage(String message){
        tts.speak(message,TextToSpeech.QUEUE_FLUSH,null,null);
    }


}