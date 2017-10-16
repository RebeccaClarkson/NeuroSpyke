from neurospyke.response import Response
import matplotlib as mpl
mpl.use('TkAgg')
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
import matplotlib.pyplot as plt

class Sweep(object):
    def __init__(self, sweep_df, cell=None):
        self.sweep_df = sweep_df
        self.cell = cell
        
    def current_inj_waveforms(self):
        """
        Returns a list with n dictionaries  where n = number of current injections.
        """
        curr_inj_waveform_list = []
        assert self.sweep_df['commands'][0] == 0
    
        delta_commands = self.sweep_df['commands'].diff()
        delta_commands[0] = 0
        non_zero = delta_commands.nonzero()[0]
        num_commands = int(len(non_zero))
        assert num_commands % 2 == 0 # should have even number of command steps 
    
        for i in range(0, num_commands, 2): # verify these are symmetrical square waves pulses
            assert delta_commands.iloc[non_zero].values[i] + delta_commands.iloc[non_zero].values[i+1] == 0
    
            onset = non_zero[i]; offset = non_zero[i+1] 

            onset_time = self.sweep_df['time'].iloc[onset] 
            offset_time = self.sweep_df['time'].iloc[offset]
            wave_amplitude = self.sweep_df['commands'].iloc[onset]
            sweep_index = self.sweep_df['sweep_index'].iloc[offset] 
    
            # Now that have all the values, append to dataframe 
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
        return [Response(curr_inj_params, self) for curr_inj_params in self.current_inj_waveforms()]

    def plot(self, filepath):
        fig, (ax1, ax2) = plt.subplots(2, sharex=True)
        ax1.plot(self.sweep_df.time, self.sweep_df.data)
        ax2.plot(self.sweep_df.time, self.sweep_df.commands)

        # set labels
        ax1.set(title = f"sweep #{self.sweep_df.sweep_index[0]}")
        ax1.set_ylabel('mV'); 
        ax2.set_xlabel('time (s)'); ax2.set_ylabel('pA')
        
        # set axes limits
        ax1.set_xlim([0, 1]); ax1.set_ylim([-150, 50])
        ax2.set_ylim([-400, 250])

        # save figure
        fig.savefig(filepath)
