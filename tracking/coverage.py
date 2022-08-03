################################################################################
################################################################################


import argparse
import h5py
import json
import numpy as np
import pandas as pd
import seaborn as sns


with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\trajectories\\clustering\\'))+'\\'
    videopath = os.path.dirname(str(paths['datapath']+
                                '\\videos\\clustering\\'))+'\\'

# img_shape, array_shape -> [h,w] (np array)
# ant = (1, 2) np array

def coverage(img_shape, array_shape, head, radius):
    cover = np.full(array_shape, False)
    binsizes = img_shape / array_shape
    headbins = np.flip(head) // binsizes
    headbins = headbins.astype(int)
    
    y, x = np.ogrid[:array_shape[0],:array_shape[1]]
    distance_from_head = np.sqrt((x - headbins[1])**2 + (y - headbins[0])**2)
    mask = distance_from_head <= radius

    cover[mask] = True

    return cover


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True, nargs='+',
                    help='Data file name')
    ap.add_argument('-v', '--video', nargs='+',
                    help='Video file name')

    args = vars(ap.parse_args())
        

