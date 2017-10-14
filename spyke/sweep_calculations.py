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
