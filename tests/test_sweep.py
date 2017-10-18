from neurospyke.sweep import Sweep
import pandas as pd

ex_5APsweep_df = pd.read_pickle("tests/data/5APsweep.pkl")
ex_2inj_sweep_df = pd.read_pickle("tests/data/ex_2inj_sweep.pkl")

ex_2inj_sweep = Sweep(ex_2inj_sweep_df, property_names=['APmax_val'])
ex_5APsweep = Sweep(ex_5APsweep_df, property_names=['APmax_val'])


image_save_filepath = "/Users/Becky/Dropbox/Data_Science/Classification_in_Python/Images/"

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

def test_run_sweep():
    result_df = ex_5APsweep.run_sweep()
    assert isinstance(result_df, pd.DataFrame)
    print(f"\nThe result of the sweep for display is \n{result_df}")


