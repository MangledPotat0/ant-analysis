################################################################################
#                                                                              #
#   Date created: 4/22/2022                                                    #
#   Last modified: 4/22/2022                                                   #
#                                                                              #
################################################################################

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

if __name__ == '__main__':

    dframe = pd.read_csv('calibration_reduced.csv', index_col='id')
    vidlength = dframe['frames'] / (dframe['fps'] * 60)
    dframe['instance target'] = dframe['antcount'] * dframe['frames']
    dframe['instance error fraction'] = (dframe['instance'] 
                                            / dframe['instance target'])
    dframe['trajectory error fraction'] = (dframe['trajectory'] 
                                            / dframe['antcount'])
    dframe['trajectory error / min'] = dframe['trajectory error fraction'] / vidlength
    dframe['instance error / min'] = dframe['instance error fraction'] / vidlength
    dframe['runtime per ant (s)'] = (dframe['runtime'] / 
                                        (dframe['antcount'] * vidlength))

    sns.lineplot(x='fps', y='runtime per ant (s)', hue='resolution (px/mm)',
                 data=dframe)
    plt.savefig('runtime.png')
    plt.close()

    sns.lineplot(x='fps', y='trajectory error fraction', 
                 hue='resolution (px/mm)', data=dframe)
    plt.savefig('trajectory_error.png')
    plt.close()

    sns.lineplot(x='fps', y='instance error fraction',
                 hue='resolution (px/mm)', data=dframe)
    plt.savefig('instance_error.png')
    plt.close()

    sns.lineplot(x='resolution (px/mm)', y='instance error fraction',
                 data=dframe)
    plt.savefig('res-instance.png')
    plt.close()

    sns.lineplot(x='resolution (px/mm)', y='trajectory error fraction',
                 data=dframe)
    plt.savefig('res-trajectory.png')
    plt.close()

    sns.lineplot(x='fps', y='trajectory error / min', hue='resolution (px/mm)',
                 data=dframe)
    plt.savefig('trajectory_error_rate.png')
    plt.close()

    sns.lineplot(x='fps', y='instance error / min', hue='resolution (px/mm)',
                 data=dframe)
    plt.savefig('instance_error_rate.png')
    plt.close()

    sns.lineplot(x='resolution (px/mm)', y='instance error / min', data=dframe)
    plt.savefig('res-instance_rate.png')
    plt.close()

    sns.lineplot(x='resolution (px/mm)', y='trajectory error / min',
                 data=dframe)
    plt.savefig('res-trajectory_rate.png')
    plt.close()
# EOF
