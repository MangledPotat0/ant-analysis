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

# Source: https://www.reneshbedre.com/blog/kmeans-clustering-python.html


# Settings

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\a')) + '\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\a'))+'\\'


def perform_dbscan(frame, frameset, t, vidwriter):
    db = cluster.DBSCAN(eps=80, min_samples=3).fit(frameset)
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
    ap.add_argument('-f', '--file', required=True,
                    help='Data file name')
    ap.add_argument('-v', '--video',
                    help='Video file name')
    
    args = vars(ap.parse_args())

    dfile = h5py.File(str(datapath+args['file']), 'r')
    vidstream = cv.VideoCapture(str(videopath+args['video']))
    maxframe = 12000


    fig, ax = plt.subplots()

    try:
        os.mkdir('output_dump')
    except:
        pass

    wh = (4150, 2020)
    
    out = cv.VideoWriter('output.mp4', apiPreference = cv.CAP_ANY,
                         fourcc = cv.VideoWriter_fourcc(*'mp4v'),
                         fps = 10.0,
                         frameSize = wh,
                         isColor = True)

    imstack = []
    for t in range(maxframe):
        _, frame = vidstream.read()
        if t % 1 == 0:
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
            perform_dbscan(frame, frameset, t, out)
            
    out.release()


# EOF
