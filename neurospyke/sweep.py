from neurospyke.response import Response
import pandas as pd

class Sweep(object):
    def __init__(self, sweep_df, cell=None):
        self.sweep_df = sweep_df
        self.cell = cell

    def run(self):
        """
        Returns a dataframe with one row for each response meeting the
        reponse_criteria, for all response_properties.
        """
        results_df = None
        for response in self.responses():
            if response.meets_criteria():
                if results_df is None:
                    results_df = response.run()
                else: 
                    results_df = pd.concat([results_df, response.run()])
        return results_df

    def time(self):
        return self.sweep_df['time']

    def data(self):
        return self.sweep_df['data']

    def commands(self):
        return self.sweep_df['commands']

    def sweep_index(self):
        return self.sweep_df['sweep_index'][0]

    def current_inj_waveforms(self):
        """
        Returns a list with n dictionaries  where n = number of current injections.
        """
        curr_inj_waveform_list = []
        assert self.commands()[0] == 0
    
        delta_curr = self.commands().diff()
        delta_curr[0] = 0
        non_zero = delta_curr.nonzero()[0]
        num_commands = int(len(non_zero))
        assert num_commands % 2 == 0 # should have even number of command steps 
    
        for i in range(0, num_commands, 2): # verify these are symmetrical square waves pulses
            this_val = delta_curr.iloc[non_zero].values[i] 
            next_val = delta_curr.iloc[non_zero].values[i+1]
    
            assert this_val == -next_val
            onset = non_zero[i]; offset = non_zero[i+1] 

            onset_time = self.time().iloc[onset] 
            offset_time = self.time().iloc[offset]
            wave_amplitude = self.commands().iloc[onset]
            sweep_index = self.sweep_index() 
    
            # Now that have all the values, append to list 
            tmp_dict = {
                    'sweep_index':sweep_index,
                    'onset_pnt':onset,
                    'offset_pnt':offset,
                    'onset_time':onset_time, 
                    'offset_time':offset_time,
                    'amplitude':wave_amplitude
                    }
            curr_inj_waveform_list.append(tmp_dict)
    
        return curr_inj_waveform_list

    def responses(self): 
        return [Response(curr_inj_params, self) 
                for curr_inj_params in self.current_inj_waveforms()]

    def plot(self, filepath=None):

        for fig, (ax1, ax2) in self.cell.sweep_plot_setup(filepath):
            ax1.plot(self.sweep_df.time, self.sweep_df.data)
            ax2.plot(self.sweep_df.time, self.sweep_df.commands)
            ax1.set(title = f"sweep #{self.sweep_df.sweep_index[0]}")
            ax1.set_xlim([0, max(self.sweep_df.time)]); 
