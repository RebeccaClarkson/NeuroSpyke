from neurospyke.query import Query
from neurospyke.utils import load_cells
from neurospyke.utils import concat_dfs_by_index
from neurospyke.utils import reorder_df

cell_file_pattern = 'docs/ExampleCells/*.mat' 
example_cells = load_cells(cell_file_pattern)

# Query 1 
response_criteria = {'curr_duration':.3, 'num_spikes': 5}
response_properties = ['doublet_index', 'num_spikes']
query1 = Query(example_cells, response_criteria=response_criteria, 
        response_properties=response_properties)
df1 = query1.run()

# Query 2
response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
calculated_cell_properties = ['reb_delta_t'] 
query2 = Query(example_cells, response_criteria=response_criteria, 
        cell_properties=calculated_cell_properties)
df2 = query2.run()

# Combined resulting dataframes for both queries
combined_df = concat_dfs_by_index(df1, df2)
example_cells_df = reorder_df(combined_df, ['genetic_marker', 'ca_buffer', 'num_spikes'])

print(f"\n\nCombined query results:\n {example_cells_df}")

# Save output dataframe
example_cells_df.to_pickle('docs/output/example_cells_df.pkl')

