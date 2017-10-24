import neurospyke; neurospyke # hack to get default inits to run
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

example_cells_df = pd.read_pickle('docs/output/example_cells_df.pkl')
print(f"\n{example_cells_df}")

with open('docs/output/example_cell_table.txt', 'w') as outputfile:
        outputfile.write(tabulate(example_cells_df,headers='keys', tablefmt="pipe"))

print(tabulate(example_cells_df.head(), headers='keys', tablefmt='pipe'))

D1_cells = example_cells_df[example_cells_df['genetic_marker'] == 'D1']
D3_cells = example_cells_df[example_cells_df['genetic_marker'] == 'D3']

x1 = D1_cells['doublet_index']; y1 = D1_cells['reb_delta_t']
x2 = D3_cells['doublet_index']; y2 = D3_cells['reb_delta_t']

plt.figure()
plt.plot(x1, y1, 'ko', x2, y2, 'bo')
plt.xlabel('doublet index (ISI2/ISI1)')
plt.ylabel('rebound time constant (ms)')
plt.xlim([0,14]); plt.ylim([20, 50])
plt.legend({'D1', 'D3'})
plt.savefig('docs/output/example_plot.png')
