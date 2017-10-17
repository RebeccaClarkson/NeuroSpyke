import numpy as np
np.set_printoptions(precision = 2, linewidth = 40, suppress = True)

class Response(object):

    def __init__(self, curr_inj_params, sweep):
        self.curr_inj_params = curr_inj_params
        self.sweep = sweep
        self._cache = {}

    def sweep_data(self):
        return self.sweep.sweep_df['data']

    def sweep_time(self):
        return self.sweep.sweep_df['time']

    def sweep_commands(self):
        return self.sweep.sweep_df['comm']

    def calc_points_per_ms(self):
        """Calculate data acquisition sampling rate, in points per ms"""
        delta_t_sec = self.sweep_time()[1]- self.sweep_time()[0]
        points_per_ms = 1/(delta_t_sec * 1000) 
        return points_per_ms

    def calc_cell_name(self):
        return self.sweep.cell.cell_name()

    def calc_sweep_index(self):
        return self.sweep.sweep_df['sweep_index'][0]

    def meets_criteria(self):
        return all(self.meets_criterion(criterion)
                for criterion in self.sweep.cell.experiment.criteria)

    def meets_criterion(self, criterion):
        attr_name, condition = criterion
        value = self.calculate_or_read_from_cache(attr_name)

        if isinstance(condition, str):
            # process condition of string
            raise Exception("TODO implement")
        else:
            # use simple equality
            return value == condition

    def calculate_or_read_from_cache(self, attr_name):
        if not attr_name in self._cache:
            fn = getattr(self, f"calc_{attr_name}")
            value = fn()
            self._cache[attr_name] = value
        return self._cache[attr_name]

    def reset_cache(self):
        self._cache = {}
    
    def debug_cache(self):
        print(f"Cache has {len(self._cache)} items.")
        for key, value in self._cache.items():
            print(f"key: {key} value: {value}")

    def calc_spike_points(self):
        """ Calculates points where spikes occur (defined by voltage going  > -10 mV) """
        thresh = -10
        above_thresh = np.where(self.sweep_data()[1:] > thresh)           
        below_thresh = np.where(self.sweep_data()[0:-1] <= thresh)
        spike_points = np.intersect1d(above_thresh, below_thresh)
        return spike_points

    def calc_num_spikes(self):
        spike_points = self.calculate_or_read_from_cache('spike_points')
        return len(spike_points)
   
    def calc_spike_time_windows(self):
        spike_points = self.calculate_or_read_from_cache('spike_points')
        points_per_ms = self.calculate_or_read_from_cache('points_per_ms') 
        start_point =  (spike_points - 5 * points_per_ms) # start window at 5 ms prior to -10 mV
        print(start_point)


    def calc_APmax_idx_and_val(self):
        spike_points = self.calculate_or_read_from_cache('spike_points')
        num_spikes = self.calculate_or_read_from_cache('num_spikes')

        max_AP_idxs = []; max_AP_vals = []
        for i in range(num_spikes):

            if i < num_spikes-1:
                stop_idx = spike_points[i+1]
            else:
                stop_idx = self.curr_inj_params['offset_pnt']

            # find max data value that occurs between spike point indices
            start_idx = spike_points[i]; 
            max_val = max(self.sweep_data()[start_idx:stop_idx])

            # across entire data, find all indices where data == max_val
            poss_max_idx = np.flatnonzero(self.sweep_data() == max_val)

            # determine which of these are actually within the spike times 
            within_spike = np.logical_and(poss_max_idx > start_idx, poss_max_idx < stop_idx)
            
            # take first idx within spike window that = max_val
            max_idx = int(poss_max_idx[np.where(within_spike)[0][0]])

            # append values
            max_AP_vals.append(max_val)
            max_AP_idxs.append(max_idx)
        idxs = max_AP_idxs
        vals = max_AP_vals
        return list(zip(idxs, vals))         

    def calc_APmax_val(self):
        vals = [val 
                for idx, val 
                in self.calculate_or_read_from_cache('APmax_idx_and_val')]
        return vals

    def calc_APmax_idx(self):
        return [idx for idx, val in self.calculate_or_read_from_cache('APmax_idx_and_val')]

    def calc_ISIs(self):
        idxs = self.calculate_or_read_from_cache('APmax_idx')
        ISI_idx = np.diff(idxs) # ISI in idices 
        ISI_ms = ISI_idx/self.calculate_or_read_from_cache('points_per_ms') 
        return(ISI_ms)

    def properties(self):
        return self.calc_properties(self.sweep.cell.experiment.property_names)

    def calc_properties(self, property_names):
        property_dict = {
                property_name: self.calculate_or_read_from_cache(property_name) 
                for property_name in property_names
                }
        return property_dict 
