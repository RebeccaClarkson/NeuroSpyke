from neurospyke.query import Query
from neurospyke.sweep import Sweep
from neurospyke.utils import load_cells
import pandas as pd

response_criteria = [('curr_duration', .3), ('num_spikes', 5)]
response_properties = ['APmax_vals']
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


ex_5APsweep = Sweep(ex_5APsweep_df, cell=cell1)
ex_2inj_sweep = Sweep(ex_2inj_sweep_df, cell=cell2)


def test_current_inj_waveforms():
    current_inj_list_ex_2inj = ex_2inj_sweep.current_inj_waveforms()
    assert isinstance(current_inj_list_ex_2inj[0], dict)
    assert len(current_inj_list_ex_2inj) == 2

    current_inj_list_ex_5APsweep = ex_5APsweep.current_inj_waveforms()
    assert len(current_inj_list_ex_5APsweep) == 1


def test_plot():
    ex_5APsweep.plot(f"{image_save_filepath}response_plot.png")
    ex_2inj_sweep.plot(f"{image_save_filepath}response_plot2.png")

def test_run():
    result_df = ex_5APsweep.run()
    assert isinstance(result_df, pd.DataFrame)
    print(f"\nThe result of the sweep is \n{result_df}")
