from neurospyke.query import Query
from neurospyke.sweep import Sweep
from neurospyke.response import Response
from neurospyke.utils import load_cells
import pandas as pd
import numpy as np

response_criteria = {'curr_duration': .3, 'num_spikes': 5}
response_properties = ['APmax_val', 'doublet_index']
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


ex_5AP_sweep_obj = Sweep(ex_5APsweep_df, cell=cell1)
ex_2inj_sweep_obj = Sweep(ex_2inj_sweep_df, cell=cell2)
response_obj1 = Response(ex_2inj_sweep_obj.current_inj_waveforms()[0], ex_2inj_sweep_obj)
response_obj_5AP = Response(ex_5AP_sweep_obj.current_inj_waveforms()[0], ex_5AP_sweep_obj)

ex_5AP_sweep_obj.plot(image_save_filepath + '5APs')
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
