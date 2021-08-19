import numpy as np
import time
import threading
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle

import conditionevents
import spikeevents
import eventcode
import customlib as lib
# Network Address
eCubeAddress = '10.120.10.55' # IISc network ip of the PC running server-node control
openephysAddress = '10.120.10.55' # OpenEphys ~0.4.2-0.4.3 EventBroadcaster module address after spike sorting


RelativeSpikes_all_correct   =  []
RelativeSpikes_same_correct  =  []
RelativeSpikes_diff_correct  =  []
RelativeSpikes_same_wrong    =  []
RelativeSpikes_diff_wrong    =  []

EventCodeArray      =   []
SpikeArray          =   []

# Event Codes directly used
start_ec                = eventcode.Dict['trl.start']
stop_ec                 = eventcode.Dict['trl.footerStop']
same_ec                 = eventcode.Dict['trl.expRespSame']
diff_ec                 = eventcode.Dict['trl.expRespDiff']
sample_on_ec            = eventcode.Dict['pic.sampleOn']
sample_off_ec           = eventcode.Dict['pic.sampleOff']
test_on_ec              = eventcode.Dict['pic.testOn']

#  Footer Shifts  
ec_trialtype_shift      = 9000  # 9000+  1 for same , 9000 +2 for different  
ec_trial_error_shift    = eventcode.Dict['trl.outcomeShift']   # 8500 + 0 correct, 8500 + 6 wrong 
errorcode_correct       = 0
errorcode_wrong         = list(range(1,9+1))



# maintain sample_width and delay_between sample and test as per the running experiment.
sample_width=0.4 # 400 ms, 
delay_between_sample_test= 0.2 # 200 ms

# Plotting
ax0_ylim=1
ax1_ylim=1
# relative time axis wrt to sample on time. 
bin_width = 0.02
relative_time_range = (-0.2,sample_width+delay_between_sample_test+0.4)
relative_time_range_globalraster = (-0.4,sample_width+delay_between_sample_test+2.0)

nbin    =   round((relative_time_range[1]-relative_time_range[0])/bin_width) # dividing by bin width
hist_bins =np.linspace(relative_time_range[0],relative_time_range[1],nbin+1)

# trial_counters
tc_same_correct =1
tc_diff_correct =1
tc_all_correct =1
tc_same_wrong =1
tc_diff_wrong =1


colors_value = ['C{}'.format(i) for i in range(6)] # Colours used

(fig,ax) = lib.figure_layout_creation(0) # Initializing the Layout
for i in range(7):
    ax[i].add_patch( Rectangle((0.0,0.0 ),sample_width, 100,color ='k',alpha=0.1) ) # Sample ON
    if(i!=4):
        ax[i].add_patch( Rectangle((sample_width+delay_between_sample_test, 0.0),relative_time_range[1]-(sample_width+delay_between_sample_test), 100,color ='k',alpha=0.1) ) # Test ON
    else:
        ax[i].add_patch( Rectangle((sample_width+delay_between_sample_test, 0.0),relative_time_range_globalraster[1]-(sample_width+delay_between_sample_test), 100,color ='k',alpha=0.1) ) # Test ON


# ******************************************************************************************************************************************* #
def animation_frame(FrameNumber):
    global RelativeSpikes_all_correct, RelativeSpikes_same_correct, RelativeSpikes_diff_correct, ax 
    global RelativeSpikes_same_wrong, RelativeSpikes_diff_wrong
    global tc_same_correct,tc_diff_correct,tc_all_correct,tc_same_wrong,tc_diff_wrong
    global relative_time_range
    global ax0_ylim, ax1_ylim
    # Calculate N to avoid considering synchronous updation. 
    # This current updation happens only till the first N value. Remaining will be considered during the next cycle. 
    N=len(EventCodeArray)
    Nspike=len(SpikeArray)

    # Finding all the trial start-event codes
    start_index = [i for i,v in enumerate(EventCodeArray[:N]) if v[1]==start_ec] # v is 1x 2 dimensional vector in the form [time, eventcode].
    
    if(bool(start_index)):
    # Finding all trial stop events
        time_start = EventCodeArray[start_index[0]][0]
        stop_index = [i for i,v in enumerate(EventCodeArray[:N]) if (v[1]==stop_ec and float(v[0])>(time_start) )]
        if(bool(stop_index)):
            ctrialEventCodes=EventCodeArray[start_index[0]:stop_index[0]]
            # Discarding all the event codes between start and stop event codes
            for i in range(stop_index[0],start_index[0]-1,-1):  
                EventCodeArray.pop(i)

            time_stop = ctrialEventCodes[-1][0]
            trial_outcome = [int(v[1]-ec_trial_error_shift) for v in (ctrialEventCodes) if (v[1]>=ec_trial_error_shift and v[1]<=ec_trial_error_shift+max(errorcode_wrong) )]

            # Correctly responded trials (pressed either of the choices correctly)
            if(trial_outcome[0]==0 or trial_outcome[0]==6  ):
                
                # sample ON, OFF, test ON
                sampleON_time   = [v[0] for v in ctrialEventCodes   if v[1]==sample_on_ec]
                sampleON_time   = sampleON_time[0]
                
                sampleOFF_time  = [v[0] for v in ctrialEventCodes   if v[1]==sample_off_ec]
                sampleOFF_time  = sampleOFF_time[0]

                testON_time     = [v[0] for v in ctrialEventCodes   if v[1]==test_on_ec]
                testON_time     = testON_time[0]

                # extract trial type
                trial_type = [int(v[1]-ec_trialtype_shift) for v in ctrialEventCodes   if (v[1]-ec_trialtype_shift)>=0 and (v[1]-ec_trialtype_shift)<=2]
                
                # Spike times
                ctrial_relative_spike_times = [v[0]-sampleON_time for i,v in enumerate(SpikeArray[:Nspike]) if (v[0]>=(sampleON_time+relative_time_range[0]) and v[0]<=min(time_stop,(sampleON_time+relative_time_range[1])))]
                ctrial_relative_spike_times_global = [v[0]-sampleON_time for i,v in enumerate(SpikeArray[:Nspike]) if (v[0]>=(sampleON_time+relative_time_range_globalraster[0]) and v[0]<=min(time_stop,(sampleON_time+relative_time_range_globalraster[1])))]
                
                if(trial_outcome[0]==0):
                    # SAME trial
                    if(trial_type[0]==1):
                        print('SAME')
                        # All spikes
                        RelativeSpikes_all_correct=RelativeSpikes_all_correct+ctrial_relative_spike_times_global # For histogram
                        ax[4].eventplot (positions = ctrial_relative_spike_times_global,lineoffset =tc_all_correct ,orientation ='horizontal', linewidths =2,linelengths =1,colors=colors_value[0] )
                        ax[4].set_xlim(relative_time_range_globalraster)
                        tc_all_correct+=1
                        # Histogram
                        RelativeSpikes_same_correct=RelativeSpikes_same_correct+ctrial_relative_spike_times 
                        ax[0].clear()
                        ax[0].set_title('Response correct SAME trials')
                        ax[0].set_ylabel('Norm. Firing Rate')
                        ax[0].add_patch( Rectangle((0.0,0.0 ),sample_width, 100,color ='k',alpha=0.25) ) # Sample ON
                        ax[0].add_patch( Rectangle((sample_width+delay_between_sample_test, 0.0),relative_time_range[1]-(sample_width+delay_between_sample_test), 100,color ='k',alpha=0.1) ) # Test ON
                        ax[0].set_xlim(relative_time_range)
                        data_ax0=ax[0].hist(RelativeSpikes_same_correct,bins=hist_bins,density=True,color=colors_value[0])
                        # same_ylim on both histograms
                        ax0_ylim=np.max(data_ax0[0])
                        ax[0].set_ylim(0,1.2*max(ax0_ylim,ax1_ylim))
                        ax[1].set_ylim(0,1.2*max(ax0_ylim,ax1_ylim))
                        
                        # Raster
                        ax[2].eventplot (positions = ctrial_relative_spike_times,lineoffset =tc_same_correct ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[0] )
                        ax[2].set_xlim(relative_time_range)
                        tc_same_correct+=1

                    if(trial_type[0]==2):
                        print('DIFF')
                        # All spikes
                        RelativeSpikes_all_correct=RelativeSpikes_all_correct+ctrial_relative_spike_times_global # For histogram
                        ax[4].eventplot (positions = ctrial_relative_spike_times_global,lineoffset =tc_all_correct ,orientation ='horizontal', linewidths =2,linelengths =1,colors=colors_value[1] )
                        ax[4].set_xlim(relative_time_range_globalraster)
                        tc_all_correct+=1
                        # Histogram
                        RelativeSpikes_diff_correct=RelativeSpikes_diff_correct+ctrial_relative_spike_times 
                        ax[1].clear()        
                        ax[1].set_title('Response correct DIFF trials')
                        ax[1].set_yticks([])
                        data_ax1=ax[1].hist(RelativeSpikes_diff_correct,bins=hist_bins,density=True,color=colors_value[1])
                        ax[1].add_patch( Rectangle((0.0,0.0 ),sample_width, 100,color ='k',alpha=0.25) ) # Sample ON
                        ax[1].add_patch( Rectangle((sample_width+delay_between_sample_test, 0.0),relative_time_range[1]-(sample_width+delay_between_sample_test), 100,color ='k',alpha=0.25) ) # Test ON
                        ax[1].set_xlim(relative_time_range)
                        
                        # same_ylim on both histograms
                        ax1_ylim=np.max(data_ax1[0])
                        ax[0].set_ylim(0,1.2*max(ax0_ylim,ax1_ylim))
                        ax[1].set_ylim(0,1.2*max(ax0_ylim,ax1_ylim))

                         # Raster
                        ax[3].eventplot (positions = ctrial_relative_spike_times,lineoffset =tc_diff_correct ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[1] )
                        ax[3].set_xlim(relative_time_range)
                        tc_diff_correct+=1

                                   #********************************************************************************************************************************   
                else:# Wrong Trial
                    # SAME trial
                    if(trial_type[0]==1):
                        print('SAME')
                        # Histogram
                        RelativeSpikes_same_wrong=RelativeSpikes_same_wrong+ctrial_relative_spike_times 


                        # Raster
                        ax[5].eventplot (positions = ctrial_relative_spike_times,lineoffset =tc_same_wrong ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[0] )
                        ax[5].set_xlim(relative_time_range)
                        tc_same_wrong+=1

                    if(trial_type[0]==2):
                        print('DIFF')
                        # Histogram
                        RelativeSpikes_diff_wrong=RelativeSpikes_diff_wrong+ctrial_relative_spike_times 


                         # Raster
                        ax[6].eventplot (positions = ctrial_relative_spike_times,lineoffset =tc_diff_wrong ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[1] )
                        ax[6].set_xlim(relative_time_range)
                        tc_diff_wrong+=1

# ******************************************************************************************************************************************* #



# PARALLEL THREADS
pdi = conditionevents.eCubePDStream(address=eCubeAddress)
pdi.start()

t1 = threading.Thread(target=pdi.stream_detectstates,args = (EventCodeArray,))
t1.start()

spikethread = threading.Thread(target=spikeevents.receive, args=(SpikeArray, openephysAddress))
spikethread.start()

# delay to start plotting the first time
time.sleep(1)

# Plotting frame by frame
animation = FuncAnimation(fig, func = animation_frame, interval =100)
plt.show()
