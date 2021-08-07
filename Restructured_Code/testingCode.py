def animation_frame(FrameNumber,trial_count,ax):
    global AllRelativeSpikes
  


    

    if(bool(start_index) and len(ax)>0):
        time_start = EventCodeArray[start_index[0]][0]
        
        # Finding all trail stop events
        stop_index = [i for i,v in enumerate(EventCodeArray[:N]) if (v[1]==stop_ec and float(v[0])>(time_start) )]
        
        # Finding all the sample ON times 
        sampleON_index = [i for i,v in enumerate(EventCodeArray[:N]) if (v[1]==sample_on_ec and float(v[0])>(time_start) )]

        # Finding all sample OFF times
        sampleOFF_index = [i for i,v in enumerate(EventCodeArray[:N]) if (v[1]==sample_off_ec and float(v[0])>(time_start) )]

        # Finding all test ON times
        testON_index = [i for i,v in enumerate(EventCodeArray[:N]) if (v[1]==test_on_ec and float(v[0])>(time_start) )]
    
    if(bool(start_index) and bool(stop_index)): # Execute only if trial start and stop is recorded

        time_stop = EventCodeArray[stop_index[0]][0]
        trial_count[0] = trial_count[0]+1
        
        #print('Trial Count = ',trial_count)
        # Finding the trial type
       # print(EventCodeArray)
        trial_type = [v[1] for i,v in enumerate(EventCodeArray[:N]) if  float(v[0])>(time_start) and float(v[0])<=time_stop and (v[1]==same_ec or v[1] ==diff_ec) ]
        
        # Discarding all the event codes between start and stop event codes
        for i in range(stop_index[0],start_index[0]-1,-1):  
            EventCodeArray.pop(i)

        print(EventCodeArray)
        # Finding the relative spike times wrt Sample  ON time s
        time_sample_ON=EventCodeArray[sampleON_index[0]][0];
        Relative_spike_times = [v[0]-time_sample_ON for i,v in enumerate(SpikeArray[:Nspike]) if (v[0]>=time_start and v[0]<=time_stop)]
        AllRelativeSpikes[2]=AllRelativeSpikes[2]+Relative_spike_times

        # Trial_typewise analysis
        if(bool(trial_type)):# 0: Same 1: Different 

            index = int(trial_type[0])-ec_shift_tt-1 # adding the trial raster to subplots based on trial type
            
            AllRelativeSpikes[index]=AllRelativeSpikes[index]+Relative_spike_times # Saving trialwise relative spike times to all spikes array

            # Raster
            ax[3+index].eventplot (positions = Relative_spike_times,lineoffset =trial_count ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[index] )
            ax[5].eventplot (positions = Relative_spike_times,lineoffset =trial_count ,orientation ='horizontal', linewidths =2,linelengths =1,colors=colors_value[2] )
   
           
            # Histogram
            # Plotting for both Same and Different    
            ax[index].clear()        
            ax[0].set_ylabel(ylabel_names[0])
            ax[index].set_title(title_names[index])
            ax[index].hist(AllRelativeSpikes[index],bins=hist_bins,density=True,color=colors_value[index])
            
            # Plotting for all trials
            ax[2].clear()
            ax[2].hist(AllRelativeSpikes[2],bins=hist_bins,density=True,color=colors_value[2])
            ax[2].set_title(title_names[2])