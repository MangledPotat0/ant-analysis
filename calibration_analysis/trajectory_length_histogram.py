import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

px6data = pd.read_csv('../../data/trajectories/6px/trajectory_lengths.csv')
px8data = pd.read_csv('../../data/trajectories/8px/trajectory_lengths.csv')
px10data = pd.read_csv('../../data/trajectories/10px/trajectory_lengths.csv')

df_by_fps = []
framerates = [10, 13, 16, 19, 22, 25]
for framerate in framerates:
    df_by_fps.append(px6data.loc[px6data['fps']==framerate])
    df_by_fps[-1] = df_by_fps[-1].append(px8data.loc[px8data['fps']==framerate],
                                        ignore_index=True)
    df_by_fps[-1] = df_by_fps[-1].append(px10data.loc[px10data['fps']==framerate],
                                        ignore_index=True)
    print(df_by_fps[-1].head())

    sns.histplot(x='trajectory length (frames)', hue='resolution', cumulative=False,
                stat='density', common_norm=False, element='step', fill=False,
                log_scale=False, data = df_by_fps[-1])
    plt.savefig('fps={}_hist.png'.format(framerate))
    plt.close()


sns.histplot(x='trajectory length (frames)', hue='fps', cumulative=True,
            stat='density', common_norm=False, element='step', fill=False,
            log_scale=False, data = px6data)
plt.savefig('px6_hist.png')
plt.close()

sns.histplot(x='trajectory length (frames)', hue='fps', cumulative=True,
            stat='density', common_norm=False, element='step', fill=False,
            log_scale=False, data = px8data)
plt.savefig('px8_hist.png')
plt.close()

sns.histplot(x='trajectory length (frames)', hue='fps', cumulative=True,
            stat='density', common_norm=False, element='step', fill=False,
            log_scale=False, data = px10data)
plt.savefig('px10_hist.png')
plt.close()

#EOF
