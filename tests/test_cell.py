from spyke.cell import Cell
import numpy as np
import pandas as pd
from utils import intersect_all

ex1 = Cell("tests/data/ExampleCell1.mat")
ex2 = Cell("tests/data/ExampleCell2.mat")
image_save_filepath = "/Users/Becky/Dropbox/Data_Science/Classification_in_Python/Images/"

def test_time():
    time1 = ex1.time()
    time2 = ex2.time()
    assert isinstance(time1, np.ndarray)
    assert np.shape(time1) == (68, 20000)
    assert np.shape(time2) == (43, 20000)
    for sweep in time1:
        assert len(sweep) == 20000

def test_data():
    data = ex1.data()
    assert isinstance(data, np.ndarray)
    assert np.shape(data) == (68, 20000)
    for sweep in data:
        assert len(sweep) == 20000

def test_commands():
    commands1 = ex1.commands()
    assert isinstance(commands1, np.ndarray)
    assert np.shape(commands1) == (68, 20000)
    for sweep in commands1:
        assert len(sweep) == 20000

def test_nsweeps():
    assert ex1.nsweeps() == 68
    assert ex2.nsweeps() == 43

def test_sweeps():
    for swp_df in ex1.sweeps():
        assert isinstance(swp_df, pd.DataFrame)

def test_sweep():
    swp_df = ex1.sweep(10)
    assert isinstance(swp_df, pd.DataFrame)
    assert 'time' in swp_df.columns
    assert 'data' in swp_df.columns
    assert 'commands' in swp_df.columns

def test_count_spikes():
    numspikes = ex1.count_spikes()
    assert numspikes[10] == 5

def test_detect_spikes():
    pass



def test_select_sweep_by_current_inj():
    sweep_index = ex2.select_sweep_by_current_inj(.3, 100)
    assert {0, 6, 15}.issubset(sweep_index)
    assert 16  not in sweep_index
    assert isinstance(sweep_index, np.ndarray) 

    sweep_index = ex2.select_sweep_by_current_inj(.3, 1)
    assert type(sweep_index[0]) == np.int64
    assert {0, 6, 14, 15, 16, 17}.issubset(sweep_index)
    assert 1 not in sweep_index

def test_select_sweep_by_spike_count():
    sweep_index = ex2.select_sweep_by_spike_count(3)
    assert type(sweep_index[0]) == np.int64
    assert isinstance(sweep_index, np.ndarray)
    assert {14, 34}.issubset(sweep_index)
    assert 1 not in sweep_index

def test_select_sweep_by_sweep_time():
    sweep_index = ex2.select_sweep_by_sweep_time(150)
    assert type(sweep_index[0]) == np.int64
    assert isinstance(sweep_index, np.ndarray)
    assert max(sweep_index) == 22

def test_current_inj_waveforms():
    command_waveform_df2 = ex2.current_inj_waveforms()
    assert {
        'sweep_index', 'onset_pnt', 'offset_pnt',
        'onset_time', 'offset_time',  'amplitude'
        }.issubset(command_waveform_df2.columns)
    #print(f"\n{command_waveform_df2.head()}")

def test_selection_by_multiple_criteria():
    idx1 = ex2.select_sweep_by_spike_count(5)
    idx2 = ex2.select_sweep_by_current_inj(duration=.3,amplitude= 1)
    idx3 = ex2.select_sweep_by_sweep_time(stop_time= 3.5 * 60)
    sweeps_to_plot = (intersect_all([idx1, idx2, idx3]))
    assert {16, 36, 37}.issubset(sweeps_to_plot)
    assert 1 not in sweeps_to_plot
    
    #ex_5APsweep = ex2.sweep(sweeps_to_plot[0])
    #ex_5APsweep.to_pickle("tests/data/5APsweep.pkl")

def detect_spikes():
    assert isinstance(ex2.detect_spikes(), list)
