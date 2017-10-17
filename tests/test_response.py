from neurospyke.sweep import Sweep
import pandas as pd
import numpy as np

ex_5APsweep_df = pd.read_pickle("tests/data/5APsweep.pkl")
ex_2inj_sweep_df = pd.read_pickle("tests/data/ex_2inj_sweep.pkl")
assert isinstance(ex_2inj_sweep_df, pd.DataFrame)

image_save_filepath = "/Users/Becky/Dropbox/Data_Science/Classification_in_Python/Images/"

ex_5AP_sweep_obj = Sweep(ex_5APsweep_df)
ex_2inj_sweep_obj = Sweep(ex_2inj_sweep_df)

response_obj1 = ex_2inj_sweep_obj.responses()[0]
response_obj_5AP = ex_5AP_sweep_obj.responses()[0]

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

def test_calc_spike_time_windows():
    pass
    #response_obj1.calc_spike_time_windows()
