'''
HMD calibration client example.
This script shows how to talk to Pupil Capture or Pupil Service
and run a gaze mapper calibration.
'''
import zmq, msgpack, time, json, socket, msvcrt, zmq_receiver, csv
from network import TCPSocket
'''
ctx = zmq.Context()
print 'work'
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
n = {'subject':'calibration.should_start', 'hmd_video_frame_size':(1280,720), 'outlier_threshold':60}
print send_recv_notification(n)

i = raw_input('Y/N')

# Mockup logic for sample movement:
# We sample some reference positions (in normalized screen coords).
# Positions can be freely defined

csv_file = open('pupil_data.csv','wb')
writer = csv.writer(csv_file)

writer.writerow(['pos','pupil.0 x','pupil.0 y','pupil.0 confidence','pupil.1 x','pupil.1 y','pupil.1 confidence'])

ref_data = []
for pos in ((0.5,0.5),(0,0),(0,0.5),(0,1),(0.5,1),(1,1),(1,0.5),(1,0),(0.5,0)):
    print 'subject now looks at position:',pos

    notification_sender.send('u')

    time.sleep(3)

    s = 0
    if ord(msvcrt.getch()) == 32:
        avg = [0,0,0,0]
        while s < 60:
            sub_p0 = zmq_receiver.create_subscriber(ctx,req,u'pupil.0')
            sub_p1 = zmq_receiver.create_subscriber(ctx,req,u'pupil.1')

            p0_data = zmq_receiver.get_data(sub_p0)
            p1_data = zmq_receiver.get_data(sub_p1)

            # you direct screen animation instructions here
    #        data, addr = receiver.recvfrom(1024)
    #        json_data = json.loads(data)

            # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
            # You can set the pupil timebase to another clock and use that.
            t = get_pupil_timestamp()

    #        if json_data[0]['confidence'] <= 0.6 or json_data[1]['confidence'] <= 0.6:
    #            continue

            if p0_data['confidence'] <= 0.6 or p1_data['confidence'] <= 0.6:
                continue

            # in this mockup  the left and right screen marker positions are identical.
    #        datum0 = {'norm_pos':json_data[0]['norm_pos'],'timestamp':t,'id':0}
    #        datum1 = {'norm_pos':json_data[1]['norm_pos'],'timestamp':t,'id':1}

            #pnorm_pos = p0_data['norm_pos']
            #p1_data = p1_data['norm_pos']

            p0_img_coor = p0_data['ellipse']['center']
            p1_img_coor = p1_data['ellipse']['center']

            datum0 = {'norm_pos':p0_img_coor,'timestamp':t,'id':0}
            datum1 = {'norm_pos':p1_img_coor,'timestamp':t,'id':1}

    #        avg[0]+=datum0['norm_pos'][0]/60
    #        avg[1]+=datum0['norm_pos'][1]/60
    #        avg[2]+=datum1['norm_pos'][0]/60
    #        avg[3]+=datum1['norm_pos'][1]/60

    #        print datum0['norm_pos'],json_data[0]['confidence'],json_data[0]['timestamp']
    #        print datum1['norm_pos'],json_data[1]['confidence'],json_data[1]['timestamp']

            print datum0['norm_pos'],p0_data['confidence'],p0_data['timestamp']
            print datum1['norm_pos'],p1_data['confidence'],p1_data['timestamp']

            print ' '

            writer.writerow([pos,p0_data['norm_pos'][0],p0_data['norm_pos'][1],p0_data['confidence'],p1_data['norm_pos'][0],p1_data['norm_pos'][1],p1_data['confidence']])

            csv_file.flush()

            ref_data.append(datum0)
            ref_data.append(datum1)
            time.sleep(1/60) #simulate animation speed.

            s+=1

        #    n = {'subject':'calibration.add_ref_data','ref_data':ref_data}
        #    print send_recv_notification(n)

    #    print avg



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

csv_file.close()

while True :
    if msvcrt.kbhit():
        if ord(msvcrt.getch()) == 32:
            break
'''
'''
HMD calibration client example.
This script shows how to talk to Pupil Capture or Pupil Service
and run a gaze mapper calibration.
'''
ctx = zmq.Context()


#create a zmq REQ socket to talk to Pupil Service/Capture
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:50124')

notification_sender = TCPSocket('localhost',65535)

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


if raw_input('Do you want to do calibration ?').lower() == 'y' :

    # Mockup logic for sample movement:
    # We sample some reference positions (in normalized screen coords).
    # Positions can be freely defined

    ref_data = []
    for pos in ((0.5,0.5),(0,0),(0,0.5),(0,1),(0.5,1),(1,1),(1,0.5),(1,0),(.5,0)):
        print 'subject now looks at position:',pos
        notification_sender.send('u')

        if raw_input('Ready ?').lower() == 'y' :

            for s in range(60):
                # you direct screen animation instructions here
                # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
                # You can set the pupil timebase to another clock and use that.
                t = get_pupil_timestamp()

                # in this mockup  the left and right screen marker positions are identical.
                datum0 = {'norm_pos':pos,'timestamp':t,'id':0}
                datum1 = {'norm_pos':pos,'timestamp':t,'id':1}
                ref_data.append(datum0)
                ref_data.append(datum1)
                print s
                time.sleep(1/60.) #simulate animation speed.


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
