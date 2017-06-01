package com.home.banana.bananahome;



import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageView;


/**
 * A simple {@link Fragment} subclass.
 */
public class music_player extends Fragment {
    boolean buttonplay = true;
    EditText songname;
    String compare = "";
    ImageView playbutton;
    ImageView lowvolume;
    ImageView highvolume;
    ImageView forward5;
    ImageView backward5;
    ImageView mutebutton;
    boolean ismuted = false;
    boolean isPlay = true;

    public music_player() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
       View view = inflater.inflate(R.layout.fragment_music_player, container, false);
        playbutton = (ImageView)view.findViewById(R.id.playPauseButton);

        songname = (EditText)view.findViewById(R.id.songName);
        lowvolume = (ImageView)view.findViewById(R.id.low);
        highvolume = (ImageView)view.findViewById(R.id.high);
        forward5 = (ImageView) view.findViewById(R.id.forwardButton);
        backward5 = (ImageView)view.findViewById(R.id.backButton);
        mutebutton = (ImageView)view.findViewById(R.id.muteButton);

        if(ismuted){
            mutebutton.setImageResource(R.drawable.mute);
        }
        else{
            mutebutton.setImageResource(R.drawable.unmute);
        }


        mutebutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                putVoiceCommand pvc = new putVoiceCommand();
                pvc.comm = "mute";
             //   pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                 pvc.execute();

                if(ismuted){
                    mutebutton.setImageResource(R.drawable.unmute);
                    ismuted = false;
                }else{
                    mutebutton.setImageResource(R.drawable.mute);
                    ismuted = true;
                }


            }
        });


        lowvolume.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                putVoiceCommand pvc = new putVoiceCommand();
                pvc.comm = "volume down";
                pvc.execute();
                //pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            }
        });

        highvolume.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                putVoiceCommand pvc = new putVoiceCommand();
                pvc.comm = "volume up";
                pvc.execute();

                //  pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            }
        });

        forward5.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                putVoiceCommand pvc = new putVoiceCommand();
                pvc.comm = "forward";
                pvc.execute();
                //     pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            }
        });

        backward5.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                putVoiceCommand pvc = new putVoiceCommand();
                pvc.comm = "backward";
                pvc.execute();

                //   pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            }
        });


        if(isPlay) {
            playbutton.setImageResource(R.drawable.playbutton);
        }
        else{
            playbutton.setImageResource(R.drawable.pausebutton);
        }



        playbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(buttonplay){

                    String songName = songname.getText().toString();
                    if(songName.equals("")){

                    }
                    else if(songName.equals(compare)){
                        playbutton.setImageResource(R.drawable.pausebutton);
                        buttonplay = false;
                        String voice = "Resuming music ";
                        MainActivity.sendMessage(voice);
                        putVoiceCommand pvc = new putVoiceCommand();
                        pvc.comm = "pause music";
                        pvc.execute();
                        //       pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                        isPlay = false;
                    }
                    else {

                            playbutton.setImageResource(R.drawable.pausebutton);
                            buttonplay = false;
                            String voice = "Playing music " + songName;
                        compare = songName;
                            MainActivity.sendMessage(voice);
                               putVoiceCommand pvc = new putVoiceCommand();
                              pvc.comm = "play music " +songName;
                       //      pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                        pvc.execute();
                        isPlay = false;
                        }

                }
                else{

                        buttonplay = true;
                        MainActivity.sendMessage("Pausing music");
                        playbutton.setImageResource(R.drawable.playbutton);
                    putVoiceCommand pvc = new putVoiceCommand();
                    pvc.comm = "pause music";
                    pvc.execute();
                    //  pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                        isPlay = true;



                }
            }
        });



        return view;
    }


}
