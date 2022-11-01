import argparse as arg
import h5py
import json
import numpy as np
import scipy.spatial as sp

mlem = 'mlem'


# Setting up paths
with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']

src = str(datapath + 'preprocessed' + '/')


# Load trajectory data from file, return numpy Array object

def load_trajectories(fname):
    with h5py.File('{}{}/{}_proc.hdf5'.format(srcpath,fname,fname),
                                                        'r') as dfile:
        keys = dfile.keys()
        length = max(len(dfile[key]) for key in keys)
        trajectories = np.full((len(keys),length,4,2), 0, dtype=float)
        ct = 0
        for key in keys:
            trajectory = dfile[key]
            trajectories[ct,:len(trajectory)] = trajectory[:]
            ct += 1
    
    return trajectories


# Find pairwise distance for every ants and return the distances as a square
# matrix. Note that the diagonal elements should all be 0.

def compute_distances(trajectories):
    n = len(trajectories)
    time = max([traj[-1, 0, 0] for traj in trajectories])
    distance_matrices = []
    for t in range(int(time)):
        distance_matrix = sp.distance_matrix(trajectories[:,t,2],
                                             trajectories[:,t,2])
        distance_matrices.append(distance_matrix)

    return distance_matrices


if __name__ == '__main__':
    ap = arg.ArgumentParser()
    ap.add_argument('-id', '--expid', required=True,
                    help='Data file')
    args = vars(ap.parse_args())
    expid = args['expid']

    trajectories = load_trajectories("{}{}/{}".format(src, expid, expid))

    distances = compute_distances(trajectories)

    with h5py.File('{}{}/{}_distance_matrices.hdf5'.format(src, expid, expid),
                   'w') as outfile:
        outfile.create_dataset('matrix', data = distances)

# EOF
