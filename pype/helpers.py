from functools import reduce
from collections import defaultdict
import itertools
from copy import deepcopy
from operator import itemgetter
import pprint as pp

#################
# TYPE CHECKING #
#################

is_tuple=lambda x: isinstance(x,tuple)
is_dict=lambda x: isinstance(x,dict)
is_list=lambda x: isinstance(x,list)
is_mapping=lambda x: isinstance(x,dict)
is_bool=lambda x: isinstance(x,bool)
is_object=lambda x: isinstance(x,object)
is_string=lambda x: isinstance(x,str)
is_set=lambda x: isinstance(x,set)
is_int=lambda x: isinstance(x,int)
is_slice=lambda x: isinstance(x,slice)
is_getter=lambda x: isinstance(x,Getter)
is_pype_val=lambda x: isinstance(x,PypeVal)
is_getter=lambda x: isinstance(x,Getter)
is_lam_tup=lambda x: isinstance(x,LamTup) and not is_pype_val(x) and not is_getter(x)
is_iterable=lambda x: isinstance(x,Iterable)
is_mapping=lambda x: isinstance(x,Mapping)
is_hashable=lambda x: isinstance(x,Hashable)
is_ndarray=lambda x: isinstance(x,np.ndarray)
is_sequence=lambda x: isinstance(x,Sequence) or is_ndarray(x)
is_container=lambda x: isinstance(x,Container)

key=lambda x: tup[0]
val=lambda x: tup[1]
slc=lambda ls,start,stop: ls[start:stop]

def is_callable(fArg):

    return callable(fArg)


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


def dct_merge_ls_vals(dct1,dct2):

    for (k,d) in dct2.items():

        if k not in dct1:

            dct1[k]=d

        else:

            dct1[k].extend(dct2[k])

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


def flatten_tuple(ls):

    tup=tuple([(el,) if not isinstance(el,tuple) else el for el in ls])

    return tuple(itertools.chain.from_iterable(tup))


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


def zip_ls(ls1,ls2):

    return list(zip(ls1,ls2))


def sort_by_key(ls,key,rev=False):

    return sorted(ls,key=lambda js: js[key], reverse=rev)


def sort_by_index(ls,index,rev=False):

    return sorted(ls,key=itemgetter(index), reverse=rev)


def sort_by_func(ls,func,rev=False):

    return sorted(ls,key=func,reverse=rev)


def ls_product(ls):

    return list(itertools.product(ls,ls))


def ls_append(ls,el):

    ls.append(el)

    return ls


def key_ls_append(js,key,el):

    js[key].append(el)

    return js


def ls_extend(ls1,ls2):

    ls1.extend(ls2)

    return ls1


def add_key_as(dct,key):

    for (k,d) in dct.items():

        dct[k][key]=k

    return dct

    
def zip_to_dct(tups,keys):

    return {tup[0]:dict(zip(keys,tup[1:])) for tup in tups}


def dct_from_tup(tup,*keys):

    return dict(zip(keys,tup))


def dct_from_tups(tups,*keys):

    return [dct_from_tup(tup,*keys) for tup in tups]

    
def middle(ls):

    if len(ls) == 0:

        return 0

    return ls[int(len(ls)/2)]


def range_list(n,m):

    return list(range(n,m))


def list_range(ls):

    return range(len(ls))


def zip_to_dicts(tups,*keys):

    return [dict(zip(keys,tup)) for tup in tups]



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


def prod_by_one(el,ls):

    return list(product([el],ls))


def one_val_dct(keys,val):

    return {k:val for k in keys}


def prod_ls_dct(keys,vals):

    return tup_ls_dct(itertools.product(keys,vals))


def all_t(collection):

    if isinstance(collection,dict):

        vals=collection.values()

    return all([bool(v) for v in vals])


def select(dct,*keys):

    return {k:dct[k] for k in keys}



def rng(ln):

    return range(ln)


def get_or_false(obj,*keys):

    if keys:

        if is_list(obj):

            if keys[0] >= len(obj):
                
                return False

            obj=obj[keys[0]]
        
            return get_or_false(obj,keys[1:])

        if is_dict(obj):

            if keys[0] not in obj:

                return False

            obj=obj[keys[0]]
        
            return get_or_false(obj,keys[1:])

        if is_string(keys[0]) and hasattr(obj,keys[0]):

            attr=getattr(obj,keys[0])

            return get_or_false(attr,keys[1:])

    return obj


def get_call_or_false(obj,*keys):

    #print('='*30)
    #print('get_call_or_false')
    #print(f'{obj} is obj')
    #print(f'{keys} is keys')

    if keys:

        if is_list(obj) or is_tuple(obj):

            if keys[0] >= len(obj):
                
                return False

            #print(f'returning {obj[keys[0]]}')

            obj=obj[keys[0]]

        elif is_dict(obj):

            if keys[0] not in obj:

                return False

            obj=obj[keys[0]]
        
        elif is_string(keys[0]) and hasattr(obj,keys[0]):

            obj=getattr(obj,keys[0])

        if len(keys) == 1:

            return obj

        return get_call_or_false(obj,keys[1:])

    if is_callable(obj):

        if not keys or not keys[0]:

            return obj()

        firstKey=keys[0]
        obj=obj(firstKey)

        return get_call_or_false(obj,keys[1:])
    
    return obj


def reduce_func(func,iterable):

    return reduce(lambda h,x: func(h,x),iterable)


def reduce_func_start_val(func,startVal,iterable):

    return reduce(lambda h,x: func(h,x),iterable,startVal)


def str_join(st,ls):

    return st.join(ls)


def set_union(set1,set2):

    return set1|set2


def set_intersection(set1,set2):

    return set1&set2


def val_div(d1,d2):

    return {k1:v1/d2[k1] if k1 in d2 else 0 for (k1,v1) in d1.items()}


def val_sum(js):

    return sum(dct_values(js))


def dct_add(dct1,dct2):

    for (k,v) in dct2.items():

        if k not in dct1:

            dct1[k]=0

        dct1[k]+=dct2[k]

    return dct1


def first_dct_items(dct,n=10):

    return {k:v for (k,v) in list(dct.items())[:n]}


def sum_dct_vals(dct1,dct2):

    keys1=set(dct1.keys())
    keys2=set(dct2.keys())

    for k in keys1&keys2:

        dct1[k]=dct1[k]+dct2[k]

    for k in keys2-keys1:

        dct1[k]=dct2[k]
    
    return dct1


def multiply_dct_vals(dct1,dct2):

    keys1=set(dct1.keys())
    keys2=set(dct2.keys())

    for k in keys1&keys2:

        dct1[k]=dct1[k]*dct2[k]

    for k in keys2-keys1:

        dct1[k]=0
    
    return dct1


def merge_dct_sums(dctLS):

    return reduce(lambda h,dct:sum_dct_vals(h,dct),dctLS)


def cartesian(ls1,ls2):

    return itertools.product(ls1,ls2)


def tups_product_filtered(tupLs1,tupLs2):

    return [(tup1,tup2) for (tup1,tup2) \
            in itertools.product(tupLs1,tupLs2)\
            if tup1[0] != tup2[0]]


def dct_product_filtered(dct1,dct2):

    return tups_product_filtered(dct1.items(),dct2.items())


def key1_val2(tup1,tup2):

    return [tup1[0],tup2[1]]


def scalar_dct_multiply(scalarDct,dct):

    return {k:scalarDct[k]*v if k in scalarDct else 0 for (k,v) in dct.items()}


def scalar_dcts_multiply(scalarDct,dcts):

    return {k:scalar_dct_multiply(scalarDct[k],dct) for (k,dct) in dcts.items()}


def dcts_val_multiply(*dcts):

    print(f'{dcts} is dcts')

    return reduce(lambda h,dct:multiply_dct_vals(h,dct),dcts)
        

def get_min(ls):

    return min(ls)


def ls_elements(ls,indices):

    return [ls[i] for i in indices]
