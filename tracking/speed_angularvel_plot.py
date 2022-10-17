################################################################################
#                                                                              #
#                                                                              #
################################################################################

# Load data from several data files and compute walking speed for each ant
# Sort the dataset of walking speed by number of ants in the file
# After sorting, create dataframe with an additional column that identifies how
# many ants were in the dataset
# Create a lineplot with x = number of ants per dataset and y = walking speed
# using seaborn, and it will generate average and 'error bars' (spread)


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
import seaborn as sns


resolution = 10
coarse_grain = 5
fps = 10
n = 6


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


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', help='Experiment file id')

    args = vars(ap.parse_args())
    expid = args['expid']
    
    dfile = h5py.File('{}{}\\{}_proc.hdf5'.format(srcpath, expid, expid), 'r')

    dfile_pool = pd.DataFrame()
    for key in dfile.keys():
        dset = dfile[key]
        data = TrajectoryData(dset[:])
        dfile_pool = dfile_pool.append(data.speed(), ignore_index=True)
        sns.scatterplot(x='centroid speed', y='angular velocity', data=data.speed())
        plt.savefig('{}{}{}.png'.format(figspath,expid,key))
        plt.close()

    sns.scatterplot(x='centroid speed', y='angular velocity', data=dfile_pool)
    plt.savefig('{}{}.png'.format(figspath,expid))
    plt.close()

# EOF
