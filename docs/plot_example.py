from neurospyke.utils import rgb_colors
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

example_cells_df = pd.read_pickle('docs/output/example_cells_df.pkl')
print(f"\n{example_cells_df}")


D1_cells = example_cells_df[example_cells_df['genetic_marker'] == 'D1']
D3_cells = example_cells_df[example_cells_df['genetic_marker'] == 'D3']

plt.figure()
D1_plot = plt.scatter(D1_cells['doublet_index'], D1_cells['reb_delta_t'],
        marker = 'o', color = 'k', label='D1')
D3_plot = plt.scatter(D3_cells['doublet_index'], D3_cells['reb_delta_t'],
        marker = 'o', color = rgb_colors['dodgerblue'] , label='D3')

plt.xlabel('doublet index (ISI2/ISI1)')
plt.ylabel('rebound time constant (ms)')
plt.xlim([0,14]); plt.ylim([20, 50])
plt.legend()
plt.savefig('docs/output/example_plot.png')

