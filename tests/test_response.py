from neurospyke.sweep import Sweep
import pandas as pd

ex_5APsweep_df = pd.read_pickle("tests/data/5APsweep.pkl")
ex_2inj_sweep_df = pd.read_pickle("tests/data/ex_2inj_sweep.pkl")
assert isinstance(ex_2inj_sweep_df, pd.DataFrame)

ex_5AP_sweep_obj = Sweep(ex_5APsweep_df)
ex_2inj_sweep_obj = Sweep(ex_2inj_sweep_df)
response_obj1 = ex_2inj_sweep_obj.responses()[0]
response_obj_5AP = ex_5AP_sweep_obj.responses()[0]

def test_calc_spike_points():
    spike_points = response_obj_5AP.calc_spike_points()
    assert {2728,3077,3900,5113,6450}.issubset(spike_points)

def test_calc_num_spikes():
    num_spikes = response_obj_5AP.calc_num_spikes()
    assert num_spikes == 5

def test_calculate_or_read_from_cache():
    criteria = ['num_spikes']
    #response_obj1.debug_cache() 
    for criterion in criteria:
        response_obj1.calculate_or_read_from_cache(criterion)
        assert criterion in response_obj1._cache
    #response_obj1.debug_cache()

def test_invalid_name_raises_exception():
    try: 
        response_obj1.calculate_or_read_from_cache('invalid_name') 
        assert False
    except Exception as e:
        assert "calc_invalid_name" in str(e)
