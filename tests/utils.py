import numpy as np

def intersect_all(list_of_arrays):
    """ 
    Finds intersecting values of n np.arrays within a list 
    """
    for i in range(0, len(list_of_arrays)):
        if i == 0:
            intersection = np.intersect1d(
                    list_of_arrays[0], list_of_arrays[1]
                    )
        if i < len(list_of_arrays)-1:
            intersection_tmp = np.intersect1d(
                    list_of_arrays[i], list_of_arrays[i+1])
            intersection = np.intersect1d(
                    intersection_tmp, intersection
                    )
    return intersection
