from neurospyke.query import Query
from neurospyke.utils import concat_dfs_by_index 
from neurospyke.utils import load_cells 
from neurospyke.utils import reorder_df 
from neurospyke.utils import rgb_colors
from tabulate import tabulate
import matplotlib.pyplot as plt

cell_file_pattern = 'docs/example_cells/*.mat' 
output_dir = 'docs/output/'

""" Load example cells """
example_cells = load_cells(cell_file_pattern)



"""Run two queries """
# Query 1 
response_criteria = {'curr_duration':.3, 'num_spikes': 5}
response_properties = ['doublet_index', 'delta_thresh', 'num_spikes']
query1 = Query.create_or_load_from_cache(example_cells, response_criteria=response_criteria, 
        response_properties=response_properties)
df1 = query1.mean_df

# Plot example 5 AP sweep
#TODO 

# Query 2
response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
calculated_cell_properties = ['reb_delta_t'] 
query2 = Query.create_or_load_from_cache(example_cells, response_criteria=response_criteria, 
        cell_properties=calculated_cell_properties)
df2 = query2.mean_df

# Plot example reb_delta_t sweep  
query2.cells[0].plot_reb_delta_t(output_dir + 'example_reb_delta_t.png')



""" Combine resulting dataframes """
# Combined resulting dataframes for both queries
combined_df = concat_dfs_by_index(df1, df2)
example_cells_df = reorder_df(combined_df, ['genetic_marker', 'ca_buffer', 'num_spikes'])

print(f"\n\nCombined query results:\n {example_cells_df}")
# Get tabular format for README file
with open(output_dir + 'example_cells_df.txt', 'w') as outputfile:
        outputfile.write(tabulate(example_cells_df,headers='keys', tablefmt="pipe"))

D1_cells = example_cells_df[example_cells_df['genetic_marker'] == 'D1']
D3_cells = example_cells_df[example_cells_df['genetic_marker'] == 'D3']



""" Plot data from example cells """
# Plot rebound time constant vs. doublet index
plt.figure()
D1_plot = plt.scatter(D1_cells['doublet_index'], D1_cells['reb_delta_t'],
        marker = 'o', color = 'k', label='D1')
D3_plot = plt.scatter(D3_cells['doublet_index'], D3_cells['reb_delta_t'],
        marker = 'o', color = rgb_colors['dodgerblue'] , label='D3')

plt.xlabel('doublet index (ISI2/ISI1)'); plt.ylabel('rebound time constant (ms)')
plt.xlim([0,14]); plt.ylim([20, 50])
plt.legend()
plt.savefig(output_dir + 'reb_vs_doublet_example_plot.png')

# Plot change in threshold from 1st to last AP vs doublet index
plt.figure()
D1_plot = plt.scatter(D1_cells['doublet_index'], D1_cells['delta_thresh4'],
        marker = 'o', color = 'k', label='D1')
D3_plot = plt.scatter(D3_cells['doublet_index'], D3_cells['delta_thresh4'],
        marker = 'o', color = rgb_colors['dodgerblue'] , label='D3')

plt.xlabel('doublet index (ISI2/ISI1)'); plt.ylabel('delta threshold')
plt.legend()
plt.savefig(output_dir + 'delta_thresh_vs_doublet_example_plot.png')
