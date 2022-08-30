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

    args = vars(ap.parse_args())
    expid = args['expid']

    dtable = pd.read_hdf('{}{}_active_ants.hdf5'.format(figspath, expid))

    maxant = max(dtable['antID'])

    values = []
    for ant in range(maxant):
        print(ant)
        thisant = dtable[dtable['antID']==ant].copy()
        active_counts = len(thisant[thisant['state']=='active'])
        inactive_counts = len(thisant[thisant['state']=='inactive'])
        values.append(active_counts / (active_counts+inactive_counts))

    values = pd.Series(values)

    sns.histplot(data=values)
    plt.savefig('{}{}_check.png'.format(figspath,expid))

# EOF
