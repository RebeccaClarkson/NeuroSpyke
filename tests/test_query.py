from neurospyke.query import Query
from neurospyke.cell import Cell
from neurospyke.utils import load_cells
import pandas as pd
import numpy as np

response_criteria = {'curr_duration': .3, 'num_spikes': 5}
response_properties = ['num_spikes', 'APmax_vals', 'doublet_index', 
                        'dVdt_pct_APamp_last_spike__20__rising__5', 'dVdt_pct_APamp__20__rising',
                        'delta_thresh', 'delta_thresh_last_spike__5']

data_dir_path = "tests/data/initial_examples/*.mat"
cells = load_cells(data_dir_path)

ex_query1 = Query(cells, response_criteria=response_criteria, 
        response_properties=response_properties)

def test_run():
    df1 = ex_query1.run()
    print(f"\nResult of test_run: \n {df1}") 

def test_last_spike_query():
    df1 = ex_query1.run()
    assert np.allclose(df1['dVdt_pct_APamp__20__rising4'], 
            df1['dVdt_pct_APamp_last_spike__20__rising__5'])
    assert np.allclose(df1['delta_thresh4'], 
            df1['delta_thresh_last_spike__5'])
    

def test_query_properties():
    print(ex_query1.query_properties())
    assert 'cell_criteria', 'cell_names' in ex_query1.query_properties()
    assert isinstance(ex_query1.query_properties(), str)

def test_query_id():
    assert isinstance(ex_query1.query_id(), str)

def test_query_cache_filename():
    print(ex_query1.query_cache_filename())
    assert ex_query1.query_id() in ex_query1.query_cache_filename()

def test_load_cells():
    assert isinstance(cells[0], Cell)
    assert len(cells) == 2

def test_create_or_load_from_cache():
    new_query = Query.create_or_load_from_cache(cells, 
            response_criteria={'curr_duration': .3, 'num_spikes': 5}, 
            response_properties=['num_spikes', 'delta_thresh'])
    print(f"\n New query created, results: \n {new_query.mean_df}")
    print(f"\n Next will try to create again, see if loads from cache")

    new_query2 = Query.create_or_load_from_cache(cells, 
            response_criteria={'curr_duration': .3, 'num_spikes': 5},
            response_properties=['num_spikes', 'delta_thresh'])

    print(f"\n new_query2: \n {new_query2.mean_df}")
    


def test_query_with_descriptive_cell_properties():
    new_query = Query(cells)
    new_query.run()
    df = new_query.mean_df
    print(f"\n{df}")
    assert len(df) == 2
    assert {'genetic_marker', 'ca_buffer'}.issubset(df.columns)
    assert {'010417-1', '041015A'}.issubset(df.index)

def test_query_with_numeric_response_criteria_and_properties():
    response_criteria = {'curr_duration': .3, 'num_spikes': 5}
    response_properties = ['APmax_vals', 'doublet_index']
    new_query = Query(cells, response_criteria=response_criteria, 
            response_properties=response_properties)
    df = new_query.run()
    assert {'genetic_marker', 'ca_buffer'}.issubset(df.columns)
    assert {'010417-1', '041015A'}.issubset(df.index)
    print(df.head())
    APmax_columns = [s for s in df.columns if 'APmax' in s]
    assert len(APmax_columns) == 5
    print(f"\n{df}")


def test_query_with_no_responses():
    response_criteria = {'curr_duration': .3, 'num_spikes': 4}
    response_properties = ['num_spikes', 'APmax_vals', 'doublet_index']
    query2 = Query(cells, response_criteria=response_criteria, 
            response_properties=response_properties)
    df2 = query2.run()
    print(f"\n\ndf with cell with no responses for criteria: \n{df2}")

def test_combining_queries():
    response_criteria = {'curr_duration': .3, 'num_spikes': 5}
    response_properties = ['num_spikes','APmax_vals', 'doublet_index']
    query1 = Query(cells, response_criteria=response_criteria, 
            response_properties=response_properties)
    df1 = query1.run()
    #print(f"\n\nQuery 1 is: \n{df1}")
    
    response_criteria = {'curr_duration': .3, 'num_spikes': 6}
    response_properties = ['num_spikes', 'APmax_vals', 'doublet_index']
    query2 = Query(cells, response_criteria=response_criteria, 
            response_properties=response_properties)
    df2 = query2.run()
    #print(f"\n\nQuery 2 is: \n{df2}")
    combined_df = pd.concat([df1, df2])

    important = ['genetic_marker', 'ca_buffer', 'num_spikes']
    reordered = important + [c for c in combined_df.columns if c not in important]
    combined_df = combined_df[reordered]
    print(f"\n\nCombined query results:\n {combined_df}")
    


def test_describe():
    print(ex_query1.describe())

def test_query_with_calculated_cell_properties():
    # TODO: need to first put methods in place to get averaged sweep
    #calculated_cell_properties = ['sag_amplitude']
    #response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
    pass


