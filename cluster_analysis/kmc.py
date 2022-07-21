import argparse
import cv2 as cv
import h5py
import json
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn import cluster
import seaborn as sns
import seaborn_image as isns
from yellowbrick.cluster import KElbowVisualizer


# Settings
model = cluster.KMeans()

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\a')) + '\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\a'))+'\\'


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
            frameset = np.zeros((len(dfile.keys()), 2))
            ct = 0
            for key in dfile.keys():
                dset = dfile[key]
                try:
                    instance = np.where(dset[:,0,0] == t)[0][0]
                    position = dset[instance, 2]
                    frameset[ct] = position
                except IndexError:
                    print('idk')
                ct += 1
            fig, splt = plt.subplots(2,1)
            isns.imshow(frame, ax=splt[0])
            visualizer = KElbowVisualizer(model, k=(2,maxclusters), ax=splt[1],
                                metric='distortion').fit(frameset)
            visualizer.finalize()
            plt.savefig('optimal_clusters_{}.png'.format(t), bbox_inches='tight')
            plt.close()

# EOF
