import pandas as pd
import numpy as np
import queue
from collections import OrderedDict

# Example data structure to keep conditions

class EventStream:

    def __init__(self, condnames=None, numconds=None, cellnames=None, numcells=None, maxspikes=5000, maxconds=50, peritime=(-0.5, 1), cond_debounce=0.005, debug=False):
        self.spikedata = pd.DataFrame(columns=['Time', 'HWTime', 'CellType'])
        #self.conddata = pd.DataFrame(columns=['Time', 'CondType', 'TrialCount']) 
        self.conddata = pd.DataFrame(columns=['TrialStartTime', 'TrialEndTime','CondType', 'TrialNumber','TrialCount',])
        self.archivedata = pd.DataFrame(columns=['Time', 'DeltaTime', 'TrialNumber', 'CondType', 'CellType','TrialCount'])
        self.trialData  = pd.DataFrame(columns= ['TrialID','TrialStartTime','TrialEndTime','CondType','EventCodes','Cell','SpikeTime'])
        self.eventCodeData = pd.DataFrame(columns=['EventTime','EventCode'])
        if condnames is not None:
            if numconds is not None:
                raise ValueError('condnames and numconds cannot be simultaneously defined')
            else:
                self.condnames = condnames
                self.numconds = len(self.condnames)
        else:
            if numconds is not None:
                self.numconds = numconds
                self.condseen = [] # keep track of unique conditions seen so far
            else:
                raise ValueError('either condnames (map) or numconds (int) must be defined')

        if cellnames is not None:
            if numcells is not None:
                raise ValueError('cellnames and numcells cannot be simultaneously defined')
            else:
                self.cellnames = cellnames
                self.numcells = len(self.cellnames)
        else:
            if numcells is not None:
                self.numcells = numcells
                self.cellseen = [] # keep track of unique cell types seen so far
            else:
                raise ValueError('either cellnames (map) or numcells (int) must be defined')

        self.maxspikes = maxspikes
        self.maxconds = maxconds
        self.peritime = peritime
        self.cond_debounce = cond_debounce
        self.debug = debug

    def get_plot_meta(self):
        # used by the plotting thread to get the cell and condition names

        if self.condnames is not None:
            condmapout = OrderedDict(sorted(self.condnames.items(), key=lambda t: t[0])) # note sure why this should be sorted and OrderedDict
        else:
            condmapout = self.condseen.copy()
            if len(condmapout) < self.numconds:
                condmapout.extend(['Unknown']*(self.numconds - len(condmapout)))

        if self.cellnames is not None:
            cellnameout = OrderedDict(sorted(self.cellnames.items(), key=lambda t: t[0]))
        else:
            cellnameout = self.condseen.copy()
            if len(cellnameout) < self.numcells:
                cellnameout.extend(['Unknown']*(self.numcells - len(cellnameout)))

        return (condmapout, cellnameout)

    #def add_conditions(self, newtime, newcond, curr_trialno, prevcond=None):
    def add_conditions(self, starttime, endtime, newcond, trialNumber,curr_trialno, prevcond=None):
        if prevcond is None:
            return self.add_condition_single(starttime, endtime,newcond,trialNumber, curr_trialno)
        #else:
        #    self.add_condition_single(newtime, -1 * prevcond)
        #    return self.add_condition_single(newtime, newcond, curr_trialno)

    def add_condition_single(self, starttime,endtime, newcond, trialNumber,curr_trialno):
        # add a new digital panel condition event to the dataframe

     
        if self.conddata.shape[0] > 0:
            prev_valid_cond = self.conddata.iloc[-1][2]
        else:
            prev_valid_cond = None

        # validate condition
        if self.condnames is not None:
            if newcond not in self.condnames:
                print("Warning: {} not found in allowed list of conditions - ignored".format(newcond))
                return prev_valid_cond
        else:
            if len(self.condseen) < self.numconds:
                self.condseen.append(newcond)
            else:
                if newcond not in self.condseen:
                    print("Warning: new condition {} exceeds allowed number of conditions - ignored".format(newcond))
                    return prev_valid_cond

        if self.conddata.shape[0] > 0:
            if starttime - self.conddata.iloc[-1][0] <= self.cond_debounce:
                return prev_valid_cond

        if self.conddata.shape[0] < self.maxconds:
            condrow = {'TrialStartTime': starttime, 'TrialEndTime' : endtime,'CondType': newcond,'TrialNumber' : trialNumber, 'TrialCount': curr_trialno}
            self.conddata = self.conddata.append(condrow, ignore_index=True)
        else:
            self.conddata = self.conddata.shift(-1)
            self.conddata.iloc[-1] = [starttime, endtime, newcond, trialNumber,curr_trialno]

        return newcond

    def addEventCode(self,eventTime, eventCode):
        eventCodeRow = {'EventTime': eventTime, 'EventCode': eventCode}
        self.eventCodeData = self.eventCodeData.append(eventCodeRow,ignore_index=True)

        return eventCode # not sure if we need to return this value

    def add_spike(self, newtime, hwtime, celltype):
        # add a spike event to the dataframe

        spikerow = {'Time': newtime, 'HWTime': hwtime, 'CellType': celltype}

        # validate spike
        if self.cellnames is not None:
            if celltype not in self.cellnames:
                print("Warning: {} not found in allowed list of CellTypes - ignored".format(celltype))
                return None
        else:
            if len(self.cellseen) < self.numcells:
                self.cellseen.append(celltype)
            else:
                if celltype not in self.cellseen:
                    print("Warning: new CellType {} exceeds allowed number of CellTypes - ignored".format(celltype))
                    return None

        if self.spikedata.shape[0] < self.maxspikes:
            self.spikedata = self.spikedata.append(spikerow, ignore_index=True)
        else:
            self.spikedata = self.spikedata.shift(-1)
            self.spikedata.iloc[-1] = [newtime, hwtime, celltype]

        return celltype
    
    def add_trialData(self,trialStartTime, trialEndTime,trialNum, trialType):
        # selecting the spike data and eventcode data corresponding to the trial number from spikedata , conddata dataframes
       
        selectedSpikeData = pd.DataFrame(columns=['Time', 'HWTime', 'CellType'])
        selectedSpikeData = self.spikedata[ (self.spikedata['Time'] > trialStartTime + self.peritime[0])& (self.spikedata['Time'] <= trialEndTime + self.peritime[1]) ] # contains all cells
        selectedEventCode = self.eventCodeData[(self.eventCodeData['EventTime'] > trialStartTime)  &  (self.eventCodeData['EventTime']  <= trialEndTime)  ]
        ordSelectedSpikeData = selectedSpikeData.sort_values(by = ['CellType'] ) # sorting the spike data by cell ids

        trialEventCode =[]
        for row in selectedEventCode.itertuples(index = False):
            trialEventCode.append(row[1])
        
        # this will gather spike times from all neurons whose spike timing fall in the specified range 
        
        prevCell = 0
        spikeTimeCell = []
        for row in ordSelectedSpikeData.itertuples(index=False):
            if(prevCell != row[2]):
                lastCellSpikeTime = spikeTimeCell
                if(len(lastCellSpikeTime)>0):
                    trialDataRecord = {'Trial ID':trialNum,'TrialStartTime':trialStartTime ,'TrialEndTime': trialEndTime,'CondType':trialType,'EventCodes':trialEventCode,'Cell' : prevCell,'SpikeTime':lastCellSpikeTime}
                    self.trialData = self.trialData.append(trialDataRecord,ignore_index=True)
                spikeTimeCell = []
                prevCell = row[2]
                spikeTimeCell.append(row[0])
                if(all(row == ordSelectedSpikeData.iloc[-1])):
                    trialDataRecord = {'Trial ID':trialNum,'TrialStartTime':trialStartTime ,'TrialEndTime': trialEndTime,'CondType':trialType,'EventCodes':trialEventCode,'Cell' : row[2],'SpikeTime':spikeTimeCell}
                    self.trialData = self.trialData.append(trialDataRecord,ignore_index=True)
            else:
                spikeTimeCell.append(row[0])
                if all((row == ordSelectedSpikeData.iloc[-1])):
                    trialDataRecord = {'Trial ID':trialNum,'TrialStartTime':trialStartTime ,'TrialEndTime': trialEndTime,'CondType':trialType,'EventCodes':trialEventCode,'Cell' : row[2],'SpikeTime':spikeTimeCell}
                    self.trialData = self.trialData.append(trialDataRecord,ignore_index=True)        

        return trialNum # not sure if we need to return this value

    def archive_segment(self, event_time):
        # archive dataframes in the past

        archiveconds = self.conddata[self.conddata['TrialEndTime'] < (event_time - self.peritime[1])]
        archivespikes = self.spikedata[self.spikedata['Time'] <= event_time]

        self.conddata = self.conddata[self.conddata['TrialEndTime'] >= (event_time - self.peritime[1])]
        self.spikedata = self.spikedata[self.spikedata['Time'] >= (event_time + self.peritime[0] - self.peritime[1])]

        spikes_archived = 0
        # update the archived dataframe
        for row in archiveconds.itertuples(index=False):
            trialraster = get_raster_spikes(archivespikes, row[0], row[2], row[3], self.peritime)
            if len(trialraster) > 0:
                self.archivedata = self.archivedata.append(trialraster, ignore_index=True)  # integrates the condition and spike data for archived conditions and keep it in archivedata
                spikes_archived += len(trialraster) 

        return spikes_archived

    def get_segment(self, cond, cell):
        # Used by the plotting function to pull all historical rasters
        new_rasters = pd.DataFrame(columns=['Time', 'DeltaTime', 'TrialCount', 'CondType', 'CellType'])

        cond_selected = self.conddata[self.conddata['CondType'] == float(cond)]
        spike_selected = self.spikedata[self.spikedata['CellType'] == float(cell)]

        for row in cond_selected.itertuples(index=False):
            trialraster = get_raster_spikes(spike_selected, row[0], row[2], row[4], self.peritime)
            if len(trialraster) > 0:
                new_rasters = new_rasters.append(trialraster, ignore_index=True, sort = False)

        old_rasters = self.archivedata[(self.archivedata['CondType'] == float(cond)) & (self.archivedata['CellType'] == float(cell))]

        all_rasters = old_rasters.append(new_rasters, ignore_index=True, sort = False)
        return all_rasters

 
    def update_eventstream(self, q, drawq):
        # When new spikes occur, update relevant archived and current data structures

        curr_cond = None
        last_condtime = None
        last_spiketime = None

        while True:
            newevent = q.get(block=True)
            if newevent[0] ==1:
                curr_eventCode = self.addEventCode(newevent[1],newevent[2])
                
            
            if newevent[0] == 2: # spike: (2, time.monotonic(), timestamp, cellcode)
                curr_cell = self.add_spike(newevent[1], newevent[2], newevent[3])
                last_spiketime = newevent[1]
                

            elif newevent[0] == 3: # condition: (3,trialStartTime,trialEndTime,decTrialNum,decTrialType,decCondition,decOutCome, trialTypeCounter)
                trialStartTime = newevent[1]
                trialEndTime = newevent[2]
                trialNumber = int(newevent[3]) 
                trialType = int(newevent[4])
                trialTypeCounter = int(newevent[5])
                curr_cond = self.add_conditions(trialStartTime, trialEndTime, trialType,trialNumber,curr_trialno=trialTypeCounter)
                last_condStarttime = newevent[1]
                last_condEndtime = newevent[2]
                


                #if curr_cond is not None and curr_cell is not None and last_spiketime <= (last_condEndtime + self.peritime[1]):
                if curr_cond is not None:
                    # a function which takes, spike data and conddata as input and forms trial wise structure (based on times)
                    #curr_trialData = self.add_trialData(trialStartTime, trialEndTime,trialNumber,trialType)
                    if self.debug is True:
                        print("Cond {}: {}".format(curr_cond, self.get_segment(curr_cond, curr_cell)))

                    spikes_archived = self.archive_segment(last_spiketime)
                    # once a trial is completed, take out the list of cells from spike data whose spike timings fall between the trial start and trial end time and update drawq with the current condition and all the relevant neuron ids
                    selectedCellData = self.spikedata[ (self.spikedata['Time'] > last_condStarttime + self.peritime[0]) & (self.spikedata['Time'] <= last_condEndtime + self.peritime[1]) ]
                    for row in selectedCellData.itertuples(index=False):
                        
                        drawq.put((int(curr_cond), int(row[2])))                        

def get_raster_spikes(spikedata, cond_t, condtype, cond_trialno, timebounds):
    # Given input time cond_t, search through spikedata pandas frame for matching rasters within time bounds
    
    outraster = pd.DataFrame(columns=['Time', 'DeltaTime', 'TrialCount', 'CondType', 'CellType'])
   
    deltaspiketimes = spikedata['Time'] - cond_t
    #print('delta spike time :', deltaspiketimes)
    validtimes = deltaspiketimes.between(timebounds[0], timebounds[1])
    outraster['Time'] = spikedata[validtimes]['Time']
    outraster['CellType'] = spikedata[validtimes]['CellType']
    outraster['DeltaTime'] = deltaspiketimes[validtimes]
    outraster['CondType'] = condtype
    outraster['TrialCount'] = cond_trialno
    
    return outraster # return deltaspiketimes[deltaspiketimes[validtimes].abs().idxmin()] for closest per condition
