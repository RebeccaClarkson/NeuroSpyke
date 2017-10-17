from neurospyke.experiment import Experiment
import numpy as np

data_dir_path = "/Users/Becky/Dropbox/Data_Science/Classification_in_Python/Python_Files/tests/data/"
criteria = [('curr_duration', .3), ('num_spikes', 4)]
property_names = ['APmax_val']
ex1 = Experiment(criteria, property_names)

def test_load_cells():
    #print(ex1.cells)
    ex1.load_cells(data_dir_path)
    #print(ex1.cells)

def test_run():
    assert len(ex1.cells) == 2
    result_df = ex1.run() 
    print("")
    pretty_print_df(result_df)

def test_describe():
    print(ex1.describe())

def pretty_print_df(df):
    new_df = df.copy()
    for col in df:
        new_df[col] = pretty_print_series(df[col])
    print(new_df)
        
def pretty_print_series(series):
    new_series = series.copy()
    for item in series.iteritems():
        idx = item[0]
        vals = item[1]
        if isinstance(vals, np.ndarray):
            round_vals = np.around(vals, 2)
            new_series[idx] = round_vals
    return new_series
