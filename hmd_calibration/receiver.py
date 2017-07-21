import zmq, msgpack
from zmq_tools import Msg_Receiver

class Receiver :
    def __init__(self) :

        ctx = zmq.Context()
        url = 'tcp://localhost'

        self.requester = ctx.socket(zmq.SUB)
        self.requester.connect('%s:%s'%(url,50124))
        #requester.send('SUB_PORT')

        #ipc_sub_port = requester.recv().decode('utf-8')

        #sub_url = '%s:%s'%(url,ipc_sub_port)

        #self.receiver = Msg_Receiver(ctx,sub_url,topics=('gaze',))
        self.requester.set(zmq.SUBSCRIBE, 'gaze.')
        #self.topic = 'gaze'
        #self.payload = msgpack.dumps({'topic':'gaze'})

    #    requester.send_multipart([self.topic,self.payload])

    def receiveData(self) :
        self.topic,self.payload = self.requester.recv_multipart()
        return self.payload


ctx = zmq.Context()
url = 'tcp://localhost'

requester = ctx.socket(zmq.SUB)
requester.connect('%s:%s'%(url,50124))
requester.set(zmq.SUBSCRIBE, 'gaze.')

topic = 'gaze.'
payload = msgpack.dumps({'topic':'gaze'})

requester.send_multipart((topic,payload))
while True :
    print 'aaa'
    topic,payload = requester.recv_multipart()
    print topic,payload
