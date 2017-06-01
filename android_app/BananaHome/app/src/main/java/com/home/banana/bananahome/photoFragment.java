package com.home.banana.bananahome;

import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.ProgressBar;



public class photoFragment extends Fragment {
    private ProgressBar spinner;
    static ImageView photo;
    static boolean startedFromNotification = false;
    public photoFragment() {
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_photo, container, false);
        spinner = (ProgressBar) view.findViewById(R.id.progressBar1);
        photo = (ImageView)view.findViewById(R.id.photo);
        LoadingBar();

        if(startedFromNotification){
           getPhoto gp = new getPhoto();
            gp.photo = photo;
            gp.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
        }


        return view;
    }


    private void LoadingBar() {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                Log.d("ÇALIŞIYORUM","ÇALIŞIYORUM");
                spinner.setVisibility(View.GONE);
            }
        }, 5000);
    }

}
