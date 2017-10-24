import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
class Response(object):
    def __init__(self, curr_inj_params, sweep, response_properties=None, response_critiera=None):
        self.onset_pnt = int(curr_inj_params['onset_pnt'])
        self.offset_pnt = int(curr_inj_params['offset_pnt'])
        self.onset_time = curr_inj_params['onset_time']
        self.offset_time = curr_inj_params['offset_time']
        self.amplitude = curr_inj_params['amplitude']
        self.sweep = sweep
        self._cache = {}

    
    def data(self):
        return self.sweep.sweep_df['data']

    def time(self):
        return self.sweep.sweep_df['time']

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

    def meets_criterion(self, criterion):
        attr_name, condition = criterion
        value = self.calc_or_read_from_cache(attr_name)
        if isinstance(condition, str):
            # process condition of string
            # TODO implement
            raise Exception("TODO")
        else:
            # use simple equality
            return np.isclose(value, condition)

    def meets_criteria(self):
        if hasattr(self.sweep.cell, 'query'):
            criteria = self.sweep.cell.query.response_criteria
        else: 
            criteria = self.sweep.cell.response_criteria

        return all(self.meets_criterion(criterion)
                for criterion in criteria.items())

    def calc_properties(self, property_names):
        property_dict = {}
        for property_name in property_names:
            property_value = self.calc_or_read_from_cache(property_name)
            if isinstance(property_value, np.ndarray):
                tmp_dict = {f"{property_name}{i}":item for i, item in enumerate(property_value)}
            else:
                tmp_dict = {property_name: property_value}
            property_dict.update(tmp_dict)
        return property_dict 

    def run(self):
        """ 
        Returns a one row dataframe with data for all response_properties.
        """
        if hasattr(self.sweep.cell, 'query'):
            response_properties = self.sweep.cell.query.response_properties
        else:
            response_properties = self.sweep.cell.response_properties

        results_dict = self.calc_properties(response_properties)
        return pd.DataFrame([results_dict])

    def calc_curr_duration(self):
        return self.offset_time - self.onset_time

    def calc_curr_amplitude(self):
        return self.amplitude

    def calc_points_per_ms(self):
        """Calculate data acquisition sampling rate, in points per ms"""
        delta_t_sec = self.sweep.time()[1]- self.sweep.time()[0]
        points_per_ms = 1/(delta_t_sec * 1000) 
        return int(points_per_ms)

    def window(self, left_window=50, right_window=50):
        """
        Returns a dataframe of the sweep_df format with only the specified
        response window.  Left and right are how far the window should extend
        from the current injection (in ms)
        """
        points_per_ms = self.calc_or_read_from_cache('points_per_ms')
        
        
        window_onset_pnt = int(self.onset_pnt - left_window*points_per_ms)
        window_offset_pnt = int(self.offset_pnt + right_window*points_per_ms)

        if window_onset_pnt < 0:
            raise Exception("Left window too big")
        if window_offset_pnt > len(self.sweep.sweep_df.index):
            raise Exception("Right window too big")

        window_df = self.sweep.sweep_df[window_onset_pnt:window_offset_pnt]
        window_df = window_df.reset_index(drop=True)
        window_df['time'] = window_df['time'] - window_df['time'][0] 
        
        return window_df

    def calc_spike_points(self):
        """ Calculates points where spikes occur (defined by voltage going  > -10 mV) """
        thresh = -10
        above_thresh = np.where(self.sweep.data()[1:] > thresh)           
        below_thresh = np.where(self.sweep.data()[0:-1] <= thresh)
        spike_points = np.intersect1d(above_thresh, below_thresh)
        return spike_points

    def calc_num_spikes(self):
        spike_points = self.calc_or_read_from_cache('spike_points')
        return len(spike_points)
   
    def calc_APmax_idx_and_val(self):
        spike_points = self.calc_or_read_from_cache('spike_points')
        num_spikes = self.calc_or_read_from_cache('num_spikes')
        max_AP_idxs = []; max_AP_vals = []

        for i in range(num_spikes):

            if i < num_spikes-1:
                stop_idx = spike_points[i+1]
            else:
                stop_idx = self.offset_pnt

            # find max data value that occurs between spike point indices
            start_idx = spike_points[i]; 
            max_idx = np.argmax(self.sweep.data()[start_idx:stop_idx]) 
            max_val = self.sweep.data()[max_idx]
            
            # append values
            max_AP_vals.append(max_val)
            max_AP_idxs.append(max_idx)
        return max_AP_idxs, max_AP_vals

    def calc_APmax_val(self):
        _, vals = self.calc_or_read_from_cache('APmax_idx_and_val')
        return np.array(vals)

    def calc_APmax_idx(self):
        idxs, _ = self.calc_or_read_from_cache('APmax_idx_and_val')
        return np.array(idxs)

    def calc_ISIs(self):
        idxs = self.calc_or_read_from_cache('APmax_idx')
        ISI_idx = np.diff(idxs)  
        ISI_ms = ISI_idx/self.calc_or_read_from_cache('points_per_ms') 
        return(ISI_ms)

    def calc_doublet_index(self):
        return(self.calc_ISIs()[1]/self.calc_ISIs()[0]) 

    def calc_sag_amplitude(self):
        # TODO 
        pass 

    def calc_sag_steady_state_avg_amp(self):
        """
        Returns the mean value of sag steady state, defined as 10ms before
        current offset for -400 pA injections.
        """
        points_per_ms = self.calc_or_read_from_cache('points_per_ms')
        steady_state_offset_pnt = self.offset_pnt
        steady_state_onset_pnt = steady_state_offset_pnt - 10 * points_per_ms
        steady_state_vals = self.data()[steady_state_onset_pnt:steady_state_offset_pnt]
        return np.mean(steady_state_vals)
        
    def calc_max_rebound_amp(self):
        """
        Returns the max rebound amplitude after current offset within the response window.
        """
        reb_data = self.data()[self.offset_pnt:]
        return max(reb_data)

    def find_nearest_pnt_df(self, df, value):
        array = np.array(df)
        idx_array = (np.abs(array-value)).argmin()
        return df.index[0] + idx_array
        
    def calc_reb_delta_t(self):
        """
        Returns time to get from 20% to 80% of voltage change from steady state
        to maximum repolarization within response window. 
        """
        max_rebound_amp = self.calc_or_read_from_cache('max_rebound_amp')
        steady_state_avg_amp = self.calc_or_read_from_cache('sag_steady_state_avg_amp')
        rebound_amp_change = max_rebound_amp - steady_state_avg_amp
        twenty_percent_rebound_voltage = steady_state_avg_amp + rebound_amp_change * 0.20
        eighty_percent_rebound_voltage = steady_state_avg_amp + rebound_amp_change * 0.80

        reb_data = self.data()[self.offset_pnt:]
        closest_pnt20 = self.find_nearest_pnt_df(reb_data, 
                twenty_percent_rebound_voltage)
        closest_pnt80 = self.find_nearest_pnt_df(reb_data, 
                eighty_percent_rebound_voltage)

       # plt.figure()
       # x1 = self.time(); y1 = self.data()
       # x2 = self.time()[closest_pnt20:closest_pnt80]
       # y2 = self.data()[closest_pnt20:closest_pnt80]
       # plt.plot(x1, y1, x2, y2); plt.show()

        reb_delta_t = (closest_pnt80-closest_pnt20)/self.calc_or_read_from_cache('points_per_ms')
        return reb_delta_t 
