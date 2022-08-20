################################################################################
################################################################################

import sys
sys.path.append('..\\common')

import argparse
from datetime import date
import h5py
import json
from matplotlib import pyplot
import numpy as np
import os
import pandas as pd
import seaborn as sns

from datahandler import TrajectoryData
import logmaker as lm

with open('../paths.json','r') as f:
    paths = json.load(f)
    codepath = paths['codepath']
    datapath = paths['datapath']


today = date.today()
today = today.strftime('%Y%m%d')

outputpath = str(datapath + 'processed\\state_tracking\\')
figspath = str(datapath + 'processed\\state_tracking\\' + today + '\\')

try:
    os.mkdir(outputpath)
    os.mkdir(figspath)
except:
    pass


if __name__ == '__main__':

    print('mlem')


# EOF
