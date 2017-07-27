import zmq_receiver,zmq,json
from sender import UDPSender

streamer = UDPSender('127.0.0.1',5500)

ctx = zmq.Context()

req = zmq_receiver.init_requester(ctx,50124)

p0_sub = zmq_receiver.create_subscriber(ctx,req,u'pupil.0')
p1_sub = zmq_receiver.create_subscriber(ctx,req,u'pupil.1')

while True :

    p0_data = zmq_receiver.get_data(p0_sub)
    p1_data = zmq_receiver.get_data(p1_sub)
    streamer.send(json.dumps([{'id':p0_data['id'],'norm_pos':p0_data['norm_pos'],'confidence':p0_data['confidence'],'timestamp':p0_data['timestamp']},{'id':p1_data['id'],'norm_pos':p1_data['norm_pos'],'confidence':p1_data['confidence'],'timestamp':p1_data['timestamp']}]))
