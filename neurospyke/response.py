import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class Response(object):
    def __init__(self, curr_inj_params, sweep):
        self.onset_pnt = int(curr_inj_params['onset_pnt'])
        self.offset_pnt = int(curr_inj_params['offset_pnt'])
        self.onset_time = curr_inj_params['onset_time']
        self.offset_time = curr_inj_params['offset_time']
        self.amplitude = curr_inj_params['amplitude']
        self.sweep = sweep
        self._cache = {}

    def criteria_priority(self):
        """
        This method sets "sweep_time" as the first criteria to be checked, as
        this can speed processing time.
        """
        first_criteria = 'sweep_time'
        response_criteria = self.sweep.cell.query.response_criteria
        first_list = []
        other_list = []
        for criteria in response_criteria:
            if first_criteria in criteria:
                first_list.append(criteria)
            else:
                other_list.append(criteria)
        return first_list + other_list

    def data(self):
        return self.sweep.sweep_df['data']

    def time(self):
        return self.sweep.sweep_df['time']

    def commands(self):
        return self.sweep.sweep_df['commands']

    def calc_or_read_from_cache(self, attr_name_with_args):
        """
        This method either calculates the given attribute or gets it from the
        cache if it has already been calculated.
        """
        attr_pieces = attr_name_with_args.split('__') 
        attr_name = attr_pieces[0]
        args = attr_pieces[1:]

        if not attr_name in self._cache:
            fn = getattr(self, f"calc_{attr_name}")
            value = fn(*args)
            self._cache[attr_name_with_args] = value
        return self._cache[attr_name_with_args]

    def debug_cache(self):
        print(f"Cache has {len(self._cache)} items.")
        for key, value in self._cache.items():
            print(f"key: {key} value: {value}")

    def meets_criterion(self, criterion):
        """
        This method returns True if the response meets the given criterion.
        """
        attr_name, condition = criterion
        value = self.calc_or_read_from_cache(attr_name)

        if isinstance(condition, str):
            condition_val_str = ''.join([s for s in condition if s.isdigit() or '.' in s or '-' in s])
            condition_val = float(condition_val_str) 
            if "<" in condition and ">" in condition:
                raise Exception("TODO")   
            elif "<" in condition:
                #print(f"Sweep # {self.sweep.sweep_index()}")
                #print(value, condition, value < condition_val)
                return value < condition_val
            elif ">" in condition:
                #print(f"Sweep # {self.sweep.sweep_index()}")
                #print(value, condition, value>condition_val)
                return value > condition_val
            else:
                raise Exception(f"{condition} is invalid condition")
        else:
            #print(f"Sweep # {self.sweep.sweep_index()}")
            #print(value, condition, np.isclose(value, condition))
            return np.isclose(value, condition)

    def meets_criteria(self):
        return all(self.meets_criterion(criterion)
                for criterion in self.criteria_priority())

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
        return pd.DataFrame([results_dict], index=[self.sweep.sweep_index()])

    def window(self, left_window=100, right_window=100):
        """
        Returns a dataframe of the sweep_df format with only the specified
        response window.  Left and right are how far the window should extend
        from the current injection (in ms)
        """
        points_per_ms = self.calc_or_read_from_cache('points_per_ms')
        
        window_onset_pnt = int(self.onset_pnt - int(left_window)*points_per_ms)
        window_offset_pnt = int(self.offset_pnt + int(right_window)*points_per_ms)

        if window_onset_pnt < 0:
            raise Exception("Left window too big")
        if window_offset_pnt > len(self.sweep.sweep_df.index):
            raise Exception("Right window too big")

        window_df = self.sweep.sweep_df[window_onset_pnt:window_offset_pnt]
        window_df = window_df.reset_index(drop=True)
        window_df['time'] = window_df['time'] - window_df['time'][0] 
        
        return window_df

###############################################################################
##########################   BASIC PROPERTIES    ##############################
###############################################################################

    def calc_sweep_time(self):
        return self.sweep.sweep_df.sweep_time[0]

    def calc_sweep_index(self):
        return self.sweep.sweep_index()

    def calc_curr_duration(self):
        return self.offset_time - self.onset_time

    def calc_curr_amplitude(self):
        return self.amplitude

    def calc_points_per_ms(self):
        """Calculate data acquisition sampling rate, in points per ms"""
        delta_t_sec = self.sweep.time()[1]- self.sweep.time()[0]
        points_per_ms = 1/(delta_t_sec * 1000) 
        return int(round(points_per_ms))

    def calc_ms_per_point(self):
        points_per_ms = 1/self.calc_or_read_from_cache('points_per_ms')
        return points_per_ms


    def calc_baseline(self):
        """
        Calculates the voltage immediately before current injection.
        """
        baseline_start = self.onset_pnt - 10 * self.calc_or_read_from_cache('points_per_ms')
        baseline_stop = self.onset_pnt
        return np.mean(self.sweep.data()[baseline_start:baseline_stop])
        
###############################################################################
##########################   SPIKE PROPERTIES    ##############################
###############################################################################

    def calc_spike_points(self):
        """ Calculates points where spikes occur (defined by voltage going  > -10 mV) """
        thresh = -10
        above_thresh = np.where(self.sweep.data()[1:] > thresh)           
        below_thresh = np.where(self.sweep.data()[0:-1] <= thresh)
        spike_points = np.intersect1d(above_thresh, below_thresh)
        idx = np.where((spike_points > self.onset_pnt) & (spike_points < self.offset_pnt))
        return spike_points[idx] 
        #all_spike_points_during_current_injection = all(spike_point 
        #        in range(self.onset_pnt, self.offset_pnt) 
        #        for spike_point in spike_points)
        #if all_spike_points_during_current_injection: 
        #    return spike_points
        #else:
        #    # if there are spikes outside of current injection, don't analyze
        #    return []
     
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
        if num_spikes == 1:
            # for rheobase calculations
            start_idx = APmax_idxs[0]
            stop_idx = self.offset_pnt
            min_idx = np.argmin(self.sweep.data()[start_idx:stop_idx])
            min_val = self.sweep.data()[min_idx]
            AHP_vals.append(min_val)
            AHP_idxs.append(min_idx)
        else:
            for i in range(num_spikes-1):
                # find min voltage that occurs between given AP max and next AP max
                start_idx = APmax_idxs[i]
                stop_idx = APmax_idxs[i+1]
                min_idx = np.argmin(self.sweep.data()[start_idx:stop_idx])
                min_val = self.sweep.data()[min_idx]
                
                # append values
                AHP_vals.append(min_val)
                AHP_idxs.append(min_idx)
            # in order to have len(AHP_vals) and len(AHP_idxs) == num_spikes
            AHP_vals.append(np.nan)
            AHP_idxs.append(np.nan)

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
                start_idx = int(self.onset_pnt)
            else: 
                start_idx = int(AHP_idx[i-1])
            stop_idx = int(AP_max_idx[i])

            #TODO assert that monotonically increasing?
            thresh_idx = start_idx + np.searchsorted(dVdt[start_idx:stop_idx], 15) - 1
             
            thresh_idxs.append(thresh_idx)
            thresh_vals.append(self.sweep.data()[thresh_idx])
        return np.array(thresh_idxs), np.array(thresh_vals)

    def calc_threshold_idxs(self):
        idxs, _ = self.calc_or_read_from_cache('threshold_idx_and_vals')
        return np.array(idxs)

    def calc_threshold_timing(self):
        """
        This method returns the the timing (in ms) of each AP threshold with
        respect to initial current onset. 
        """
        thresh_idxs = self.calc_or_read_from_cache('threshold_idxs')
        threshold_offset_pnts = thresh_idxs - self.onset_pnt
        return threshold_offset_pnts * self.calc_or_read_from_cache('ms_per_point')

    def calc_threshold_vals(self):
        _, vals = self.calc_or_read_from_cache('threshold_idx_and_vals')
        return np.array(vals)

    def calc_AHP_vs_threshold(self):
        AHP_vals = self.calc_or_read_from_cache('AHP_vals')
        threshold_vals = self.calc_or_read_from_cache('threshold_vals')
        return AHP_vals - threshold_vals
    
    def calc_AP_amplitudes(self):
        AP_max = self.calc_or_read_from_cache('APmax_vals')
        threshold = self.calc_or_read_from_cache('threshold_vals')
        return np.array(AP_max - threshold)

    def calc_val_pct_APamp(self, percent):
        AP_amplitudes = self.calc_or_read_from_cache('AP_amplitudes')
        thresh_vals = self.calc_or_read_from_cache('threshold_vals') 
        amplitude_at_percent = thresh_vals + AP_amplitudes * percent/100
        return amplitude_at_percent
    
    def calc_AP_width_and_idxs(self, percent):
        num_spikes = self.calc_or_read_from_cache('num_spikes')
        rising_start_idxs = self.AP_start_idxs(num_spikes, 'rising')
        rising_stop_idxs = self.AP_stop_idxs(num_spikes, 'rising')
        falling_start_idxs = self.AP_start_idxs(num_spikes, 'falling')
        falling_stop_idxs = self.AP_stop_idxs(num_spikes, 'falling')

        amplitudes_at_percent = self.calc_val_pct_APamp(int(percent))
        spike_widths = []; idxs_rising = []; idxs_falling = []
        for i in range(num_spikes):
            rising_start_idx = int(rising_start_idxs[i])
            rising_stop_idx = int(rising_stop_idxs[i])
            falling_start_idx = int(falling_start_idxs[i])
            falling_stop_idx = int(falling_stop_idxs[i])
            
            rising_spike_data = self.sweep.data()[rising_start_idx:rising_stop_idx]
            falling_spike_data = self.sweep.data()[falling_start_idx:falling_stop_idx]

            amplitude_at_percent = amplitudes_at_percent[i]
            idx_rising = np.argmin(abs(rising_spike_data-amplitude_at_percent))
            idx_falling = np.argmin(abs(falling_spike_data-amplitude_at_percent))
            spike_width = (idx_falling-idx_rising) * self.calc_or_read_from_cache('ms_per_point')
            idxs_rising.append(int(idx_rising))
            idxs_falling.append(int(idx_falling))
            spike_widths.append(np.float(spike_width))


        return idxs_rising, idxs_falling, np.array(spike_widths)
    
    def calc_AP_width(self, percent):
        _, _, spike_widths = self.calc_AP_width_and_idxs(int(percent))
        return spike_widths

    def AP_start_idxs(self, num_spikes, direction):
        AP_max_idx = self.calc_or_read_from_cache('APmax_idxs')
        AHP_idx = self.calc_or_read_from_cache('AHP_idxs') 
        start_idxs = []
        for i in range(num_spikes):
            if direction == 'rising':
                if i == 0:
                    start_idx = self.onset_pnt
                else:
                    start_idx = AHP_idx[i-1]
            elif direction == 'falling':
                start_idx = AP_max_idx[i]
            start_idxs.append(int(start_idx))
        return start_idxs

    def AP_stop_idxs(self, num_spikes, direction):
        AP_max_idx = self.calc_or_read_from_cache('APmax_idxs')
        AHP_idx = self.calc_or_read_from_cache('AHP_idxs') 
        stop_idxs = []
        for i in range(num_spikes):
            if direction == 'rising':
                stop_idx = AP_max_idx[i]
            elif direction == 'falling':
                if i < num_spikes-1:
                    stop_idx = AHP_idx[i] 
                else:
                    stop_idx = self.offset_pnt
            stop_idxs.append(int(stop_idx))
        return stop_idxs

    def calc_dVdt_pct_APamp(self, percent, direction):
        num_spikes = self.calc_or_read_from_cache('num_spikes')
        dVdt = self.calc_or_read_from_cache('dVdt_mV_per_ms')
        
        if percent.isdigit():
            amplitudes_at_percent = self.calc_val_pct_APamp(int(percent))

        dVdt_vals = []
        
        AP_start_idxs = self.AP_start_idxs(num_spikes, direction)
        AP_stop_idxs = self.AP_stop_idxs(num_spikes, direction)

        for i in range(num_spikes):
            start_idx = AP_start_idxs[i]
            stop_idx = AP_stop_idxs[i]
            spike_data = self.sweep.data()[start_idx:stop_idx]
            dVdt_data = dVdt[start_idx:stop_idx]

            if percent.isdigit():
                amplitude_at_percent = amplitudes_at_percent[i] 
                idx = np.argmin(abs(spike_data-amplitude_at_percent))
                dVdt_val = np.float(dVdt[idx])
            elif percent == 'max':
                dVdt_abs = np.abs(dVdt_data)
                max_idx = np.argmax(dVdt_abs)
                dVdt_val = np.float(dVdt_data[max_idx])
                
            # append value as float to dVdt_vals
            dVdt_vals.append(dVdt_val)
                
        return np.array(dVdt_vals)

    def calc_dVdt_pct_APamp_last_spike(self, percent, direction,  num_spikes):
        num_spikes = int(num_spikes)
        if self.calc_or_read_from_cache('num_spikes') == num_spikes:
            return self.calc_or_read_from_cache(f'dVdt_pct_APamp__{percent}__{direction}')[num_spikes-1]

    def calc_delta_thresh(self):
        """
        This method returns the change in threshold for each AP compared to the
        first AP of the response.
        """
        threshold_vals = self.calc_threshold_vals()
        return np.array(threshold_vals - threshold_vals[0])

    def calc_delta_thresh_last_spike(self, num_spikes):
        num_spikes = int(num_spikes)
        if self.calc_or_read_from_cache('num_spikes') == num_spikes:
            return self.calc_or_read_from_cache('delta_thresh')[num_spikes-1]

    def calc_ISIs(self):
        idxs = self.calc_or_read_from_cache('APmax_idxs')
        ISI_idx = np.diff(idxs)  
        ISI_ms = ISI_idx/self.calc_or_read_from_cache('points_per_ms') 
        return(ISI_ms)

    def calc_doublet_index(self):
        return(self.calc_ISIs()[1]/self.calc_ISIs()[0]) 
    
    def calc_doublet_index_by_num_spikes(self, num_spikes):
        num_spikes = int(num_spikes)
        if self.calc_or_read_from_cache('num_spikes') == num_spikes:
             return self.calc_or_read_from_cache('doublet_index')

###############################################################################
##########################   SAG/REB PROPERTIES    ############################
###############################################################################

    def calc_peak_sag_idx_and_val(self):
        peak_sag_idx = np.argmin(self.sweep.data()[self.onset_pnt:self.offset_pnt])
        peak_sag_val = self.sweep.data()[peak_sag_idx]
        return peak_sag_idx, peak_sag_val

    def calc_peak_sag_idx(self):
        idx, _ = self.calc_or_read_from_cache('peak_sag_idx_and_val')
        return idx

    def calc_peak_sag_val(self):
        _, val = self.calc_or_read_from_cache('peak_sag_idx_and_val')
        return val

    def calc_sag_onset_time(self):
        peak_sag_idx = self.calc_or_read_from_cache('peak_sag_idx')
        current_onset_idx = self.onset_pnt # -2 to match matlab 
        return (peak_sag_idx-current_onset_idx)*self.calc_or_read_from_cache('ms_per_point')

    def calc_sag_abs_amplitude(self):
        """
        Calculates absolute sag amplitude (mV change from peak to steady state)
        """
        peak_sag_amp  = self.calc_or_read_from_cache('peak_sag_val')
        steady_state_amp = self.calc_or_read_from_cache('sag_steady_state_avg_amp')
        return peak_sag_amp - steady_state_amp  

    def calc_sag_offset_idx(self):
        """
        Returns point of sag offset, which is 1 point before end of current injection to avoid transient.
        """
        return self.offset_pnt-1

    def calc_sag_steady_state_avg_amp(self):
        """
        Returns the mean value of sag steady state, defined as ~10ms before
        current offset to current_offset for -400 pA injections.
        """
        points_per_ms = self.calc_or_read_from_cache('points_per_ms')
        steady_state_offset_idx = self.calc_or_read_from_cache('sag_offset_idx')
        steady_state_onset_idx = steady_state_offset_idx - 10 * points_per_ms # -1 to match matlab analysis
        steady_state_vals = self.data()[steady_state_onset_idx:steady_state_offset_idx]
        return np.mean(steady_state_vals)
       
    def calc_sag_fit_amplitude(self):
        """
        Calculates sag amplitude based on an exponential fit from peak sag to sag offset. 
        """
        assert self.calc_or_read_from_cache('sag_onset_time') < 80, "Fitting to no sag"
        def exponential(x, a, b):
            return a * np.exp(b*x) 

        def goodness_of_fit(y, y_fit):
            ss_res = np.sum((y - y_fit) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            return r2

        start_idx = self.calc_or_read_from_cache('peak_sag_idx')
        end_idx = self.calc_or_read_from_cache('sag_offset_idx')

        x = self.time()[start_idx:end_idx] - self.time()[start_idx]
        y = self.data()[start_idx:end_idx]

        y_start0 = y-np.min(y)
        y_end0 = y-np.max(y)
        popt_vals = []; r2_vals = []; y_fit_vals = []
        for y in y_start0, y_end0:
            popt, _ = curve_fit(exponential, x, y)
            y_fit = exponential(x, *popt)
            r2 = goodness_of_fit(y, y_fit)
           
            popt_vals.append(popt)
            r2_vals.append(r2)
            y_fit_vals.append(y_fit)
     
        best_fit_idx = np.argmax(r2_vals)
        sag_amplitude = popt_vals[best_fit_idx][0]

        return sag_amplitude 

    def calc_max_rebound_val_and_time(self):
        """
        Returns the max rebound amplitude and time after current offset within the response window
        """
        reb_data = self.data()[self.offset_pnt:]
        max_idx = np.argmax(reb_data)
        max_val = reb_data[max_idx]

        max_pnt_offset = max_idx - self.offset_pnt
        max_rebound_location_ms = max_pnt_offset * self.calc_or_read_from_cache('ms_per_point')

        return max_rebound_location_ms, max_val

    def calc_max_rebound_val(self):
        _, max_val = self.calc_or_read_from_cache('max_rebound_val_and_time')
        return max_val

    def calc_max_rebound_time(self):
        max_rebound_location_ms, _ = self.calc_or_read_from_cache('max_rebound_val_and_time')
        return max_rebound_location_ms

    def find_nearest_pnt_series(self, pd_series, value):
        array = np.array(pd_series)
        idx_array = (np.abs(array-value)).argmin()
        return pd_series.index[0] + idx_array
        
    def calc_reb_delta_t(self):
        """
        Returns time to get from 20% to 80% of voltage change from steady state
        to maximum repolarization within response window. 
        """
        max_rebound_val = self.calc_or_read_from_cache('max_rebound_val')
        steady_state_avg_amp = self.calc_or_read_from_cache('sag_steady_state_avg_amp')

        rebound_amp_change = max_rebound_val - steady_state_avg_amp
        twenty_percent_rebound_voltage = steady_state_avg_amp + rebound_amp_change * 0.20
        eighty_percent_rebound_voltage = steady_state_avg_amp + rebound_amp_change * 0.80

        reb_data = self.data()[self.offset_pnt:]
        closest_pnt20 = self.find_nearest_pnt_series(reb_data, 
                twenty_percent_rebound_voltage)
        closest_pnt80 = self.find_nearest_pnt_series(reb_data, 
                eighty_percent_rebound_voltage)

        self._cache['closest_pnt20'] = closest_pnt20
        self._cache['closest_pnt80'] = closest_pnt80

        reb_delta_t = (closest_pnt80-closest_pnt20)/self.calc_or_read_from_cache('points_per_ms')
        return reb_delta_t 


###############################################################################
##################################   PLOT    ##################################
###############################################################################
    
    def plot_response(self, filepath=None, plotting_above=False, plot_commands=True, xscale='s'):
        #TODO: currently this creates a generator, so can't plot externally without a loop
        fig = None; ax1 = None; ax2 = None
        if xscale == 'ms':
            time = self.time() * 1000
        elif xscale == 's':
            time = self.time()
        if plot_commands:
            fig, (ax1, ax2) = plt.subplots(2, sharex=True)

            ax2.set_xlabel(f'time ({xscale})'); ax2.set_ylabel('pA')
            ax2.set_ylim([-450, 250])
            ax2.plot(time, self.commands(), color='k')

            ax1.spines['bottom'].set_visible(False)
            ax1.axes.get_xaxis().set_visible(False)
        else:
            fig, ax1 = plt.subplots(1)

        ax1.set_ylabel('mV'); 
        ax1.plot(time, self.data(), color='k')

        ax1.set_xlabel(f'time ({xscale})')
        ax1.set_ylabel('mV')
        ax1.set_title(self.sweep.cell.calc_cell_name())

        yield fig, (ax1, ax2)

        if filepath:
            plt.savefig(filepath, bbox_inches="tight")

    def plot_reb_time(self, filepath=None):
        """ Add line showing timing of peak rebound """
        rebound_time_sec = self.calc_or_read_from_cache('max_rebound_time')/1000

        for fig, (ax1, ax2) in self.plot_response():
            ax1.axvline(x=self.offset_time+rebound_time_sec)
            ax1.axvline(x=self.offset_time + .09,color='r')

            if rebound_time_sec < .09:
                ax1.set_title(ax1.get_title() + ': Type 2')
            else:
                ax1.set_title(ax1.get_title() + ': Type 1/3')
    
        if filepath:
            plt.savefig(filepath)
        else:
            plt.show()

    def plot_reb_delta_t(self, filepath=None):
        """
        Adds annotations for reb_delta_t analysis to a figure object created
        with self.plot_response()
        """
        self.calc_or_read_from_cache('reb_delta_t')

        # These two values should be in cache when 'reb_delta_t' is in cache.
        closest_pnt20 = self._cache['closest_pnt20']
        closest_pnt80 = self._cache['closest_pnt80']

        reb_calc_times = self.time()[closest_pnt20:closest_pnt80]
        reb_calc_data = self.data()[closest_pnt20:closest_pnt80]
        
        for fig, (ax1, ax2) in self.plot_response():

            ax1.plot(reb_calc_times, reb_calc_data, color = 'r'); 

            # Add arrows to indicate where the measurements were taken from 
            ax1.annotate("", xy=(reb_calc_times.iloc[0], reb_calc_data.iloc[0]), 
                    xytext=(reb_calc_times.iloc[-1], reb_calc_data.iloc[0]),
                    arrowprops=dict(arrowstyle="<->"))
            ax1.annotate("", xy=(reb_calc_times.iloc[-1], reb_calc_data.iloc[0]), 
                    xytext=(reb_calc_times.iloc[-1], reb_calc_data.iloc[-1]),
                    arrowprops=dict(arrowstyle="<->"))

            # Add text for the arrows, at the middle point of both
            xmin, xmax = ax1.get_xlim();
            ymin, ymax = ax1.get_ylim();
            ax1.annotate(r'$\Delta$t', 
                xy=((reb_calc_times.iloc[0]+reb_calc_times.iloc[-1])/2, 
                    reb_calc_data.iloc[0]-.08*(ymax-ymin)), 
                ha='center')
            ax1.annotate(r'$\Delta$amplitude', 
                xy=(reb_calc_times.iloc[-1] + .02*(xmax-xmin), 
                (reb_calc_data.iloc[0]+reb_calc_data.iloc[-1])/2 ), 
                va='center')
        if filepath:
            plt.savefig(filepath)
        else:
            plt.show()


    def plot_spiking_properties(self, threshold=False, AHP=False, AP_width__50=False, 
            filepath=None, plot_commands=True, xscale='ms'):

        if xscale == 'ms':
            scalar = 1000
        if xscale == 's':
            scalar = 1
        time = self.time() * scalar


        for fig, (ax1, ax2) in self.plot_response(
                filepath=filepath, 
                plot_commands=plot_commands,
                xscale=xscale):

            if threshold:
                threshold_vals = self.calc_or_read_from_cache('threshold_vals')
                threshold_times = time.values[self.calc_or_read_from_cache('threshold_idxs')]
                ax1.scatter(threshold_times, threshold_vals, facecolors='r', edgecolors='r', s=30)
            if AHP:
                AHP_vals = self.calc_or_read_from_cache('AHP_vals')
                AHP_times= time.values[self.calc_or_read_from_cache('AHP_idxs')]
                ax1.scatter(AHP_times, AHP_vals, facecolors='r', edgecolors='r', s=20)
            if AP_width__50:
                idxs_rising, idxs_falling, _ = self.calc_AP_width_and_idxs(50)
                ax1.plot((time.values[idxs_rising], time.values[idxs_falling]), 
                        (self.data().values[idxs_rising], self.data().values[idxs_falling]))

            ax1.set_xlim([threshold_times[0]-.005*scalar, threshold_times[-1]+.01*scalar])
            ax1.set_ylim([-60, 60])
                #ax1.set_xlim([self.onset_time-.01, self.offset_time+.1])
            if plot_commands:
                ax2.set_ylim([-50, 250])
        cell_name = self.sweep.cell.calc_cell_name()
        mouse_genotype = self.sweep.cell.calc_mouse_genotype()
        age = self.sweep.cell.calc_age()
        sweep_index = self.sweep.sweep_index()
        ax1.set_title(
                f"{cell_name}, sweep {sweep_index}, {self.amplitude} pA" +
                f"\nP{int(age)}, {mouse_genotype}"
                )
        if filepath:
            plt.savefig(filepath)
        else:
            plt.show()
        plt.close()
