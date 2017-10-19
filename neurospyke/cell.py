import scipy.io
import numpy as np
import pandas as pd
from neurospyke.sweep import Sweep


class Cell(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.mat = scipy.io.loadmat(file_path)
        self.cell = self.mat['Cell']
        self.descriptive_cell_properties = ['genetic_marker', 'ca_buffer'] 
        self._cache = {}

    def cell_property_names(self):
        return self.descriptive_cell_properties + self.query.cell_properties 

    def calc_or_read_from_cache(self, attr_name):
        if not attr_name in self._cache:
            fn = getattr(self, f"calc_{attr_name}")
            value = fn()
            self._cache[attr_name] = value
        return self._cache[attr_name]

    def debug_cache(self):
        print(f"Cache has {len(self._cache)} items.")
        for key, value in self._cache.items():
            print(f"key: {key} value: {value}")

    def response_properties_df(self):
        """
        This method returns a dataframe with one row per response.
        """
        results_df = None
        for sweep in self.sweeps():
            result_tmp_df = sweep.run()
            if result_tmp_df is not None:
                if results_df is None:
                    results_df = result_tmp_df
                else:
                    results_df = pd.concat([results_df, result_tmp_df])
        return results_df

    def calc_mean_response_properties_df(self):
        """
        This method returns a single row dataframe that has the mean values for
        all response_properties. It uses a dataframe that has one row per
        response.
        """
        response_df = self.response_properties_df()
        if response_df is not None:
            mean_series = response_df.mean()
            mean_response_df = pd.DataFrame(
                    [list(mean_series.values)], columns=list(mean_series.index), 
                    index=[self.calc_cell_name()]
                    )
        else: 
            mean_response_df=None
        return mean_response_df

    def calc_cell_properties_df(self):
        """
        Returns a single row dataframe with all Cell properties, including both
        descriptive and calculated properties.
        """
        property_names = self.cell_property_names()
        property_dict = {}
        for property_name in property_names:
            property_dict[property_name] = self.calc_or_read_from_cache(property_name)
        cell_properties_df = pd.DataFrame(property_dict, index=[self.calc_cell_name()])
        return cell_properties_df[property_names] 

    def combine_dfs(self, df1, df2):
        if df1 is None:
            return df2
        elif df2 is None:
            return df1
        else:
            return pd.concat([df1, df2],axis=1, join_axes=[df1.index])

    def run(self):
        """
        This method returns a dataframe with a single row that has all the
        averaged response_properties data and the calculated cell_properties
        data.
        """
        return self.combine_dfs(
                self.calc_cell_properties_df(),
                self.calc_mean_response_properties_df())

    def calc_cell_name(self):
        return self.cell['name'][0, 0][0]

    def calc_genetic_marker(self):
        return self.cell['genetic_marker'][0,0][0]

    def calc_ca_buffer(self):
        return self.cell['CaBuffer'][0,0][0]

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
        return Sweep(self.sweep_df(sweep_index), self)

    def sweeps(self):
        for i in self.sweep_index_iter():
            yield self.sweep(i)

    def calc_sag_amplitude(self):
        # TODO 
        return 1

    def calc_reb_delta_t(self):
        # TODO
        return 5
