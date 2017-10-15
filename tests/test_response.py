from spyke.response import Response
import pandas as pd

ex_5APsweep_df = pd.read_pickle("tests/data/5APsweep.pkl")
assert isinstance(ex_5APsweep_df, pd.DataFrame)

image_save_filepath = "/Users/Becky/Dropbox/Data_Science/Classification_in_Python/Images/"
ex_5APsweep = Response(ex_5APsweep_df)

def test_max_sweep_amplitude():
    max_amplitude = ex_5APsweep.max_sweep_amplitude()
    assert max_amplitude == 45.7

def test_plot_response():
    ex_5APsweep.plot_response(f"{image_save_filepath}response_plot.png")

def test_spike_points():
    spike_points = ex_5APsweep.spike_points()
    assert {2728,3077,3900,5113,6450}.issubset(spike_points)
