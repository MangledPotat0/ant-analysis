################################################################################
################################################################################
mlem = 'mlem'

import sys
sys.path.append('..\\common')

import argparse
import cv2 as cv
from datahandler import TrajectoryData 
from datetime import date
import h5py
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy import signal as sig
import seaborn as sns


with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']


today = date.today()
today = today.strftime('%Y%m%d')

srcpath = str(datapath + 'preprocessed\\')
outputpath = str(datapath + 'processed\\speed_plots\\')
figspath = str(datapath + 'processed\\speed_plots\\' + today + '\\')

try:
    os.mkdir(outputpath)
except:
    pass

try:
    os.mkdir(figspath)
except:
    pass


def compute_speed(velocity):
    velocity = velocity.to_numpy()
    hx, hy, tx, ty, ax, ay = np.transpose(velocity)
    head = np.sqrt(hx**2 + hy**2)
    thorax = np.sqrt(tx**2 + ty**2)
    abdomen = np.sqrt(ax**2 + ay**2)

    fullbody = np.transpose([head, thorax, abdomen])
    mask = ~np.isnan(fullbody)
    speeds = np.sum(fullbody, axis=1, where=mask)

    return speeds


if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True, nargs='+',
                    help='Experiment ID')

    args = vars(ap.parse_args())
        

    cols = ['frame', 'orientation', 'head_x', 'head_y',
            'thorax_x', 'thorax_y', 'abdomen_x', 'abdomen_y']

    ct = 0
    
    dspeed_all = pd.DataFrame()
    for fname in args['expid']:
        dfile = h5py.File('{}{}\\{}_proc.hdf5'.format(
                                srcpath, fname, fname), 'r')
        #vfile = cv.VideoCapture('{}preprocessed\\{}\\{}corrected.mp4'.format(
        #                        datapath, fname, fname))
        dframe = pd.DataFrame(columns=cols)
        dspeed = pd.DataFrame()
        
        for key in dfile.keys():
            dset = dfile[key][:]
            data = TrajectoryData(dset)
            df = data.speed()
            df = pd.DataFrame([df.frame, df.centroid]).transpose()
            dspeed = dspeed.append(df.copy(),ignore_index=True)
            ct += 1

        dspeed = dspeed.loc[dspeed['centroid'] <= 50]
        dspeed_all = dspeed_all.append(dspeed)
        g = sns.histplot(data=dspeed, x='centroid', log_scale=True)
        plt.savefig('{}{}_speed_histogram.png'.format(figspath,fname))
        plt.close()

    g = sns.histplot(data=dspeed_all, x='centroid', log_scale=True)
    plt.savefig('{}{}_speed_histogram.png'.format(figspath,fname))
    plt.close()


## EOF
