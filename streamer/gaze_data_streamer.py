import zmq_receiver,zmq,json,msvcrt
from sender import UDPSender

streamer = UDPSender('127.0.0.1',5500)

ctx = zmq.Context()

req = zmq_receiver.init_requester(ctx,50124)

while True :

    g_sub = zmq_receiver.create_subscriber(ctx,req,u'gaze')

    g_data = zmq_receiver.get_data(g_sub)
    norm_pos = g_data['norm_pos']
    eye_id = g_data['base_data'][0]['id']
    if len(g_data['base_data']) > 1 :
        eye_id = 2
    if g_data['confidence'] > 0.6 :
        streamer.send('%s,%s,%s'%(str(norm_pos[0]),str(norm_pos[1]),eye_id))

        if msvcrt.kbhit():
            if ord(msvcrt.getch()) == 32:
                print 'g',g_data['norm_pos'],g_data['timestamp'],g_data['confidence'],len(g_data['base_data']),g_data['base_data'][0]['id']
