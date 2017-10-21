# Python package for analysis of neuronal whole cell patch clamp electrophysiological data. 
### Import electrophysiological data from Matlab 
* see [NeuroClassify](github.com/RebeccaClarkson/NeuroClassify) for import to Matlab from Igor Pro
```python
	from neurospyke.utils import load_cells
	# filepath is location of .mat files
	file_pattern = filepath + *.mat
	cells = load_cells(file_pattern)
```

### Query the electrophysiological properties of these cells.
#### Each Query can include both desired criteria and properties to be calculated.
```python
	from neurospyke.query import Query
	response_criteria = {'curr_duration':.3, 'num_spikes': 5}
	response_properties = ['doublet_index', 'num_spikes']
	
	query1 = Query(cells, response_criteria=response_criteria,
          	response_properties=response_properties)
			
	# Run the query to get a dataframe of the results.
	query1_results_df = query1.run()
```


Copyright 2017, Rebecca L. Clarkson. All rights reserved.
