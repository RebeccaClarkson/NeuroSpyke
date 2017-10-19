# set up module defaults across project

import numpy as np
print("Setting defualts for numpy")
np.set_printoptions(precision=2, linewidth=40, suppress=True)

import matplotlib as mpl
print("Setting defualts for matplotlib") 
mpl.use('TkAgg')
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

import pandas as pd
print("Settings defaults for pandas")
pd.set_eng_float_format(accuracy=2, use_eng_prefix=True)
