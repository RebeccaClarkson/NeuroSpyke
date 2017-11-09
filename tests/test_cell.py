from neurospyke.sweep import Sweep
from neurospyke.utils import load_cells
from neurospyke.query import Query
from neurospyke.response import Response
import numpy as np
import pandas as pd

data_dir_path = "tests/data/initial_examples/*.mat"
cells = load_cells(data_dir_path)
query = Query(cells); query.run()
cell1 = query.cells[0]; cell2 = query.cells[1]

####################################################################################################
################################   DESCRIPTIVE  PROPERTIES    ######################################
####################################################################################################

def test_time():
    time1 = cell1.time()
    time2 = cell2.time()
    assert isinstance(time1, np.ndarray)
    assert np.shape(time1) == (68, 20000)
    assert np.shape(time2) == (43, 20000)
    for sweep in time1:
        assert len(sweep) == 20000

def test_data():
    data = cell1.data()
    assert isinstance(data, np.ndarray)
    assert np.shape(data) == (68, 20000)
    for sweep in data:
        assert len(sweep) == 20000

def test_commands():
    commands1 = cell1.commands()
    assert isinstance(commands1, np.ndarray)
    assert np.shape(commands1) == (68, 20000)
    for sweep in commands1:
        assert len(sweep) == 20000

def test_nsweeps():
    assert cell1.nsweeps() == 68
    assert cell2.nsweeps() == 43

def test_sweeps():
    for swp_obj in cell1.sweeps():
        assert isinstance(swp_obj, Sweep)

def test_sweep():
    swp_obj = cell1.sweep(10)
    assert isinstance(swp_obj, Sweep)

def test_sweep_df():
    sweep_df = cell1.sweep_df(10)
    assert 'time' in sweep_df.columns
    assert 'data' in sweep_df.columns
    assert 'commands' in sweep_df.columns
    assert 'sweep_time' in sweep_df.columns

####################################################################################################
##################################   RUN QUERY, GET DATAFRAMES  ####################################
####################################################################################################

def test_run():
    results1 = cell1.run()
    results2 = cell2.run()
    assert isinstance(results1, pd.DataFrame)
    assert isinstance(results2, pd.DataFrame)

def test_calc_mean_response_properties_df():
    data_dir_path = "tests/data/initial_examples/*.mat"
    cells = load_cells(data_dir_path)
    response_criteria = {'curr_duration': .3, 'num_spikes': 5}
    response_properties = ['delta_thresh']
    query = Query(cells, response_criteria=response_criteria, response_properties=response_properties)
    query.run()
    cell1 = query.cells[0]
    mean_df = cell1.calc_mean_response_properties_df()

    assert isinstance(mean_df, pd.DataFrame)
    assert len(mean_df.index) == 1
    spike_cols = [s for s in mean_df.columns if 'delta_thresh' in s]
    assert len(spike_cols) == 5

def test_response_properties_df():
    data_dir_path = "tests/data/initial_examples/*.mat"
    cells = load_cells(data_dir_path)
    response_criteria = {'curr_duration': .3, 'num_spikes': 5}
    response_properties = ['APmax_vals']
    query = Query(cells, response_criteria=response_criteria, response_properties=response_properties)
    query.run()
    cell1 = query.cells[0]
    results_df = cell1.response_properties_df()
    APmax_columns = [s for s in results_df.columns if 'APmax' in s]
    assert isinstance(results_df, pd.DataFrame)
    assert len(APmax_columns) == 5
    assert len(results_df.index) == 7 # 7 sweeps with 5 APs

####################################################################################################
#################################   SAG/REBOUND PROPERTIES    ######################################
####################################################################################################

data_dir_path = "tests/data/more_cells/*.mat"
response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
cell_properties = ['reb_delta_t']
cells = load_cells(data_dir_path)
query = Query(cells, response_criteria=response_criteria, cell_properties=cell_properties)
query.run()
reb_ex_cell = [query.cells[0]][0]

def test_calc_reb_delta_t():
    reb_ex_cell.calc_reb_delta_t()

#def test_calc_max_rebound_amp_and_idx():
#    max_val = response_obj_rebound.calc_max_rebound_amp()
#    max_time = response_obj_rebound.calc_max_rebound_time()
#    print(max_time, max_val)

####################################################################################################
###############################   GET AVERAGE RESPONSE SWEEP   #####################################
####################################################################################################

def test_average_response():
    data_dir_path = "tests/data/more_cells/*.mat"
    response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
    cell_properties = ['reb_delta_t']
    cells = load_cells(data_dir_path)
    query = Query(cells, response_criteria=response_criteria, cell_properties=cell_properties)
    query.run()
    reb_ex_cell = [query.cells[0]][0]
    
    response_obj = reb_ex_cell.average_response()
    assert isinstance(response_obj, Response)
    assert response_obj.amplitude == -400

    response_sweep_df = response_obj.sweep.sweep_df
    assert np.isclose(response_sweep_df['sweep_time'][0], 174.43)
