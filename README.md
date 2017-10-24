# Python package for analysis of neuronal whole cell patch clamp electrophysiological data. 
* see [NeuroClassify](github.com/RebeccaClarkson/NeuroClassify) for import to Matlab from Igor Pro

First, import packages needed for these examples:
```python
    from neurospyke.query import Query
    from neurospyke.utils import load_cells
    from neurospyke.utils import concat_dfs_by_index
    from neurospyke.utils import reorder_df
    from tabulate import tabulate
```
### Import electrophysiological data from Matlab. 

Next, load cellular data that has been saved as .mat files. 
```python
    cell_file_pattern = 'docs/ExampleCells/*.mat' 
    example_cells = load_cells(cell_file_pattern)
```

### Query the electrophysiological properties of these cells. 
#### Each Query can include both desired criteria and properties to be calculated.

Query 1 examines action potential spiking properties, for electrophysiological sweeps that have .3 second current injection that elicited 5 spikes. For all sweeps that fit these criteria, this query determines the doublet index as well as number of spikes (which will of course in this case be directly determined by the criteria.
```python
    # Query 1 
    response_criteria = {'curr_duration':.3, 'num_spikes': 5}
    response_properties = ['doublet_index', 'num_spikes']
    query1 = Query(example_cells, response_criteria=response_criteria, 
            response_properties=response_properties)
    df1 = query1.run()
```
Query 2 examines hyperpolarization-related properties, in this case with a current duration of .12 seconds and a very large hyperpolarizing current injection (-400 pA). This query calculates the rebound time constant of the average response meeting these criteria, indicated by using "calculated_cell_properties." 
```python
    # Query 2
    response_criteria = {'curr_duration': .12, 'curr_amplitude': -400}
    calculated_cell_properties = ['reb_delta_t'] 
    query2 = Query(example_cells, response_criteria=response_criteria, 
            cell_properties=calculated_cell_properties)
    df2 = query2.run()
```
### Aggregate the results of both queries
```python
    combined_df = concat_dfs_by_index(df1, df2)                                                                                           
    example_cells_df = reorder_df(combined_df, ['genetic_marker', 'ca_buffer', 'num_spikes'])    
    print(tabulate(example_cells_df.head(), headers='keys', tablefmt='pipe')) 
```
|          | genetic_marker   | ca_buffer   |   num_spikes |   doublet_index |   reb_delta_t |
|:---------|:-----------------|:------------|-------------:|----------------:|--------------:|
| 040915-2 | D3               | EGTA        |            5 |         2.23207 |         33.75 |
| 040915-4 | D3               | EGTA        |            5 |         3.17862 |         36.9  |
| 040915-7 | D3               | EGTA        |            5 |         3.00712 |         32.45 |
| 040915-9 | D3               | EGTA        |            5 |         4.78366 |         28.15 |
| 041015-3 | D3               | EGTA        |            5 |         2.52443 |         40.4  |

Copyright 2017, Rebecca L. Clarkson. All rights reserved.
