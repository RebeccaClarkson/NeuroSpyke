import pandas as pd
import hashlib
import pickle
import os
from neurospyke.utils import query_cache_dir
from neurospyke.sweep import Sweep

class Query(object):
    def __init__(self, cells, response_criteria=None, response_properties=None, 
            cell_criteria=None, cell_properties=None):
        self.cells = cells

        self.response_criteria = response_criteria or {}
        self.response_properties = response_properties or []
        self.cell_criteria = cell_criteria or {}
        self.cell_properties = cell_properties or []

        self.validate_parameters()   

    @classmethod
    def create_or_load_from_cache(cls, cells, overwrite=False,  **kwargs):
        """ 
        Make an instance of a query to have access to its instance methods.
        This will be the actual query object used if not in the cache.
        """
        tmp_query = cls(cells, **kwargs)
        path_exists =  os.path.isfile(tmp_query.query_cache_filename())
        if overwrite or not path_exists:
            #print(f"\nMaking new query")
            tmp_query.run()
            tmp_query.save_query()
            return tmp_query
        else: 
            print(f"\nLoading query from cache")
            query = cls.load_query(tmp_query.query_cache_filename())
            query.cells = cells

            for cell in query.cells:
                cell.query = query
                cell.analyzed_sweep_ids = query.analyzed_sweeps_dict[cell.calc_cell_name()]

            return query

    def validate_parameters(self):
        # TODO: ensure num_spikes criterion is set if spike properties in property names 
        pass 

    def run(self): 
        """
        This method returns a dataframe with averaged Cell data for
        reponse_properties and cell_properties. Response_properties are
        calculated at the level of the individual response, and averaged at the
        Cell level, while cell_properties are calculated at the level of the
        cell.
        """
        mean_df=pd.DataFrame()
        column_names = []
        df_list = []
        for cell in self.cells: 
            cell.query = self
            cell_df = cell.run()
            df_list.append(cell_df)
            if len(cell_df.columns) > len(column_names):
                column_names = cell_df.columns
        mean_df = pd.concat(df_list)

        # added to query so that can be accessed with re-loaded query
        self.mean_df = mean_df[column_names]
        self.analyzed_sweeps_dict = self.create_analyzed_sweeps_dict()
        return self.mean_df 
    
    def query_properties(self):
        cell_criteria = list(self.cell_criteria.items())
        response_criteria = list(self.response_criteria.items())
        cell_properties = self.cell_properties
        response_properties = self.response_properties

        cell_names = []
        for cell in self.cells:
            cell_names.append(cell.calc_cell_name())

        return f"""cell_names: {cell_names};
        cell_criteria: {cell_criteria};
        response_criteria: {response_criteria};
        cell_properties: {cell_properties};
        response_properties: {response_properties}
        """
        
    def create_analyzed_sweeps_dict(self):
        """
        Stores in the query  all analyzed sweep_ids for each cell in the query, so can work with
        these sweeps in a re-loaded query.
        """
        cell_names = [cell.calc_cell_name() for cell in self.cells]
        analyzed_sweep_ids = [cell.analyzed_sweep_ids for cell in self.cells]
        analyzed_sweeps_dict = dict(zip(cell_names, analyzed_sweep_ids))
        return analyzed_sweeps_dict

    def query_id(self):
        q = hashlib.sha256()
        q.update(bytes(str(self.query_properties()), encoding="ASCII"))
        return q.hexdigest()

    def query_cache_filename(self):
        return os.path.join(query_cache_dir, f"{self.query_id()}.pickle")

    def is_cached(self):
        return os.path.exists(self.query_cache_filename())

    def save_query(self):
        assert hasattr(self, 'mean_df'), "query must be run before it can be saved"

        filename = self.query_cache_filename()

        cells = self.cells
        self.analyzed_sweeps_dict = self.create_analyzed_sweeps_dict()
        self.cells=None # remove cells to save filespace

        with open(filename, 'wb') as f:
            pickle.dump(self, f)

        self.cells = cells # add cells back 
   
    @classmethod
    def load_query(cls, query_cache_filepath):
        with open(query_cache_filepath, 'rb') as f:
            query = pickle.load(f)
            return query 

    def describe(self):
        criteria = f"Cell: {self.cell_criteria}, Response: {self.response_criteria}"
        properties = f"Cell: {self.cell_properties}, Response: {self.response_properties}"
        cell_names = [cell.calc_cell_name() for cell in self.cells]
        return f"""
        This exeriment was run on {cell_names},
        with criteria {criteria}, 
        and generates a dataframe with columns {properties}"""
