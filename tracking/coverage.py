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

    radius = 5

    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True,
                    help='Data file name')
    ap.add_argument('-v', '--video',
                    help='Video file name')

    args = vars(ap.parse_args())

    dfile = hdf5.File('{}{}.hdf5'.format(datapath, args['file']), 'r')
    vfile = cv.VideoCapture('{}{}.mp4'.format(vidpath, args['video']))

    ret, frame = vfile.read()

    ct = 0
    while ret:
        img_shape = np.shape(frame)[:1]
        array_shape = img_shape/10
        covered = np.full(array_shape, False)
        for key in dfile.keys():
            trajectory = dset[key][:]
            idx = np.where(trajectory[:,0,0] == ct)
            positions = trajectory[idx]
            head = positions[1]
            overwrite = coverage(img_shape, array_shape, head, radius)
            covered += overwrite
            
        ret, frame = vfile.read()
        ct += 1

            
            

        

# EOF
