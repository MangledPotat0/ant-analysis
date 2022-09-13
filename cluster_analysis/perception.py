################################################################################
################################################################################


import argparse
from datetime import date
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
    datapath = paths['datapath']

today = date.today()
today = today.strftime('%Y%m%d')

src = str(datapath + 'preprocessed' + '\\')
outputpath = str(datapath + 'processed\\contact\\')
figspath = str(datapath + 'processed\\contact\\' + today + '\\')

try:
    os.mkdir(outputpath)
except:
    pass

try:
    os.mkdir(figspath)
except:
    pass


# Perception radius from head in pixels, 10px ~= 1mm
radius = 120

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True,
                    help='Experiment name')

    args = vars(ap.parse_args())
    expid = args['expid']
    
    dfile = h5py.File('{}{}\\{}_proc.hdf5'.format(src,expid,expid), 'r')
    dist_matrix_file = h5py.File('{}{}\\{}_distance_matrices.hdf5'.format(
                                        src,expid,expid),'r')
    #vfile = cv.VideoCapture('{}preprocessed\\{}.mp4'.format(datapath,
    #                                            args['expid'][0]))
    
    dmatrices = dist_matrix_file['matrix'][:]

    antcount = np.shape(dmatrices)[1]
    dframes = np.full(antcount, 0, dtype=object)
    for n in range(len(dframes)):
        dframes[n] = pd.DataFrame()


    for t in range(len(dmatrices)):
        for row in range(len(dmatrices[t])):
            df = pd.DataFrame([dmatrices[t,row]])
            dframes[row] = dframes[row].append(df, ignore_index=True)

    ant = 0
    for series in dframes:
        ant += 1
        interactions = [np.count_nonzero(
                                 (distances < radius) & (distances > 0)
                                 ) for distances in series.to_numpy()]

        interactions = pd.DataFrame(interactions, columns=['interactions'])
        interactions = interactions.rolling(10).sum()
        sns.lineplot(data = interactions)
        plt.savefig('{}{}{}'.format(figspath, expid, ant))
        plt.close()

# EOF
