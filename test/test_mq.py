#! /usr/bin/python2
# coding: utf8
import sys
sys.path.append("..")
import unittest
import os
import zmq
from threading import Thread

from time import sleep

from record import mq

def mock_noop(*args, **kwargs):
    pass

def mock_false(*args, **kwargs):
    return False

class TestMq(unittest.TestCase):
    def verify(self, que2):
        return True

    def compare(self, a):
        return True

    def setUp(self):
        #monkey patch other port numbers 
        mq.backbone = "tcp://127.0.0.1:105558"
        mq.publish = "tcp://*:105556"
        self.q_backbone = mq.NodeBackbone.get()
        self.q_publish = mq.NodePublisher.get()
        self.thread =Thread(target=self.q_backbone.do_copyto, args=(self.q_publish, ))
        self.thread.start()
        #self.q_backbone.do_copyto(self.q_publish)

    def tearDown(self):
        return
        
    def test_backbone_node_proxy_test(self):
        # Send a message to the request que (acting as proxy)
        # and see if it is broadcast by the publisher
        # 1. start subscriber
        pubsocket = zmq.Context().socket(zmq.SUB)
        pubsocket.connect("tcp://localhost:105556")
        pubsocket.setsockopt_string(zmq.SUBSCRIBE, u'node-update')
        
        # 2. Connect to NodeBackboneRequest
        req = mq.NodeBackboneRequest.get()
        # 3. Send a message on the wire
        req.send("vpn0 1.1.1.1 0")

        # 4. Check that it reaches the subscriber
        raw = pubsocket.recv_string()
        self.assertTrue(raw.count(" ") == 3)
        self.assertEquals(raw.split(" ")[1], "vpn0")
        
        

if __name__ == '__main__':
    unittest.main()
