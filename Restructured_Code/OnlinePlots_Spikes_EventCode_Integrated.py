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
AllRelativeSpikes   =   [[],[],[]]
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
ec_shift_tt             = 9000  # 9000+  1 for same , 9000 +2 for different  
ec_trial_error_shift    = eventcode.Dict['trl.outcomeShift']   # 8500 + 0 correct, 8500 + 6 wrong 



# Plotting
ltime   =   -0.5
utime   =   3 
nbin    =   20
hist_bins =np.linspace(ltime,utime,nbin+1)

colors_value = ['C{}'.format(i) for i in range(6)] # Colours used

ax= lib.figure_layout_creation(0)
###############################################
def animation_frame(ax):
    global AllRelativeSpikes

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
