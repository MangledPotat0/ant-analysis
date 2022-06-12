################################################################################
#                                                                              #
#   Created: 2022/05/30                                                        #
#   Last Modified: 2022/05/30                                                  #
#                                                                              #
################################################################################

import h5py
import numpy as np


def compute_distances(positions):

    distances = np.array([])
    for position in positions:
        
        distance = positions - np.fill(position, len(positions) - 1)
        distances = np.append(distances, distance)
        


if __name__ == '__main__':
    print('doo')

# EOF
