import numpy as np
np.set_printoptions(precision = 2, linewidth = 40, suppress = True)

class Response(object):

    def __init__(self, curr_inj_params, sweep):
        self.curr_inj_params = curr_inj_params
        self.sweep = sweep
        self._cache = {}

    def swp_data(self):
        return self.sweep.sweep_df['data']

    def swp_time(self):
        return self.sweep.sweep_df['time']

    def swp_commands(self):
        return self.sweep.sweep_df['comm']

    def calc_cell_name(self):
        return self.sweep.cell.cell_name()

    def calc_sweep_index(self):
        return self.sweep.sweep_index()

    def calc_curr_duration(self):
        return self.curr_inj_params['offset_time'] - self.curr_inj_params['onset_time']


    def calc_points_per_ms(self):
        """Calculate data acquisition sampling rate, in points per ms"""
        delta_t_sec = self.sweep.time()[1]- self.sweep.time()[0]
        points_per_ms = 1/(delta_t_sec * 1000) 
        return points_per_ms

    def meets_criteria(self):
        for criterion in self.sweep.cell.experiment.criteria:
            if self.meets_criterion(criterion):
                print(f"for sweep {self.calc_sweep_index()}, cell {self.calc_cell_name()}:\n")
                print(f"conditions are met")

        return all(self.meets_criterion(criterion)
                for criterion in self.sweep.cell.experiment.criteria)

    def meets_criterion(self, criterion):
        attr_name, condition = criterion
        value = self.calc_or_read_from_cache(attr_name)
        if isinstance(condition, str):
            # process condition of string
            raise Exception("TODO implement")
        else:
            # use simple equality
            return np.isclose(value, condition)

    def calc_or_read_from_cache(self, attr_name):
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
                stop_idx = self.curr_inj_params['offset_pnt']

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
        ISI_idx = np.diff(idxs) # ISI in idices 
        ISI_ms = ISI_idx/self.calc_or_read_from_cache('points_per_ms') 
        return(ISI_ms)

    def properties(self):
        return self.calc_properties(self.sweep.cell.experiment.property_names)

    def calc_properties(self, property_names):
        property_dict = {
                property_name: self.calc_or_read_from_cache(property_name) 
                for property_name in property_names
                }
        return property_dict 
