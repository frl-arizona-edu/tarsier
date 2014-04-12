import os

from PIL import Image
import zmq
import cv2
import matplotlib.pyplot as plt
from skimage.filter import canny, sobel
from skimage import morphology
from scipy import ndimage
import numpy as np


def run():
    context = zmq.Context()
    zin = context.socket(zmq.PULL)
    zin.connect("tcp://127.0.0.1:5557")

    zout = context.socket(zmq.PUSH)
    zout.bind("tcp://127.0.0.1:5558")

    while(True):
        (name, img) = zin.recv_pyobj()
        print "segment got image : %s" % name
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = edge_and_fill(img_grey)

        for (section, bbox) in segment(edges, img):
            zout.send_pyobj((name, section, bbox))


def edge_and_fill(image):
    image = sobel(image)
    image = canny(image, sigma=0.5)
    image = ndimage.binary_fill_holes(image)
    image = morphology.remove_small_objects(image, 100)
    image = image.astype(np.uint8)
    return image


def segment(image, orig):
    cntrs, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_h, img_w = image.shape

    for contour in cntrs:
        image_copy = np.copy(image)

        area = cv2.contourArea(contour)
        if area < 200 or area > 5000:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # add some padding before we crop
        y0 = max(0, y - h/10)
        y1 = min(img_h, y + h + h/5)
        x0 = max(0, x - w/10)
        x1 = min(img_w, x + w + w/5)

        cropped = orig[y0:y1, x0:x1]
        yield (cropped, (x0, y0, x1-x0, y1-y0))

        #plt.imshow(cropped)
        #plt.show()

run()
