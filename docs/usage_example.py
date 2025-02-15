from neurospyke.classify_cell import classify_cell
from neurospyke.plot_df_utils import D1_D3_scatter_subplots
from neurospyke.query import Query
from neurospyke.utils import concat_dfs_by_index 
from neurospyke.utils import load_cell
from neurospyke.utils import load_cells 
from neurospyke.utils import reorder_df 
from tabulate import tabulate

cell_file_pattern = 'docs/example_cells/*.mat' 
output_dir = 'docs/output/'

""" Load example cells and run queries """
example_cells = load_cells(cell_file_pattern)

# Query 1 
response_criteria = [('sweep_time', '<150'), ('curr_duration',.3), ('num_spikes', 5)]
response_properties = [
    'num_spikes', 
    'doublet_index', 
    'delta_thresh', 
    'dVdt_pct_APamp__20__rising'
    ]

query1 = Query.create_or_load_from_cache(
        example_cells, 
        response_criteria=response_criteria, 
        response_properties=response_properties,
        )
df1 = query1.mean_df

# Plot example 5 AP sweep
query1.cells[0].plot_sweeps(filepath=output_dir + '5AP_example.png')

# Query 2
response_criteria = [('curr_duration', .12), ('curr_amplitude', -400)]
calculated_cell_properties = ['reb_delta_t', 'sag_fit_amplitude'] 
query2 = Query.create_or_load_from_cache(
        example_cells, 
        response_criteria=response_criteria, 
        cell_properties=calculated_cell_properties,
        )
df2 = query2.mean_df

# Plot example reb_delta_t sweep
query2.cells[0].plot_reb_delta_t(filepath=output_dir + 'example_reb_delta_t.png')

""" Combine resulting dataframes """

# Combined resulting dataframes for both queries
combined_df = concat_dfs_by_index(df1, df2)
example_cells_df = reorder_df(combined_df, ['genetic_marker', 'ca_buffer', 'num_spikes'])

print(f"\n\nCombined query results:\n {example_cells_df.head()}")

# Get tabular format for README file
with open(output_dir + 'example_cells_df.txt', 'w') as outputfile:
        outputfile.write(tabulate(example_cells_df.head(),headers='keys', tablefmt="pipe"))



""" Plot data from example cells """
comparisons = [
        ('sag_fit_amplitude', 'reb_delta_t'), 
        ('doublet_index', 'delta_thresh4'),
        ('doublet_index', 'dVdt_pct_APamp__20__rising4'),
        ('delta_thresh4', 'dVdt_pct_APamp__20__rising4'), 
        ]
D1_D3_scatter_subplots(example_cells_df, comparisons, 'EGTA',  output_path=output_dir + 'D1_vs_D3_ephys.png')


""" Classify a cell according to published classifier """
cell_to_classify = load_cell('docs/example_cells/082615-8.mat')
cell_type = classify_cell(cell_to_classify, filepath=output_dir + 'example_classified_cell.png')
print(f"Cell {cell_to_classify.calc_cell_name()} is Type {cell_type}")
