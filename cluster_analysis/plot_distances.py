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


# Setting paths
with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']

today = date.today()
today = today.strftime('%Y%m%d')

outputpath = str(datapath + 'processed/distance_plots/')
figspath = str(datapath + 'processed/distance_plots/' + today + '/')

# Attempt to create the directories
try:
    os.mkdir(outputpath)
except OSError:
    pass

try:
    os.mkdir(figspath)
except OSError:
    pass


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
    g = sns.lineplot(data=dframe, ax=splt[1])

    plt.title('frame={}'.format(ct))
    g.set_xlim(0,200)
    g.set_ylim(0,0.007)
    plt.savefig('plot{}.png'.format(ct),
                bbox_inches='tight')
    plt.close()
    
    return


if __name__=="__main__":
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True,
                    help = 'Experiment ID')

    args = vars(ap.parse_args())
    expid = args['expid']

    with h5py.File('{}{}/{}_distance_matrices.hdf5'.format(
                                datapath,expid,expid), 'r') as dfile:
        distance_matrices = dfile['matrix'][:]

    vidstream = cv.VideoCapture('{}{}/{}corrected.mp4'.format(
                                            datapath,expid,expid))
    
    # Generate plot stack through time
    
    stride = 250
    ct = 0

    stack = []
    fig = plt.figure(figsize=(5.5, 5.5))
    # unpack the distance matrix and turn it into a radial distribution
    # function plot
    for distance_matrix in distance_matrices:
        _, image = vidstream.read()
        if ct % stride == 0:
            distance_list = convert_to_list(distance_matrix)
            rdf = radial_distribution(distance_list, 10)
            generate_figure(rdf, image, ct)
        ct += 1

            
##EOF
