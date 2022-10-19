import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def montage_generator(expid, trajectory, rawvid, window):

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
