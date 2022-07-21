import argparse
import cv2 as cv
import h5py
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn import cluster
import seaborn as sns
import seaborn_image as isns
from yellowbrick.cluster import KElbowVisualizer


# Source: https://www.reneshbedre.com/blog/kmeans-clustering-python.html


# Settings
model = cluster.KMeans()

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\a')) + '\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\a'))+'\\'


def find_optimal_kvalue(frame, frameset, t):

    fig, splt = plt.subplots(2,1)
    isns.imshow(frame, ax=splt[0])
    visualizer = KElbowVisualizer(model, k=(1,maxclusters), ax=splt[1],
                        metric='distortion').fit(frameset)
    visualizer.finalize()
    plt.savefig('optimal_clusters_{}.png'.format(t), bbox_inches='tight')
    plt.close()

    return visualizer.elbow_value_


def perform_kmeans(frame, frameset, t):
    kmc = cluster.KMeans(n_clusters=k, init='k-means++', n_init = 20,
                         algorithm='auto').fit(frameset)
    
    centers = pd.DataFrame(kmc.cluster_centers_, columns=['x','y'])

    isns.imshow(frame)
    sns.scatterplot(data=frameset, x='x', y='y', hue=kmc.labels_)
    sns.scatterplot(data=centers, x='x', y='y', marker='X', 
                    label='centroids')
    plt.savefig('kmeans_vis{}.png'.format(t))
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
    maxframe = 12000

    for t in range(maxframe):
        _, frame = vidstream.read()
        if t % 250 == 0:
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
                    print('idk')
                ct += 1
            k = find_optimal_kvalue(frame, frameset, t)
            perform_kmeans(frame, frameset, t)


# EOF
