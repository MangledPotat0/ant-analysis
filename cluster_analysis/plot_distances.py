import argparse
import h5py
import json
import matplotlib.animation as ani
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns

# TODO: The path management looks sketchy, check that it works in unix env

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = os.path.dirname(str(paths['datapath']+
                               '\\clustering_data\\10px\\a')) + '\\'


# Extract the upper triangle of the distance matrix to eliminate redundancy
# since distance in the metric space is symmetric. Then, flatten the nonzero
# elements into a list and return it.

def convert_to_list(distance_matrix):
    upper = np.triu(distance_matrix)
    flattened_list = upper.flatten()
    sieved = flattened_list[flattened_list != 0]

    return sieved


def generate_figure(values1d, ct):
    dframe = pd.DataFrame(data=values1d, columns=['distances (px)'])
    ax = sns.displot(dframe, x='distances (px)')
    plt.title('frame={}'.format(ct))
    plt.savefig('fig.png', bbox_inches='tight')
    plt.close

    return


if __name__=="__main__":
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required=True,
                    help = 'data file name')

    args = vars(ap.parse_args())

    with h5py.File(str(datapath + args['file']), 'r') as dfile:
        distance_matrices = dfile['matrix'][:]
    
    # Generate plot stack through time
    
    ct = 0
    for distance_matrix in distance_matrices:
        distance_list = convert_to_list(distance_matrix)
        generate_figure(distance_list, ct)
        ct += 1
##EOF
