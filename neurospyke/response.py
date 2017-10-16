import numpy as np

class Response(object):
    def __init__(self, curr_inj_params, sweep_obj,  cell=None):
        self.curr_inj_params = curr_inj_params
        self.sweep_obj = sweep_obj
        self.cell = cell
        self._cache = {}

    def meets_criteria(self):
        return all(self.meets_criterion(criterion)
                for criterion in self.experiment.criteria)

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

    def calc_spike_points(self, thresh = 20):
        #thresh = self.experiment.criteria.thresh
        above_thresh = np.where(self.sweep_obj.sweep_df['data'][1:] > thresh)           
        below_thresh = np.where(self.sweep_obj.sweep_df['data'][0:-1] <= thresh)
        spike_points = np.intersect1d(above_thresh, below_thresh)
        return spike_points

    def calc_num_spikes(self):
        spike_points = self.calculate_or_read_from_cache('spike_points')
        return len(spike_points)
