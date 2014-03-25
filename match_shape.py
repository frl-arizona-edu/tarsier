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
        img = zin.recv_pyobj()
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        check_for_match(img_grey)


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

    for section in cntrs:

        area = cv2.contourArea(section)
        if area < 200 or area > 3000:
            continue

        for target_name in target_contours.keys():

            area_of_interest = np.copy(area_copy)

            target = target_contours[target_name]

            ret = cv2.matchShapes(section, target, 1, 0.0)

            if ret < min_ret:
                min_ret = ret
                min_name = target_name
                cv2.drawContours(area_of_interest, [section], 0, (0, 0, 0), 4)
                plt.imshow(area_of_interest)
                plt.show()

    if min_ret < 0.1:
        print "Closest match was %s with error = %f" % (min_name, min_ret)


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
