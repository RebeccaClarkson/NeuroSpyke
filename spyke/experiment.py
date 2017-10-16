class Experiment(object):
    def __init__(self, cells, criteria, properties):
        self.cells = cells 
        self.criteria = criteria
        self.properties = properties 
    
    def run(self):
        df = pseudo_df
        for cell in self.cells:
            for sweep in cell.sweeps:
                for response in sweep.responses:
                    response.experiment = self
                    if response.meets_criteria():
                        df.append(response.data())
        return df 

    def describe(self):
        return f"""
        This exeriment was run on {self.cells},
        with criteria {self.criteria}, 
        and generates a dataframe with columns {self.properties}"""
