################################################################################
################################################################################

import sys
sys.path.append('..\\common')

import argparse
import cv2 as cv
from datetime import date
import h5py
import json
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns

from datahandler import TrajectoryData
import logmaker as lm

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']


today = date.today()
today = today.strftime('%Y%m%d')

outputpath = str(datapath + 'processed\\state_tracking\\')
figspath = str(datapath + 'processed\\state_tracking\\' + today + '\\')

try:
    os.mkdir(outputpath)
except:
    pass

try:
    os.mkdir(figspath)
except:
    pass


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', help='Experiment ID')
    ap.add_argument('-t', '--threshold', help='Threshold value for speed')
    args = vars(ap.parse_args())
    expid = args['expid']
    threshold = int(args['threshold'])

    dfile = h5py.File('{}preprocessed\\{}\\{}_proc.hdf5'.format(
                                datapath, expid, expid))
    vfile = cv.VideoCapture('{}preprocessed\\{}\\{}corrected.mp4'.format(
                                datapath, expid, expid))
    maxframe = int(vfile.get(cv.CAP_PROP_FRAME_COUNT))
    dtable = pd.DataFrame()

    fig, ax = plt.subplots()

    ct = 0
    for key in dfile.keys():
        dset = TrajectoryData(dfile[key][:])
        speed = dset.speed()
        speed = dset.moving_average(speed, 20)
        positions = dset.trajectory().loc[1:].copy()
        positions['antID'] = ct
        idx = speed.to_numpy()
        inactive = positions[idx[:,-1]<threshold].copy()
        inactive['state'] = 'inactive'
        active = positions[idx[:,-1]>=threshold].copy()
        active['state'] = 'active'
        dtable = dtable.append(active, ignore_index=True)
        dtable = dtable.append(inactive, ignore_index=True)
        ct += 1
    
    active = dtable[dtable['state']=='active']
    inactive = dtable[dtable['state']=='inactive']

    dtable.to_hdf('{}{}_active_ant.shdf5'.format(figspath, expid), mode='w',
                  key='ant_state_data')

    '''
    wh = (4150, 2020)
    out = cv.VideoWriter('{}{}_cluster_montage.mp4'.format(figspath, expid),
                         apiPreference = cv.CAP_ANY,
                         fourcc = cv.VideoWriter_fourcc(*'mp4v'),
                         fps = 10.0,
                         frameSize = wh,
                         isColor = True)

    imstack = []

    for n in range(maxframe):
        ret, frame = vfile.read()
        assert ret, "Video read is failing"
        
        objects = dtable[dtable['frame']==n]

        fig = plt.figure(figsize=(8.3,4.04),dpi=500)
        ax = fig.subplots()

        hue_order = ['inactive', 'active']
        sns.scatterplot(data=objects, x='thorax_x', y='thorax_y', ax=ax,
                        hue='state', hue_order=hue_order, palette='deep')
        ax.imshow(frame)
        ax.set_axis_off()
        plt.subplots_adjust(top=1,bottom=0,right=0.91,left=0,hspace=0,wspace=0)
        plt.legend(bbox_to_anchor=(1,1), loc='upper left')

        fig.canvas.draw()

        outframe = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        outframe = outframe.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close()
        out.write(outframe)

    out.release()
    '''
    

    sns.histplot(data=active, x='frame', binwidth=100) 
    plt.savefig('{}{}active_hist.png'.format(figspath, expid))
    plt.close()
    sns.histplot(data=inactive, x='frame', binwidth=100) 
    plt.savefig('{}{}_inactive_hist.png'.format(figspath, expid))
    

# EOF
