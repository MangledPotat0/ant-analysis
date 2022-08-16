################################################################################
################################################################################


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

outputpath = str(datapath + 'processed\\position_plots\\')
figspath = str(datapath + 'processed\\position_plots\\' + today + '\\')

try:
    os.mkdir(outputpath)
    os.mkdir(figspath)
except:
    pass

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
    n = 0
    
    for fname in args['file']:
        dfile = h5py.File('{}preprocessed\\{}\\{}_proc.hdf5'.format(
                          datapath,fname,fname), 'r')
        #vfile = cv.VideoCapture('{}{}\\{}'.format(datapath, 
        #                        args['video'], args['video']))
        dframe = pd.DataFrame(columns=cols)
        
        for key in dfile.keys():
            dset = dfile[key][:]
            data = TrajectoryData(dset)
            df = data.trajectory()
            df['ant_number'] = ct
            n = len(dfile.keys())

## Trajectory plot
            sns.scatterplot(x='thorax_x',y='thorax_y', data=df, alpha=0.1)
            plt.savefig('{}{}_trajectory_{}.png'.format(figspath,fname,ct))
            plt.close()

## Spatial Autocorrelation function
            
            pair = pd.DataFrame()
            for column in df.loc[:,'thorax_x':'thorax_y']:
                acf = autocorrelate(column, df)
                pair[column] = acf
                sns.lineplot(data=acf, legend=False).set(xlabel='t (frames)',
                                            ylabel='acf_{}'.format(column))
                plt.savefig('{}{}_{}_{}_acf.png'.format(figspath, fname,
                                                        ct, column))
                plt.close()

            sns.lineplot(x='thorax_x', y='thorax_y', data=pair,
                        sort=False, alpha=0.2)
            plt.savefig('{}check.png'.format(figspath))
            plt.close()

            sns.set(style='darkgrid')
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            x = range(len(pair))
            y = pair['thorax_x']
            z = pair['thorax_y']

            ax.plot(x, y, z)
            plt.show()
            plt.close()
            
            dframe = dframe.append(df, ignore_index=True)
            ct += 1

        sns.histplot(x='thorax_x', y='thorax_y', data=dframe, bins=(50,40), 
                     cbar=True)
        plt.savefig('{}{}_histogram_alltime.png'.format(figspath,fname))
        plt.close()

    sns.histplot(x='thorax_x', y='thorax_y', data=dframe, bins=(50,40), cbar=True)
    plt.savefig('{}n{}_histogram_alltime.png'.format(figspath,n))
    plt.close()


## EOF
