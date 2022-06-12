################################################################################
#                                                                              #
#   Created: 2022/06/12                                                        #
#   Last modified: 2022/06/12                                                  #
#                                                                              #
################################################################################

import argparse as arg
import h5py
import numpy as np

def load_trajectories(fname):
    trajectories = np.array([])
    with h5py.File(fname, 'r') as dfile:
        keys = dfile.keys()











if __name__ == '__main__':
    ap = arg.ArgumentParser()
    ap.add_argument('-f', '--file', required=True,
                    help='Data file')
    args = vars(ap.parse_args())

    trajectories = load_trajectories(args['file'])

# EOF
