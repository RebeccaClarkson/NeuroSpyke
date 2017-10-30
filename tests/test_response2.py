from neurospyke.query import Query
from neurospyke.sweep import Sweep
from neurospyke.response import Response
from neurospyke.utils import load_cells
import pandas as pd

response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
cell_properties = ['reb_delta_t']
data_dir_path = "tests/data/more_cells/*.mat"
cells = load_cells(data_dir_path)
reb_query = Query(cells, response_criteria=response_criteria,
        cell_properties=cell_properties)
reb_query.run()
cell1 = reb_query.cells[0]
reb_sweep_df = cell1.sweep_df(1)
reb_sweep_obj = Sweep(reb_sweep_df, cell=cell1)
reb_resp_obj = Response(reb_sweep_obj.current_inj_waveforms()[0], reb_sweep_obj)


image_save_path = "tests/data/images/"

reb_sweep_obj.plot(image_save_path + 'rebound_sweep')

def test_response_window():
    window_df = reb_resp_obj.window(left_window=100, right_window=130)
    assert isinstance(window_df, pd.DataFrame)
    assert 'time' in window_df.columns
    assert 'data' in window_df.columns
    assert 'commands' in window_df.columns
    assert 'sweep_time' in window_df.columns
    assert 'sweep_index' in window_df.columns
    assert window_df.index[0] == 0
    assert window_df['time'][0] == 0
    reb_window_sweep_obj = Sweep(window_df, cell1) 
    reb_window_sweep_obj.plot(image_save_path + 'rebound_window')


def test_too_big_left_window():
    try:
        reb_resp_obj.window(left_window=10000, right_window=0)
        assert False
    except Exception as e:
        assert 'Left window too big' in str(e)

def test_too_big_right_window():
    try:
        reb_resp_obj.window(left_window=0, right_window=10000)
        assert False
    except Exception as e:
        assert 'Right window too big' in str(e)
