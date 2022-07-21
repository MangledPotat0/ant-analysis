import argparse
import cv2 as cv
import h5py
import json
import math
import matplotlib.animation as ani
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import seaborn_image as isns

# TODO: The path management looks sketchy, check that it works in unix env

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\clustering\\a')) + '\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\a'))+'\\'


# Extract the upper triangle of the distance matrix to eliminate redundancy
# since distance in the metric space is symmetric. Then, flatten the nonzero
# elements into a list and return it.

def convert_to_list(distance_matrix):
    upper = np.triu(distance_matrix)
    flattened_list = upper.flatten()
    sieved = flattened_list[flattened_list != 0]

    return sieved


def radial_distribution(distances, dr):

    maxval = max(distances)
    bins = int(np.ceil(maxval/dr))
    rawcounts = np.zeros(bins)
    normalization = np.zeros(bins)

    for r in range(bins):
        for distance in distances:
            if (distance > r) & (distance <= r + dr):
                rawcounts[r] += 1    

        normalization[r] = math.pi*(r + dr)**2 - math.pi * r**2

    rdf = rawcounts / normalization

    return rdf

def generate_figure(values1d, image, ct):
    plt.clf()
    fig, splt = plt.subplots(2,1)
    dframe = pd.DataFrame(data=values1d)
    isns.imshow(image, ax=splt[0])
    sns.lineplot(data=dframe, ax=splt[1])

    plt.title('frame={}'.format(ct))
    if ct % 250 == 0:
        plt.savefig('plot{}.png'.format(ct),
                    bbox_inches='tight')
    plt.close()
    
    return


if __name__=="__main__":
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True,
                    help = 'data file name')
    ap.add_argument('-v', '--video',
                    help='Video file name (optional)')

    args = vars(ap.parse_args())

    with h5py.File(str(datapath + args['file']), 'r') as dfile:
        distance_matrices = dfile['matrix'][:]

    vidstream = cv.VideoCapture(str(videopath+args['video']))
    
    # Generate plot stack through time
    
    ct = 0

    stack = []
    fig = plt.figure(figsize=(5.5, 5.5))
    for distance_matrix in distance_matrices:
        _, image = vidstream.read()
        distance_list = convert_to_list(distance_matrix)
        rdf = radial_distribution(distance_list, 10)
        generate_figure(rdf, image, ct)
        ct += 1
            
    #anim = ani.ArtistAnimation(fig, stack)
    #anim.save('test.mp4', fps = 10)

##EOF
