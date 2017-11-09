from neurospyke.response import Response
from neurospyke.sweep import Sweep
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io

class Cell(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.mat = scipy.io.loadmat(file_path)
        self.cell = self.mat['Cell']
        self.descriptive_cell_properties = ['genetic_marker', 'ca_buffer'] 
        self._cache = {}

    def calc_or_read_from_cache(self, attr_name):
        """
        This method either calculates the given attribute or gets it from the
        cache if it has already been calculated.
        """
        if not attr_name in self._cache:
            fn = getattr(self, f"calc_{attr_name}")
            value = fn()
            self._cache[attr_name] = value
        return self._cache[attr_name]

    def debug_cache(self):
        print(f"Cache has {len(self._cache)} items.")
        for key, value in self._cache.items():
            print(f"key: {key} value: {value}")

    def valid_responses(self):
        self.analyzed_sweep_ids = []
        for sweep in self.sweeps():
            for response in sweep.responses():
                if response.meets_criteria():
                    # save references to analyzed sweeps for later plot/analysis
                    self.analyzed_sweep_ids.append(sweep.sweep_index())
                    yield response
 
    def analyzed_sweeps(self):
        """
        Returns all sweeps analyzed for given query.
        """
        analyzed_sweeps = []
        for sweep_id in self.analyzed_sweep_ids:
            analyzed_sweeps.append(Sweep(self.sweep_df(sweep_id), self))
        return analyzed_sweeps

####################################################################################################
################################   DESCRIPTIVE  PROPERTIES    ######################################
####################################################################################################

    def cell_property_names(self):
        return self.descriptive_cell_properties + self.query.cell_properties

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

####################################################################################################
##################################   RUN QUERY, GET DATAFRAMES  ####################################
####################################################################################################

    def run(self):
        """
        This method returns a dataframe with a single row that has all the
        averaged response_properties data and the calculated cell_properties
        data.
        """
        return self.combine_dfs(
                self.calc_cell_properties_df(),
                self.calc_mean_response_properties_df())

    def response_properties_df(self):
        df_list = [response.run() for response in self.valid_responses()]
        if len(df_list) == 0:
            return None
        else:
            return pd.concat(df_list)

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
        """
        This method returns a combined dataframe, with index values being cell names.
        """
        if df1 is None:
            return df2
        elif df2 is None:
            return df1
        else:
            return pd.concat([df1, df2],axis=1, join_axes=[df1.index])


####################################################################################################
###############################   GET AVERAGE RESPONSE SWEEP   #####################################
####################################################################################################

    def average_response(self):
        """
        Takes a mean of response data for all responses meeting the
        response_criteria, used to calculate properties which need an 'average'
        waveform.
        """
        waveforms_list = []

        consistency_dict = {}

        def verify_consistency(property_name, value):
            if property_name not in consistency_dict:
                consistency_dict[property_name] = value
            else:
                assert consistency_dict[property_name] == value
        left_window = 100
        right_window = 100

        for response in self.valid_responses():
            verify_consistency('sampling_frequency', response.calc_points_per_ms())
            verify_consistency('curr_duration', response.calc_curr_duration())
            verify_consistency('curr_amplitude', response.amplitude)

            window_df = response.window(left_window, right_window)
            window_df['sweep_index'] = np.nan
            waveforms_list.append(window_df)

        windows_df = pd.concat(waveforms_list)

        by_row_index = windows_df.groupby(windows_df.index)
        window_df_means = by_row_index.mean()
 
        pts_per_ms = response.calc_points_per_ms()
        curr_inj_params = {
                'onset_pnt': left_window * pts_per_ms,
                'offset_pnt': len(window_df_means.index) - right_window * pts_per_ms,
                'onset_time': None,
                'offset_time': None, 
                'amplitude': response.amplitude
                }
        # create 'sweep' and 'response' objects with this averaged df
        average_sweep = Sweep(sweep_df=window_df_means, cell=self)
        return Response(curr_inj_params, average_sweep)

####################################################################################################
#################################   SAG/REBOUND PROPERTIES    ######################################
####################################################################################################

    def calc_sag_onset_time(self):
        return self.average_response().calc_sag_onset_time()

    def calc_peak_sag_val(self):
        return self.average_response().calc_peak_sag_val()

    def calc_sag_abs_amplitude(self):
        return self.average_response().calc_sag_abs_amplitude()

    def calc_sag_fit_amplitude(self):
        return self.average_response().calc_sag_fit_amplitude()

    def calc_reb_delta_t(self):
        return self.average_response().calc_reb_delta_t()

####################################################################################################
########################################       PLOT         ########################################
####################################################################################################

    def sweep_plot_setup(self, filepath=None):
        fig, (ax1, ax2) = plt.subplots(2, sharex=True)

        ax1.set_ylabel('mV'); 
        ax2.set_xlabel('time (s)'); ax2.set_ylabel('pA')
        ax2.set_ylim([-450, 250])

        yield fig, (ax1, ax2)

        if filepath:
            fig.savefig(filepath, bbox_inches="tight")
        else:
            plt.show()

    def plot_sweeps(self, sweeps=None, filepath=None):

        sweeps = sweeps or self.analyzed_sweeps()
        
        for fig, (ax1, ax2) in self.sweep_plot_setup(filepath):
            x_max = 0
            for sweep in sweeps:
                ax1.plot(sweep.sweep_df.time, sweep.sweep_df.data)
                ax2.plot(sweep.sweep_df.time, sweep.sweep_df.commands)
                x_max = max([x_max, max(sweep.sweep_df.time)])
            ax1.set_xlim([0, x_max])
            ax1.spines['bottom'].set_visible(False)
            ax1.axes.get_xaxis().set_visible(False)
            ax1.set_title(self.calc_cell_name())
    
    def plot_reb_delta_t(self, filepath=None):
        return self.average_response().plot_reb_delta_t(filepath)
