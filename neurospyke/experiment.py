import glob
from  neurospyke.cell import Cell
import pandas as pd

class Experiment(object):
    def __init__(self, criteria, property_names):
        self.cells = [] 
        self.criteria = criteria
        self.property_names = property_names 
   
    def load_cells(self, data_dir_path):
        paths = glob.glob(data_dir_path + "*.mat")
        self.cells.extend(Cell(path, self) for path in paths)

    def run(self): 
        mean_df=pd.DataFrame()
        for cell in self.cells: 
            tmp_df = cell.aggregate_result() 
            mean_df = pd.concat([mean_df, tmp_df])
        return mean_df

    def describe(self):
        cell_names = [cell.cell_name() for cell in self.cells]
        return f"""
        This exeriment was run on {cell_names},
        with criteria {self.criteria}, 
        and generates a dataframe with columns {self.property_names}"""
