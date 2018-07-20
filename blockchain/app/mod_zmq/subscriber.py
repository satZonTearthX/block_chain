import zmq
from blockchain.config import *


class Sub:

    def __init__(self,host,port):
        self.context=zmq.Context()
        self.socket=self.context.socket(zmq.REQ)
        self.socket.connect('tcp://{0}:{1}'.format(host,port))

    def send_message(self,message):
        self.socket.send(message)
