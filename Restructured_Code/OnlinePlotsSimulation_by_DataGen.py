import numpy as np
import time
import threading
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

EventCodeArray  =   []
SpikeArray      =   []
trial_count     =   0


def do_eventcode():
    while(True):
        # Start of the trial
        event_code   = 10 
        current_time = time.perf_counter()
        EventCodeArray.append([current_time,event_code]) 
        
        # trial type
        event_code  = random.randrange(1,3,1) # Randomly assigning 1 or 2 : Same or Diff
        print(f'Event Code = {event_code}') # Trial Type
        current_time = time.perf_counter()
        EventCodeArray.append([current_time,event_code])   
        
        # Trial Duration
        seconds     = round(random.uniform(1, 3),2)
        time.sleep(seconds)
        
        # End of trial      
        event_code   = 20
        current_time= time.perf_counter()
        EventCodeArray.append([current_time,event_code])

def do_spikes():
    while(True):
        # randomly generate spike duration
        seconds = round(random.random(),2)

        # sleep for the duration
        time.sleep(seconds)

        # sending current-times
        current_time= time.perf_counter()
        SpikeArray.append([current_time,1])
        print(f'Spike {1}')

# Plotting 
fig, ax = plt.subplots(1,2)
xdata,ydata=[],[]

# Initilizing the plot by setting axis limits
def init():
    for i in range(2):
        ax[i].set_xlim(0,3)
        ax[i].set_ylim(1,100)
        ax[i].set_xlabel('Relative Time') 
    
    ax[0].set_ylabel('Trials 1-100') 
    ax[0].set_title('Same Trial')
    ax[1].set_title('Diff Trial')
    return ax

def animation_frame(FrameNumber):
    print('Frame Number = ',FrameNumber)
    # Predefined Event Codes
    start_ec    = 10  
    stop_ec     = 20
    same_ec     = 1
    diff_ec     = 2

    # Calculate N to avoid considering synchronous updation
    N=len(EventCodeArray)
    Nspike=len(SpikeArray)

    # Finding all the trial start-event codes
    start_index = [i for i,v in enumerate(EventCodeArray[:N]) if v[1]==start_ec]
    if(bool(start_index)):
        time_start = EventCodeArray[start_index[0]][0]
        # Finding all trail stop events
        stop_index = [i for i,v in enumerate(EventCodeArray[:N]) if (v[1]==stop_ec and float(v[0])>(time_start) )]
    
    
    if(bool(start_index) and bool(stop_index)): # Execute only if trial start and stop is recorded
        time_stop = EventCodeArray[stop_index[0]][0]

        # Finding the trial type
        trial_type = [v[1] for i,v in enumerate(EventCodeArray[:N]) if  float(v[0])>(time_start) and float(v[0])<=time_stop and (v[1]==same_ec or v[1] ==diff_ec) ]

        # Discarding all the event codes between start and strop event codes
        for i in range(stop_index[0],start_index[0]-1,-1):
            EventCodeArray.pop(i)

        # Finding the relative spike times
        Relative_spike_times = [v[0]-time_start for i,v in enumerate(SpikeArray[:Nspike]) if (v[0]>=time_start and v[0]<=time_stop)]
        print(f'Start = {time_start}, Stop = {time_stop}')
        print(Relative_spike_times)

        print('Trial type =',trial_type)
        ax[trial_type[0]-1].eventplot (positions = Relative_spike_times,lineoffset =FrameNumber ,orientation ='horizontal', linewidths =2,linelengths =1 )
    #return ax



t1 = threading.Thread(target=do_eventcode)
t1.start()

t2 = threading.Thread(target=do_spikes)
t2.start()


# delay to start plotting the first time
time.sleep(1)

# Plotting frame by frame
animation = FuncAnimation(fig, func = animation_frame, frames = np.arange(0,500,1),init_func=init,interval =1000)
plt.show()
#t3 = threading.Thread(target=animation_frame)
#t3.start()

#t1.join()
#t2.join()