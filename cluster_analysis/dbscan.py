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

mlem='mlem'

# Usage example taken from:
# https://scikit-learn.org/stable/modules/clustering.html#dbscan

# Knee location example taken from:
# https://towardsdatascience.com/how-to-use-dbscan-effectively-ed212c02e62
# While the above method works ok a more effective alternative should be found
# because using the above method at every frame results in wildly varying cutoff

# Reference for general information: 'Cluster Analysis and Application'
# (isbn: 9783030745523)


# configuring paths

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']

today = date.today()
today = today.strftime('%Y%m%d')

outputpath = str(datapath + 'processed/cluster_dbscan/')
figspath = str(datapath + 'processed/cluster_dbscan/' + today + '/')

# Attempt to create the directories
try:
    os.mkdir(outputpath)
except OSError:
    pass

try:
    os.mkdir(figspath)
except OSError:
    pass


# Search for the distances to n nearest neighbors for each ants. This distance
# is needed to perform the unsupervised knee location.

# Input:
#  frameset    | pandas DataFrame object containing all coordinates used for
#              | clustering.
#  min_samples | int, number of nearest neighbors to find

# output:
#  distances   | numpy Array() object containing list of distances from ant to
#              | its neighbors

# The function call in the __main__ is currently disabled because of the above
# issue with using knee locator.

def find_nearest_neighbors(frameset, min_samples):
    nearest_neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors = nearest_neighbors.fit(frameset)
    distances, indices = neighbors.kneighbors(frameset)

    distances = np.sort(distances[:,min_samples-1], axis=0)
    
    return distances


# Use the distances from find_nearest_neighbors() to find the knee position.
# The function call in the __main__ is currently disabled because of the above
# issue with using knee locator.

# Input:
#  distances | numpy array object from find_nearest_neighbors()
#  t         | int frame label
#  stride    | int, number of steps to skip between knee plots

# Output:
#  knee      | float value indicating distance to the knee position

def locate_knee_point(distances, t, stride):
    idx = np.arange(len(distances))
    # Compute the index of the knee position 
    knee_ = kneed.KneeLocator(idx, distances, S=1, curve='convex',
                             direction='increasing', interp_method='polynomial')

    # Generate the knee (elbow) plot at every 'stride' steps
    if t % stride == 0:
        sns.lineplot(data=distances)
        knee_.plot_knee()
        plt.xlabel('points')
        plt.ylabel('distance (px)')
        plt.savefig('{}distances_{}.png'.format(figspath,t))
        plt.close()

    # Find the distance corresponding to the knee
    knee = distances[knee_.knee]

    return knee


# Feed input data to perform clustering using DBSCAN and generate figure

# Input:
#  frame     | numpy Array object holding the frame (image)
#  frameset  | pandas DataFrame object containing coordinates for clustering
#  eps       | float, epsilon (size of the 'neighborhood' that DBSCAN uses to
#            | search for other instances)
#  vidwriter | cv2.VideoWriter buffer where the frames are saved

# Output:
#  None (tagged frames are saved to the buffer instead of being returned. An
#  output pandas DataFrame should later be added where frameset is augmented
#  with the cluster number assigned to the ant)

def perform_dbscan(frame, frameset, eps, vidwriter):
    npfy = frameset.to_numpy()[:,-2:]
    # min_samples=3 is used because the ant trajectory data has three body
    # segments which are independently considered for clustering
    db = cluster.DBSCAN(eps=eps, min_samples=3).fit(npfy)
    # Extract core samples, this is technically not necessary right now since
    # the distinction between core sample and peripheral samples is not used for
    # the analysis.
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Augment the frame image with markers indicating cluster membership of
    # each coordinate pair. The choice of DPI and figsize needs to be tuned
    # to correctly align the legends. I think this is dependent on code user's
    # display resolution.
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


# Takes the dataframe with three x-y pairs in their own columns and stack them
# into two columns for x and y

# Input:
#  dframe | pandas DataFrame object containing the coordinates of body parts

# Output:
#  combined | pandas DataFrame object where the x,y coordinates are all stacked
#           | into the same columns regardless of body part designation.

def stack_coordinates(dframe):
    combined = pd.DataFrame()
    for part in ['head', 'thorax', 'abdomen']:
        copy = dframe.to_dict()
        coords = ['x','y']
        newdict = {}
        for coord in coords:
            newdict[coord] = {}
            ref = list(copy['{}_{}'.format(part,coord)].keys())
            for pair in ref:
                newID = (pair[0],
                         pair[1],
                         part)
                newdict[coord][newID] = copy['{}_{}'.format(part,coord)][pair]
        newf = pd.DataFrame.from_dict(newdict)

        if newf.empty:
            emptydict = {'x':{(0,1,2):0},'y':{(0,1,2):0}}
            newf = pd.DataFrame.from_dict(emptydict)
        newf.index.names = ['frame', 'antID', 'part']
        combined = combined.append(newf)
    combined = combined.sort_index()

    return combined


if __name__ == '__main__':
    # Input handling and initialization
    ap = argparse.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True,
                    help='Data file name')
    args = vars(ap.parse_args())
    expid = args['expid']
    dtable = pd.read_hdf('{}/preprocessed/{}/{}_active_ants.hdf5'.format(
                            datapath, expid, expid))
    vidstream = cv.VideoCapture('{}/preprocessed/{}/{}corrected.mp4'.format(
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


    # Main loop performing DBSCAN frame by frame
    for t in range(maxframe):
        readable, frame = vidstream.read()
        if (t % 1 == 0) && readable:
            frameset = pd.DataFrame()
            ct = 0
            # Extract instances corresponding to the current frame
            try:
                instance = dtable[dtable['frame']==t+1]
                inactive = instance[instance['state']=='inactive']
                position = inactive.drop(['orientation', 'state'], axis=1)
                position.dropna(inplace=True)
                
                position = position.set_index(['frame','antID'])

                position = stack_coordinates(position)
                position = position.reset_index()
                frameset = frameset.append(position, ignore_index=True)
                
            except IndexError:
                print('Warning: IndexError. ',
                      'Likely means a missing instance.')

            ct += 1
            # Perform knee location and DBSCAN
            if np.size(frameset.to_numpy()) != 0:
                #nearest = find_nearest_neighbors(frameset, min_samples, t)
                eps = 90#locate_knee_point(nearest, t)
                perform_dbscan(frame, frameset, eps, t, out)
            else:
                pass
            
    out.release()


# EOF
