'''
HMD calibration client example.
This script shows how to talk to Pupil Capture or Pupil Service
and run a gaze mapper calibration.
'''
import zmq, msgpack, time,sys,csv
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

# open a sub port to listen to pupil
req.send_string('SUB_PORT')
sub_port = req.recv_string()

sub_p1 = ctx.socket(zmq.SUB)
sub_p1.connect('tcp://localhost:'+str(sub_port))
sub_p1.setsockopt_string(zmq.SUBSCRIBE, u'pupil.0')

# open a sub port to listen to pupil
req.send_string('SUB_PORT')
sub_port = req.recv_string()

sub_p2 = ctx.socket(zmq.SUB)
sub_p2.connect('tcp://localhost:'+str(sub_port))
sub_p2.setsockopt_string(zmq.SUBSCRIBE, u'pupil.1')

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

def get_pupil_data(subscriber) :
    topic = subscriber.recv_string()
    msg = subscriber.recv()
    msg = loads(msg, encoding='utf-8')
    return msg

def is_in_bound(norm_pos) :
    return norm_pos[0] >= 0 and norm_pos[0] <= 1 and norm_pos[1] >= 0 and norm_pos[1] <= 1

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

    csv_file = open("pupil_data.csv", "wb")
    print csv_file
    w = csv.writer(csv_file, delimiter=',', quotechar='"')
    print w

    for pos in ((0.5,0.5),(0,0),(0,0.5),(0,1),(0.5,1),(1,1),(1,0.5),(1,0),(0.5,0)):
        print 'subject now looks at position:',pos
        sender.send('u')
        time.sleep(2)
        s = 0
        while s < 120 :
        #for s in range(60):
            # you direct screen animation instructions here
            # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
            # You can set the pupil timebase to another clock and use that.
            t = get_pupil_timestamp()
            #topic,payload = subscriber.recv_multipart()
        #    payload = recv.receiveData()
            # in this mockup  the left and right screen marker positions are identical.
            eye0_msg = get_pupil_data(sub_p1)
            eye1_msg = get_pupil_data(sub_p2)
            if eye0_msg['confidence'] <= 0.6 or eye1_msg['confidence'] <=0.6 or not is_in_bound(eye0_msg['norm_pos']) or not is_in_bound(eye1_msg['norm_pos']):
                continue
            datum0 = {'norm_pos':eye0_msg['norm_pos'],'timestamp':t,'id':eye0_msg['id']}
            datum1 = {'norm_pos':eye1_msg['norm_pos'],'timestamp':t,'id':eye1_msg['id']}
            w.writerow([pos,datum0['norm_pos'][0],datum0['norm_pos'][1],datum1['norm_pos'][0],datum1['norm_pos'][1],t])
            csv_file.flush()

        #    print 0,datum0
        #    print 1,datum1
       #     topic = sub.recv_string()
       #     msg = sub.recv()
       #     msg = loads(msg, encoding='utf-8')
          #  if msg['confidence'] <= 0.6 :
            #    print s,msg['confidence']
           #     continue
     #       bad_value = False
            #print 'size',len(msg['base_data'])
            #msg = msg.decode('ascii')
         #   for pupil_datum in msg['base_data'] :
            #    print 'pre', pupil_datum['norm_pos']
       #         if pupil_datum['norm_pos'][0] < 0 or  pupil_datum['norm_pos'][0] > 1 or pupil_datum['norm_pos'][1] < 0 or  pupil_datum['norm_pos'][1] > 1 :
       #             bad_value = True
       #             break
            #    print 'sub' , pupil_datum['norm_pos']
       #         if pupil_datum['id'] == 0 :
      #             datum0 = {'norm_pos':pupil_datum['norm_pos'],'timestamp':pupil_datum['timestamp'],'id':0}
     #           else :
      #             datum1 = {'norm_pos':pupil_datum['norm_pos'],'timestamp':pupil_datum['timestamp'],'id':1}
    #        if bad_value :
     #           continue
        #    print datum1['norm_pos'],datum0['norm_pos']
            ref_data.append(datum0)
#            ref_data.append(datum1)
            time.sleep(1/60.) #simulate animation speed.
            s+=1
        time.sleep(1)

    # Send ref data to Pupil Capture/Service:
    # This notification can be sent once at the end or multiple times.
    # During one calibraiton all new data will be appended.
    n = {'subject':'calibration.add_ref_data','ref_data':ref_data}
    print send_recv_notification(n)
    csv_file.close()
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
#    print len(msg['base_data'])
#    print (norm_pos)
#    print (msg['confidence'])
#    print ('%s,%s'%(str(norm_pos[0]),str(norm_pos[1])))
    if msg['confidence'] > 0.6 and norm_pos[0] >= 0 and norm_pos[0] <= 1 and norm_pos[1] >= 0 and norm_pos[1] <= 1  :
        #print msg['confidence'],norm_pos
    #    print (len(msg['base_data']))
        data_sender.send('%s,%s'%(str(norm_pos[0]),str(norm_pos[1])))
