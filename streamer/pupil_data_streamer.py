import zmq_receiver,zmq,json,msvcrt
from sender import UDPSender

streamer = UDPSender('127.0.0.1',6500)

ctx = zmq.Context()

req = zmq_receiver.init_requester(ctx,50124)

while True :

    g_sub = zmq_receiver.create_subscriber(ctx,req,u'gaze')
    p0_sub = zmq_receiver.create_subscriber(ctx,req,u'pupil.0')
    p1_sub = zmq_receiver.create_subscriber(ctx,req,u'pupil.1')

    g_data = zmq_receiver.get_data(g_sub)
    p0_data = zmq_receiver.get_data(p0_sub)
    p1_data = zmq_receiver.get_data(p1_sub)
    streamer.send(json.dumps([{'id':p0_data['id'],'norm_pos':p0_data['norm_pos'],'confidence':p0_data['confidence'],'timestamp':p0_data['timestamp']},{'id':p1_data['id'],'norm_pos':p1_data['norm_pos'],'confidence':p1_data['confidence'],'timestamp':p1_data['timestamp']}]))
    if p0_data['confidence'] > 0.6 or p1_data['confidence'] > 0.6 :
        if msvcrt.kbhit():
            if ord(msvcrt.getch()) == 32:
                print 'g',g_data['norm_pos'],g_data['timestamp'],g_data['confidence'],len(g_data['base_data'])
                print 'p.0',p0_data['norm_pos'],p0_data['timestamp'],p0_data['confidence']
                print 'p.1',p1_data['norm_pos'],p1_data['timestamp'],p1_data['confidence']
                print ' '
