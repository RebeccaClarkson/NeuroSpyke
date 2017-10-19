import glob 
from neurospyke.cell import Cell

def load_cells(data_dir_path):
    paths = glob.glob(data_dir_path)
    return [Cell(path) for path in paths]
