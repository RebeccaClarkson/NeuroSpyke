import pandas as pd
import matplotlib as mpl
mpl.use('TkAgg')
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
import matplotlib.pyplot as plt

D1_and_D3_df = pd.read_pickle('tests/data/D1_and_D3_cells/D1_and_D3_df')
print(f"\n{D1_and_D3_df}")

D1_cells = D1_and_D3_df[D1_and_D3_df['genetic_marker'] == 'D1']
D3_cells = D1_and_D3_df[D1_and_D3_df['genetic_marker'] == 'D3']

x1 = D1_cells['doublet_index']; y1 = D1_cells['reb_delta_t']
x2 = D3_cells['doublet_index']; y2 = D3_cells['reb_delta_t']

plt.figure()
plt.plot(x1, y1, 'ko', x2, y2, 'bo')
plt.xlabel('doublet index (ISI2/ISI1)')
plt.ylabel('rebound time constant (ms)')
plt.xlim([0,14]); plt.ylim([20, 50])
plt.legend({'D1', 'D3'})
plt.show()
