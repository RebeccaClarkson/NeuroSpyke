import glob 
from neurospyke.cell import Cell
import pandas as pd

def load_cells(data_dir_path):
    paths = glob.glob(data_dir_path)
    return [Cell(path) for path in paths]

def concat_dfs_by_index(df1, df2):
    cols_to_use = df2.columns.difference(df1.columns)
    combined_df = pd.concat([df1, df2[cols_to_use]], axis=1, join_axes=[df1.index])
    return combined_df

def reorder_df(df, first_columns):
    reordered = first_columns + [c for c in df.columns if c not in first_columns]
    return df[reordered]

rgb_colors = dict()
rgb_colors['dodgerblue'] = (.12, .56, 1)
