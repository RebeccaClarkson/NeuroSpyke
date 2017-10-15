import scipy.io
import numpy as np
import pandas as pd
from spyke.sweep_calculations import current_inj_per_sweep  
from spyke.sweep_calculations import do_select_sweep_by_current_inj
from spyke.sweep_calculations import do_select_sweep_by_spike_count
from spyke.sweep_calculations import do_select_sweep_by_sweep_time
import matplotlib as mpl
from spyke.response import Response
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

    def sweep_index_iter(self):
        return range(self.nsweeps())

    def sweeps(self):
        for i in self.sweep_index_iter():
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

    def response(self, sweep_index):
        return Response(self.sweep(sweep_index))

    def responses(self):
        return [self.response(sweep_index) 
                for sweep_index in self.sweep_index_iter()]

    def sweep_time(self):
        """
        Return time after cell break-in for each sweep (in seconds)
        """
        return self.cell['sweep_time'][0, 0].flatten()
    
    def detect_spikes(self):
        return [response.spike_points() 
                for response in self.responses()]

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

    def select_sweep_by_current_inj(self, duration, amplitude):
        """
        Return sweep indices as np.ndarray for sweeps with duration/amplitude 
        input parameters.
        For returning all depol./hyperpol. current injections, amplitude = 1/-1.
        """
        all_waveforms_df = self.current_inj_waveforms()
        return do_select_sweep_by_current_inj(all_waveforms_df, duration, amplitude)
    
   
    def select_sweep_by_spike_count(self, num_spikes):
        """
        Return sweep indices as np.ndarray for sweeps that have a given number of APs
        """
        spike_counts = np.array(self.count_spikes())
        return do_select_sweep_by_spike_count(spike_counts, num_spikes)
    

    def select_sweep_by_sweep_time(self, stop_time, start_time = 0):
        """ 
        Return sweep indices as np.ndarray for sweeps that are within a certain sweep time.
        """
        return do_select_sweep_by_sweep_time(self.sweep_time(), stop_time, start_time)


