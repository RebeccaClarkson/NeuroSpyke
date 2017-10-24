# Python package for analysis of neuronal whole cell patch clamp electrophysiological data. 
### Import electrophysiological data from Matlab 
* see [NeuroClassify](github.com/RebeccaClarkson/NeuroClassify) for import to Matlab from Igor Pro
```python
    from neurospyke.utils import load_cells
    cell_file_pattern = 'docs/ExampleCells/*.mat' 
    example_cells = load_cells(cell_file_pattern)
```

### Query the electrophysiological properties of these cells.
#### Each Query can include both desired criteria and properties to be calculated.
```python
    # Query 1 
    response_criteria = {'curr_duration':.3, 'num_spikes': 5}
    response_properties = ['doublet_index', 'num_spikes']
    query1 = Query(example_cells, response_criteria=response_criteria, 
            response_properties=response_properties)

    # Query 2
    response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
    calculated_cell_properties = ['reb_delta_t'] 
    query2 = Query(example_cells, response_criteria=response_criteria, 
            cell_properties=calculated_cell_properties)
```


Copyright 2017, Rebecca L. Clarkson. All rights reserved.
