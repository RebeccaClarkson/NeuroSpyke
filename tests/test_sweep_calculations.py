from spyke.cell import Cell
from spyke.sweep_calculations import current_inj_per_sweep 

ex1 = Cell("tests/data/ExampleCell1.mat")
ex2 = Cell("tests/data/ExampleCell2.mat")

def test_current_inj_per_sweep():
    current_inj_params_df1 = current_inj_per_sweep(ex1.sweep(10))
    current_inj_params_df2 = current_inj_per_sweep(ex2.sweep(0))
    assert {
        'sweep_index', 'onset_pnt', 'offset_pnt',
        'onset_time', 'offset_time',  'amplitude'
        }.issubset(current_inj_params_df1.columns)
    assert current_inj_params_df1.shape[0] == 1
    assert current_inj_params_df2.shape[0] == 2
   # print("\n\nExample Cell 1:")
   # print(f"\n{current_inj_params_df1}")
   # print("\n\nExample Cell 2:")
   # print(f"\n{current_inj_params_df2}")
