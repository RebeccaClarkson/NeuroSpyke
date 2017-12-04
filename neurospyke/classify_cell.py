from neurospyke.plot_df_utils import rgb_colors
from neurospyke.query import Query
from neurospyke.utils import concat_dfs_by_index 
from neurospyke.utils import reorder_df 
from scipy.stats import norm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def classify_cell(cell_to_classify, plot=True, filepath=None):
    
    """ Check if cell is Type 2 """
    response_criteria = [('curr_duration', .12), ('curr_amplitude', -400)]
    calculated_cell_properties = ['max_rebound_time']
    Type2_query = Query.create_or_load_from_cache(
            [cell_to_classify],
            response_criteria=response_criteria, 
            cell_properties=calculated_cell_properties,
            )
    
    if Type2_query.mean_df.max_rebound_time.values < 90:
        cell_type = 2
    
    """ Get df with variables used for published classifier """
    cell_df = classifier_df(cell_to_classify)
    
    """ Apply published classifier to this data """
    LDA_coeff = pd.read_csv("neurospyke/data/LDA_coefficients.csv")
    LDA_mean_values = pd.read_csv("neurospyke/data/LDA_mean_values.csv")
    LDA_std_values = pd.read_csv("neurospyke/data/LDA_std_values.csv")
    LDA_dist_values = pd.read_csv("neurospyke/data/LDA_distributions.csv")
    
    fig = plt.figure()
    i = 1
    cell_type = []
    for num_spikes in range(3, 9):
    
        ax = fig.add_subplot(2, 3, i)
    
        all_variables = ['reb_delta_t', 'sag_fit_amplitude',
                'log_doublet_index_by_num_spikes', 
                'delta_thresh_last_spike', 
                'dVdt_pct_APamp_last_spike__20__rising']
    
        current_variables = [variable + f'__{num_spikes}' if 'spike' in variable 
                else variable for variable in all_variables]
    
        ca_buffer = cell_df['ca_buffer'].values[0]
    
        def get_LDA_data(df):
            ca_buffer_rows = df['ca_buffer']==ca_buffer
            num_spikes_rows = df['num_spikes']==num_spikes
            return df.loc[ca_buffer_rows & num_spikes_rows]
         
        lda_coeff = get_LDA_data(LDA_coeff)[all_variables].as_matrix()
        lda_intercept = get_LDA_data(LDA_coeff)['intercept'].as_matrix()
        lda_mean = get_LDA_data(LDA_mean_values)[all_variables].as_matrix()
        lda_std = get_LDA_data(LDA_std_values)[all_variables].as_matrix()
    
        cell_vals = cell_df[['genetic_marker', 'ca_buffer'] + current_variables].copy()
        cell_vals.dropna(inplace=True)
        X = cell_vals[current_variables].as_matrix()
    
        # Get linear discriminant fit 
        lda = LDA()
        lda.coef_ = lda_coeff
        lda.intercept_ = lda_intercept
    
        current_LDA_dist_values = LDA_dist_values[(LDA_dist_values.num_spikes == num_spikes) & 
                (LDA_dist_values.ca_buffer == ca_buffer)]
        D1_dist_mean = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D1']['mean']
        D3_dist_mean = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D3']['mean']
        D1_dist_std = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D1']['std']
        D3_dist_std = current_LDA_dist_values[current_LDA_dist_values.genetic_marker == 'D3']['std']
    
        # plot the score distributions that established the published classifier
        x_vals = np.arange(-10, 10, .01) 
        ax.plot(x_vals, norm.pdf(x_vals, D1_dist_mean, D1_dist_std),color='k')
        ax.plot(x_vals, norm.pdf(x_vals, D3_dist_mean, D3_dist_std), color=rgb_colors['dodgerblue'])
    
        # plot the decision boundary and exclusion zone
        left_exclusion_border = D1_dist_mean.values - 1.64 * D1_dist_std.values
        right_exclusion_border = D3_dist_mean.values + 1.64 * D3_dist_std.values
        if left_exclusion_border > 0:
            left_exclusion_border = 0
    
        if right_exclusion_border < 0:
            right_exclusion_border = 0
    
        ax.axvline(x=0,color= 'r') 
        patch = ax.add_patch(patches.Rectangle(
            (left_exclusion_border, 0),
            abs(left_exclusion_border - right_exclusion_border),
            100)) 
        patch.set_color('grey')
        patch.set_zorder(0)
    
        if not cell_df[current_variables].isnull().values.any():
            # if none of the current values are nan, classifier for current conditions:
    
            # standardize cell 
            X = X.astype(float)
            if ~np.isnan(X).any():
                Xs = (X-lda_mean)/lda_std
                discriminant_score = -lda.decision_function(Xs)
            else:
                discriminant_score = np.nan 
    
            # plot the score of the current cell
            ax.scatter(discriminant_score,  .2, edgecolors='r', s=50, color='None', zorder=6)
    
            if discriminant_score < left_exclusion_border:
                cell_type.append(3)
                cell_ID = "Type 3"
            elif discriminant_score > right_exclusion_border:
                cell_type.append(1)
                cell_ID = "Type 3"
            else:
                cell_type.append(np.nan)
                cell_ID = "Unidentified"
        else:
            cell_ID = "Unidentified (no sweep)"
    
        ax.set_xlabel('score')
        ax.set_ylabel('probability')
        ax.set_xlim([-10, 8]); ax.set_ylim([0, .5])
        ax.set_title(f"{num_spikes} APs: {cell_ID}")
    
        i +=1
    
    cell_type = [x for x in cell_type if not np.isnan(x)]
    if len(set(cell_type)) > 1:
        cell_type_final = np.nan
        cell_ID_final = "Unidentified"
    elif set(cell_type) == {1}:
        cell_type_final = 1
        cell_ID_final = "Type 1"
    elif set(cell_type) == {3}:
        cell_type_final = 3
        cell_ID_final = "Type 3"

    plt.suptitle(f"{cell_to_classify.calc_cell_name()}: {cell_ID_final}, {ca_buffer}", fontsize=15)
    fig.set_size_inches(18.5, 10.5, forward=True)
    if filepath:
        plt.savefig(filepath, bbox_inches="tight")
    else:
        plt.show()

    return cell_type_final 

def classifier_df(cell_to_classify):
    if cell_to_classify is not list:
        cell_to_classify = [cell_to_classify]

    """ Run queries for 5 properties used in published classifier """
    response_criteria = [('sweep_time', '<150'), ('curr_duration', .3), ('curr_amplitude', '>0')]
    response_property_spike_categories = [
        'log_doublet_index_by_num_spikes', 
        'delta_thresh_last_spike', 
        'dVdt_pct_APamp_last_spike__20__rising'
        ]
    
    spike_query = Query.create_or_load_from_cache(
            cell_to_classify,
            response_criteria=response_criteria,
            response_property_spike_categories=response_property_spike_categories)
    
    response_criteria = [('curr_duration', .12), ('curr_amplitude', -400)]
    calculated_cell_properties = ['reb_delta_t', 'sag_fit_amplitude'] 
    sag_reb_query = Query.create_or_load_from_cache(
            cell_to_classify, 
            response_criteria=response_criteria, 
            cell_properties=calculated_cell_properties,
            )

    """ Combine resulting dataframes """
    combined_df = concat_dfs_by_index(spike_query.mean_df, sag_reb_query.mean_df)
    cell_df = reorder_df(combined_df, ['genetic_marker', 'ca_buffer'])

    return cell_df
