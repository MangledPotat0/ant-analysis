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

resolution = 10
coarse_grain = 5
fps = 10
n = 6

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\'))+'\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\'))+'\\'


# Compute distances from head to thorax and thorax to abdomen. Filters out
# any value pair containing nan to prevent skews in average

def check_body_size(coords, resolution):
    headx, heady, thorx, thory, abdox, abdoy = np.transpose(coords)
    diffsq1 = np.sum(np.array([headx - thorx, heady - thory])**2,axis=0)
    dist1 = np.sqrt(diffsq1)
    diffsq2 = np.sum(np.array([thorx - abdox, thory - abdoy])**2,axis=0)
    dist2 = np.sqrt(diffsq2)

    distances = np.transpose(np.array([dist1,dist2]))
    idx = np.where(np.isnan(dist1+dist2))
    np.delete(distances, idx)

    return distances / resolution


def check_speed(speeds, resolution, fps, coarse_grain):
    trans = np.transpose(speeds)
    timeavg = trans / trans[0]
    _, _, headx, heady, thorx, thory, abdox, abdoy = timeavg
    head = np.sqrt(headx**2 + heady**2)
    thorax = np.sqrt(thorx**2 + thory**2)
    abdomen = np.sqrt(abdox**2 + abdoy**2)

    new = (head + thorax + abdomen) / 3
    idx = np.where(np.isnan(speeds))
    np.delete(new, idx)
    
    if coarse_grain>0:
        t = coarse_grain
        temp = new
        tempa = temp[0::t] 
        tempb = temp[t-1::t]
        end = min([len(tempa), len(tempb)])
        new = tempa[:end] + tempb[:end]

    return fps * new / resolution


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
    speeds = pd.DataFrame()
    ct = 0
    
    for fname in args['file']:
        dfile = h5py.File('{}{}.hdf5'.format(datapath,fname), 'r')
        #vfile = cv.VideoCapture('{}{}'.format(videopath, args['video']))
        dframe = pd.DataFrame(columns=cols)
        vframe = pd.DataFrame(columns=cols)
        
        for key in dfile.keys():
            dset = dfile[key][:]
            t, _, _ = np.shape(dset)
            dset = dset.reshape([t,8])
            velocityset = dset[1:] - dset[:-1]
            print(dset[np.where(velocityset>100)[0],0],np.where(velocityset>100))
            df = pd.DataFrame(dset, columns=cols)
            df['ant_number'] = ct
            sf = pd.DataFrame(velocityset, columns=cols)
            sf['ant_number'] = ct
            dframe = dframe.append(df)
            vframe = vframe.append(sf)
            ct += 1

        coords = dframe.loc[:,'head_x':'abdomen_y'].to_numpy()
        dists = check_body_size(coords, resolution)
        distances = distances.append(
                        pd.DataFrame(dists, columns=['head-thorax (mm)',
                                                     'thorax-abdomen (mm)']),
                                     ignore_index=True)

        speed = check_speed(vframe.loc[:,:'abdomen_y'].to_numpy(),
                            resolution, fps, coarse_grain)
        speeds = speeds.append(pd.DataFrame(speed, columns=['speed (mm/s)']),
                               ignore_index=True)
    
    g = sns.JointGrid(x='head-thorax (mm)', data=distances,
                      y='thorax-abdomen (mm)', space=0)
    g.plot_joint(sns.histplot)
    g.plot_marginals(sns.histplot)
    plt.savefig('n{}_bodysize_check.png'.format(n))
    plt.close()

    distances['total (mm)'] = (distances['head-thorax (mm)'] + 
                               distances['thorax-abdomen (mm)'])

    sns.histplot(x='total (mm)', data=distances).set(title='Estimated body length')
    plt.savefig('n{}_total_length.png'.format(n))
    plt.close()

    g = sns.histplot(x='speed (mm/s)',data=speeds, log_scale=False)
    g.set_xlim(0., 20)
    g.set_ylim(0, 15000)
    plt.savefig('n{}_speed.png'.format(n))
    plt.close()
        

## EOF
