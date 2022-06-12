################################################################################
#                                                                              #
#   Date Created: 2022/04/12                                                   #
#   Last modified: 2022/05/09                                                  #
#                                                                              #
################################################################################

import argparse as ape
import glob
import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Load the trajectory data
def load_data(filename):
    with h5py.File(filename, 'r') as dfile:
        data = dfile['tracks'][:]
    return data

def count_trajectories(tracks):

    return np.shape(tracks)[0]


def count_instances(tracks):
    shape = np.shape(tracks)
    instance_counts = []

    # Count instances per frame
    for frame in range(shape[3]):
        booleanized = tracks[:,:,:,frame] ** 2 > -1
        rawcount = np.sum(booleanized)
        instance_count = rawcount / (shape[1] * shape[2])
        instance_counts.append(instance_count)
    instance_counts = np.array(instance_counts)
    
    '''lengths = []
    for track in tracks:
        lengths.append(int(shape[3] - np.sum(np.isnan(track))/6))

    df = pd.DataFrame(data={
                    'fps': int(shape[3] / 120),
                    'resolution': 0,
                    'trajectory length (frames)': lengths})
    df.to_csv('trajectory_lengths.csv', mode='a', index=False, header=False)
    '''
    return instance_counts, shape[3]

# Turn the data into a fraction of maximally tolerable value
def make_fraction(values, maximum_tolerable_value):
    fraction = values / fraction
    return fraction


if __name__ == '__main__':

    ap = ape.ArgumentParser()
    ap.add_argument('-f', '--file', required=True, help = 'Data file')
    ap.add_argument('-tt', '--target_trajectories', required=True, type=int,
                    help = 'target trajectory count')
    ap.add_argument('-ti', '--target_instances', required=True, type=int,
                    help = 'Target instance count')
    args = vars(ap.parse_args())
    for dfile in glob.glob(args['file']):
        data = load_data(dfile)
        trajectory_count = count_trajectories(data)
        instance_counts, frames = count_instances(data)

        difference = instance_counts - args['target_trajectories']
        absdiff = abs(difference)

        print('filename: ',dfile)
        print('trajectory count error: ', 
                trajectory_count - args['target_trajectories'])
        print('instance count error: ', np.sum(absdiff))

# EOF
