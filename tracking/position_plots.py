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
from scipy import signal as sig
import seaborn as sns


n = 50

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\'))+'\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\'))+'\\'


def autocorrelate(column, dset):
    dseries = pd.Series(dset[column])
    output = []
    for n in range(len(dseries)):
        acval = dseries.autocorr(lag=n)
        output.append(acval)

    output = pd.DataFrame(output, columns=['acf'])

    return output


if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True, nargs='+',
                    help='Data file name')
    ap.add_argument('-v', '--video', nargs='+',
                    help='Video file name')

    args = vars(ap.parse_args())
        

    cols = ['frame', 'orientation', 'head_x', 'head_y',
            'thorax_x', 'thorax_y', 'abdomen_x', 'abdomen_y']

    distances = pd.DataFrame()
    ct = 0
    
    for fname in args['file']:
        dfile = h5py.File('{}{}.hdf5'.format(datapath,fname), 'r')
        #vfile = cv.VideoCapture('{}{}'.format(videopath, args['video']))
        dframe = pd.DataFrame(columns=cols)
        
        for key in dfile.keys():
            dset = dfile[key][:]
            t, _, _ = np.shape(dset)
            dset = dset.reshape([t,8])
            df = pd.DataFrame(dset, columns=cols)
            df['ant_number'] = ct

## Trajectory plot
            sns.scatterplot(x='thorax_x',y='thorax_y', data=df, alpha=0.1)
            plt.savefig('{}_trajectory_{}.png'.format(fname,ct))
            plt.close()

## Spatial Autocorrelation function
            
            for column in df.loc[:,'thorax_x':'thorax_y']:
                acf = autocorrelate(column, df)
                sns.lineplot(data=acf, legend=False).set(xlabel='t (frames)',
                                            ylabel='acf_{}'.format(column))
                plt.savefig('{}_{}_{}_acf.png'.format(fname, ct, column))
                plt.close()
            
            dframe = dframe.append(df, ignore_index=True)
            ct += 1

        sns.histplot(x='thorax_x', y='thorax_y', data=dframe, bins=(50,40), cbar=True)
        plt.savefig('{}_histogram_alltime.png'.format(fname))
        plt.close()

    sns.histplot(x='thorax_x', y='thorax_y', data=dframe, bins=(50,40), cbar=True)
    plt.savefig('n{}_histogram_alltime.png'.format(n))
    plt.close()


## EOF
