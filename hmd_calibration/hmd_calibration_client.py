'''
HMD calibration client example.
This script shows how to talk to Pupil Capture or Pupil Service
and run a gaze mapper calibration.
'''
import zmq, msgpack, time,sys
from network import TCPSocket
from zmq_tools import Msg_Receiver
from msgpack import loads
from sender import UDPSender

#from receiver import Receiver

ctx = zmq.Context()

port = 50124

if len(sys.argv) >= 2 :
    port = sys.argv[1]

print 'Im working'

#create a zmq REQ socket to talk to Pupil Service/Capture
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:'+str(port))
print 'Im working'

# open a sub port to listen to pupil
req.send_string('SUB_PORT')
sub_port = req.recv_string()

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:'+str(sub_port))
sub.setsockopt_string(zmq.SUBSCRIBE, u'gaze')

#create a tcp sender
sender = TCPSocket('localhost',65535)
data_sender = UDPSender('127.0.0.1',5500)
print 'Im working'

#req.set(zmq.SUBSCRIBE,'gaze.')

#recv = Receiver()
print 'Im working'

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
n = {'subject':'calibration.should_start', 'hmd_video_frame_size':(1000,1000), 'outlier_threshold':35}
print send_recv_notification(n)

should_start = raw_input('Are you ready for doing calibration ? (Y/N) : ')

# Mockup logic for sample movement:
# We sample some reference positions (in normalized screen coords).
# Positions can be freely defined
if should_start.lower() == 'y' :
    ref_data = []
    for pos in ((0.5,0.5),(0,0),(0,0.5),(0,1),(0.5,1),(1,1),(1,0.5),(1,0),(.5,0)):
        print 'subject now looks at position:',pos
        sender.send('u')
        time.sleep(1)
        for s in range(60):
            # you direct screen animation instructions here

            # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
            # You can set the pupil timebase to another clock and use that.
            t = get_pupil_timestamp()

            #topic,payload = subscriber.recv_multipart()
        #    payload = recv.receiveData()

            # in this mockup  the left and right screen marker positions are identical.
            datum0 = {'norm_pos':pos,'timestamp':t,'id':0}
            datum1 = {'norm_pos':pos,'timestamp':t,'id':1}
            topic = sub.recv_string()
            msg = sub.recv()
            msg = loads(msg, encoding='utf-8')
            #msg = msg.decode('ascii')
            for pupil_datum in msg['base_data'] :
                if pupil_datum['id'] == 0 :
                   datum0 = {'norm_pos':pupil_datum['norm_pos'],'timestamp':pupil_datum['timestamp'],'id':0}
                else :
                   datum1 = {'norm_pos':pupil_datum['norm_pos'],'timestamp':pupil_datum['timestamp'],'id':1}
            ref_data.append(datum0)
            ref_data.append(datum1)
            time.sleep(1/60.) #simulate animation speed.
        time.sleep(1)

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
sender.send('e')

while True :
    topic = sub.recv_string()
    msg = sub.recv()
    msg = loads(msg, encoding='utf-8')
    norm_pos = msg['norm_pos']
    data_sender.send('%s,%s'%(str(norm_pos[0]),str(norm_pos[1])))
