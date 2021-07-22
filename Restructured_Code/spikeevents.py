import zmq
#import queue
import time

# Receives spikes sorted by OpenEphys SpikeSorter (and broadcasted via EventBroadcaster)

def receive(SpikeArray, hostname='127.0.0.1', port=5557):

	with zmq.Context() as ctx:
		with ctx.socket(zmq.SUB) as sock:
			sock.connect('tcp://%s:%d' % (hostname, port))

			sock.subscribe(b'')

			while True:
				parts = sock.recv_multipart()
				eventcode = int.from_bytes(parts[0], 'little', signed=False)
				if eventcode == 2:
					timestamp = int.from_bytes(parts[1][0:8], 'little', signed=False)/2.5e13
					sortedID = int.from_bytes(parts[2][16:18], 'little', signed=False)
					print('Spike = ',sortedID)
					if(sortedID==0):
						SpikeArray.append([time.perf_counter(),sortedID, timestamp])
						print('Spike = ',sortedID)
