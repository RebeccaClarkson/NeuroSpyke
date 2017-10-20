from neurospyke.query import Query
from neurospyke.utils import load_cells
from neurospyke.utils import concat_dfs_by_index

cell_file_pattern = 'tests/data/more_cells/*.mat' 
cells = load_cells(cell_file_pattern)

# Query 1 
response_criteria = {'curr_duration':.3, 'num_spikes': 5}
response_properties = ['doublet_index', 'num_spikes']
query1 = Query(cells, response_criteria=response_criteria, 
        response_properties=response_properties)

# Query 2
response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
calculated_cell_properties = ['reb_delta_t'] 
query2 = Query(cells, response_criteria=response_criteria, 
        cell_properties=calculated_cell_properties)

# Run queries and combine resulting dataframes
df1 = query1.run()
print(f"\ndf1 is \n{df1}")
df2 = query2.run()
print(f"\ndf2 is \n{df2}")

combined_df = concat_dfs_by_index(df1, df2)
print(f"\ncombined before reordering\n{combined_df}") 
# Correct ordering of df columns
important = ['genetic_marker', 'ca_buffer', 'num_spikes']
reordered = important + [c for c in combined_df.columns if c not in important]
combined_df = combined_df[reordered]
print(f"\n\nCombined query results:\n {combined_df}")
