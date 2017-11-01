from neurospyke.query import Query
from neurospyke.sweep import Sweep
from neurospyke.response import Response
from neurospyke.utils import load_cells
import pandas as pd
import numpy as np

response_criteria = {'curr_duration': .3, 'num_spikes': 5, 'sweep_time': '<150'}
response_properties = ['dVdt_pct_APamp__20__rising']
data_dir_path = "tests/data/initial_examples/*.mat"
cells = load_cells(data_dir_path)
query1 = Query(cells, response_criteria=response_criteria, 
        response_properties=response_properties)
query1.run()

cell1 = query1.cells[0]
cell2 = query1.cells[1]

ex_5APsweep_df = cell1.sweep_df(16)
ex_2inj_sweep_df = cell2.sweep_df(0)

image_save_filepath = "tests/data/images/"


ex_5AP_sweep_obj = Sweep(ex_5APsweep_df, cell=cell1) # cell_name = 010417-1, sweep_idx = 16 (sweep 17)
ex_2inj_sweep_obj = Sweep(ex_2inj_sweep_df, cell=cell2) # cell_name = 041015A, sweep_idx = 0 (sweep 1)
response_obj1 = Response(ex_2inj_sweep_obj.current_inj_waveforms()[0], ex_2inj_sweep_obj)
response_obj_5AP = Response(ex_5AP_sweep_obj.current_inj_waveforms()[0], ex_5AP_sweep_obj)
#ex_5AP_sweep_obj.plot(image_save_filepath + '5APs')

def test_criteria_priority():
    criteria = response_obj_5AP.criteria_priority()
    assert criteria[0] == 'sweep_time'



def test_calc_val_pct_APamplitude():
    calc_vals = response_obj_5AP.calc_val_pct_APamp(percent=20)
    known_vals = np.array([-25.1947, -24.1427, -24.5680, -24.9613, -24.7053])
    assert np.allclose(calc_vals, known_vals)

def test_calc_dVdt_rising_pct_APamplitude():
    calc_vals = response_obj_5AP.calc_dVdt_pct_APamp(percent=20, direction='rising')
    known_vals = [263.6667,265.6000,291.0000,228.5333,243.1333] 
    assert np.allclose(calc_vals, known_vals)
    calc_vals = response_obj_5AP.calc_dVdt_pct_APamp(percent=20, direction='falling')
    known_vals = [-54.6667,-28.3333,-33.2000,-38.0667,-38.0667]
    assert np.allclose(calc_vals, known_vals)

def test_calc_delta_thresh():
    calc_vals = response_obj_5AP.calc_delta_thresh()
    print(calc_vals)
    known_vals = np.array([0, 2.3400, 1.1733, 0.7800, 1.1733])
    assert np.allclose(calc_vals, known_vals, atol=1e-4)

def test_calc_threshold_and_vals():
    calc_idxs, calc_vals = response_obj_5AP.calc_threshold_idx_and_vals()
    known_idxs = np.array([2796, 3091, 4050, 5328, 6828])
    known_vals = np.array([-43.5533, -41.2133, -42.3800, -42.7733, -42.3800])
    assert np.allclose(calc_idxs, known_idxs)
    assert np.allclose(calc_vals, known_vals)

def test_AP_amplitudes():
    calc_vals = response_obj_5AP.calc_AP_amplitudes()
    known_vals = np.array([91.7933, 85.3533, 89.0600, 89.0600, 88.3733])
    assert np.allclose(calc_vals, known_vals)


def test_calc_AHP_idx_and_val():
    calc_idx, calc_vals = response_obj_5AP.calc_AHP_idx_and_vals()

    known_vals = np.array([-47.7533, -47.8533,-50.1000, -51.2667])
    assert np.allclose(calc_vals, known_vals)
    known_idx = np.array([2863, 3528, 4342, 5810])
    assert np.allclose(calc_idx, known_idx)

def test_calc_points_per_ms():
    points_per_ms = response_obj1.calc_points_per_ms()
    assert points_per_ms == 20 

def test_calc_spike_points():
    spike_points = response_obj1.calc_spike_points()
    assert {2968,3465,5174,7308}.issubset(spike_points)

def test_calc_num_spikes():
    num_spikes = response_obj_5AP.calc_num_spikes()
    assert num_spikes == 5

def test_calc_curr_duration():
    curr_duration = response_obj_5AP.calc_curr_duration()
    print(curr_duration)

def test_calc_or_read_from_cache():
    criteria = ['num_spikes']
    #response_obj1.debug_cache() 
    for criterion in criteria:
        response_obj1.calc_or_read_from_cache(criterion)
        assert criterion in response_obj1._cache
    #response_obj1.debug_cache()

def test_invalid_name_raises_exception():
    try: 
        response_obj1.calc_or_read_from_cache('invalid_name') 
        assert False
    except Exception as e:
        assert "calc_invalid_name" in str(e)

def test_calc_properties():
    assert isinstance(response_obj1.calc_properties(['num_spikes']), dict)
    assert response_obj1.calc_properties(['num_spikes'])['num_spikes'] == 4

def test_calc_ISI():
    ISIs = response_obj1.calc_ISIs()
    assert {25,85,107}.issubset([round(ISI) for ISI in ISIs])
    assert not {30}.issubset([round(ISI) for ISI in ISIs])
    assert len(ISIs) == 3
    
    ISIs = response_obj_5AP.calc_ISIs()
    assert len(ISIs) == 4

def test_calc_APmax_idx_and_val():
    results = response_obj1.calc_APmax_idx_and_val()
    assert {2975, 3473, 5182, 7316}.issubset(results[0])
    assert {47, 42, 44, 43}.issubset(np.around(results[1]))

    results = response_obj_5AP.calc_APmax_idx_and_val()
    assert len(results[0]) == 5

def test_run():
    results_df = response_obj_5AP.run()
    assert isinstance(results_df, pd.DataFrame)
    assert results_df.shape[0] == 1
    print(f"\nResults of run: \n {results_df}")
