###############################################################################
#   Ant labeled montage generator                                             #
#   Code written by Dawith Lim                                                #
#                                                                             #
#   Version: 2.1.0                                                            #
#   First written on: 2020/12/20                                              #
#   Last modified: 2022/08/16                                                 #
#                                                                             #
#   Packages used                                                             #
#   -   numpy: Useful for array manipulation and general calculations         #
#   -   pims: Image handler for trackpy                                       #
#   -   trackpy: Soft-matter particle tracker                                 #
#   -   cv2: OpenCV module                                                    #
#   -   sys: Only really used for the sys.exit() to terminate the code        #
#   -   argparse: Argument parser, allows me to use required & optional       #
#                 inputs with various flags                                   #
#                                                                             #
###############################################################################

import argparse
import cv2 as cv
import h5py
import numpy as np
import os
import random as rand
import sys


with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']

outputpath = str(datapath + 'processed\\speed_plots\\')
montpath = str(datapath + 'processed\\montages\\')

try:
    os.mkdir(outputpath)
    os.mkdir(figspath)
except:
    pass


if __name__ =='__main__':

    ap = argparse.ArgumentParser()

    ap.add_argument('-id', '--expid', required = True,
                    help = 'Trajectory file name')

    args = vars(ap.parse_args())
    fname = args['expid']

    try:
        os.mkdir(str(montpath+fname))
    except OSError:
        print('Failed to create new directory')

    video = cv.VideoCapture('{}{}\\{}corrected.mp4'.format(
                                datapath, fname, fname))
    trajfile = h5py.File('{}{}\\{}_proc.hdf5'.format(
                                datapath, fname, fname),'r')

    trajectories = {}
    for key in trajfile:
        trajectories[key] = trajfile[key]

    offset = 1
    length = video.get(cv.CAP_PROP_FRAME_COUNT)
    ct = 0
    while ct < offset:
        success, frame = video.read()
        ct += 1
    radius = 3
    thickness = 2
    color = {}

    plotstack = []

    try:
        os.makedirs('{}{}{}'.format(self.outpath,
                                    self.fileid, 
                                    self.bincount))
    except:
        print('Directory already exists.\n')


    h = frame.shape[0]
    w = frame.shape[1]

    fps = 10.0
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    api = cv.CAP_ANY
    out = cv.VideoWriter('{}\\{}_tracking_montage.mp4'.format(montpath,vidname),
                        apiPreference = api,
                        fourcc = fourcc,
                        fps = float(fps),
                        frameSize = (w, h),
                        isColor = True)
    for key in trajectories:
        color[key] = (rand.randint(0,255), # B
                       rand.randint(0,255), # G
                       rand.randint(0,255)) # R

    ct = 0
    while success:
        for key in trajectories:
            traj = trajectories[key]
            try:
                mark = np.where(traj[:,0,0]==ct)[0][0]
                coords = traj[mark,1]
                frame = cv.circle(frame, (int(coords[0]),int(coords[1])), 
                                  radius, color[key], thickness)
                coords = traj[mark,2]
                frame = cv.circle(frame, (int(coords[0]),int(coords[1])), 
                                  radius, color[key], thickness)
                coords = traj[mark,3]
                frame = cv.circle(frame, (int(coords[0]),int(coords[1])), 
                                  radius, color[key], thickness)
            except IndexError:
                print('foo')
                pass
            except ValueError:
                print('Missing body segment')
                pass

        out.write(frame) 
        success, frame = video.read()
        ct += 1
        if ct > length:
            success = False

    out.release()
    sys.exit(0)


#EOF
