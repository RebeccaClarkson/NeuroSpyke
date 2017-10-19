from neurospyke.query import Query
from neurospyke.sweep import Sweep
from neurospyke.utils import load_cells
import numpy as np
import pandas as pd


response_criteria = {'curr_duration': .3, 'num_spikes': 5}
response_properties = ['APmax_val', 'doublet_index']
data_dir_path = "tests/data/*.mat"
cells = load_cells(data_dir_path)
query1 = Query(cells, response_criteria=response_criteria, 
        response_properties=response_properties)
query1.run()
ex1 = query1.cells[0]
ex2 = query1.cells[1]
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
    for swp_obj in ex1.sweeps():
        assert isinstance(swp_obj, Sweep)

def test_sweep():
    swp_obj = ex1.sweep(10)
    assert isinstance(swp_obj, Sweep)

def test_sweep_df():
    sweep_df = ex1.sweep_df(10)
    assert 'time' in sweep_df.columns
    assert 'data' in sweep_df.columns
    assert 'commands' in sweep_df.columns
    assert 'sweep_time' in sweep_df.columns

def test_response_properties_df():
    results_df = ex1.response_properties_df()
    assert isinstance(results_df, pd.DataFrame)
    APmax_columns = [s for s in results_df.columns if 'APmax' in s]
    assert len(APmax_columns) == 5
    assert len(results_df.index) == 7 # 7 sweeps with 5 APs
    print(f"""\n\nResponse properties dataframe for ex1 ({ex1.calc_cell_name()}) is: 
            \n{results_df}""")

def test_calc_mean_response_properties_df():
    mean_df = ex1.calc_mean_response_properties_df()
    assert isinstance(mean_df, pd.DataFrame)
    assert len(mean_df.index) == 1
    APmax_columns = [s for s in mean_df.columns if 'APmax' in s]
    assert len(APmax_columns) == 5

def test_run():
    results1 = ex1.run()
    results2 = ex2.run()
    assert isinstance(results1, pd.DataFrame)
    assert isinstance(results2, pd.DataFrame)
    print(f"\nEx2 results for run() are \n{results2}")
