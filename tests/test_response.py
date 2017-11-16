from neurospyke.query import Query
from neurospyke.response import Response
from neurospyke.sweep import Sweep
from neurospyke.utils import load_cells
import numpy as np
import pandas as pd


# load cells
data_dir_path = "tests/data/initial_examples/*.mat"
cells = load_cells(data_dir_path)

# run query, select cells to exampe
query1 = Query(cells, response_criteria = {'curr_duration':.3, 'sweep_time': '>0'})
query1.run()
cell1 = query1.cells[0]; cell2 = query1.cells[1]

# response with 5 APs in response to a current injection
# cell_name = 010417-1, sweep_idx = 16 
sweep_obj_5AP = Sweep(cell1.sweep_df(16), cell=cell1) 
response_obj_5AP = Response(sweep_obj_5AP.current_inj_waveforms()[0], sweep_obj_5AP)

# response with -400 pA current injection for sag/rebound
# cell_name = 010417-1, sweep_idx = 23 
sweep_obj_rebound = Sweep(cell1.sweep_df(23), cell=cell1)
response_obj_rebound = Response(sweep_obj_rebound.current_inj_waveforms()[0], sweep_obj_rebound)

# response with both positive and negative current injections
# cell_name = 041015A, sweep_idx = 0
sweep_obj_2inj = Sweep(cell2.sweep_df(0), cell=cell2) 
response_obj_2inj = Response(sweep_obj_2inj.current_inj_waveforms()[0], sweep_obj_2inj) 

def test_criteria_priority():
    print(f"\n\n\t\tSTART TESTS")
    criteria = response_obj_5AP.criteria_priority()
    assert criteria[0] == 'sweep_time'

def test_meets_criterion():
    assert response_obj_5AP.meets_criterion(('curr_amplitude', '>0'))
    assert not response_obj_5AP.meets_criterion(('curr_amplitude', -400))
    try: 
        response_obj_2inj.calc_or_read_from_cache('invalid_name') 
        assert False
    except Exception as e:
        assert "calc_invalid_name" in str(e)
    
def test_calc_properties():
    assert isinstance(response_obj_2inj.calc_properties(['num_spikes']), dict)
    assert response_obj_2inj.calc_properties(['num_spikes'])['num_spikes'] == 4

def test_run():
    results_df = response_obj_5AP.run()
    assert isinstance(results_df, pd.DataFrame)
    assert results_df.shape[0] == 1

def test_calc_or_read_from_cache():
    criteria = ['num_spikes']
    for criterion in criteria:
        response_obj_2inj.calc_or_read_from_cache(criterion)
        assert criterion in response_obj_2inj._cache

def test_window():
    window_df = response_obj_rebound.window(left_window=100, right_window=130)
    assert isinstance(window_df, pd.DataFrame)
    assert 'time', 'data'  in window_df.columns
    assert 'commands', 'sweep_time'  in window_df.columns
    assert 'sweep_index' in window_df.columns
    assert window_df.index[0] == 0
    assert window_df['time'][0] == 0

def test_too_big_left_window():
    try:
        response_obj_rebound.window(left_window=10000, right_window=0)
        assert False
    except Exception as e:
        assert 'Left window too big' in str(e)

def test_too_big_right_window():
    try:
        response_obj_rebound.window(left_window=0, right_window=10000)
        assert False
    except Exception as e:
        assert 'Right window too big' in str(e)
    print(f"\n\n\t\t BASIC PROPERTIES")

    
##################################################################################
###############################   BASIC PROPERTIES    ############################
##################################################################################

def test_calc_curr_duration():
    curr_duration = response_obj_5AP.calc_curr_duration()
    assert np.isclose(curr_duration, .3)

def test_calc_points_per_ms():
    points_per_ms = response_obj_2inj.calc_points_per_ms()
    assert points_per_ms == 20 
    print(f"\n\n\t\tSPIKE PROPERTIES")

##################################################################################
###############################   SPIKE PROPERTIES    ############################
##################################################################################

def test_calc_spike_points():
    spike_points = response_obj_2inj.calc_spike_points()
    assert {2968,3465,5174,7308}.issubset(spike_points)

def test_calc_num_spikes():
    assert response_obj_5AP.calc_num_spikes() == 5
    assert response_obj_rebound.calc_num_spikes() == 0

# AP max 
def test_calc_APmax_idx_and_val():
    results = response_obj_2inj.calc_APmax_idx_and_val()
    assert {2975, 3473, 5182, 7316}.issubset(results[0])
    assert {47, 42, 44, 43}.issubset(np.around(results[1]))
    results = response_obj_5AP.calc_APmax_idx_and_val()
    assert len(results[0]) == 5

# AHP
def test_calc_AHP_idx_and_val():
    calc_idx, calc_vals = response_obj_5AP.calc_AHP_idx_and_vals()
    known_vals = np.array([-47.7533, -47.8533,-50.1000, -51.2667, np.nan])
    assert np.allclose(calc_vals, known_vals, equal_nan=True)
    known_idx = np.array([2863, 3528, 4342, 5810, np.nan])
    assert np.allclose(calc_idx, known_idx, equal_nan=True)

# Threshold
def test_calc_threshold_and_vals():
    calc_idxs, calc_vals = response_obj_5AP.calc_threshold_idx_and_vals()
    known_idxs = np.array([2796, 3091, 4050, 5328, 6828])
    known_vals = np.array([-43.5533, -41.2133, -42.3800, -42.7733, -42.3800])
    assert np.allclose(calc_idxs, known_idxs)
    assert np.allclose(calc_vals, known_vals)

# AHP compared to threshold
def test_AHP_vs_threshold():
    threshold_vals = response_obj_5AP.calc_threshold_vals()
    AHP_vals = response_obj_5AP.calc_AHP_vals()
    known_vals = AHP_vals - threshold_vals
    calc_vals = response_obj_5AP.calc_AHP_vs_threshold()
    assert np.allclose(known_vals, calc_vals, equal_nan=True)

# AP amplitude
def test_AP_amplitudes():
    calc_vals = response_obj_5AP.calc_AP_amplitudes()
    known_vals = np.array([91.7933, 85.3533, 89.0600, 89.0600, 88.3733])
    assert np.allclose(calc_vals, known_vals)

def test_calc_val_pct_APamp():
    calc_vals = response_obj_5AP.calc_val_pct_APamp(percent=20)
    known_vals = np.array([-25.1947, -24.1427, -24.5680, -24.9613, -24.7053])
    assert np.allclose(calc_vals, known_vals)

# AP width
def test_calc_AP_width():
    calc_vals = response_obj_5AP.calc_AP_width(percent=50)
    known_vals = [0.85, 1.4, 1.2, 1.1, 1.1]
    assert np.allclose(calc_vals, known_vals)

# dVdt rising 
def test_calc_dVdt_rising_pct_APamplitude():
    calc_vals = response_obj_5AP.calc_dVdt_pct_APamp(percent='20', direction='rising')
    known_vals = [263.6667,265.6000,291.0000,228.5333,243.1333] 
    assert np.allclose(calc_vals, known_vals)
    calc_vals = response_obj_5AP.calc_dVdt_pct_APamp(percent='20', direction='falling')
    known_vals = [-54.6667,-28.3333,-33.2000,-38.0667,-38.0667]
    assert np.allclose(calc_vals, known_vals)
    calc_vals = response_obj_5AP.calc_dVdt_pct_APamp(percent='max', direction='rising')
    known_vals = [433.6, 345.73, 372.0667, 379.8667, 377.9333]
    assert np.allclose(calc_vals, known_vals)

def test_calc_dVdt_pct_APamp_last_spike():
    calc_val = response_obj_5AP.calc_dVdt_pct_APamp_last_spike(
            percent=20, direction='rising', num_spikes=5)
    known_val = 243.1333
    assert np.allclose(calc_val, known_val, atol=1e-4)

# delta threshold
def test_calc_delta_thresh():
    calc_vals = response_obj_5AP.calc_delta_thresh()
    known_vals = np.array([0, 2.3400, 1.1733, 0.7800, 1.1733])
    assert np.allclose(calc_vals, known_vals, atol=1e-4)

def test_calc_delta_thresh_last_spike():
    calc_val = response_obj_5AP.calc_delta_thresh_last_spike(5)
    known_val = 1.1733
    assert np.isclose(calc_val, known_val, atol=1e-4)

# ISI
def test_calc_ISI():
    ISIs = response_obj_2inj.calc_ISIs()
    assert {25,85,107}.issubset([round(ISI) for ISI in ISIs])
    assert not {30}.issubset([round(ISI) for ISI in ISIs])
    assert len(ISIs) == 3
    ISIs = response_obj_5AP.calc_ISIs()
    assert len(ISIs) == 4
    print(f"\n\n\t\tSAG/REBOUND PROPERTIES")
