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

srcpath = str(datapath + 'preprocessed/')
outputpath = str(datapath + 'processed/state_tracking/')
figspath = str(datapath + 'processed/state_tracking/' + today + '/')

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
    ap.add_argument('-id', '--expid', help='Experiment ID', nargs='+')
    ap.add_argument('-n', '--nants', help='Number of ants in each set')
    args = vars(ap.parse_args())
    expids = args['expid']

    dtable = pd.DataFrame()
    for expid in expids:
        dfile = h5py.File('{}{}/{}_proc.hdf5'.format(
                                    srcpath, expid, expid))
        vfile = cv.VideoCapture('{}{}/{}corrected.mp4'.format(
                                    srcpath, expid, expid))
        maxframe = int(vfile.get(cv.CAP_PROP_FRAME_COUNT))
        
        df = pd.read_hdf('{}{}/{}_active_ants.hdf5'.format(srcpath, expid, expid)) 
        dtable = dtable.append(df, ignore_index=True)
    active = dtable[dtable['state']=='active']
    inactive = dtable[dtable['state']=='inactive']

    n = args['nants']
    sns.histplot(data=active, x='frame', binwidth=100) 
    plt.savefig('{}{}active_hist.png'.format(figspath, n))
    plt.close()
    sns.histplot(data=inactive, x='frame', binwidth=100) 
    plt.savefig('{}{}_inactive_hist.png'.format(figspath, n))

# EOF
