from neurospyke.cell import Cell
from neurospyke.plot_df_utils import rgb_colors
from scipy.stats import norm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import glob 
import matplotlib.pylab as plt
import numpy as np
import os
import pandas as pd
import pickle 


cache_dir = 'cached_data/'
cell_cache_dir = cache_dir + 'cells/'
query_cache_dir = cache_dir + 'queries/'

os.makedirs(query_cache_dir, exist_ok=True)
os.makedirs(cell_cache_dir, exist_ok=True)

def calc_pickle_cell_path(mat_cell_path):
    # Cell files have unique names
    mat_name = os.path.basename(os.path.normpath(mat_cell_path))
    pickle_name = mat_name.replace('.mat', '.pickle')
    return cell_cache_dir + pickle_name 

def load_cell(mat_cell_path):
    pickle_cell_path = calc_pickle_cell_path(mat_cell_path)
    try: 
        with open(pickle_cell_path, 'rb') as f:
            cell = pickle.load(f)
            return cell
    except:
        cell = Cell(mat_cell_path)
        with open(pickle_cell_path, 'wb') as f:
            pickle.dump(cell, f)
        return cell

def load_cells(data_dir_path):
    paths = glob.glob(data_dir_path)
    cells = [load_cell(path) for path in paths]
    assert len(cells)>0, f"no cells were found in {data_dir_path}"
    return cells

def concat_dfs_by_index(df1, df2):
    cols_to_use = df2.columns.difference(df1.columns)
    combined_df = pd.concat([df1, df2[cols_to_use]], axis=1, join_axes=[df1.index])
    return combined_df

def reorder_df(df, first_columns):
    reordered = first_columns + [c for c in df.columns if c not in first_columns]
    return df[reordered]



def plot_classifier_comparison(full_df, file_path):
    """ Compare published classifier with classifier from this subset of data"""
    LDA_coeff = pd.read_csv("neurospyke/data/LDA_coefficients.csv")
    LDA_dist_values = pd.read_csv("neurospyke/data/LDA_distributions.csv")
    
    all_variables = ['reb_delta_t', 'sag_fit_amplitude',
            'log_doublet_index_by_num_spikes', 
            'delta_thresh_last_spike', 
            'dVdt_pct_APamp_last_spike__20__rising']
    
    assert len(set(full_df.ca_buffer)) == 1, "Not implemented if also use Fluo5"
    current_ca_buffer = 'EGTA'
    
    fig = plt.figure()
    i = 1
    for num_spikes in range(3, 9):
    
        ax = fig.add_subplot(3, 2, i)
    
        current_variables = [variable + f'__{num_spikes}' if 'spike' in variable 
                else variable for variable in all_variables]
    
        """
        Get discriminant coefficients for published classifier and add the
        coefficients to a discriminant object
        """
        def get_LDA_data(df):
            ca_buffer_rows = df['ca_buffer']==current_ca_buffer
            num_spikes_rows = df['num_spikes']==num_spikes
            return df.loc[ca_buffer_rows & num_spikes_rows]
    
        # Get all LDA values from published classifier
        lda_coeff = get_LDA_data(LDA_coeff)[all_variables].as_matrix()
        lda_intercept = get_LDA_data(LDA_coeff)['intercept'].as_matrix()
    
        # Create discriminant classifier using these published coefficients/intercept
        lda = LDA()
        lda.coef_ = lda_coeff
        lda.intercept_ = lda_intercept
    
        # get score distributions for python calculation clssifier
        current_LDA_dist_values = LDA_dist_values[(LDA_dist_values.num_spikes == num_spikes) & 
                (LDA_dist_values.ca_buffer == current_ca_buffer)]
    
        def LDA_dist_stat(df, genetic_marker, stat):
            return df[df.genetic_marker == genetic_marker][stat]
    
        D1_dist_mean = LDA_dist_stat(current_LDA_dist_values, 'D1', 'mean')
        D3_dist_mean = LDA_dist_stat(current_LDA_dist_values, 'D3', 'mean')
        D1_dist_std = LDA_dist_stat(current_LDA_dist_values, 'D1', 'std')
        D3_dist_std = LDA_dist_stat(current_LDA_dist_values, 'D3', 'std')
    
        # plot the score distributions that established the published classifier
        x_vals = np.arange(-10, 10, .01) 
        plt.plot(x_vals, norm.pdf(x_vals, D1_dist_mean, D1_dist_std),color = 'k')
        plt.plot(x_vals, norm.pdf(x_vals, D3_dist_mean, D3_dist_std), color=rgb_colors['dodgerblue'])
    
        """
        Generate a discriminant fit with current cell subset analyzed with python
        code
        """
        current_df = full_df[['genetic_marker'] + current_variables].copy()
        current_df.dropna(inplace=True)
    
        X_all = current_df[current_variables]
        y_all = current_df['genetic_marker']
    
        # Standardize current cells 
        Xmeans = X_all.mean(); Xstd = X_all.std()
        Xs_all = (X_all-Xmeans)/Xstd
    
        # Create LDA classifier from current cells
        lda_new = LDA()
        lda_new.fit(Xs_all, y_all)
    
        # Get discriminant scores for new discriminant classifier for current cell
        # subset
        LDA_scores_new = lda_new.decision_function(Xs_all)
        score_D1 = -LDA_scores_new[y_all=='D1']
        score_D3 = -LDA_scores_new[y_all=='D3']
       
        # Plot the distributions of D1+ and D3+ cells with respect to the decision
        # boundary using new classifier
        plt.axvline(x=0,color= 'r') # decision boundary
        x_vals = np.arange(-10, 10, .01) 
        plt.plot(x_vals, 
                norm.pdf(x_vals, np.nanmean(score_D1), np.nanstd(score_D1)), 
                '--', color = 'k')
        plt.plot(x_vals, 
                norm.pdf(x_vals, np.nanmean(score_D3), np.nanstd(score_D3)), 
                '--', color=rgb_colors['dodgerblue'])
    
        ax.set_xlabel('score')
        ax.set_ylabel('probability')
        ax.set_xlim([-10, 8]); ax.set_ylim([0, .5])
        ax.set_title(f"{num_spikes} APs")
    

        if i % 2 == 0:
            ax.get_yaxis().set_visible(False)
            ax.spines['left'].set_visible(False)
        
        i +=1

    fig.set_size_inches(10.5, 15, forward=True)
    plt.savefig(file_path, bbox_inches="tight")
