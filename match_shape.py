import os
import sys

import zmq
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from skimage.filter import canny, sobel
from scipy import ndimage
from skimage import morphology


def run():
    context = zmq.Context()

    zin = context.socket(zmq.PULL)
    zin.connect("tcp://127.0.0.1:5558")

    zout = context.socket(zmq.PUSH)
    zout.bind("tcp://127.0.0.1:5559")

    while(True):
        (name, img, bbox) = zin.recv_pyobj()
        print "match shape got %s" % name
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        match_stats = check_for_match(img_grey)
        print "match shape processed %s" % name
        zout.send_pyobj((name, img, bbox, match_stats))
        print "match shape sent %s" % name


def edge_and_fill(image):
    image = sobel(image)
    image = canny(image, sigma=0.5)
    image = ndimage.binary_fill_holes(image)
    image = morphology.remove_small_objects(image, 100)
    image = image.astype(np.uint8)
    return image


def check_for_match(area_of_interest):

    clean = edge_and_fill(area_of_interest)

    cntrs, _ = cv2.findContours(clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    area_copy = np.copy(area_of_interest)

    min_ret = 1000000000000
    min_name = ''

    print "cehck for match : num_contours : %d" % len(cntrs)

    probs = {}
    for target_name in target_contours.keys():
        probs[target_name] = []

    for section in cntrs:

        area = cv2.contourArea(section)
        if area < 200 or area > 3000:
            continue

        for target_name in target_contours.keys():

            area_of_interest = np.copy(area_copy)

            target = target_contours[target_name]

            ret = cv2.matchShapes(section, target, 1, 0.0)

            probs[target_name].append(ret)

    print "area_probs" + str(probs)
    area_match_prob = {}
    for target_name in probs.keys():
        if len(probs[target_name]) == 0:
            avg = 0
        else:
            avg = 1-sum(probs[target_name])/float(len(probs[target_name]))

        area_match_prob[target_name] = avg

    print "area_prob" + str(area_match_prob)

    return area_match_prob


def load_known_contours():
    known_contours = {}
    path = './images/targets'
    paths = [os.path.join(path, fn) for fn in next(os.walk(path))[2]]
    for fname in paths:

        target = Image.open(fname).convert('L')
        target = np.asarray(target)

        _, thresh = cv2.threshold(target, 127, 255, 0)

        cntrs = cv2.findContours(thresh,
                                 cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        known_contours[fname.split('/')[-1]] = cntrs[0][0]

    return known_contours


target_contours = load_known_contours()
if __name__ == "__main__":
    run()
