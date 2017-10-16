from neurospyke.cell import Cell
from neurospyke.sweep import Sweep
import numpy as np

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
