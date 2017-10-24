from neurospyke.query import Query
from neurospyke.utils import load_cells
from neurospyke.utils import concat_dfs_by_index

cell_file_pattern = 'docs/ExampleCells/*.mat' 
example_cells = load_cells(cell_file_pattern)

# Query 1 
response_criteria = {'curr_duration':.3, 'num_spikes': 5}
response_properties = ['doublet_index', 'num_spikes']
query1 = Query(example_cells, response_criteria=response_criteria, 
        response_properties=response_properties)

# Query 2
response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
calculated_cell_properties = ['reb_delta_t'] 
query2 = Query(example_cells, response_criteria=response_criteria, 
        cell_properties=calculated_cell_properties)

# Run queries and combine resulting dataframes
print(f"Now processing query 1")
df1 = query1.run()
print(f"Now processing query 2")
df2 = query2.run()

combined_df = concat_dfs_by_index(df1, df2)

# Correct ordering of df columns
important = ['genetic_marker', 'ca_buffer', 'num_spikes']
reordered = important + [c for c in df1.columns if c not in important]
example_cells_df = df1[reordered]
example_cells_df = combined_df[reordered]
print(f"\n\nCombined query results:\n {example_cells_df}")

example_cells_df.to_pickle('docs/output/example_cells_df.pkl')
