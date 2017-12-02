from neurospyke.cell import Cell
import glob 
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

def load_cell(mat_cell_path, to_pickle=True):
    pickle_cell_path = calc_pickle_cell_path(mat_cell_path)
    try: 
        with open(pickle_cell_path, 'rb') as f:
            cell = pickle.load(f)
            return cell
    except:
        cell = Cell(mat_cell_path)
        if to_pickle:
            with open(pickle_cell_path, 'wb') as f:
                pickle.dump(cell, f)
        return cell

def load_cells(data_dir_path, to_pickle=True):
    paths = glob.glob(data_dir_path)
    cells = [load_cell(path, to_pickle) for path in paths]
    assert len(cells)>0, f"no cells were found in {data_dir_path}"
    return cells

def concat_dfs_by_index(df1, df2):
    cols_to_use = df2.columns.difference(df1.columns)
    combined_df = pd.concat([df1, df2[cols_to_use]], axis=1, join_axes=[df1.index])
    return combined_df

def reorder_df(df, first_columns):
    reordered = first_columns + [c for c in df.columns if c not in first_columns]
    return df[reordered]


