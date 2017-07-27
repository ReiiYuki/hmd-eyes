import zmq_receiver,zmq,json
from sender import UDPSender

streamer = UDPSender('127.0.0.1',5500)

ctx = zmq.Context()

req = zmq_receiver.init_requester(ctx,50124)

g_sub = zmq_receiver.create_subscriber(ctx,req,u'gaze')

while True :

    g_data = zmq_receiver.get_data(g_sub)
    norm_pos = g_data['norm_pos']

    if get_data['confidence'] > 0.6 :
        streamer.send('%s,%s'%(str(norm_pos[0]),str(norm_pos[1])))
