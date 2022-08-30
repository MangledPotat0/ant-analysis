################################################################################
################################################################################


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
    ap.add_argument('-f', '--file', required=True, nargs='+',
                    help='Data file name')

    args = vars(ap.parse_args())
        

    cols = ['frame', 'orientation', 'head_x', 'head_y',
            'thorax_x', 'thorax_y', 'abdomen_x', 'abdomen_y']

    ct = 0
    
    for fname in args['file']:
        dfile = h5py.File('{}preprocessed\\{}\\{}_proc.hdf5'.format(
                                datapath, fname, fname), 'r')
        #vfile = cv.VideoCapture('{}preprocessed\\{}\\{}corrected.mp4'.format(
        #                        datapath, fname, fname))
        dframe = pd.DataFrame(columns=cols)
        dspeed = pd.DataFrame()
        
        for key in dfile.keys():
            dset = dfile[key][:]
            data = TrajectoryData(dset)
            df = data.speed()
            dspeed = dspeed.append(df['thorax'].copy(),ignore_index=True)
            ct += 1

        g = sns.histplot(data=dspeed)
        g.set_xlim(0,80)
        g.set_ylim(0,7000)
        plt.savefig('{}{}_speed_histogram.png'.format(figspath,fname))
        plt.close()


## EOF
