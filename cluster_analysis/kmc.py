import argparse
import cv2 as cv
import h5py
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn import cluster.KMeans as model
import seaborn as sns
import seaborn_image as isns
from yellowbrick.cluster import KElbowVisualizer

# Source: https://www.reneshbedre.com/blog/kmeans-clustering-python.html


# Setting paths
with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']

today = date.today()
today = today.strftime('%Y%m%d')

outputpath = str(datapath + 'processed/cluster_kmeans/')
figspath = str(datapath + 'processed/cluster_kmeans/' + today + '/')

# Attempt to create the directories
try:
    os.mkdir(outputpath)
except OSError:
    pass

try:
    os.mkdir(figspath)
except OSError:
    pass


# Knee (Elbow) locator

# Input:
#  frame    | numpy Array object containing image
#  frameset | pandas DataFrame object containing all ants in current frame
#  t        | int for current frame number

# Output:
#  visualizer.elbow_value_ | float value indicating the position of the elbow

def find_optimal_kvalue(frame, frameset, t):

    fig, splt = plt.subplots(2,1)
    isns.imshow(frame, ax=splt[0])
    visualizer = KElbowVisualizer(model, k=(1,maxclusters), ax=splt[1],
                        metric='distortion').fit(frameset)
    visualizer.finalize()
    plt.savefig('optimal_clusters_{}.png'.format(t), bbox_inches='tight')
    plt.close()

    return visualizer.elbow_value_


# Do the K-means clustering

# Input:
#  Same as find_optimal_kvalue()

# Output:
#  NONE (Labeled image is saved directly to figspath)

def perform_kmeans(frame, frameset, t):
    kmc = cluster.KMeans(n_clusters=k, init='k-means++', n_init = 20,
                         algorithm='auto').fit(frameset)
    
    centers = pd.DataFrame(kmc.cluster_centers_, columns=['x','y'])

    isns.imshow(frame)
    sns.scatterplot(data=frameset, x='x', y='y', hue=kmc.labels_)
    sns.scatterplot(data=centers, x='x', y='y', marker='X', 
                    label='centroids')
    plt.savefig('{}kmeans_vis{}.png'.format(figspath,t))
    plt.close()
    


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True,
                    help='Data file name')
    ap.add_argument('-v', '--video',
                    help='Video file name')
    
    args = vars(ap.parse_args())

    dfile = h5py.File(str(datapath+args['file']), 'r')
    vidstream = cv.VideoCapture(str(videopath+args['video']))
    maxclusters = len(dfile.keys())
    maxframe = int(vidstream.get(cv.CAP_PROP_FRAME_COUNT))
    stride = 250

    for t in range(maxframe):
        _, frame = vidstream.read()
        if t % stride == 0:
            frameset = pd.DataFrame(columns=['x', 'y'])
            ct = 0
            for key in dfile.keys():
                dset = dfile[key]
                try:
                    instance = np.where(dset[:,0,0] == t)[0][0]
                    position = pd.DataFrame(dset[instance:instance+1, 2],
                                            columns=['x','y'])
                    frameset = frameset.append(position)
                except IndexError:
                    print('Warning: IndexError. ',
                          'Likely means a missing instance.')
                ct += 1
            k = find_optimal_kvalue(frame, frameset, t)
            perform_kmeans(frame, frameset, t)


# EOF
