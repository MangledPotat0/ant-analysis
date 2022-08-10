################################################################################
################################################################################


import argparse
import cv2 as cv
from datahandler import TrajectoryData 
import h5py
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy import signal as sig
import seaborn as sns


n = 1

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\'))+'\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\'))+'\\'


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
    ap.add_argument('-v', '--video', nargs='+',
                    help='Video file name')

    args = vars(ap.parse_args())
        

    cols = ['frame', 'orientation', 'head_x', 'head_y',
            'thorax_x', 'thorax_y', 'abdomen_x', 'abdomen_y']

    ct = 0
    
    for fname in args['file']:
        dfile = h5py.File('{}{}.hdf5'.format(datapath,fname), 'r')
        #vfile = cv.VideoCapture('{}{}'.format(videopath, args['video']))
        dframe = pd.DataFrame(columns=cols)
        dspeed = pd.DataFrame()
        
        for key in dfile.keys():
            dset = dfile[key][:]
            data = TrajectoryData(dset)
            df = data.firstderivative()
            df['ant_number'] = ct
            ds = pd.DataFrame(compute_speed(df.loc[:,2:7]),
                              columns=['speed (px/mm)'])
            dspeed = dspeed.append(ds)
            dframe = dframe.append(df, ignore_index=True)
            ct += 1

        g = sns.histplot(data=dspeed)
        g.set_xlim(0,80)
        g.set_ylim(0,7000)
        plt.savefig('asdf.png')
        plt.close()

    sns.histplot(x='thorax_x', y='thorax_y', data=dframe, bins=(50,40), cbar=True)
    plt.savefig('n{}_histogram_alltime.png'.format(n))
    plt.close()



## EOF
