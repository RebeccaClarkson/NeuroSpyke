import scipy.io
import numpy as np
import pandas as pd
from neurospyke.sweep import Sweep

np.set_printoptions(precision = 2, linewidth = 40, suppress = True)

class Cell(object):

    def __init__(self, filename, experiment=None, property_names=None):
        self.filename = filename
        self.mat = scipy.io.loadmat(filename)
        self.cell = self.mat['Cell']
        self.experiment = experiment
         
        if not property_names:
            try:
                self.property_names = self.experiment.property_names
            except Exception as e:
                assert "'NoneType' object has no attribute 'experiment'" in str(e)
                self.property_names = None
        else:
            self.property_names = property_names


    def run_first(self):
        results_df = pd.DataFrame()
        sweep_idx = []
        for sweep in self.sweeps():
            result_tmp = sweep.run()
            if not result_tmp.empty:
                assert result_tmp.shape[0] == 1
                results_df = pd.concat([results_df, result_tmp])
                sweep_idx.append(sweep.sweep_index())
        
        return results_df, sweep_idx
    
    def run(self):
        results_df, _ = self.run_first()
        return results_df
    
    def run_cell(self):
        initial_results_df, sweep_idx = self.run_first()
        results_df = initial_results_df.assign(sweep_index=sweep_idx, 
                cell_name=self.cell_name())
        return results_df

    def aggregate_result(self):
        mean_series = self.run().mean(numeric_only=True)
        mean_df = pd.DataFrame([list(mean_series.values)],columns=list(mean_series.index))
        mean_df_full = mean_df.assign(cell_name=self.cell_name())
        return(mean_df_full)

    def cell_name(self):
        return self.cell['name'][0, 0][0]

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
        return Sweep(self.sweep_df(sweep_index), self, property_names=self.property_names)

    def sweeps(self):
        for i in self.sweep_index_iter():
            yield self.sweep(i)

