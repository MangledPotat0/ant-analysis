import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Function for generating cropped montage that focuses only on one ant. Note
# that this is a generator function that just spits out the images, the referent
# needs to collect the images and export.

# Inputs:
#  trajectory | pandas DataFrame object containing the trajectory of interest
#  rawvid     | string, full path to the target video
#  window     | size of the window that is moving around with the trajectory

# Output:
#  roi        | numpy Array object containing cropped image of the region of
#             | interest.

def montage_generator(trajectory, rawvid, window):

    video = cv.VideoCapture(rawvid)
    ct = 0
    initial_frame = trajectory['frame'].to_numpy()[0]
    while ct < initial_frame:
        exists, img = video.read()
        assert exists, "Frame doesn't exist!"
        ct += 1

    for _, capture in trajectory.iterrows():
        exists, img = video.read()
        assert exists, "Frame doesn't exist!"
        frame = capture['frame']
        pos_x = int(capture['thorax_x'])
        pos_y = int(capture['thorax_y'])
        roi = img[pos_y-window:pos_y+window, pos_x-window:pos_x+window]
        yield roi


# EOF
