import zmq
from blockchain.config import *
class Publisher:

    def __init__(self, host, port):
        self.context=zmq.Context()
        self.socket=self.context.socket(zmq.REP)
        self.socket.bind('tcp://{0}:{1}'.format(host, port))

    def start(self):
        while True:
            message = self.socket.recv()
            self.socket.send("server response!")



if __name__ == '__main__':
    publisher = Publisher(HOST, PORT)
    # 开始监听接受消息
    publisher.start()