from neurospyke.experiment import Experiment

data_dir_path = "/Users/Becky/Dropbox/Data_Science/Classification_in_Python/Python_Files/tests/data/"
criteria = [('num_spikes', 3)]
property_names = ['num_spikes', 'APmax_val', 'ISIs']
ex1 = Experiment(criteria, property_names)

def test_load_cells():
    #print(ex1.cells)
    ex1.load_cells(data_dir_path)
    #print(ex1.cells)

def test_run():
    assert len(ex1.cells) == 2
    result_df = ex1.run() 
    print(f"\n{result_df}")

def test_describe():
    print(ex1.describe())


