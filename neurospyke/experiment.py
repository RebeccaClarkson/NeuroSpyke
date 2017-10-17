import glob
from  neurospyke.cell import Cell
import pandas as pd

class Experiment(object):
    def __init__(self, criteria, property_names):
        self.cells = [] 
        self.criteria = criteria
        self.property_names = ['cell_name', 'sweep_index'] +  property_names 
   
    def load_cells(self, data_dir_path):
        paths = glob.glob(data_dir_path + "*.mat")
        self.cells.extend(Cell(path, self) for path in paths)

    def run(self): 
        result = []
        for cell in self.cells: 
            # result.append(cell.run()), run method would know how to average
            # loop within each class, aggregate for next level 
            for sweep in cell.sweeps():
                for response in sweep.responses():
                    if response.meets_criteria():
                        result.append(response.properties())
        result_df = pd.DataFrame(result)
        result_df = result_df[self.property_names]
        return result_df

    def describe(self):
        cell_names = [cell.cell_name() for cell in self.cells]
        return f"""
        This exeriment was run on {cell_names},
        with criteria {self.criteria}, 
        and generates a dataframe with columns {self.property_names}"""
