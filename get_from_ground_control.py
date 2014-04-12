import zmq
import cv2
import os
import numpy as np


def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://127.0.0.1:5557")

    # Start your result manager and workers before you start your producers
    path = './images/dummy'
    paths = [os.path.join(path, fn) for fn in next(os.walk(path))[2]]
    for fname in paths:
        #print "attempting to send %s" % fname
        target = cv2.imread(fname)
        #print "loaded %s" % fname

        zmq_socket.send_pyobj((fname, target))
        print "get_from_ground_control : sent %s" % fname

producer()
