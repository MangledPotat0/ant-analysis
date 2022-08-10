################################################################################
################################################################################


import argparse
import h5py
import json
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import scipy.spatial as sp
import seaborn as sns


with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\'))+'\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\'))+'\\'


# Perception radius from head in pixels, 10px ~= 1mm
radius = 20

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True, nargs='+',
                    help='Data file name')
    ap.add_argument('-v', '--video', nargs='+',
                    help='Video file name')

    args = vars(ap.parse_args())
    
    dfile = h5py.File('{}{}.hdf5'.format(datapath, args['file'][0]), 'r')
    dist_matrix_file = h5py.File('{}{}_distance_matrices.hdf5'.format(
                                        datapath,args['file'][0]),'r')
    #vfile = cv.VideoCapture('{}{}.mp4'.format(videopath, args['video'][0]))
    
    dmatrices = dist_matrix_file['matrix'][:]

    antcount = np.shape(dmatrices[0])[0]
    dframes = np.full(antcount, 0, dtype=object)
    for n in range(len(dframes)):
        dframes[n] = pd.DataFrame()


    for t in range(len(dmatrices)):
        for row in range(len(dmatrices[t])):
            df = pd.DataFrame(dmatrices[t,row])
            dframes[row] = dframes[row].append(df, ignore_index=True)
    
    for dframe in dframes:
        print('next')
        print(dframe.head())

# EOF
