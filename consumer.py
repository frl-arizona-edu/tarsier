import time
import zmq
import pprint
import matplotlib.pyplot as plt


def result_collector():
    context = zmq.Context()
    zin = context.socket(zmq.PULL)
    zin.connect("tcp://127.0.0.1:5559")

    while(True):
        (name, img, bbox, match_stats) = zin.recv_pyobj()
        print "RESULTS"
        print "\tname: %s" % name
        print "\tbbox : " + str(bbox)
        for m in match_stats.keys():
            print "\t\t%s prob = %f" % (m, match_stats[m])
        plt.imshow(img)
        plt.show()


result_collector()
