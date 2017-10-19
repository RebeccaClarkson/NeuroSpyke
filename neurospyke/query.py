import pandas as pd

class Query(object):
    def __init__(self, cells, response_criteria=None, response_properties=None, 
            cell_criteria=None, cell_properties=None):
        self.cells = cells

        self.response_criteria = response_criteria or {}
        self.response_properties = response_properties or []
        self.cell_criteria = cell_criteria or {}
        self.cell_properties = cell_properties or []

        self.validate_parameters()   


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
        df_list = []
        for cell in self.cells: 
            cell.query = self
            df_list.append(cell.run())
        # need to get column names from response that has all properties
        # so that can use to preserve column order for display 
        num_columns = [len(df.columns) for df in df_list]
        column_names = df_list[num_columns.index(max(num_columns))].columns
        mean_df = pd.concat(df_list)
        return mean_df[column_names]

    def describe(self):
        criteria = f"Cell: {self.cell_criteria}, Response: {self.response_criteria}"
        properties = f"Cell: {self.cell_properties}, Response: {self.response_properties}"
        cell_names = [cell.calc_cell_name() for cell in self.cells]
        return f"""
        This exeriment was run on {cell_names},
        with criteria {criteria}, 
        and generates a dataframe with columns {properties}"""
