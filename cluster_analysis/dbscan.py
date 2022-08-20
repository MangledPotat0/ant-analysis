import argparse
import cv2 as cv
from datetime import date
import h5py
import json
import kneed
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn import cluster
from sklearn.neighbors import NearestNeighbors
import seaborn as sns
import seaborn_image as isns


# Usage example taken from:
# https://scikit-learn.org/stable/modules/clustering.html#dbscan

# Knee location example taken from:
# https://towardsdatascience.com/how-to-use-dbscan-effectively-ed212c02e62

# Additional information from Cluster Analysis and Application
# (isbn: 9783030745523)

# Settings

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']

today = date.today()
today = today.strftime('%Y%m%d')

outputpath = str(datapath + 'processed\\cluster_dbscan\\')
figspath = str(datapath + 'processed\\cluster_dbscan\\' + today + '\\')

try:
    os.mkdir(outputpath)
except:
    pass

try:
    os.mkdir(figspath)
except:
    pass


def find_nearest_neighbors(frameset, min_samples, t):
    nearest_neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors = nearest_neighbors.fit(frameset)
    distances, indices = neighbors.kneighbors(frameset)

    distances = np.sort(distances[:,min_samples-1], axis=0)
    
    return distances


def locate_knee_point(distances, t):
    idx = np.arange(len(distances))
    knee = kneed.KneeLocator(idx, distances, S=1, curve='convex',
                             direction='increasing', interp_method='polynomial')

    if t % 250 == 0:
        sns.lineplot(data=distances)
        knee.plot_knee()
        plt.xlabel('points')
        plt.ylabel('distance (px)')
        plt.savefig('{}distances_{}.png'.format(figspath,t))
        plt.close()

    return distances[knee.knee]


def perform_dbscan(frame, frameset, eps, t, vidwriter):
    db = cluster.DBSCAN(eps=eps, min_samples=3).fit(frameset)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    dbframe = pd.DataFrame()
    fig = plt.figure(figsize=(8.3,4.04),dpi=500)
    ax = fig.subplots()
    for k in set(labels):
        class_member_mask = labels == k
        df = pd.DataFrame(frameset[class_member_mask])
        df['set'] = np.full(df.shape[0],k)
        dbframe.append(df)

    sns.scatterplot(data=frameset, x='x', y='y', ax=ax,
                    hue=db.labels_, palette='deep')
    ax.imshow(frame)
    ax.set_axis_off()
    plt.legend(bbox_to_anchor=(1,1), loc='upper left')
    plt.subplots_adjust(top=1,bottom=0,right=0.91,left=0,hspace=0,wspace=0)

    fig.canvas.draw()

    outframe = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    outframe = outframe.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()
    vidwriter.write(outframe)


    return 



if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True,
                    help='Data file name')
    
    args = vars(ap.parse_args())
    expid = args['expid']

    dfile = h5py.File('{}\\preprocessed\\{}\\{}_proc.hdf5'.format(
                            datapath, expid, expid), 'r')
    vidstream = cv.VideoCapture('{}\\preprocessed\\{}\\{}corrected.mp4'.format(
                            datapath, expid, expid))
    maxframe = int(vidstream.get(cv.CAP_PROP_FRAME_COUNT))


    fig, ax = plt.subplots()

    wh = (4150, 2020)
    
    out = cv.VideoWriter('{}cluster_montage.mp4'.format(figspath),
                         apiPreference = cv.CAP_ANY,
                         fourcc = cv.VideoWriter_fourcc(*'mp4v'),
                         fps = 10.0,
                         frameSize = wh,
                         isColor = True)

    imstack = []
    
    # For min_samples the 'rule of thumb' is to use dimensionality * 2 or
    # greater (Sander et al., 1998).
    min_samples = 9
    for t in range(maxframe):
        _, frame = vidstream.read()
        if t % 250 == 0:
            frameset = pd.DataFrame(columns=['x', 'y'])
            ct = 0
            for key in dfile.keys():
                dset = dfile[key]
                try:
                    instance = np.where(dset[:,0,0] == t)[0][0]
                    position = pd.DataFrame(dset[instance, 1:],
                                            columns=['x','y'])
                    position.dropna(inplace=True)
                    frameset = frameset.append(position)
                except IndexError:
                    print('Warning: IndexError. ',
                          'Likely means a missing instance.')
                ct += 1
            nearest = find_nearest_neighbors(frameset, min_samples, t)
            eps = 90#locate_knee_point(nearest, t)
            perform_dbscan(frame, frameset, eps, t, out)
            
    out.release()


# EOF
