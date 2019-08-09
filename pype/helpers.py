from functools import reduce
from collections import defaultdict
import itertools
from copy import deepcopy
from operator import itemgetter
import pprint as pp

def pair_dd(f=lambda:int()):

    return defaultdict(lambda:defaultdict(f))


def dct_intersect(dct,keys):

    return {k:dct[k] for k in keys if k in dct}

 
def dct_assoc(dct,key,val):

    dct[key]=val

    return dct


def dct_dissoc(dct,key):

    if key in dct:

        del dct[key]

    return dct


def key_d(dct,key):

    return {dct[key]:dct}


def key_tup(dct,key):

    keyVal=dct[key]
    
    del dct[key]

    return (keyVal,dct)


def add_to_counter(counter,el):

    counter[el]+=1

    return counter

def add_tup_to_pair_counter(counter,tup):

    counter[tup[0]][tup[1]]+=1

    return counter


def add_to_pair_counter(counter,el1,el2):

    counter[el1][el2]+=1

    return counter


def pair_counter_to_prob(counter):

    sums={el:sum(d.values()) for (el,d) in counter.items()}

    return { el1:{el2:val/sums[el1] for (el2,val) in d.items()} \
             for (el1,d) in counter.items()}


def add_tup(dct,tup):

    dct[tup[0]]=tup[1]

    return dct


def tup_dct(tups):

    return reduce(add_tup,tups,{})


def add_tup_ls_dct(dct,tup):

    #print('{} is dct'.format(dct))
    #print('{} is tup'.format(tup))

    dct[tup[0]].append(tup[1])

    return dct

import pprint as pp

def tup_ls_dct(tups):

    return dict(reduce(add_tup_ls_dct,tups,defaultdict(lambda:list())))


def add_empty_ls(dct,key):

    dct[key]

    return dct


def empty_ls_dct(ls):

    return reduce(add_empty_ls,ls,defaultdict(lambda:list()))


def add_to_ls_dct(listDict,key,val):

    listDict[key].append(val)

    return listDict


def ls_dct_union(listDict1,listDict2):

    listDict2Tups=[(k,v) for (k,ls) in listDict2.items() for v in ls]

    return reduce(add_tup_ls_dct,listDict2Tups,listDict1)



def merge_ls_dct(dctLS,key):

    dd=reduce(lambda h,dct:add_to_ls_dct(h,dct[key],dct),
              dctLS,
              defaultdict(lambda:list()))

    return dict(dd)

def add_to_ls_dct_no_key(listDict,key,deletedKey,val):

    del val[deletedKey]

    listDict[key].append(val)

    return listDict


def merge_ls_dct_no_key(dctLS,key):
    '''
    gets rid of key in the added value
    '''
    #print('*'*30)
    #print('merge_ls_dct_no_key')
    #print(f'{key} is key')
    #pp.pprint(dctLS)

    dd=reduce(lambda h,dct:add_to_ls_dct_no_key(h,dct[key],key,dct),
              dctLS,
              defaultdict(lambda:list()))

    return dict(dd)


def unroll_ls_dct(dctLS):

    return [(k,el) for (k,ls) in dctLS.items() for el in ls]


def dct_merge(dct1,dct2):

    for (k,v) in dct2.items():

        dct1[k]=v

    return dct1


def dct_merge_vals(dct1,dct2):

    for (k,d) in dct2.items():

        if k not in dct1:

            dct1[k]=d

        else:

            dct1[k]=dct_merge(dct1[k],d)

    return dct1


def dct_merge_vals_if(dct1,dct2):

    for (k,d) in dct1.items():

        if k in dct2:

            dct1[k]=dct_merge(d,dct2[k])

    return dct1

def dct_merge_copy(dct1,dct2):

    return dct_merge(deepcopy(dct1),dct2)


def dct_diff(dct1,dct2):

    return {key:el for (key,el) in dct2.items() if key not in dct1}


def dct_zip(ls1,ls2):

    return {el1:el2 for (el1,el2) in zip(ls1,ls2)}


def merge_dcts(dctLS):

    return reduce(dct_merge,dctLS)


def merge_dcts_vals(dctLS):

    return reduce(dct_merge_vals,dctLS)


def jn(ls):

    return ' '.join(ls)


def first(ls,n):

    return ls[:n]


def last(ls,index,lastIndex):

    return ls[(index-lastIndex):index]


def flatten_list(ls):

    ls=[[el] if not isinstance(el,list) else el for el in ls]

    return list(itertools.chain.from_iterable(ls))


frist=lambda st,n: st[:n]


def d_to_tup(dct,key1,key2):

    return (dct[key1],dct[key2])


is_dict=lambda x: isinstance(x,dict)
is_ddict=lambda x: isinstance(x,defaultdict)

def dd_to_dict(d):

    if is_dict(d) or is_ddict(d):

        return {k:dd_to_dict(v) for (k,v) in d.items()}

    else:

        return d


def dct_items(dct):

    return list(dct.items())


def dct_values(dct):

    return list(dct.values())


def dct_keys(dct):

    return list(dct.keys())


def filter_by_indices(ls,indices):

    return [ls[i] for i in indices]


def enum_list(ls):

    return list(enumerate(ls))


def zip_ls(ls):

    return list(zip(ls,ls[1:]))


def sort_by_key(ls,key,rev=False):

    return sorted(ls,key=lambda js: js[key], reverse=rev)


def sort_by_index(ls,index,rev=False):

    return sorted(ls,key=itemgetter(index), reverse=rev)


def ls_product(ls):

    return list(itertools.product(ls,ls))


def ls_append(ls,el):

    ls.append(el)

    return ls


def key_ls_append(js,key,el):

    js[key].append(el)

    return js


def add_key_as(dct,key):

    for (k,d) in dct.items():

        dct[k][key]=k

    return dct

    
def zip_to_dct(tups,keys):

    return {tup[0]:dict(zip(keys,tup[1:])) for tup in tups}


def dict_from_tups(tups,*keys):

    return [dict(zip(keys,tup)) for tup in tups]


    
def middle(ls):

    if len(ls) == 0:

        return 0

    return ls[int(len(ls)/2)]


def range_list(n,m):

    return list(range(n,m))

def range_list(n,m):

    return list(range(n,m))


def zip_to_dicts(tups,*keys):

    return [dict(zip(keys,tup)) for tup in tups]


def get_or_false(dct,*keys):

    if not dct:

        return False

    d=dct

    for key in keys:

        if key not in d:

            return False

        d=d[key]

    return d


def get_by_key_or_false(dct,dctKey,*keys):

    d=dct

    for key in keys:

        if key not in d:

            return False

        d=d[key]

    return d[dctKey]

    
def do_func(accum,f):

    result=f(accum)

    if result == None:
        
        return accum

    return result


def is_dict_helper(accum):

    return isinstance(accum,dict)


def reverse_ls_dct(dct):

    dd=defaultdict(lambda:list())
    
    for (k,ls) in dct.items():

        for v in ls:

            dd[v].append(k)

    return dict(dd)


def empty_ls_dct(keys):

    return {key:[] for key in keys}


def ls_dct_product(dct):

    prod=[]

    for k,ls in dct.items():

        for v in ls:

            prod.append((k,v))

    return prod


def reverse_dct_vals(dct):

    newD=defaultdict(lambda:dict())

    for (k1,d) in dct.items():

        for (k2,v) in d.items(): 

            newD[k2][k1]=v

    return dict(newD)
