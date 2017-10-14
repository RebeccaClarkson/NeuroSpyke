# sweep calculations
import pandas as pd
import numpy as np

def current_inj_per_sweep(sweep_df):
    column_names =  ['sweep_index', 'onset_pnt', 'offset_pnt', 'onset_time', 'offset_time', 'amplitude']
    command_waveform_df = pd.DataFrame(columns = column_names)
    assert sweep_df['commands'][0] == 0

    delta_commands = sweep_df['commands'].diff()
    delta_commands[0] = 0
    non_zero = delta_commands.nonzero()[0]
    num_commands = int(len(non_zero))
    assert num_commands % 2 == 0 # should have even number of command steps 

    for i in range(0, num_commands, 2): # verify these are symmetrical square waves pulses
        assert delta_commands.iloc[non_zero].values[i] + delta_commands.iloc[non_zero].values[i+1] == 0

        onset = non_zero[i]; offset = non_zero[i+1] 
        onset_time = sweep_df['time'].iloc[onset] 
        offset_time = sweep_df['time'].iloc[offset]
        wave_amplitude = sweep_df['commands'].iloc[onset]
        sweep_index = sweep_df['sweep_index'].iloc[offset] 

        # Now that have all the values, append to dataframe 
        params = np.array([[sweep_index, onset, offset, onset_time, offset_time, wave_amplitude]])
        tmp_df = pd.DataFrame(data = params, columns = column_names)
        command_waveform_df = command_waveform_df.append(tmp_df)

    command_waveform_df[['sweep_index']] = command_waveform_df[['sweep_index']].astype(int)
    return command_waveform_df

def do_select_sweep_by_current_inj(all_waveforms_df, duration, amplitude):
    """
    Return sweep indices for sweeps with duration/amplitude input parameters.
    For returning all depol./hyperpol. current injections, amplitude = 1/-1.
    """
    duration_bool = np.isclose(all_waveforms_df['offset_time'] 
            - all_waveforms_df['onset_time'], duration, 1e-5)

    if amplitude == 1: # depolarizing current injections
        amplitude_bool = np.greater(all_waveforms_df['amplitude'], 0).as_matrix()
    elif amplitude == -1: # hyperpolarizing current injections
        amplitude_bool = np.less(all_waveforms_df['amplitude'], 0).as_matrix()
    else:
        amplitude_bool = np.isclose(all_waveforms_df['amplitude'] , amplitude, 1e-5)
        
    select_df = all_waveforms_df.loc[duration_bool & amplitude_bool]
    sweep_index = select_df['sweep_index']
    return np.array(sweep_index)
 
def do_select_sweep_by_spike_count(spike_counts,  num_spikes):
    """
    Return sweep indices as np.array for sweeps that have a given number of APs
    """
    return np.where(spike_counts == num_spikes)[0]

def do_select_sweep_by_sweep_time(sweep_time, stop_time, start_time = 0):
    after_start_idx = np.where(sweep_time > start_time)
    before_stop_idx = np.where(sweep_time < stop_time)
    return np.intersect1d(after_start_idx, before_stop_idx) 

