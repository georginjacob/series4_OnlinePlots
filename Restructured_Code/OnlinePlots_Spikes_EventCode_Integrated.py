import numpy as np
import time
import threading
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

import conditionevents
import spikeevents
import eventcode

# Network Address
eCubeAddress = '192.168.137.1' # IP Address for eCube or ServerNode, for directly connecting and reading DigitalPanel via the eCube API
openephysAddress = '10.120.10.55' # OpenEphys ~0.4.2-0.4.3 EventBroadcaster module address after spike sorting

global ltime, utime, nbin
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
errorcode_wrong         = list(range(1,9))



# Plotting
ltime   =   -0.5
utime   =   3 
nbin    =   20
hist_bins =np.linspace(ltime,utime,nbin+1)

colors_value = ['C{}'.format(i) for i in range(6)] # Colours used

ax= lib.figure_layout_creation(0) # Initializing the Layout
###############################################
def animation_frame(ax):
    global RelativeSpikes_all_correct, RelativeSpikes_same_correct, RelativeSpikes_diff_correct

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
            trial_outcome = [(v[1]-ec_trial_error_shift) for v in (ctrialEventCodes) if (v[1]>=ec_trial_error_shift and v[1]<=ec_trial_error_shift+max(errorcode_wrong) )]
            
            # Correct trial
            if(trial_outcome==0):
                # sample ON, OFF, test ON
                sampleON_time   = [v[0] for v in ctrialEventCodes   if v[1]==sample_on_ec]
                sampleOFF_time  = [v[0] for v in ctrialEventCodes   if v[1]==sample_off_ec]
                testON_time     = [v[0] for v in ctrialEventCodes   if v[1]==test_on_ec]
                
                # extract trial type
                trial_type = [(v[1]-ec_trialtype_shift) for v in ctrialEventCodes   if (v[1]-ec_trialtype_shift)>=0 and (v[1]-ec_trialtype_shift)<=2]
                
                # Spike times
                ctrial_relative_spike_times = [v[0]-sampleON_time for i,v in enumerate(SpikeArray[:Nspike]) if (v[0]>=time_start and v[0]<=time_stop)]
                
                # All spikes
                RelativeSpikes_all_correct=RelativeSpikes_all_correct+ctrial_relative_spike_times # For histogram
                ax[5].eventplot (positions = ctrial_relative_spike_times,lineoffset =len(RelativeSpikes_all_correct) ,orientation ='horizontal', linewidths =2,linelengths =1,colors=colors_value[2] )
   
                # SAME trial
                if(trial_type==1):
                    # Histogram
                    RelativeSpikes_same_correct=RelativeSpikes_same_correct+ctrial_relative_spike_times 
                    ax[0].clear()        
                    ax[0].set_ylabel('Normalized Firing Rate')
                    ax[0].set_title('SAME Trial')
                    ax[0].hist(RelativeSpikes_same_correct,bins=hist_bins,density=True,color=colors_value[0])

                    # Raster
                    ax[3].eventplot (positions = ctrial_relative_spike_times,lineoffset =len(RelativeSpikes_same_correct) ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[0] )


                if(trial_type==2):
                    # Histogram
                    RelativeSpikes_diff_correct=RelativeSpikes_diff_correct+ctrial_relative_spike_times 
                    ax[1].clear()        
                    ax[1].set_title('DIFF Trial')
                    ax[1].hist(RelativeSpikes_diff_correct,bins=hist_bins,density=True,color=colors_value[1])

                     # Raster
                    ax[4].eventplot (positions = ctrial_relative_spike_times,lineoffset =len(RelativeSpikes_diff_correct) ,orientation ='horizontal', linewidths =2,linelengths =1, colors=colors_value[1] )
            # Wrong Trial


###############################################
pdi = conditionevents.eCubePDStream(address=eCubeAddress)
pdi.start()

t1 = threading.Thread(target=pdi.stream_detectstates,args = (EventCodeArray,))
t1.start()

spikethread = threading.Thread(target=spikeevents.receive, args=(SpikeArray, openephysAddress))
spikethread.start()

# delay to start plotting the first time
time.sleep(1)

# Plotting frame by frame
animation = FuncAnimation(fig, func = animation_frame, fargs = (trial_count,ax),interval =100)
plt.show()
