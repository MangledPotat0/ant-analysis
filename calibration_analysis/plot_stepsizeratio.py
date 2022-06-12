import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

dframe = pd.read_csv('size_ratio.csv')

dframe['ratio'] = dframe['step size'] / dframe['ant size']

dframe = dframe[dframe['ratio'] < 1]

dframe = dframe[dframe['ratio']>0.00000001]

sns.histplot(x='ratio', log_scale=True, stat='density', hue='framerate',
             fill=False, element='step', data=dframe)
plt.savefig('size_ratio')
plt.close()

filtered = dframe[dframe['ratio']>0.02]

sns.histplot(x='ratio', log_scale=True, stat='density', hue='framerate',
            fill=False, element='step', data=filtered)
plt.savefig('size_ratio_filtered')
plt.close()
