import scipy.io
import numpy as np
import pandas as pd
from spyke.sweep_calculations import current_inj_per_sweep
import matplotlib as mpl
mpl.use('TkAgg')
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

import matplotlib.pyplot as plt

np.set_printoptions(precision = 2, linewidth = 40, suppress = True)

class Cell(object):

    def __init__(self, filename):
        self.filename = filename
        self.mat = scipy.io.loadmat(filename)
        self.cell = self.mat['Cell']

    def time(self):
        return self.cell['time'][0,0].T

    def data(self):
        return self.cell['data'][0,0].T

    def commands(self):
        return self.cell['commands'][0, 0].T

    def nsweeps(self):
        return np.shape(self.data())[0]

    def sweeps(self):
        for i in range(self.nsweeps()):
            yield self.sweep(i)

    def sweep(self, sweep_index):
        """
        Return specific values for given sweep# as a dataframe (time, data, commands).
        """
        time = self.time()[sweep_index,:]
        data = self.data()[sweep_index,:]
        commands = self.commands()[sweep_index,:]
        return pd.DataFrame(data = {
            'sweep_index':sweep_index,
            'time':time,
            'data':data, 
            'commands':commands
            })

    def sweep_time(self):
        """
        Return time after cell break-in for each sweep (in seconds)
        """
        return self.cell['sweep_time'][0, 0].flatten()
    
    def detect_spikes(self):
        thresh = 20

        def spike_points(sweep):
            above_thresh = np.where(sweep[1:] > thresh) 
            below_thresh = np.where(sweep[0:-1] <= thresh)
            spike_points = np.intersect1d(above_thresh, below_thresh)
            return spike_points

        return [spike_points(sweep) for sweep in self.data()]

    def count_spikes(self):
        return [len(spikes) for spikes in self.detect_spikes()]

    def current_inj_waveforms(self):
        """
        Return dataframe containing current inj. params (all sweeps)
        Assumes all data in current clamp.  
        """
        all_dfs_in_list = [current_inj_per_sweep(sweep_df) 
                for n, sweep_df in 
                enumerate(self.sweeps())]
        command_waveform_df = pd.concat(all_dfs_in_list)
        return command_waveform_df 

    # all selection functions being passed ..
    def select_sweep_by_current_inj(self, duration, amplitude):
        """
        Return sweep indices for sweeps with duration/amplitude input parameters.
        For returning all depol./hyperpol. current injections, amplitude = 1/-1.
        """
        all_waveforms_df = self.current_inj_waveforms()
        duration_bool = np.isclose(all_waveforms_df['offset_time'] 
                - all_waveforms_df['onset_time'], duration, 1e-5)

        if amplitude == 1: # depolarizing current injections
            amplitude_bool = np.greater(all_waveforms_df['amplitude'], 0).as_matrix()
        elif amplitude == -1: # hyperpolarizing current injections
            amplitude_bool = np.less(all_waveforms_df['amplitude'], 0).as_matrix()
        else:
            amplitude_bool = np.isclose(all_waveforms_df['amplitude'] , amplitude, 1e-5)
            
        select_df = all_waveforms_df.loc[duration_bool & amplitude_bool]
        sweep_index = select_df['sweep_index']
        return np.array(sweep_index)
    
    def select_sweep_by_spike_count(self, num_spikes):
        """
        Return sweep indices as np.array for sweeps that have a given number of APs
        """
        spike_counts = np.array(self.count_spikes())
        return np.where(spike_counts == num_spikes)[0]

    def select_sweep_by_sweep_time(self, stop_time, start_time = 0):
        after_start_idx = np.where(self.sweep_time() > start_time)
        before_stop_idx = np.where(self.sweep_time() < stop_time)
        return np.intersect1d(after_start_idx, before_stop_idx) 
    # move above to separate module 

    def plot_sweeps(self, sweep_indices, filepath):
        """Plot sweep with given sweep indices, save to filepath"""

        fig, (ax1, ax2) = plt.subplots(2, sharex=True)

        for sweep_index in sweep_indices:
            sweep_index = int(sweep_index)
            sweep_df = self.sweep(sweep_index)
            ax1.plot(sweep_df.time, sweep_df.data)
            ax2.plot(sweep_df.time, sweep_df.commands)
    
        # set labels
        ax1.set(title = f"sweep #{sweep_indices}")
        ax1.set_ylabel('mV'); 
        ax2.set_xlabel('time (s)'); ax2.set_ylabel('pA')
        
        # set axes limits
        ax1.set_xlim([0, 1]); ax1.set_ylim([-150, 50])
        ax2.set_ylim([-400, 250])

        # save figure
        fig.savefig(filepath)
