import csv , zmq , msgpack

ctx = zmq.Context()
port = 50124
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:'+str(port))

req.send_string('SUB_PORT')
sub_port = req.recv_string()

sub_p1 = ctx.socket(zmq.SUB)
sub_p1.connect('tcp://localhost:'+str(sub_port))
sub_p1.setsockopt_string(zmq.SUBSCRIBE, u'pupil.0')

req.send_string('SUB_PORT')
sub_port = req.recv_string()

sub_p2 = ctx.socket(zmq.SUB)
sub_p2.connect('tcp://localhost:'+str(sub_port))
sub_p2.setsockopt_string(zmq.SUBSCRIBE, u'pupil.1')

def get_pupil_data(subscriber) :
    topic = subscriber.recv_string()
    msg = subscriber.recv()
    msg = loads(msg, encoding='utf-8')
    return msg

with open('pupil_data.csv', 'wb') as csvfile:
    
    while n < 120 :

        e1d = get_pupil_data(sub_p1)
        e2d = get_pupil_data(sub_p2)

        csvfile.writerow(e1d['norm_pos'][0],e1d['norm_pos'][1],e2d['norm_pos'][0],e2d['norm_pos'][1],e1d['confidence'],e2d['confidence'])
