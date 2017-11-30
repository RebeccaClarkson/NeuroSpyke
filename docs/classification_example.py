from neurospyke.plot_df_utils import rgb_colors
from neurospyke.query import Query
from neurospyke.utils import concat_dfs_by_index 
from neurospyke.utils import load_cells 
from neurospyke.utils import reorder_df 
from scipy.stats import norm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

cell_file_pattern = 'docs/example_cells/*.mat'
output_dir = 'docs/output/' 

""" Load example cells and run queries """
example_cells = load_cells(cell_file_pattern)

""" Set response criteria and properties, run Query """
response_criteria = [('sweep_time', '<150'), ('curr_duration', .3), ('curr_amplitude', '>0')]
response_property_spike_categories = [
    'log_doublet_index_by_num_spikes', 
    'delta_thresh_last_spike', 
    'dVdt_pct_APamp_last_spike__20__rising'
    ]

spike_query = Query.create_or_load_from_cache(
        example_cells,
        response_criteria=response_criteria,
        response_property_spike_categories=response_property_spike_categories)

response_criteria = [('curr_duration', .12), ('curr_amplitude', -400)]
calculated_cell_properties = ['reb_delta_t', 'sag_fit_amplitude'] 
sag_reb_query = Query.create_or_load_from_cache(
        example_cells, 
        response_criteria=response_criteria, 
        cell_properties=calculated_cell_properties,
        )

""" Combine resulting dataframes """
combined_df = concat_dfs_by_index(spike_query.mean_df, sag_reb_query.mean_df)
example_cells_df = reorder_df(combined_df, ['genetic_marker', 'ca_buffer'])
example_cells_df.to_pickle(output_dir + 'example_cells_df.pkl')

example_cells_df = pd.read_pickle(output_dir + 'example_cells_df.pkl')
example_cell_to_classify = example_cells_df.iloc[2]

""" Apply published classifier to this data """
fig = plt.figure()
LDA_coeff = pd.read_csv("neurospyke/data/LDA_coefficients.csv")
LDA_mean_values = pd.read_csv("neurospyke/data/LDA_mean_values.csv")
LDA_std_values = pd.read_csv("neurospyke/data/LDA_std_values.csv")
LDA_dist_values = pd.read_csv("neurospyke/data/LDA_distributions.csv")

i = 1
for num_spikes in range(3, 9):

    ax = fig.add_subplot(2, 3, i)

    all_variables = ['reb_delta_t', 'sag_fit_amplitude',
            'log_doublet_index_by_num_spikes', 
            'delta_thresh_last_spike', 
            'dVdt_pct_APamp_last_spike__20__rising']

    current_variables = [variable + f'__{num_spikes}' if 'spike' in variable 
            else variable for variable in all_variables]
    ca_buffer = example_cell_to_classify['ca_buffer']

    def get_LDA_data(df):
        ca_buffer_rows = df['ca_buffer']==ca_buffer
        num_spikes_rows = df['num_spikes']==num_spikes
        return df.loc[ca_buffer_rows & num_spikes_rows]
     
    lda_coeff = get_LDA_data(LDA_coeff)[all_variables].as_matrix()
    lda_intercept = get_LDA_data(LDA_coeff)['intercept'].as_matrix()
    lda_mean = get_LDA_data(LDA_mean_values)[all_variables].as_matrix()
    lda_std = get_LDA_data(LDA_std_values)[all_variables].as_matrix()

    # Example cell 
    current_cell_vals = example_cell_to_classify[['genetic_marker', 'ca_buffer'] + current_variables].copy()
    current_cell_vals.dropna(inplace=True)
    X = current_cell_vals[current_variables].as_matrix()
    y = current_cell_vals['genetic_marker']

    """ Plotting all cells """

    # All cells
    current_df = example_cells_df[['genetic_marker'] + current_variables].copy()
    current_df.dropna(inplace=True)
    current_df.to_csv(output_dir + f"{num_spikes}")
    X_all = current_df[current_variables]
    y_all = current_df['genetic_marker']

    # standardize all cells
    Xmeans = X_all.mean(); Xstd = X_all.std()
    Xs_all = (X_all-Xmeans)/Xstd
    lda_new = LDA()
    lda_new.fit(Xs_all, y_all)
    disc_scores_new = lda_new.decision_function(Xs_all)

    score_D1 = -disc_scores_new[y_all=='D1']
    score_D3 = -disc_scores_new[y_all=='D3']
    shape_D1 = np.shape(score_D1)
    shape_D3 = np.shape(score_D3)
    
    ax.scatter(score_D1, np.tile(.1, shape_D1), edgecolors='k', color='w')
    x_vals = np.arange(-10, 10, .01) 
    plt.plot(x_vals, 
            norm.pdf(x_vals, np.nanmean(score_D1), np.nanstd(score_D1)), 
            '--', color = 'k')

    ax.scatter(score_D3, np.tile(.3, shape_D3), edgecolors=rgb_colors['dodgerblue'], color='w')
    plt.plot(x_vals, 
            norm.pdf(x_vals, np.nanmean(score_D3), np.nanstd(score_D3)), 
            '--', color=rgb_colors['dodgerblue'])

    """ End plotting all cells """


    
    # Get linear discriminant fit 
    lda = LDA()
    lda.coef_ = lda_coeff
    lda.intercept_ = lda_intercept

    # standardize example cell to LDA 
    X = X.astype(float)
    if ~np.isnan(X).any():
        Xs = (X-lda_mean)/lda_std
        discriminant_score = -lda.decision_function(Xs)
    else:
        discriminant_score = np.nan 

    # plot the decision boundary
    plt.axvline(x=0,color= 'r') 

    # plot the score of the current cell
    ax.scatter(discriminant_score,  .2, edgecolors='r', color='w')
    current_LDA_dist_values = LDA_dist_values[(LDA_dist_values.num_spikes == num_spikes) & 
            (LDA_dist_values.ca_buffer == ca_buffer)]
    D1_dist_mean = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D1']['mean']
    D3_dist_mean = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D3']['mean']
    D1_dist_std = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D1']['std']
    D3_dist_std = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D3']['std']

    # plot the score distributions that established the published classifier
    x_vals = np.arange(-10, 10, .01) 
    plt.plot(x_vals, norm.pdf(x_vals, D1_dist_mean, D1_dist_std),color = 'k')
    plt.plot(x_vals, norm.pdf(x_vals, D3_dist_mean, D3_dist_std), color=rgb_colors['dodgerblue'])

    ax.set_xlabel('score')
    ax.set_xlim([-10, 8]); ax.set_ylim([0, .5])
    ax.set_title(f"{num_spikes} APs")
    i +=1

fig.set_size_inches(18.5, 10.5, forward=True)
plt.show()
