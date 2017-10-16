import scipy.io
import numpy as np
import pandas as pd
from spyke.sweep import Sweep

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

    def sweep_times(self):
        """
        Return time after cell break-in for each sweep (in seconds)
        """
        return self.cell['sweep_time'][0, 0].flatten()

    def sweep_time(self, sweep_index):
        return self.sweep_times()[sweep_index]

    def sweep_df(self, sweep_index):
        """
        Return specific values for given sweep# as a dataframe (time, data, commands).
        """
        time = self.time()[sweep_index,:]
        data = self.data()[sweep_index,:]
        commands = self.commands()[sweep_index,:]
        sweep_time = self.sweep_time(sweep_index)
        return pd.DataFrame(data = {
            'sweep_index':sweep_index,
            'sweep_time':sweep_time,
            'time':time,
            'data':data, 
            'commands':commands
            })

    def sweep(self, sweep_index):
        """ Create Sweep object for given sweep# """
        return Sweep(self.sweep_df(sweep_index))

    def sweeps(self):
        for i in self.sweep_index_iter():
            yield self.sweep(i)
