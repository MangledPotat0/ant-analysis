################################################################################
################################################################################


import argparse
import cv2 as cv
import h5py
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
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
    os.mkdir(figspath)
except:
    pass


# img_shape, array_shape -> [h,w] (np array)
# ant = (1, 2) np array

def coverage(img_shape, array_shape, head, radius):
    cover = np.full(array_shape, False)
    if np.isnan(head).any():
        pass
    else:
        binsizes = img_shape / array_shape
        headbins = np.flip(head) // binsizes
        headbins = headbins.astype(int)
        
        y, x = np.ogrid[:array_shape[0],:array_shape[1]]
        distance_from_head = np.sqrt((x - headbins[1])**2 + (y - headbins[0])**2)
        mask = distance_from_head <= radius

        cover[mask] = True

    return cover


if __name__ == '__main__':

    radius = 20
    
    # Range for moving average, in frames
    roll = 1000

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True,
                    help='Data file name')

    args = vars(ap.parse_args())
    fname = args['expid']
    dfile = h5py.File('{}preprocessed\\{}\\{}_proc.hdf5'.format(
                            datapath, fname, fname), 'r')
    vfile = cv.VideoCapture('{}preprocessed\\{}\\{}corrected.mp4'.format(
                            datapath, fname, fname))

    ret, frame = vfile.read()

    ct = 0
    timeseries = pd.DataFrame()
    while ret:
        img_shape = np.shape(frame)[:2]
        array_shape = np.array(img_shape) / 5
        array_shape = array_shape.astype(int)
        covered = np.full(array_shape, False)
        for key in dfile.keys():
            trajectory = dfile[key][:]
            idx = np.where(trajectory[:,0,0] == ct)
            if np.shape(idx[-1])[0] > 0:
                positions = trajectory[idx][0]
                head = positions[1]
                overwrite = coverage(img_shape, array_shape, head, radius)
                covered += overwrite
            
        total = array_shape[0] * array_shape[1]
        covered_count = np.count_nonzero(covered)
        covered_ratio = covered_count / total
        entry = pd.DataFrame([[ct, covered_ratio]], columns=['time (frame)', 'cover_ratio'])
        timeseries = timeseries.append(entry, ignore_index=True)
        ret, frame = vfile.read()
        ct += 1

    timeseries['mavg'] = timeseries['cover_ratio'].rolling(roll).mean()
    #timeseries.dropna(inplace=True)

    sns.lineplot(x='time (frame)', y='cover_ratio', data=timeseries)
    sns.lineplot(x='time (frame)', y='mavg', data=timeseries)
    plt.savefig('{}coverage.png'.format(figspath))

            
            

        

# EOF
