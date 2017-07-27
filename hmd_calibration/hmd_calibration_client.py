'''
HMD calibration client example.
This script shows how to talk to Pupil Capture or Pupil Service
and run a gaze mapper calibration.
'''
import zmq, msgpack, time, json, socket
from network import TCPSocket

ctx = zmq.Context()

UDP_IP = "127.0.0.1"
UDP_PORT = 6500
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver.bind((UDP_IP, UDP_PORT))

notification_sender = TCPSocket('localhost',65535)

#create a zmq REQ socket to talk to Pupil Service/Capture
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:50124')

#convenience functions
def send_recv_notification(n):
    # REQ REP requirese lock step communication with multipart msg (topic,msgpack_encoded dict)
    req.send_multipart(('notify.%s'%n['subject'], msgpack.dumps(n)))
    return req.recv()

def get_pupil_timestamp():
    req.send('t') #see Pupil Remote Plugin for details
    return float(req.recv())

# set start eye windows
n = {'subject':'eye_process.should_start.0','eye_id':0, 'args':{}}
print send_recv_notification(n)
n = {'subject':'eye_process.should_start.1','eye_id':1, 'args':{}}
print send_recv_notification(n)
time.sleep(2)


# set calibration method to hmd calibration
n = {'subject':'start_plugin','name':'HMD_Calibration', 'args':{}}
print send_recv_notification(n)

# start caliration routine with params. This will make pupil start sampeling pupil data.
n = {'subject':'calibration.should_start', 'hmd_video_frame_size':(1280,720), 'outlier_threshold':35}
print send_recv_notification(n)


# Mockup logic for sample movement:
# We sample some reference positions (in normalized screen coords).
# Positions can be freely defined

ref_data = []
for pos in ((0.5,0.5),(0,0),(0,0.5),(0,1),(0.5,1),(1,1),(1,0.5),(1,0),(0.5,0)):
    print 'subject now looks at position:',pos

    notification_sender.send('u')

    time.sleep(2)

    s = 0

    while s < 60:

        # you direct screen animation instructions here
        data, addr = receiver.recvfrom(1024)
        json_data = json.loads(data)

        # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
        # You can set the pupil timebase to another clock and use that.
        t = get_pupil_timestamp()

        if json_data[0]['confidence'] <= 0.6 or json_data[1]['confidence'] <= 0.6:
            continue

        # in this mockup  the left and right screen marker positions are identical.
        datum0 = {'norm_pos':json_data[0]['norm_pos'],'timestamp':t,'id':0}
        datum1 = {'norm_pos':json_data[1]['norm_pos'],'timestamp':t,'id':1}
        ref_data.append(datum0)
        ref_data.append(datum1)
        time.sleep(1/60) #simulate animation speed.

        s+=1


# Send ref data to Pupil Capture/Service:
# This notification can be sent once at the end or multiple times.
# During one calibraiton all new data will be appended.
n = {'subject':'calibration.add_ref_data','ref_data':ref_data}
print send_recv_notification(n)

# stop calibration
# Pupil will correlate pupil and ref data based on timestamps,
# compute the gaze mapping params, and start a new gaze mapper.
n = {'subject':'calibration.should_stop'}
print send_recv_notification(n)

time.sleep(2)
n = {'subject':'service_process.should_stop'}
print send_recv_notification(n)

notification_sender.send('e')
