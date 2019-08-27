import numpy as np

def aggregate_by_key(m):
    '''
    This is a helper which takes an array with two columns.  It is the numpy
    equivalent of grouping represented by tup_ls_dct in pype.
    The first column is the key, and the second column is the value.  We 
    perform the following operations on this:
    1) Sort the keys of m, getting their indices.
    2) Reorder the keys and values of m accordingly.
    3) Find the unique keys and their counts, stored in uniqueKeys[1].
    4) The np.split function takes an array, and splits it according to
       the counts of the unique elements.  So, take the first x elements,
       put it in one part of the list, then take the next y elements, append
       it to the list, etc.
    5) In the resulting list of arrays, we find the maximum length.
    6) We pad these arrays with zeros if they're shorter than the maximum
       length.
    7) Then, we convert this into a matrix, whose i-th row represents the
       i-th key, and whose j-th column represents the j-th value with that
       key.  
    8) We return the matrix and the unique keys.
    We do this rather than json-style grouping for performance reasons, as 
    many people have complained about using pure json-style aggregation.
    Thanks to: https://stackoverflow.com/questions/38013778/is-there-any-numpy-group-by-function
    '''
    indices=m[:,0].argsort()
    m[:,0]=m[indices,0]
    m[:,1]=m[indices,1]
    uniqueKeys=np.unique(m[:,0],return_counts=True)
    splitValues=np.split(m[:, 1], 
                         np.cumsum(uniqueKeys[1])[:-1])
    maxLen=np.max([a.shape[0] for a in splitValues])
    aggregatedValues=[np.lib.pad(a,
                                 (0,maxLen-a.shape[0]),
                                 'constant',
                                 constant_values=(0,0))\
                      for a in splitValues]
    aggregatedValues=np.array(aggregatedValues)

    return aggregatedValues,uniqueKeys[0],uniqueKeys[1]


def np_int_array(x):

    return np.array(x,dtype=np.int64)


def sum_by_row(x):

    return np.sum(x,axis=1)
