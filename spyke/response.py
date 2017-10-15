import matplotlib as mpl
mpl.use('TkAgg')
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
import matplotlib.pyplot as plt
import numpy as np

class Response(object):
    def __init__(self, sweep_df):
        self.sweep_df = sweep_df
    
    def plot_response(self, filepath):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        #ax.plot(self.sweep_df.time, self.sweep_df.data)
        ax.plot(self.sweep_df.data)
        fig.savefig(filepath)

    def spike_points(self, thresh = 20):
        above_thresh = np.where(self.sweep_df['data'][1:] > thresh)           
        below_thresh = np.where(self.sweep_df['data'][0:-1] <= thresh)
        spike_points = np.intersect1d(above_thresh, below_thresh)
        return spike_points

    def max_sweep_amplitude(self):
        return max(self.sweep_df['data'])
