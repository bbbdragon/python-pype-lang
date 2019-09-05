import numpy as np

def aggregate_by_key(m,pad=True):
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

    if pad:

        maxLen=np.max([a.shape[0] for a in splitValues])
        aggregatedValues=[np.lib.pad(a,
                                     (0,maxLen-a.shape[0]),
                                     'constant',
                                     constant_values=(0,0))\
                          for a in splitValues]
        aggregatedValues=np.array(aggregatedValues)

    else: 
        
        aggregatedValues=splitValues

    return aggregatedValues,uniqueKeys[0],uniqueKeys[1]


def aggregate_jsons_by_key(ls,key):

    uniqueVals=np.unique([js[key] for js in ls])
    indexToKeyMap={k:i for (i,k) in enumerate(uniqueVals)}
    m=np.array([(indexToKeyMap(js[key]),i) for (i,js) in enumerate(ls)])
    aggregatedValues,keys,uniqueKeys=aggregate_by_key(m,False)

    return {k:[ls[index] for index in l] \
            for (k,l) in zip(uniqueVals,aggregatedValues)}
    

def np_int_array(x):

    return np.array(x,dtype=np.int64)


def sum_by_row(x):

    return np.sum(x,axis=1)


def sum_by_column(x):

    return np.sum(x,axis=0)


def vector_copy_matrix(shape,vector):

    z=np.zeros(shape)
    z[:,:]=vector

    return z


def trans(m):

    return m.T


def square_ones_tri(rows,k=0):

    return np.triu(np.ones([rows,rows]),k)


def zero_below(x,thresh=0):

    x[x < thresh]=0

    return x


def zero_above(x,thresh=0):

    x[x > thresh]=0

    return x
    

def num_rows(a):

    return a.shape[0]


def num_cols(a):

    return a.shape[1]


def nonzero_indices(m):

    lastCol=m.shape[1]-1
    colStart=(m[0,:]!=0).argmax(axis=0)
    rowEnd=(m[:,lastCol]!=0).argmax(axis=0)
    rowEnd+=np.count_nonzero(m[rowEnd:,lastCol]>0)

    return rowEnd,colStart


def add_upper_right_corner(m1,m2):

    m1Rows=m1.shape[0]
    m2Rows=m2.shape[0]
    m1Cols=m1.shape[1]
    m2Cols=m2.shape[1]
    m1[:m2Rows,m1Cols-m2Cols:]+=m2

    return m1


def off_diagonal(ln,offset=0):

    numOnes=ln-offset
    ones=np.ones(numOnes)

    return np.diag(ones,offset)


def off_diagonal_fill(a,offset=0):

    return np.diag(a,offset)


def ones_filter(ln,offset=1):

    return square_ones_tri(ln) - square_ones_tri(ln,offset)


def log_with_zero(m):

    return zero_below(np.log(m))


def val_sum(dct):

    return np.sum([v for (k,v) in dct.items()])


def by_indices(a,tuples):

    return [a[tup] for tup in tuples]
