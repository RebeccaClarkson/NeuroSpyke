import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
        criteria = self.sweep.cell.query.response_criteria

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
        response_properties = self.sweep.cell.query.response_properties 
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

    def calc_ms_per_point(self):
        points_per_ms = 1/self.calc_or_read_from_cache('points_per_ms')
        return points_per_ms

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

        all_spike_points_during_current_injection = all(spike_point 
                in range(self.onset_pnt, self.offset_pnt) 
                for spike_point in spike_points)
        if all_spike_points_during_current_injection: 
            return spike_points
        else:
            # if there are spikes outside of current injection, don't analyze
            return []

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
        return np.array(max_AP_idxs), np.array(max_AP_vals)

    def calc_APmax_vals(self):
        _, vals = self.calc_or_read_from_cache('APmax_idx_and_val')
        return np.array(vals)

    def calc_APmax_idxs(self):
        idxs, _ = self.calc_or_read_from_cache('APmax_idx_and_val')
        return np.array(idxs)

        
    def calc_AHP_idx_and_vals(self):
        num_spikes = self.calc_or_read_from_cache('num_spikes')
        APmax_idxs = self.calc_or_read_from_cache('APmax_idxs')
        
        AHP_idxs = []; AHP_vals = []
        for i in range(num_spikes-1):
            # find min voltage that occurs between given AP max and next AP max
            start_idx = APmax_idxs[i]
            stop_idx = APmax_idxs[i+1]
            min_idx = np.argmin(self.sweep.data()[start_idx:stop_idx])
            min_val = self.sweep.data()[min_idx]
            
            # append values
            AHP_vals.append(min_val)
            AHP_idxs.append(min_idx)
        return np.array(AHP_idxs), np.array(AHP_vals)

    def calc_AHP_vals(self):
        _, vals = self.calc_or_read_from_cache('AHP_idx_and_vals')
        return np.array(vals)

    def calc_AHP_idxs(self):
        idxs, _ = self.calc_or_read_from_cache('AHP_idx_and_vals')
        return np.array(idxs)


    def calc_dVdt_mV_per_ms(self):
        return np.gradient(self.data(), self.calc_or_read_from_cache('ms_per_point'))

    def calc_threshold_idx_and_vals(self):
        """
        Threshold is defined as the voltage after which dVdt is > 15 mV/ms
        """
        num_spikes = self.calc_or_read_from_cache('num_spikes')
        dVdt = self.calc_or_read_from_cache('dVdt_mV_per_ms')
        AP_max_idx = self.calc_or_read_from_cache('APmax_idxs')
        AHP_idx = self.calc_or_read_from_cache('AHP_idxs')  
        thresh_idxs = []; thresh_vals = [];

        for i in range(num_spikes):
            if i == 0:
                start_idx = self.onset_pnt
            else: 
                start_idx = AHP_idx[i-1]
            stop_idx = AP_max_idx[i] 
            
            #TODO assert that monotonically increasing?
            thresh_idx = start_idx + np.searchsorted(dVdt[start_idx:stop_idx], 15) - 1 
             
            thresh_idxs.append(thresh_idx)
            thresh_vals.append(self.sweep.data()[thresh_idx])
        return np.array(thresh_idxs), np.array(thresh_vals)

    def calc_threshold_idxs(self):
        idxs, _ = self.calc_or_read_from_cache('threshold_idx_and_vals')
        return np.array(idxs)

    def calc_threshold_vals(self):
        _, vals = self.calc_or_read_from_cache('threshold_idx_and_vals')
        return np.array(vals)
    
    def calc_AP_amplitudes(self):
        AP_max = self.calc_or_read_from_cache('APmax_vals')
        threshold = self.calc_or_read_from_cache('threshold_vals')
        return np.array(AP_max - threshold)

    def calc_val_at_percent_APamplitude(self, percent):
        AP_amplitudes = self.calc_or_read_from_cache('AP_amplitudes')
        thresh_vals = self.calc_or_read_from_cache('threshold_vals')
        amplitude_at_percent = thresh_vals + AP_amplitudes * percent/100
        return amplitude_at_percent

    def calc_dVdt_at_percent_APamplitude(self, direction='rising',  percent=20):
        """
        This method calculates dVdt for each AP in the response, at a given
        percent of AP amplitude.
        """
        num_spikes = self.calc_or_read_from_cache('num_spikes')
        dVdt = self.calc_or_read_from_cache('dVdt_mV_per_ms')
        AP_max_idx = self.calc_or_read_from_cache('APmax_idxs')
        AHP_idx = self.calc_or_read_from_cache('AHP_idxs') 
        
        amplitudes_at_percent = self.calc_val_at_percent_APamplitude(percent) 
        dVdt_vals = []

        for i in range(num_spikes):
            if direction == 'rising':
                if i == 0: 
                    start_idx = self.onset_pnt
                else:
                    start_idx = AHP_idx[i-1]
                stop_idx = AP_max_idx[i]

            elif direction == 'falling':
                start_idx = AP_max_idx[i]
                if i < num_spikes-1:
                    stop_idx = AHP_idx[i] 
                else:
                    stop_idx = self.offset_pnt
            
            amplitude_at_percent = amplitudes_at_percent[i] 
            
            values_to_search = self.sweep.data()[start_idx:stop_idx]
            idx = np.argmin(abs(values_to_search-amplitude_at_percent))

            dVdt_val = np.float(dVdt[idx])
            dVdt_vals.append(dVdt_val)

        return np.array(dVdt_vals)

    def calc_delta_thresh(self):
        """
        This method returns the change in threshold for each AP compared to the
        first AP of the response.
        """
        threshold_vals = self.calc_threshold_vals()
        return np.array(threshold_vals - threshold_vals[0])

    def calc_ISIs(self):
        idxs = self.calc_or_read_from_cache('APmax_idxs')
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

        self._cache['closest_pnt20'] = closest_pnt20
        self._cache['closest_pnt80'] = closest_pnt80

        reb_delta_t = (closest_pnt80-closest_pnt20)/self.calc_or_read_from_cache('points_per_ms')
        return reb_delta_t 

    def plot_response(self, filepath):
        plt.figure()
        x1 = self.time(); y1 = self.data()
        plt.plot(x1, y1, color='k')
        plt.xlabel('time (s)')
        plt.ylabel('mV')
        plt.savefig(filepath)

    def plot_reb_delta_t(self, filepath):
        self.plot_response(filepath)
        self.calc_or_read_from_cache('reb_delta_t')
        # These two values should be in cache when 'reb_delta_t' is in cache.
        closest_pnt20 = self._cache['closest_pnt20']
        closest_pnt80 = self._cache['closest_pnt80']

        reb_calc_times = self.time()[closest_pnt20:closest_pnt80]
        reb_calc_data = self.data()[closest_pnt20:closest_pnt80]
        plt.plot(reb_calc_times, reb_calc_data, color = 'r'); 

        # Add arrows to indicate where the measurements were taken from 
        plt.annotate("", xy=(reb_calc_times.iloc[0], reb_calc_data.iloc[0]), 
                xytext=(reb_calc_times.iloc[-1], reb_calc_data.iloc[0]),
                arrowprops=dict(arrowstyle="<->"))
        plt.annotate("", xy=(reb_calc_times.iloc[-1], reb_calc_data.iloc[0]), 
                xytext=(reb_calc_times.iloc[-1], reb_calc_data.iloc[-1]),
                arrowprops=dict(arrowstyle="<->"))

        # Add text for the arrows, at the middle point of both
        xmin, xmax = plt.xlim();
        ymin, ymax = plt.ylim();
        plt.annotate(r'$\Delta$t', 
                xy=((reb_calc_times.iloc[0]+reb_calc_times.iloc[-1])/2, reb_calc_data.iloc[0]-.05*(ymax-ymin)), 
                ha='center')
        plt.annotate(r'$\Delta$amplitude', xy=(reb_calc_times.iloc[-1] + .02*(xmax-xmin), 
            (reb_calc_data.iloc[0]+reb_calc_data.iloc[-1])/2 ), va='center')
        plt.title(self.sweep.cell.calc_cell_name())
        plt.savefig(filepath)
