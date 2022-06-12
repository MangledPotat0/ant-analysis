################################################################################
#                                                                              #
#   Date Created: 2022/05/10                                                   #
#   Last modified: 2022/05/10                                                  #
#                                                                              #
################################################################################


import argparse as ape
import h5py
import glob
import numpy as np
import pandas as pd

def load_data(filename):
    with h5py.File(filename, 'r') as dfile:
        data = dfile['tracks'][:]

    return data


def get_ant_size(data):
    diff = data[:,:,0,1:] - data[:,:,2,1:]
    length = np.linalg.norm(diff, axis=1)

    return length.flatten()


def get_step_size(data):
    diff = data[:,:,1,1:] - data[:,:,1,:-1]
    stepsize = np.linalg.norm(diff, axis=1)

    return stepsize.flatten()


if __name__ == '__main__':
    
    ap = ape.ArgumentParser()
    ap.add_argument('-f', '--file', required=True, help='Data file')
    ap.add_argument('-fps', '--framerate', required=True, help='Framerate')
    
    args = vars(ap.parse_args())

    for dfile in glob.glob(args['file']):
        data = load_data(dfile)
        ant_size = get_ant_size(data)
        step_size = get_step_size(data)
        dframe = pd.DataFrame(data={'framerate': np.full(len(ant_size),
                                                args['framerate']),
                                    'ant size': ant_size,
                                    'step size': step_size
                                    })
        dframe.to_csv('size_ratio.csv', mode='a', index=False, header=False)

#EOF
