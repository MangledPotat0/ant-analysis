################################################################################
#                                                                              #
#   Created: 2022/06/12                                                        #
#   Last modified: 2022/06/13                                                  #
#                                                                              #
################################################################################

import argparse as arg
import h5py
import numpy as np
import scipy.spatial as sp

project_path = 'C:/Users/user/Desktop/Coding/ant/'
data_path = str(project_path+'data/trajectories/')
output_path = str(project_path+'data/clustering_data/')

def load_trajectories(fname):
    with h5py.File('{}.hdf5'.format(fname), 'r') as dfile:
        keys = dfile.keys()
        length = max(len(dfile[key]) for key in keys)
        trajectories = np.full((len(keys),length,4,2), 0, dtype=float)
        ct = 0
        for key in keys:
            trajectory = dfile[key]
            trajectories[ct,:len(trajectory)] = trajectory[:]
            ct += 1
    
    return trajectories


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
    ap.add_argument('-f', '--file', required=True,
                    help='Data file')
    args = vars(ap.parse_args())

    trajectories = load_trajectories("{}{}".format(data_path,args['file']))

    distances = compute_distances(trajectories)

    with h5py.File('{}{}_distance_matrices.hdf5'.format(output_path,
                                            args['file']), 'w') as outfile:
        outfile.create_dataset('matrix', data = distances)

# EOF
