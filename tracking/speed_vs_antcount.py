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

outputpath = str(datapath + 'processed\\speed_plots\\')
figspath = str(datapath + 'processed\\speed_plots\\' + today + '\\')

try:
    os.mkdir(outputpath)
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


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True, nargs='+',
                    help='experiment id')

    args = vars(ap.parse_args())
        

    ct = 0
    
    dspeed = pd.DataFrame()
    for fname in args['expid']:
        dfile = h5py.File('{}preprocessed\\{}\\{}_proc.hdf5'.format(
                                datapath, fname, fname), 'r')
        #vfile = cv.VideoCapture('{}{}\\{}.mp4'.format(datapath, fname, fname))
        
        setsize = len(dfile.keys())
        for key in dfile.keys():
            dset = dfile[key][:]
            data = TrajectoryData(dset)
            df = data.firstderivative()
            df['ant_number'] = ct
            ds = pd.DataFrame(compute_speed(df.loc[:,2:7]),
                              columns=['speed (px/frame)'])
            ds['setsize'] = setsize

            dspeed = dspeed.append(ds, ignore_index=True)
            ct += 1

    print(dspeed.head())
    sns.lineplot(x='setsize', y='speed (px/frame)', data=dspeed)
    plt.savefig('{}plot_of_speed_vs_antcount.png'.format(figspath))
    plt.close()


# EOF
