import zmq
from time import sleep

backbone = "tcp://127.0.0.1:5558"
publish = "tcp://*:5556"

# Publishes node data to e.g. DNS
class NodePublisher(object):
    def __init__(self, socket):
        self.socket = socket

    @classmethod
    def get(cls):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind(publish)
        return cls(socket)
        
    def send(self, msg):
        self.socket.send("node-update " + msg)

# Used to recieve data from Restapi
class NodeBackbone(object):
    def __init__(self, socket):
        self.socket = socket

    @classmethod
    def get(cls):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(backbone)
        return cls(socket)

    def do_copyto(self, que):
        while True:
            raw = self.socket.recv()
            que.send(raw)
            self.socket.send(b"OK")
            return raw

# Restapi will use this to write data to NodeBackbone
class NodeBackboneRequest(object):
    def __init__(self, socket):
        self.socket = socket

    @classmethod
    def get(cls):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(backbone)
        return cls(socket)

    def send(self, msg):
        self.socket.send(msg)

if __name__ == "__main__":
    print "Starting backbone Request-reply socket on", backbone, "..."
    q_backbone = NodeBackbone.get()
    print "Starting Publisher socket on", publish, "..."
    q_publish = NodePublisher.get()   
    print "Will now copy from backbone to publisher"
    q_backbone.do_copyto(q_publish)
