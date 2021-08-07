import time
import pyeCubeStream

# Reading raw bit states from the front digital panel from ServerNode-Control streaming
# Excecution time can be reduced by 60ms if we replace time.perf_counter with time.monotonic
class eCubePDStream:
	def __init__(self, address='127.0.0.1'):

		# connect to the interface
		self.stream = pyeCubeStream.eCubeStream('DigitalPanel', address)
		self.lateststate = 0
		self.prevstate = 0
		self.trialcounter = dict()
		self.previous_digitalsamps = 0
		#self.EventCodeArray =[]


	def start(self):
		self.stream.start()


	def stop(self):
		self.stream.stop()

	def stream_detectstates(self,EventCodeArray):
		while True:
		    eventCode =0	
		    #print('Entered the loop')
		    (ts, digitalsamps) = self.stream.get()
		    event_time=time.perf_counter()
		    #print('event_time')
		    #print(event_time)
		    for current_digitalsamps in digitalsamps:
        		if self.previous_digitalsamps != current_digitalsamps:
        			#print(current_digitalsamps)
        			self.previous_digitalsamps=current_digitalsamps
        			mlStrobe = (current_digitalsamps>>2) & 1
        			if(mlStrobe == 0):
        				#print(current_digitalsamps)
        				event_time=time.perf_counter()
        				eventCode = (current_digitalsamps>>40) & 0xFFFFFF
        				EventCodeArray.append([event_time,eventCode[0]])
        				#print(eventCode)
        				#return EventCodeArray