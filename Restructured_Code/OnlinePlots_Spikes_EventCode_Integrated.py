""""
Excecution time can be reduced by 60ms if we replace time.perf_counter with time.monotonic
"""
#import eventstream
import numpy as np
import time
import threading
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

import conditionevents
import spikeevents

# Network Address
eCubeAddress = '192.168.137.1' # IP Address for eCube or ServerNode, for directly connecting and reading DigitalPanel via the eCube API
openephysAddress = '10.120.10.55' # OpenEphys ~0.4.2-0.4.3 EventBroadcaster module address after spike sorting

global ltime, utime, nbin
AllRelativeSpikes   =   [[],[],[]]
EventCodeArray      =   []
SpikeArray          =   []
trial_count         =   [0]
bins                =   np.arange(0, 3, 0.1)
ax                  =   []

# Event Codes directly used
start_ec                = 1101 
stop_ec                 = 1104
same_ec                 = 9001
diff_ec                 = 9002
sample_on_ec            = 400
sample_off_ec           = 401
test_on_ec              = 402

#  Footer Shifts  
ec_shift_tt             = 9000  # 9000+  1 for same , 9000 +2 for different  
ec_trial_error_shift    = 8500  # 8500 + 0 correct, 8500 + 6 wrong 



# Plotting

ltime   =   -0.5
utime   =   3 
nbin    =   20

colors_value = ['C{}'.format(i) for i in range(6)] # Colours used


# Predefining the Figure layout
widths = [8,8, 8]
heightratio = [1, 4]

fig = plt.figure(constrained_layout=True,figsize=(16,8))
title_names= ['Same Condition','Diff Condition','All']
ylabel_names = ['Normalized Firing Rate','Trials 1-100']


spec = gridspec.GridSpec(ncols=3, nrows=2, figure=fig,width_ratios=widths, height_ratios=heightratio)
f_ax1 = fig.add_subplot(spec[0, 0])
f_ax2 = fig.add_subplot(spec[0, 1])
f_ax3 = fig.add_subplot(spec[0, 2])
f_ax4 = fig.add_subplot(spec[1, 0])
f_ax5 = fig.add_subplot(spec[1, 1])
f_ax6 = fig.add_subplot(spec[1, 2])

f_ax4.set_xlabel('Relative Time')
f_ax5.set_xlabel('Relative Time')
f_ax6.set_xlabel('Relative Time')

f_ax1.set_ylabel(ylabel_names[0])
f_ax4.set_ylabel(ylabel_names[1])


f_ax1.set_xlim(ltime,utime)
f_ax2.set_xlim(ltime,utime)
f_ax3.set_xlim(ltime,utime)
f_ax4.set_xlim(ltime,utime)
f_ax5.set_xlim(ltime,utime)
f_ax6.set_xlim(ltime,utime)


f_ax4.set_ylim(0,100)
f_ax5.set_ylim(0,100)
f_ax6.set_ylim(0,100)


ax =[]
ax.append(f_ax1)
ax.append(f_ax2)
ax.append(f_ax3)
ax.append(f_ax4)
ax.append(f_ax5)
ax.append(f_ax6)

for i in range(3):
    ax[i].set_title(title_names[i])


# Initilizing the plot by setting axis limits
def init():
    """
    print(ax)
    return ax

    for i in range(2):
        ax[i,0].set_ylabel(ylabel_names[0]) 
        
        ax[i,0].set_ylim(1,100)
        for j in range(3):
            ax[0,j].set_title(title_names[j])
            ax[i,j].set_xlim(0,3)
            ax[1,j].set_xlabel('Relative Time')
            ax[1,j].set_ylim(1,100) 
            ax[0,j].set_ylim(0,1)
    """
    #return ax

def animation_frame(FrameNumber,trial_count,ax):
    #print('Trial Count = ',trial_count)
    #print('Frame Number = ',FrameNumber)
    global AllRelativeSpikes
    # Predefined Event Codes

    hist_bins =np.linspace(ltime,utime,nbin+1)

 
    # Calculate N to avoid considering synchronous updation. 
    # This current updation happens only till the first N value. Remaining will be considered during the next cycle. 
    N=len(EventCodeArray)
    Nspike=len(SpikeArray)
    
    # Finding all the trial start-event codes
    start_index = [i for i,v in enumerate(EventCodeArray[:N]) if v[1]==start_ec]
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
        
        # Discarding all the event codes between start and strop event codes
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
   
            
pdi = conditionevents.eCubePDStream(address=eCubeAddress)
pdi.start()

t1 = threading.Thread(target=pdi.stream_detectstates,args = (EventCodeArray,))
t1.start()


spikethread = threading.Thread(target=spikeevents.receive, args=(SpikeArray, openephysAddress))
spikethread.start()

#t2 = threading.Thread(target=do_spikes)
#t2.start()


# delay to start plotting the first time
time.sleep(1)

# Plotting frame by frame
animation = FuncAnimation(fig, func = animation_frame, fargs = (trial_count,ax),init_func=init,interval =100)
plt.show()
