package com.home.banana.bananahome;


import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CompoundButton;
import android.widget.ImageView;
import android.widget.Switch;
import android.widget.TextView;


/**
 * A simple {@link Fragment} subclass.
 */
public class status_fragment extends Fragment {
    ImageView photo;
  static    TextView humidity;
  static     TextView temperature;
   static    TextView status;
    photoFragment photoFragment;
    Switch switchButton;
    boolean isOccured = false;

    public status_fragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view =  inflater.inflate(R.layout.fragment_status_fragment, container, false);
        photoFragment = new photoFragment();
        photo = (ImageView)view.findViewById(R.id.photoLinear);
        photo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                MainActivity.sendMessage("Showing the last photo of the door");
                FragmentTransaction ft = getFragmentManager().beginTransaction();
                ft.replace(R.id.applicationFragment,photoFragment);
                ft.addToBackStack(null);
                ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
                ft.commit();
            }
        });

        humidity = (TextView)view.findViewById(R.id.humidity);
        switchButton = (Switch)view.findViewById(R.id.switch2);
        status = (TextView) view.findViewById(R.id.status);
        temperature = (TextView)view.findViewById(R.id.temperature);
        switchButton.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    if(!isOccured) {
                        putVoiceCommand pvc = new putVoiceCommand();
                        pvc.comm = "lights on";
                        pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                        MainActivity.sendMessage("Lights on");
                        isOccured = true;
                    }
                } else {
                    putVoiceCommand pvc = new putVoiceCommand();
                    pvc.comm = "lights off";
                    pvc.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
                    MainActivity.sendMessage("Lights off");
                    isOccured = false;

                }
            }
        });
        return view;
    }



}