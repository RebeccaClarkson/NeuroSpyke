import matplotlib as mpl
mpl.use('TkAgg')
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
import matplotlib.pyplot as plt
import numpy as np

class Response(object):
    def __init__(self, sweep_df, cell=None):
        self.sweep_df = sweep_df
        self.cell = cell

    def meets_criteria(self):
        return True



    def spike_points(self, thresh = 20):
        #thresh = self.experiment.criteria.thresh
        above_thresh = np.where(self.sweep_df['data'][1:] > thresh)           
        below_thresh = np.where(self.sweep_df['data'][0:-1] <= thresh)
        spike_points = np.intersect1d(above_thresh, below_thresh)
        return spike_points

    def max_sweep_amplitude(self):
        return max(self.sweep_df['data'])

    def data(self):
        properties = self.experiment.properties
        return []

    def plot(self, filepath):

        fig, (ax1, ax2) = plt.subplots(2, sharex=True)
        ax1.plot(self.sweep_df.time, self.sweep_df.data)
        ax2.plot(self.sweep_df.time, self.sweep_df.commands)

        # set labels
        print(self.sweep_df.head())
        ax1.set(title = f"sweep #{self.sweep_df.sweep_index[0]}")
        ax1.set_ylabel('mV'); 
        ax2.set_xlabel('time (s)'); ax2.set_ylabel('pA')
        
        # set axes limits
        ax1.set_xlim([0, 1]); ax1.set_ylim([-150, 50])
        ax2.set_ylim([-400, 250])

        # save figure
        fig.savefig(filepath)
