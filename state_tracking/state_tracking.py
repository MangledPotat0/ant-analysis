################################################################################
################################################################################
mlem = 'mlem'

import sys
sys.path.append('..\\common')

import argparse
import cv2 as cv
from datetime import date
import h5py
import itertools as it
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

srcpath = str(datapath + 'preprocessed\\')
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


def groupc(src):
    for x,y in it.groupby(src, lambda n, c=it.count(): n-next(c)):
        y = list(y)
        if len(np.shape(y)) == 1:
            yield y[0], y[-1]
        else:
            yield y[0][1], y[-1][1]


# Take list of 'active' ants as input,
# Check the root square displacement over different timescales
# to examine whether the ants are actually active or if the detected
# movement is strongly timescale dependent.
def flicker_clean(dframe):
    
    groups = {}
    for ant in list(set(dframe['antID'].to_list())):
        active = dframe[dframe['antID'] == ant]
        active.sort_values(by=['frame'])
        frame_list = active['frame'].to_numpy()
        groups[ant] = list(groupc(frame_list))
        for bounds in groups[ant]:
            sequential = active.loc[
                    (active['frame']>=bounds[0]) & (active['frame']<=bounds[1])]
            yield sequential
    

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', help='Experiment ID')
    ap.add_argument('-t', '--threshold', help='Threshold value for speed')
    ap.add_argument('-m', '--montage', action='store_true',
                    help='Whether or not to make a montage')
    args = vars(ap.parse_args())
    expid = args['expid']
    threshold = float(args['threshold'])

    dfile = h5py.File('{}{}\\{}_proc.hdf5'.format(
                                srcpath, expid, expid))
    vfile = cv.VideoCapture('{}{}\\{}corrected.mp4'.format(
                                srcpath, expid, expid))
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

    dtable.to_hdf('{}{}\\{}_active_ants.hdf5'.format(srcpath, expid, expid),
                  mode='w', key='ant_state_data')

    ct = 0
    lengths = pd.DataFrame(columns=['length', 'width'])
    for iterable in flicker_clean(active):
        ct+=1
        initial = iterable.reset_index().loc[0]
        initial = initial.drop('state')
        initial = initial.drop('antID')
        initial = initial.drop('frame')
        diff = iterable.copy().subtract(initial, axis=1)
        diff = diff.apply(lambda x: x**2)
        disp = pd.DataFrame(columns=['frame', 'antID', 'displacement'])
        disp['displacement'] = (np.sqrt((diff['head_x'] + diff['head_y']
                            ).astype(float)) + np.sqrt((diff['thorax_x']
                                + diff['thorax_y']).astype(float)) +
                            np.sqrt((diff['abdomen_x'] + diff['abdomen_y']
                            ).astype(float))) / 3
        disp['frame'] = iterable['frame']
        disp['antID'] = iterable['antID']

        if disp['displacement'].to_numpy()[-1] < threshold * disp.shape[0]:
            if disp.shape[0] < 500:
                shapes = pd.DataFrame([disp.shape], columns = ['length', 'width'])
                lengths = lengths.append(shapes, ignore_index =True)

                sns.scatterplot(x='frame', y='displacement', data=disp)
                plt.savefig('{}{}.png'.format(figspath, ct))
                plt.close()

    sns.histplot(x='length', data=lengths, log_scale=True)
    plt.savefig('{}lengths.png'.format(figspath))
    plt.close()
    

    if int(args['montage']) == 1:

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

    sns.histplot(data=active, x='frame', binwidth=100) 
    plt.savefig('{}{}active_hist.png'.format(figspath, expid))
    plt.close()
    sns.histplot(data=inactive, x='frame', binwidth=100) 
    plt.savefig('{}{}_inactive_hist.png'.format(figspath, expid))


# EOF
