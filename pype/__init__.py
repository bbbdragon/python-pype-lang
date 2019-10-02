###
# USAGE: python3 pype.py
###
name='pype'
from functools import reduce
from collections import Iterable,Sequence,Mapping,Hashable,Container
from pype.helpers import *
from operator import *
from itertools import takewhile,product
from pype.vals import Quote,LamTup,PypeVal,Getter,delam
import numpy as np
import sys
import pprint as pp
from inspect import Signature
import types
from pype.vals import NameBookmark

#import __builtins__

__version__='1.1.1'

#BUILTINS=set(__builtins.__dict__.values())

###########
# LOGGING #
###########

PYPE_LOGGING={'timing':False,
              'threshold':0.1,
             }

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
is_sequence=lambda x: is_list(x) or is_ndarray(x) or isinstance(x,Sequence)
is_container=lambda x: isinstance(x,Container)

key=lambda x: tup[0]
val=lambda x: tup[1]
slc=lambda ls,start,stop: ls[start:stop]


def is_number_indexable(x):

    return is_list(x) \
        or is_ndarray(x) \
        or is_tuple(x)


################
# GETTER CLASS #
################

#############
# CONSTANTS #
#############

MIRROR=Getter('_pype_mirror_')
_=MIRROR
__=MIRROR
MIRROR_SET=set([MIRROR])
_0,_1,_2,_3=[LamTup((_,[i])) for i in range(4)]
_last=(_,[-1])
'''
_0=Getter('_arg0_')
_1=Getter('_arg1_')
_2=Getter('_arg2_')
_3=Getter('_arg3_')
_last=Getter('_arg_last')
INDEX_ARG_DICT={k:i for (i,k) in enumerate([_0,_1,_2,_3])}
INDEX_ARG_DICT[_last]=-1
'''
INDEX_ARG_DICT={}
_i=Getter('_i_index_')
_j=Getter('_j_index_')
_k=Getter('_k_index_')
_l=Getter('_l_index_')
FOR_ARG_DICT={k:i for (i,k) in enumerate([_i,_j,_k,_l])}
ALL_GETTER_IDS=set(['_',
                    '__',
                    '_0',
                    '_1',
                    '_2',
                    '_3',
                    '_last',
                    '_i',
                    '_j',
                    '_k',
                    '_l'])
ARGS='pype_args'
embedded_pype='embedded_pype'

# IN CASE YOU THINK THE ABOVE IS MESSY

d='BUILD_DICT'
assoc='DICT_ASSOC'
merge='DICT_MERGE'
dissoc='DICT_DISSOC'
l='BUILD_LS'
append='LIST_APPEND'
concat='LIST_CONCAT'
while_loop='WHILE_LOOP'
do='FARG_DO'
LIST_ARGS=set([embedded_pype,
               d,
               assoc,
               merge,
               dissoc,
               l,
               append,
               concat,
               while_loop,
               do])


###########
# HELPERS #
###########

def eval_or_val(accum,val):

    #print('*'*30)
    #print('eval_or_val')
    #print('{} is val'.format(val))
    #print('{} is f_arg_val'.format(is_f_arg(val)))

    return pype(accum,val) if is_f_arg(val) else val


def eval_or_accum(accum,fArg):

    return pype(accum,fArg) if is_f_arg(fArg) else accum


def is_arg_dict(*accum):

    return accum and is_dict(accum[0]) and ARGS in accum[0]


def args(*accum):

    # PROJECT - THINK OF PRE-INITIALIZING DICTIONARIES AND POPPING THEM FROM A STACK

    if is_arg_dict(*accum):

        return accum

    return {ARGS:accum}


##########
# MIRROR #
##########

def is_mirror(fArg):

    return is_getter(fArg) and fArg in MIRROR_SET


def eval_mirror(accum,fArg):
   
    #print('='*30)
    #print('eval_mirror')
    #print(f'{str(accum)[:100]} is accum')

    return accum


#########
# INDEX #
#########

def is_getitem(el):

    return is_list(el) \
        and len(el) == 1


def is_indexable(el):

    return is_sequence(el) or is_mapping(el)


def is_number_index(el):

    return is_list(el) or is_mapping(el)


def has_initial_object(fArg):

    if (is_list(fArg) or is_tuple(fArg)) and len(fArg) >= 1:
        
        return has_initial_object(fArg[0])

    if is_f_arg(fArg):

        return False

    return True


def mirror_index_f_arg(accum,indexFArg):

    '''
    print('*'*30)
    print('mirror_index_f_arg')
    print(f'{indexFArg} is indexFArg')
    print(f'{indexFArg[1]} is indexFArg[1]')
    print(f'{is_tuple(indexFArg)} is tuple')
    print(f'{eval_or_val(accum,indexFArg[1][0])}')
    '''

    if is_tuple(indexFArg) and len(indexFArg) >= 1:

        return (mirror_index_f_arg(accum,indexFArg[0]),
                [eval_or_val(accum,indexFArg[1][0])])

    return MIRROR


def get_initial_object(fArg):

    #print(f'{fArg} is fArg')
    #print(f'{is_tuple(fArg)} is tuple')

    if is_tuple(fArg) and len(fArg) > 0 and is_getitem(fArg[1]):

        return get_initial_object(fArg[0])

    return fArg


def get_all_indices(fArg,ls=[]):

    if not is_tuple(fArg) or len(fArg) == 1:

        ls.reverse()

        return ls

    ls.append(fArg[1][0])

    return get_all_indices(fArg[0],ls)


def is_index(fArg):

    return is_tuple(fArg) \
        and len(fArg) == 2 \
        and is_getitem(fArg[1])


FALSE_ARGS=args(False)


def eval_numpy_index(accum,fArgs):

    #print('eval_numpy_index')
    #print(f'{accum} is accum')
    #print(f'{fArgs} is fArgs')

    indices=[eval_or_val(accum,index) for index in get_all_indices(fArgs)]

    #print(f'{indices} is indices')

    return args(accum[tuple(indices)])


def eval_index(accum,fArgs):

    #print('='*20)
    #print('eval_index')
    accum=accum[ARGS][0]
    #print(f'{accum} is accum before')
    #print(f'{fArgs} is fArgs before')
    # First, let's see what the accum really is ...
    # Notice this works for recursion as well.
    #print(f'{fArgs[0]} is fArgs[0]')
    #print(f'{is_f_arg(fArgs[0])} is is_f_arg')

    if is_ndarray(accum):

        return eval_numpy_index(accum,fArgs)

    # Here we deal with the xedni case, fArgs[0] is an object.

    if has_initial_object(fArgs):

        obj=get_initial_object(fArgs)
        mirrorFArgs=mirror_index_f_arg(accum,fArgs)

        #print(f'{obj} is obj')
        #print(f'{mirrorFArgs} is mirrorFArgs')

        return args(eval_or_val(obj,mirrorFArgs))

    # Otherwise, we just evaluate recursively.

    else:

        accum=eval_or_val(accum,fArgs[0])

    index=eval_or_val(accum,fArgs[1][0])

    #print(f'{str(accum)[:100]} is accum after')
    #print(f'{is_ndarray(accum)} is nd_array')
    #print(f'{fArgs} is fArgs')
    #print(f'{index} is index')

    # Not found, so we return False.

    if not is_ndarray(accum) and accum is False:

        return FALSE_ARGS

    if is_number_indexable(accum):

        if index >= len(accum):

            return FALSE_ARGS

        return args(accum[index])

    if is_dict(accum):

        if is_dict(accum) and index not in accum:

            return FALSE_ARGS

        return args(accum[index])

    # No? Then let's see if it's an attribute of an object.

    #print('not dict, number indexable, or ndarray')
    if is_string(index) and hasattr(accum,index):

        #print('has attribute')
        accum=getattr(accum,index)
        #print(f'{is_callable(accum)} is is_callable')
        #print(f'{accum} is accum after getting attribute')
        # Now here's a problem - we need to deal with the case that the 
        # retrieved object is callable.  We're just going to take care of it 
        # in the main loop.

        return args(accum)

    return FALSE_ARGS



############
# CALLABLE #
############

def is_callable(fArg):

    return callable(fArg)



def eval_callable(accum,fArg):

    #print('='*30)

    try:

        #print(f'taking signature of {fArg}')

        argNum=len(Signature.from_callable(fArg)._parameters)

        #print(f'{argNum} is argNum')

        if argNum == 0:

            return args(fArg())

    except ValueError:

        pass

    return args(fArg(accum[ARGS][0]))


def eval_lambda_callable(accum,fArg):

    return args(fArg)


#######
# MAP #
#######

def is_map(fArg):

    return is_list(fArg) \
        and len(fArg) > 0 \
        and all([is_f_arg(f) for f in fArg])

#import pprint as pp

def eval_map(accum,fArg):

    accum=get_args(accum)
    
    #print('*'*30)
    #print('eval_map')
    #print('{} is accum iterable'.format(is_iterable(accum)))
    #pp.pprint('{} is accum'.format(accum))
    #pp.pprint('{} is fArg'.format(fArg))

    if is_mapping(accum):

        return args({k:pype(v,*fArg) for (k,v) in accum.items()})
    
    elif is_iterable(accum):
    
        return args([pype(v,*fArg) for v in accum])

    else:

        raise Exception('eval_map: accum is neither mapping nor iterable')


##########
# REDUCE #
##########

def is_reduce(fArg):

    #print('*'*30)
    #print('is_reduce')
    #print('{} is fArg'.format(fArg))
    #print('is list fArg {}'.format(is_list(fArg)))
    #print('len {}'.format(len(fArg) == 1 or len(fArg) == 2))
    #print('is tuple {}'.format(is_tuple(fArg[0])))
    #print('len fArg {}'.format(len(fArg[0]) == 1))
    #print('is_f_arg {}'.format(is_f_arg(fArg[0][0])))

    return is_list(fArg) \
        and (len(fArg) >= 1 and len(fArg) <= 3) \
        and is_tuple(fArg[0]) \
        and len(fArg[0]) == 1 \
        and is_f_arg(fArg[0][0]) 


def eval_reduce(accum,fArg):

    #print('*'*30)
    #print('eval_reduce')
    #print(f'{fArg} is fArg')
    
    accum=get_args(accum)

    #if len(fArg) >= 2:

    #    print(f'{fArg[1]} is fArg[1]')

    startVal=eval_or_val(accum,fArg[1]) if len(fArg) >= 2 else None

    #print(f'{accum} is accum')
    #print(f'{startVal} is val')

    if(len(fArg) == 3):

        accum=pype(accum,fArg[2])

    #print(f'now accum is {accum}')
    #print(f'now startVal is {startVal}')

    fArg=fArg[0][0]
    pype_f=lambda acc,x: pype(args(acc,x),fArg)

    if is_mapping(accum):

        accum=accum.values()

    elif not is_iterable(accum):

        raise Exception('eval_reduce: accum {} is not an iterable'.format(accum))

    red=reduce(pype_f,accum) if startVal is None else reduce(pype_f,accum,startVal)

    #print(f'{red} is red')

    return args(red)


###############
# SWITCH DICT #
###############

def is_switch_dict(fArg):

    return is_dict(fArg) and 'else' in fArg


def eval_switch_dict(accum,fArg):

    #print('*'*30)
    #print('eval_switch_dict')
    #print('{} is accum'.format(accum))
    #print('{} is fArg'.format(fArg))

    accum=accum[ARGS][0]
    
    #print('{} is accum'.format(accum))
    #print('{} is hashable'.format(is_hashable(accum)))

    #if is_hashable(accum) and accum in fArg:

    if is_container(fArg) and not is_container(accum) and accum in fArg:

        return args(eval_or_val(accum,fArg[accum]))

    #print('accum doesnt match keys')
    #print([(k,is_f_arg(k)) for k in fArg])

    fArgItems=[(delam(k),v) for (k,v) in fArg.items()]
    evals=[(bool(pype(accum,k)),v) for (k,v) in fArgItems if is_f_arg(k)]
    evalsTrue=[(k,v) for (k,v) in evals if is_bool(k) and k]
    v=evalsTrue[-1][1] if evalsTrue else fArg['else']
    ret=eval_or_val(accum,v)

    #print('{} is ret'.format(ret))
    #print('{} is args ret'.format(args(ret)))

    return args(eval_or_val(accum,ret))


def _if(condition,fArg):

    return {condition:fArg,
            'else':_}


def _iff(condition,fArg):

    return {condition:fArg,
            'else':False}
    

def _ifp(*fArgs):
    
    return {_:_p(*fArgs),
            'else':_}


def _iffp(*fArgs):
    
    return {_:_p(*fArgs),
            'else':False}




##########
# LAMBDA #
##########


def is_lambda(fArg):

    return is_tuple(fArg) \
        and len(fArg) > 1 \
        and not is_getitem(fArg[1]) \
        and (is_f_arg(fArg[0]) or isinstance(fArg[0],NameBookmark))


def eval_lambda(accum,fArgs):
    #print('*'*30)
    #print('eval_lambda')
    #print(f'{fArgs} is fArgs')
    firstAccum=accum
    accum=accum[ARGS][0]
    calledFArg=fArgs[0]
    # This is in cases where we do an indexing that returns a callable, like 
    # (_.add1,1).  

    # If it's not a function, the only thing it can possibly be is an index which
    # evals as a funciton.  
    if not is_callable(calledFArg):
        
        calledFArg=eval_index(firstAccum,calledFArg)[ARGS][0]

    if calledFArg is False:

        return FALSE_ARG

    if not is_callable(calledFArg):

        raise Exception(f'First fArg {str(calledFArg)[:100]} is not callable '
                        'in a lambda expression.')

    lambdaArgs=[eval_or_val(accum,f) for f in fArgs[1:]]

    #print(f'{str(lambdaArgs[1]o)[:100]} is lambdaArgs')

    return args(calledFArg(*lambdaArgs))                      


def eval_lambda_old(accum,fArgs):

    '''
    print('*'*30)
    print('eval_lambda')
    print(f'{str(accum)[:100]} is accum')
    print('{} is fArgs'.format(fArgs))
    print('{} is fArgs[1:]'.format(fArgs[1:]))
    '''

    accum=accum[ARGS][0]
    fArg=fArgs[0]
    
    if is_object_lambda(fArg):

        fArg=get_object_lambda_attr(accum,fArg)

        if not is_callable(fArg):

            raise Exception('Attempting to access a non-callable '
                            'feature {} of accum of type {}'\
                            .format(fArg,type(accum)))

    elif not is_callable(fArg):

        fArg=eval_or_val(accum,fArg)

    lambdaArgs=args(*[eval_or_val(accum,f) for f in fArgs[1:]])
    
    #print('{} is lambdaArgs'.format(lambdaArgs))
    #print('{} is eval of lambdaArgs'.format(pype(lambdaArgs,fArg)))

    return args(pype(lambdaArgs,fArg))


#################
# OBJECT LAMBDA #        
#################

def has_mirror_or_getter(fArg):

    if is_tuple(fArg) or is_list(fArg) and len(fArg) > 0:

        return has_mirror_or_getter(fArg[0])

    if is_mirror(fArg) or is_getter(fArg):

        return True

    return False

def is_object_lambda(fArg):

    #print('*'*30)
    #print('is_object_lambda')
    #print('{} is fArg'.format(fArg))
    # _.method.something (((_,['method']),['something']),)
    # (_.method,'something') => ((_,['method']),'something')
    # (_.method.othermethod,'something') => (((_,['method']),['othermethod']),'something')
 
    return is_tuple(fArg) \
        and len(fArg) > 1 \
        and has_mirror_or_getter(fArg[0]) \
        and is_string(fArg[1])


def get_object_lambda_attr(accum,fArgs):
    
    attr=fArgs[1]
    
    if is_dict(accum) and attr in accum:

        return accum[attr]

    if not hasattr(accum,attr):

        raise Exception('accum object of type {} '
                        'has no attribute {}'.format(type(accum),attr))

    attr=getattr(accum,attr)

    return attr


def eval_object_lambda(accum,fArgs):

    '''
    print('*'*30)
    print('eval_object_lambda')
    print('has_mirror_or_getter(fArgs) is {}'.format(has_mirror_or_getter(fArgs)))
    print('{} is fArgs'.format(fArgs))
    print('{} is accum'.format(accum))
    '''
    accum=accum[ARGS][0]

    if is_mirror(accum):

        obj=accum

    else:

        obj=eval_or_val(accum,fArgs[0])

    #print('{} is obj'.format(obj))

    attr=get_object_lambda_attr(obj,fArgs)

    if not is_f_arg(attr):

        return args(attr)

    fArgs=args(*[eval_or_val(accum,fArg) for fArg in fArgs[2:]])
    '''
    print('{} is attr'.format(attr))
    print('{} is fArgs'.format(fArgs))
    '''
    return args(eval_or_val(fArgs,attr))

##################
# FILTER HELPERS #
##################

def eval_filter(filter_f,accum,fArgs):

    #print('*'*30)
    #print('{} is accum'.format(accum))
    #print('{} is fArgs'.format(fArgs))

    accum=accum[ARGS][0]
    
    #print('{} is accum'.format(accum))
    #print('{} is eval'.format(args([v for v in accum if filter_f(v,fArgs)])))

    if not is_iterable(accum):

        raise Exception('eval_or_filter: accum is neither mapping nor iterable')

    if is_mapping(accum):

        return args({k:v for (k,v) in accum.items() if filter_f(v,fArgs)})
    
    elif is_iterable(accum):
    
        return args([v for v in accum if filter_f(v,fArgs)])

    else:

        raise Exception('eval_or_filter: accum is neither mapping nor iterable')

    

##########
# FILTER #
##########

def is_or_filter(fArg):

    #print('*'*30)
    #print('is_or_filter')
    #print(f'{fArg} is fArg')
    #print(f'{not is_set(fArg)} is not is_set(fArg)')

    # We had to pimp up this function when getting rid of the AND filter. 
    # First, we want to see if it's a singleton set.

    if not is_set(fArg):

        return False

    # Then, we get the first element of the set ...

    el=next(iter(fArg))

    #print(f'{el} is el')

    # Is it an fArg or a LamTup?

    #print(f'{is_f_arg(el)} is is_f_arg(el)')
    #print(f'{ is_lam_tup(el)} is is_lam_tup(el)')

    return is_f_arg(el) \
        or is_lam_tup(el)
        


def filter_or(v,fArgs):

    #print('*'*30)
    #print('filter_or')
    #print(f'{fArgs} is fArgs')
    # Now, when we evaluate, we need to unpack the set and apply delam to it.
    # We only delam it here because otherwise certain LamTups with embedded lists
    # will be unhashable.  

    fArgs=[delam(fArg) for fArg in fArgs]

    return any([pype(v,fArg) for fArg in fArgs])


def eval_or_filter(accum,fArgs):

    return eval_filter(filter_or,accum,fArgs)


################
# DICT HELPERS #
################

##############
# DICT BUILD #
##############

DICT_BUILD_ARGS=set([d])

def is_explicit_dict_build(fArg):

    return is_list(fArg) and len(fArg) >= 2 \
        and is_string(fArg[0]) and fArg[0] in DICT_BUILD_ARGS

    '''
    return is_list(fArg) and len(fArg) == 2 \
        and is_string(fArg[0]) and fArg[0] in DICT_BUILD_ARGS \
        and is_dict(fArg[1])
    '''

DICT_FARGS_LIMIT=10

valid_values=lambda ls: any([is_f_arg(el) or is_lam_tup(el) for el in ls])

def dict_values_farg(dct):

    values=list(dct.values())[:DICT_FARGS_LIMIT]

    if valid_values(values):

        return True

    keys=list(dct.keys())[:DICT_FARGS_LIMIT]
    
    if valid_values(keys):

        return True

    return False


def is_implicit_dict_build(fArg):

    return is_dict(fArg) and not 'else' in fArg and dict_values_farg(fArg)


def is_dict_build(fArg):

    # What about mappings??

    return (is_dict(fArg) and not 'else' in fArg and dict_values_farg(fArg)) \
        or is_explicit_dict_build(fArg)


def eval_dict_build(accum,fArgs):
    
    #print('*'*30)
    #print('eval_dict_build')
    #print('{} is accum'.format(accum))
    #print('{} is fArgs'.format(fArgs))

    if is_explicit_dict_build(fArgs):

        if len(fArgs) == 2:

            fArgs={fArgs[1]:accum[ARGS][0]}

        else:

            fArgs={k:v for (k,v) in zip(fArgs[1::2],fArgs[2::2])}

    # This is so that we can include lamTups in keys but not break the dictionary.

    fArgs=[(delam(k),v) for (k,v) in fArgs.items()]

    return args({eval_or_val(accum,k):eval_or_val(accum,v) for (k,v) in fArgs})


def _d(*fArgs):

    return [d,*fArgs]


def _dp(*fArgs):

    return [d,fArgs[0],_p(*fArgs[1:])]


def _select(*fArgs):

    return {fArg:_[fArg] for fArg in fArgs}


#########
# ASSOC #
#########

DICT_ASSOC_ARGS=set([assoc])

def is_dict_assoc(fArg):

    return is_list(fArg) \
        and len(fArg) >= 3 \
        and is_string(fArg[0]) \
        and fArg[0] in DICT_ASSOC_ARGS


def eval_dict_assoc(accum,fArg):

    accum=accum[ARGS][0]
    fArgs=fArg[1:]

    if len(fArgs) % 2 == 1:

        raise Exception('uneven number of keys in fArgs {}'.format(fArgs))

    if not is_mapping(accum):

        raise Exception('Trying to do a dict assoc with when accum '
                        'is of non-mapping type {}'.format(type(accum)))

    for (k,v) in zip(fArgs[0::2],fArgs[1::2]):

        accum[eval_or_val(accum,k)]=eval_or_val(accum,v)

    return args(accum)


def _assoc(*fArgs):

    return [assoc,*fArgs]


def _assoc_p(*fArgs):

    return [assoc,fArgs[0],_p(*fArgs[1:])]



#########
# MERGE #
#########

DICT_MERGE_ARGS=set([merge])

def is_dict_merge(fArg):

    return is_list(fArg) \
        and len(fArg) == 2 \
        and is_string(fArg[0]) and fArg[0] in DICT_MERGE_ARGS 


def eval_dict_merge(accum,fArg):

    #print('*'*30)
    #print('dict_merge')

    #print('{} is fArg'.format(fArg[0]))
    #print('is fArg {}'.format(is_dict_build(fArg[1])))

    accum=accum[ARGS][0]
    fArg=eval_or_val(accum,fArg[1])

    #rint('{} is accum'.format(accum))
    #rint('accum is mapping {}'.format(is_mapping(accum)))
    #rint('{} is fArg'.format(fArg))

    if not is_mapping(accum):

        raise Exception('Trying to do a dict assoc with when accum '
                        'is of non-mapping type {}'.format(type(accum)))

    if not is_mapping(fArg):

        raise Exception('Trying to do a dict assoc with when fArg '
                        'is of non-mapping type {}'.format(type(accum)))


    mergedDict={eval_or_val(accum,k):eval_or_val(accum,v) for (k,v) in fArg.items()}
    accum=dct_merge(accum,mergedDict)

    return args(accum)


def _merge(fArg):

    return [merge,fArg]


##########
# DISSOC #
##########

DICT_DISSOC_ARGS=set([dissoc])

def is_dict_dissoc(fArg):

    return is_list(fArg) \
        and len(fArg) > 1 \
        and is_string(fArg[0]) and fArg[0] in DICT_DISSOC_ARGS \


def eval_dict_dissoc(accum,fArg):

    accum=accum[ARGS][0]
    fArgs=[eval_or_val(accum,f) for f in fArg[1:]]

    for f in fArgs:

        accum=dct_dissoc(accum,f)

    return args(accum)


def _dissoc(*fArgs):

    return [dissoc,*fArgs]


##############
# LIST BUILD #
##############

LIST_BUILD_ARGS=set([l])

def is_list_build(fArg):

    return is_list(fArg) \
        and len(fArg) > 1 \
        and is_string(fArg[0]) and fArg[0] in LIST_BUILD_ARGS


def eval_list_build(accum,fArgs):

    #print('*'*30)
    #print('eval_list_build')

    return args([eval_or_val(accum,fArg) for fArg in fArgs[1:]])


def _l(*fArgs):

    return [l,*fArgs]


###############
# LIST APPEND #
###############

LIST_APPEND_ARGS=set([append])

def is_list_append(fArg):

    return is_list(fArg) \
        and len(fArg) > 1 \
        and is_string(fArg[0]) \
        and fArg[0] in LIST_APPEND_ARGS


def coerce_to_list(accum):

    if is_list(accum):
       
        return accum

    try:
        
        return list(accum)

    except Exception as e:

        raise e
    

def eval_list_append(accum,fArgs):

    accum=coerce_to_list(accum[ARGS][0])

    accum.extend([eval_or_val(accum,fArg) for fArg in fArgs[1:]])

    return args(accum)


def _append(*fArgs):

    return [append,*fArgs]


###############
# LIST CONCAT #
###############

LIST_CONCAT_ARGS=set([concat])

def is_list_concat(fArg):

    return is_list(fArg) \
        and len(fArg) > 1 \
        and is_string(fArg[0]) \
        and fArg[0] in LIST_CONCAT_ARGS


def eval_list_concat(accum,fArgs):

    accum=coerce_to_list(accum[ARGS][0])
    evalLS=[eval_or_val(accum,fArg) for fArg in fArgs[1:]]
    ls=[]

    for el in evalLS:

        if is_list(el) or is_tuple(el):

            ls.extend(el)

        else:

            ls.append(el)

    return args(ls)


def _concat(*fArgs):

    return [concat,*fArgs]


##############
# WHILE LOOP #
##############

WHILE_LOOP_ARGS=set([while_loop])

def is_while_loop(fArg):

    return is_list(fArg) \
        and (len(fArg) >= 2 and len(fArg) <= 4) \
        and is_string(fArg[0]) \
        and fArg[0] in WHILE_LOOP_ARGS


def eval_while_loop(accum,fArg):

    #print('*'*30)
    #print('eval_while_loop')
    #print('{} is fArg'.format(fArg))

    accum=accum[ARGS][0]
    condition=fArg[1] # continue loop condition
    function=fArg[2] # perform on value while condition is true

    if len(fArg) == 2:

        val=accum

    if len(fArg) == 3:

        #print(f'evaluating against function {function}')

        val=eval_or_val(accum,function)

    else:

        #print(f'evaluating against starting val {fArg[3]}')

        val=eval_or_val(accum,fArg[3])

    #print('{} is p(1,_>4)'.format(pype(1,_<4)))
    #print('{} is accum'.format(accum))
    #print('{} is condition'.format(condition))
    #print('{} is function'.format(function))
    #print('{} is startingVal'.format(startingVal))
    #print('{} is val'.format(val))
    #print('bool(pype(val,condition)) is {}'.format(bool(pype(val,condition))))
    #print('*'*30)

    #print(f'{val["diff"]} is diff')
    #print(f'{condition} is condition')
    #print(f'bool(pype(val,condition)) is {bool(pype(val,condition))}')

    while bool(pype(val,condition)):

        #print(f'bool(pype(val,condition)) is {bool(pype(val,condition))}')
        #print(f'{val} is val')

        val=pype(val,function)

    #print('val is now {}'.format(val))

    return args(val)


def _while_loop(*fArgs):

    return [while_loop,*fArgs]


def _while_list_append(condition,append_function,initialValue):

    return _while_loop(condition,
                       _append(append_function),
                       initialValue)

def _while_range(condition,append_function,initialValue):

    return _while_loop(condition,
                       _append(append_function),
                       _l(initialValue))


#################
# EMBEDDED PYPE #
#################

PYPE_ARGS=set([embedded_pype])

def is_embedded_pype(fArg):

    #print('*'*30)
    #print('is_embedded_pype')

    return is_list(fArg) \
        and len(fArg) > 1 \
        and is_string(fArg[0]) \
        and fArg[0] in PYPE_ARGS


def eval_embedded_pype(accum,fArg):

    #print('*'*30)
    #print('eval_embedded_pype')
    #print('{} is accum'.format(accum))
    #print('{} is fArg'.format(fArg))
    #print('{} is fArg[0]'.format(fArg[0] == _p))

    fArgs=fArg[1:]

    return args(pype(accum,*fArgs))


def _p(*fArgs):

    return [embedded_pype,*fArgs]



############
# ALL ARGS #
############

ALL_ARGS=set().union(PYPE_ARGS,
                     DICT_BUILD_ARGS,
                     DICT_MERGE_ARGS,
                     DICT_DISSOC_ARGS,
                     DICT_ASSOC_ARGS,
                     LIST_BUILD_ARGS,
                     LIST_APPEND_ARGS,
                     LIST_CONCAT_ARGS,
                     WHILE_LOOP_ARGS)


#########
# QUOTE #
#########

def is_quote(fArg):

    return isinstance(fArg,Quote)


def eval_quote(accum,fArg):

    print('eval_quote')
    accum=accum[ARGS][0]
    print('{} is accum'.format(accum))
    print('{} is fArg'.format(fArg))
    print('{} is quote'.format(is_quote(fArg)))
    print('{} is fArg.val()'.format(fArg.val()))

    val=fArg.val()

    return args(val)


######
# DO #
######

def is_do(fArg):

    return is_list(fArg) and len(fArg) > 1 and fArg[0] == do


def eval_do(accum,fArg):

    #print('eval_do')
    #print('{} is accum'.format(accum))
    #print('{} is fArgs'.format(fArgs))

    accum=accum[ARGS][0]
    newAccum=eval_or_val(accum,fArg[1])

    #print('{} is newAccum'.format(newAccum))
    #print('{} is accum'.format(accum))

    if newAccum is None:

        return args(accum)

    return args(newAccum)


def _do(fArg):

    return [do,fArg]


########
# MAIN #
########

# These are for lambdas in the first position.
QUOTE_PAIRS=[(is_mirror,eval_mirror),
             (is_map,eval_map),
             (is_callable,eval_callable),
             (is_reduce,eval_reduce),
             (is_or_filter,eval_or_filter),
             (is_switch_dict,eval_switch_dict),
             (is_lambda,eval_lambda),
             (is_index,eval_index),
             (is_dict_build,eval_dict_build),
             (is_dict_assoc,eval_dict_assoc),
             (is_dict_merge,eval_dict_merge),
             (is_dict_dissoc,eval_dict_dissoc),
             (is_list_build,eval_list_build),
             (is_list_append,eval_list_append),
             (is_list_concat,eval_list_concat),
             (is_quote,eval_quote),
             (is_while_loop,eval_while_loop),
             (is_do,eval_do),
             (is_embedded_pype,eval_embedded_pype),
           ]
FARG_PAIRS=[(is_mirror,eval_mirror),
            (is_callable,eval_callable),
            (is_map,eval_map),
            (is_reduce,eval_reduce),
            (is_or_filter,eval_or_filter),
            (is_switch_dict,eval_switch_dict),
            (is_lambda,eval_lambda),
            (is_index,eval_index),
            (is_dict_build,eval_dict_build),
            (is_dict_assoc,eval_dict_assoc),
            (is_dict_merge,eval_dict_merge),
            (is_dict_dissoc,eval_dict_dissoc),
            (is_list_build,eval_list_build),
            (is_list_append,eval_list_append),
            (is_list_concat,eval_list_concat),
            (is_quote,eval_quote),
            (is_while_loop,eval_while_loop),
            (is_do,eval_do),
            (is_embedded_pype,eval_embedded_pype),
           ]


def get_args(accum):

    accum=accum[ARGS]
    
    return accum[0] if len(accum) == 1 else accum

    
def is_f_arg(fArg):

    return any([is_f(fArg) for (is_f,evl) in FARG_PAIRS])

import traceback
import sys
import time as tm

def pype_eval(accum,fArg,fArgPairs=FARG_PAIRS):

    '''
    print('*'*30)
    print('pype_eval')
    print('{} is accum'.format(accum))
    print('{} is fArg'.format(fArg))
    print([(is_f,evl) for (is_f,evl) in FARG_PAIRS if is_f(fArg)])
    '''

    evalList=[evl for (is_f,evl) in fArgPairs if is_f(fArg)]

    if not evalList:

        raise Exception('fArg {} does not match any fArg types'.format(fArg))

    eval_f=evalList[-1]

    #print(f'{str(accum)[:100]} is accum')
    #print(f'{fArg} is fArg')
    #print(f'{evalList} is evalList')
    #print(f'{eval_f} is eval_f')

    try:

        # Here we add some boilerplate for time-logging. 

        if 'timing' in PYPE_LOGGING and PYPE_LOGGING['timing'] is True:

            eval_with_time(eval_f,accum,fArg)

        val=eval_f(accum,fArg)

        #print(f'after first eval of {eval_f} on {fArg} val is {val}')

        # In the case that a callable is returned, we do a greedy evaluation on the
        # fArg.  This allows us to handle object lambdas, xednis, indexes, and
        # mirrors.  If we have _.keys it will work.  If we have (_.func,1), 
        # _.func needs to be evaluated on 1.  So lambda cannot return a callable.  
        
        # If it's a quote, and the quote returns a callable, we do not evaluate
        # this callable. THIS IS A SHORT_TERM SOLUTION - we need different fArg 
        # pairs for different fArg solutions!!!!

        if val[ARGS] and is_callable(val[ARGS][0]):

            val=eval_callable(accum,val[ARGS][0])

            #print(f'after second eval of {eval_f} val is {str(val)[:100]}')

        # Some boilerplate for keeping track of the fArg.

        if 'trace' in PYPE_LOGGING and PYPE_LOGGING['trace'] is True:

            trace(accum,fArg,eval_f,val)
  
        return val

    except Exception as e:

        exc_type, exc_value, exc_traceback = sys.exc_info()

        ls=traceback.format_exception(type(e),e,exc_traceback)
        ls=[el for el in ls if '__init__' not in el \
            and 'Traceback' not in el]
        
        print('*'*30)
        print(' '.join(ls))

        raise e


def trace(accum,fArg,eval_f,val):

    print('*'*30)
    print(f'{accum} is accum')
    print(f'{fArg} is fArg')
    print(f'{eval_f} is eval_f')
    print(f'{val} is eval_f(accum,fArg)')


def eval_with_time(eval_f,accum,f_arg):

    t0=tm.time()
    val=eval_f(accum,fArg)
    d=tm.time() - t0

    if 'threshold' in PYPE_LOGGING and d >= PYPE_LOGGING['threshold']:
        
        print('='*30)
        pp.pprint(fArg)
        print(f'time to eval: {tm.time() - t0}')
    
    return val


import pprint as pp

def pype(accum,*fArgs):
    '''
    Accum is either an arg dict or an expression.
    '''
    #print('*'*30)
    #print('pype')
    #print('{} is fArgs'.format(fArgs))
    #pp.pprint(accum)
    #pp.pprint('is accum')

    if is_pype_val(accum):

        accum=accum.val()

    if not is_arg_dict(accum):

        #print('{} is not arg_dict'.format(accum))

        accum=args(accum)

    fArgs=[delam(fArg) for fArg in fArgs]

    try:

        accum=reduce(pype_eval,fArgs,accum)[ARGS]

        return accum[0] if len(accum) == 1 else accum

    except Exception as e:

        raise e

##############
# BUILD PYPE #
##############

def build_pype(*fArgs):

    return lambda accum: pype(accum,*fArgs)


def build_pype_multi(*fArgs):

    return lambda *accum: pype(args(*accum),*fArgs)


########
# TEST #
########

def test():

    #############
    # INDEX ARG #
    #############

    ls=[0,1,2,3]
    dct={'a':8,'b':9}

    def add1(dct): 

        dct['another10']=10

        return dct

    def add2(dct): 

        dct['another20']=20

        return dct

    funcDct={'add1':add1,
             'add2':add2}

    print(f'{ls} is ls')
    print(f'{dct} is dct')
    print(f'{add1} is add1')

    print('*'*30)
    print('INDEX ARG')

    print(f'{pype(ls,_0)} is pype(ls,_0)')
    print(f'{pype(ls,_1)} is pype(ls,_1)')
    print(f'{pype(ls,_2)} is pype(ls,_1)')

    print('*'*30)
    print('INDEX')

    print(f'{pype(ls,_[0])} is pype(ls,_[0])')
    print(f'{pype(ls,_[1])} is pype(ls,_[1])')
    print(f'{pype(ls,_[2])} is pype(ls,_[1])')

    print(f'{pype(dct,_["a"])} is pype(dct,_["a"])')
    print(f'{pype(dct,_["b"])} is pype(dct,_["b"])')

    print(f'{pype(dct,_.a)} is pype(dct,_.a)')
    print(f'{pype(dct,_.b)} is pype(dct,_.b)')
    print('Now trying function values of dicitonaries')

    print(f'{pype(funcDct,_["add1"])} is pype(funcDct,_["add1"])')
    print(f'{pype(funcDct,_["add2"])} is pype(funcDct,_["add2"])')

    print(f'{pype(funcDct,_.add1)} is pype(funcDct,_.add1)')
    print(f'{pype(funcDct,_.add2)} is pype(funcDct,_.add2)')

    print('*'*30)
    print('CALLING OBJECTS')
    
    class Caller:

        def call_me(self):

            return "hi"

    cllr=Caller()

    print(f'{cllr} is Caller')

    print(f'{pype(cllr,_.call_me)} is pype(cllr,_.call_me)')

if __name__=='__main__':

    test()
