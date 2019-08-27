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

__version__='1.0.1'

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
is_sequence=lambda x: isinstance(x,Sequence) or is_ndarray(x)
is_container=lambda x: isinstance(x,Container)

key=lambda x: tup[0]
val=lambda x: tup[1]
slc=lambda ls,start,stop: ls[start:stop]

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
#_0,_1,_2,_3=[(_,[i]) for i in range(4)]
_0=Getter('_arg0_')
_1=Getter('_arg1_')
_2=Getter('_arg2_')
_3=Getter('_arg3_')
_last=Getter('_arg_last')
INDEX_ARG_DICT={k:i for (i,k) in enumerate([_0,_1,_2,_3])}
INDEX_ARG_DICT[_last]=-1
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

    return pype(accum,fArg) if is_f_arg(val) else accum


##########
# MIRROR #
##########

def is_mirror(fArg):

    return is_getter(fArg) and fArg in MIRROR_SET

def eval_mirror(accum,fArg):

    return accum


#############
# INDEX ARG #
#############

def is_index_arg(fArg):

    #print('*'*30)
    #print('is_index_arg')
    #print('{} is fArg'.format(fArg))
    #print('is_getter {}'.format(is_getter(fArg) and fArg in INDEX_ARG_DICT))
    
    return is_getter(fArg) and fArg in INDEX_ARG_DICT


def eval_index_arg(accum,fArg):

    #print('*'*30)
    #print('eval_index_arg')
    #print('{} is fArg'.format(fArg))

    accum=accum[ARGS][0]
    index=INDEX_ARG_DICT[fArg]

    #print('{} is accum'.format(accum))

    if not is_dict(accum) and not is_sequence(accum):

        raise Exception('eval_index_arg: accum of type {} '
                        'must be sequence or dict'.format(type(accum)))

    if len(accum) <= index:

        raise Exception('eval_index_arg: accum of length {} '
                        'cannot be accessed by index {}'.format(len(accum),index))

    #print('{} is index'.format(index))
    #print('{} is accum[index]'.format(accum[index]))
    #print('{} is eval_or_val'.format(eval_or_val(accum,accum[index])))
    #print('{} accum[index] is farg'.format(is_f_arg(accum[index])))
    #print('is_farg: {}'.format([(is_f(accum[index]),evl) for (is_f,evl) in FARG_PAIRS]))
    #print('returning {}'.format(args(eval_or_val(accum,accum[index]))))

    # UNDER WHAT CIRCUMSTANCES WOULD YOU GET AN ARRAY ELEMENT AND EVAL IT!

    #return args(eval_or_val(accum,accum[index]))
    return args(accum[index])


############
# CALLABLE #
############

def is_callable(fArg):

    return callable(fArg)


def eval_callable(accum,fArg):

    return args(fArg(*accum[ARGS]))


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

        #print(f'{fArg[1]} is fArg[1]')

    startVal=eval_or_val(accum,fArg[1]) if len(fArg) >= 2 else None

    #print(f'{accum} is accum')

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


#########
# INDEX #
#########

def is_getitem(el):

    return is_list(el) \
        and len(el) == 1


def is_indexable(el):

    return is_sequence(el) or is_mapping(el)


def is_index_old(fArg):

    #print('*'*30)
    #print('is_index')
    #print('fArg[0] is_index {}'.format(is_tuple(fArg) and is_indexable(fArg[0])))

    return is_tuple(fArg) \
        and len(fArg) >= 2 \
        and (fArg[0] == _ or is_f_arg(fArg[0])) \
        and all([is_getitem(f) for f in fArg[1:]])


def get_index(el):

    #print('*'*30)
    #print('get_index')
    #print('{} is el'.format(el))
    
    return el[0]


def has_mirror(fArg):

    if is_mirror(fArg):

        return True

    if (is_list(fArg) or is_tuple(fArg)) and len(fArg) >= 1:
        
        return has_mirror(fArg[0])

    return False


def has_index_arg(fArg):

    if is_index_arg(fArg):

        return True

    if (is_list(fArg) or is_tuple(fArg)) and len(fArg) >= 1:
        
        return has_index_arg(fArg[0])

    return False

    
def is_index(fArg):

    return is_tuple(fArg) \
        and len(fArg) == 2 \
        and is_getitem(fArg[1]) \
        and (has_mirror(fArg[0]) or has_index_arg(fArg[0]))
        #and (fArg[0] == _ or is_f_arg(fArg[0])) 



def eval_index(accum,fArgs):

    accum=accum[ARGS][0]
    #pp.pprint(accum)
    #print('is accum')

    if accum == False:

        return args(False)

    if not is_indexable(accum):

        raise Exception('{} is not a sequence or a mapping'.format(accum))

    accum=eval_or_val(accum,fArgs[0])

    if accum == False:

        return args(False)
    
    index=eval_or_val(accum,fArgs[1][0])

    #if index == False:

    #    return args(False)

    if (is_list(accum) or is_tuple(accum)) \
       and index > len(accum)-1:
        
        return args(False)
    
    if is_dict(accum) and index not in accum:
        
        return args(False)

    return args(accum[index])

        
    

def eval_index_old(accum,fArg):

    #print('*'*30)
    #print('eval_index')

    accum=accum[ARGS][0]
    
    #print('{} is fArg'.format(fArg))
    
    accum=eval_or_accum(accum,fArg[0])

    #print('{} is accum'.format(accum))
    #print('{} is fArg'.format(fArg))

    if not is_indexable(accum):

        raise Exception('{} is not a sequence or a mapping'.format(accum))

    try:

        indices=[eval_or_val(accum,get_index(f)) for f in fArg[1:]]

        #print('{} is indices'.format(indices))

        val=reduce(lambda acc,index: acc[index],indices,accum)

        return args(val)

    except Exception as e:

        raise e


#########
# XEDNI #
#########

def is_xedni(fArg):

    return is_tuple(fArg) \
        and len(fArg) >= 2 \
        and is_indexable(fArg[0]) and not is_f_arg(fArg[0]) \
        and all([is_getitem(f) for f in fArg[1:]])


def eval_xedni(accum,fArg):

    #print('*'*30)
    #print('eval_xedni')
    #print('{} is accum'.format(accum))
    #print('{} is fArg'.format(fArg))

    accum=accum[ARGS][0]
    indexable=fArg[0]

    if not is_sequence(indexable) and not is_mapping(indexable):

        raise Exception('{} is not a sequence or a mapping'.format(indexable))

    try:

        #print('{} is fArg[1:]'.format(fArg[1:]))

        indices=[get_index(f) for f in fArg[1:]]

        #print('{} is indices'.format(indices))

        indices=[eval_or_val(accum,get_index(f)) for f in fArg[1:]]

        #print('{} is indices'.format(indices))

        val=reduce(lambda acc,index: acc[index],indices,indexable)

        return args(val)

    except Exception as e:

        raise e


##########
# LAMBDA #
##########

def is_lambda(fArg):

    #print('*'*30)
    #print('is_lambda')
    #print(f'{fArg} is fArg')
    
    #isLam=is_tuple(fArg) \
    #    and len(fArg) >= 1 \
    #    and not is_mirror(fArg[0]) \
    #    and is_f_arg(fArg[0])
    #print(f'{isLam} is lam')

    return is_tuple(fArg) \
        and len(fArg) >= 1 \
        and not is_mirror(fArg[0]) \
        and is_f_arg(fArg[0])


def eval_lambda(accum,fArgs):

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
    # (_,'method')
 
    return is_tuple(fArg) \
        and len(fArg) > 1 \
        and has_mirror_or_getter(fArg[0]) \
        and is_string(fArg[1])


def get_object_lambda_attr(accum,fArgs):
    
    attr=fArgs[1]
    
    if not hasattr(accum,attr):

        raise Exception('accum object of type {} '
                        'has no attribute {}'.format(type(accum),attr))

    attr=getattr(accum,attr)

    return attr


def eval_object_lambda(accum,fArgs):

    #print('*'*30)
    #print('eval_object_lambda')
    #print('has_mirror_or_getter(fArgs) is {}'.format(has_mirror_or_getter(fArgs)))
    #print('{} is fArgs'.format(fArgs))
    #print('{} is accum'.format(accum))

    accum=accum[ARGS][0]

    if is_mirror(accum):

        obj=accum

    else:

        obj=eval_or_val(accum,fArgs[0])

    #print('{} is obj'.format(obj))

    attr=get_object_lambda_attr(obj,fArgs)
    fArgs=args(*[eval_or_val(accum,fArg) for fArg in fArgs[2:]])

    #print('{} is attr'.format(attr))
    #print('{} is fArgs'.format(fArgs))

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

    

##############
# AND FILTER #    
##############

def is_and_filter(fArg):

    return is_list(fArg) \
        and len(fArg) == 1 \
        and is_list(fArg[0]) \
        and len(fArg[0]) >= 1 \
        and (not is_string(fArg[0][0]) or fArg[0][0] not in ALL_ARGS) \
        and all([is_f_arg(f) for f in fArg[0]])


def filter_and(v,fArgs):

    #print('*'*30)
    #print('filter_and')
    #print('{} is fArgs'.format(fArgs))
    #print('{} is f_arg'.format(is_lambda(fArgs[0])))
    #print('{} is v'.format(v))

    return all([pype(v,fArg) for fArg in fArgs])


def eval_and_filter(accum,fArgs):

    fArgs=[delam(f) for f in fArgs[0]]

    return eval_filter(filter_and,accum,fArgs)


#############
# OR FILTER #
#############

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

#############
# FOR INDEX #
#############

def is_for_index(fArg):

    return is_getter(fArg) \
        and fArg in FOR_ARG_DICT


def eval_for_index(accum,fArg):

    accum=accum[ARGS][0]
    index=FOR_ARG_DICT[fArg]

    return accum[index]


############
# FOR LOOP #
############

def is_for_loop(fArg):

    return is_list(fArg) \
        and len(fArg) >= 1 \
        and is_tuple(fArg[0]) \
        and len(fArg[0]) > 1 \
        and all([is_getitem(el) for el in fArg[0]])


def eval_for_indices(tup,fArg):
    ''' 
    What we are trying to do here is rebuild the expression, 
    replacing only the for indices.
    '''
    #print('*'*30)
    #print('eval_for_indices')
    #print('{} is tup'.format(tup))
    #print('{} is fArg'.format(fArg))

    if is_for_index(fArg):

        return eval_for_index(args(tup),fArg)

    elif is_string(fArg):

        return fArg

    elif is_mapping(fArg):

        #print('is mapping')

        return {eval_for_indices(k):eval_for_indices(v) \
                for (k,v) in fArg.items()}

    elif is_iterable(fArg):

        #print('is iterable')

        ls=[eval_for_indices(tup,el) for el in fArg]

        if is_tuple(fArg):

            return tuple(ls)

        return ls

    else:

        return fArg
    
        
def eval_for_loop(accum,fArg):

    #print('*'*30)
    #print('eval_for_loop')
    #print('{} is fArg'.format(fArg))

    accum=accum[ARGS][0]
    forLoopItems=[eval_or_val(accum,f[0]) for f in fArg[0]]
    forLoopItems=[range(item) if is_int(item) else item \
                  for item in forLoopItems]

    if len(fArg) > 1:

        fArg=fArg[1]

        #print('{} is tup replaced expression'\
        #      .format([eval_for_indices(tup,fArg) \
        #               for tup in product(*forLoopItems)]))
        #print('{} is evalled tup replaced'\
        #      .format(args([eval_or_val(accum,eval_for_indices(tup,fArg)) \
        #             for tup in product(*forLoopItems)])))

        return args([eval_or_val(accum,eval_for_indices(tup,fArg)) \
                     for tup in product(*forLoopItems)])

    return args(list(product(*forLoopItems)))


#########
# QUOTE #
#########

def is_quote(fArg):

    return isinstance(fArg,Quote)


def eval_quote(accum,fArg):

    #print('eval_quote')
    #print('{} is accum'.format(accum))
    #print('{} is fArg'.format(fArg))
    #print('{} is quote'.format(is_quote(fArg)))
    #print('{} is fArg.val()'.format(fArg.val()))

    return args(fArg.val())


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

FARG_PAIRS=[(is_mirror,eval_mirror),
            (is_index_arg,eval_index_arg),
            (is_callable,eval_callable),
            (is_map,eval_map),
            (is_for_loop,eval_for_loop),
            (is_reduce,eval_reduce),
            #(is_and_filter,eval_and_filter),
            (is_or_filter,eval_or_filter),
            (is_switch_dict,eval_switch_dict),
            (is_lambda,eval_lambda),
            (is_index,eval_index),
            (is_object_lambda,eval_object_lambda),
            (is_xedni,eval_xedni),
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


def is_arg_dict(*accum):

    return accum and is_dict(accum[0]) and ARGS in accum[0]


def args(*accum):

    # PROJECT - THINK OF PRE-INITIALIZING DICTIONARIES AND POPPING THEM FROM A STACK

    if is_arg_dict(*accum):

        return accum

    return {ARGS:accum}


def get_args(accum):

    accum=accum[ARGS]
    
    return accum[0] if len(accum) == 1 else accum

    
def is_f_arg(fArg):

    return any([is_f(fArg) for (is_f,evl) in FARG_PAIRS])

import traceback
import sys
import time as tm

def pype_eval(accum,fArg):

    '''
    print('*'*30)
    print('pype_eval')
    print('{} is accum'.format(accum))
    print('{} is fArg'.format(fArg))
    print([(is_f,evl) for (is_f,evl) in FARG_PAIRS if is_f(fArg)])
    '''

    evalList=[evl for (is_f,evl) in FARG_PAIRS if is_f(fArg)]

    if not evalList:

        raise Exception('fArg {} does not match any fArg types'.format(fArg))

    eval_f=evalList[-1]

    #print(f'{eval_f} is eval_f')

    try:

        if 'timing' in PYPE_LOGGING and PYPE_LOGGING['timing']==True:

            t0=tm.time()

            v=eval_f(accum,fArg)
        
            d=tm.time() - t0

            if 'threshold' in PYPE_LOGGING and d >= PYPE_LOGGING['threshold']:

                print('='*30)
                pp.pprint(fArg)
                print(f'time to eval: {tm.time() - t0}')

            return v

        if 'trace' in PYPE_LOGGING and PYPE_LOGGING['trace']==True:

            print('*'*30)
            print(f'{accum} is accum')
            print(f'{fArg} is fArg')
            print(f'{eval_f} is eval_f')
            print(f'{eval_f(accum,fArg)} is eval_f(accum,fArg)')

        return eval_f(accum,fArg)

    except Exception as e:

        exc_type, exc_value, exc_traceback = sys.exc_info()

        ls=traceback.format_exception(type(e),e,exc_traceback)
        ls=[el for el in ls if '__init__' not in el \
            and 'Traceback' not in el]
        
        print('*'*30)
        print(' '.join(ls))

        raise e

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
# DEMO #
########

def demo():

    print("WELCOME TO PYPE!")
    print("Here are several pype expressions, with their values")

    print("="*30)

    call_me=lambda : 1
    add1=lambda x: x+1
    sm=lambda x,y: x+y

    ##################
    # CHECKING FARGS #
    ##################

    print('>'*30)
    print('CHECKING FARGS')
    print('>'*30)

    print('='*30)
    print('is_callable(call_me)')

    x=is_callable(call_me)

    print(x)

    assert(x == True)

    print('='*30)
    print('is_mirror(_)')

    x=is_f_arg(call_me)

    print(x)

    assert(x == True)

    print('='*30)
    print('is_map([add1,add1])')

    x=is_map([add1,add1])

    print(x)

    assert(x == True)

    print('='*30)
    print('is_map([add1,add1,_])')

    x=is_map([add1,add1,_])

    print(x)

    assert(x == True)

    sm=lambda x,y: x+y

    print('='*30)
    print('is_reduce([(sm,)])')

    x=is_reduce([(sm,)])

    print(x)

    assert(x == True)

    print('='*30)
    print('is_reduce([(sm,),1])')

    x=is_reduce([(sm,),1])

    print(x)

    assert(x == True)

    print('='*30)
    print('is_switch_dict({1:2,3:4,"else":5})')

    x=is_switch_dict({1:2,3:4,'else':5})

    print(x)

    assert(x == True)

    print('='*30)
    print('is_lambda((add1,_))')

    x=is_lambda((add1,_))

    print(x)

    assert(x == True)

    print('='*30)
    print('is_index((_,[2]))')

    x=is_index((_,[2]))

    print(x)

    assert(x == True)

    print('='*30)
    print('is_index((_,[2],[3],[4]))')

    x=is_index((_,[2]))

    print(x)

    assert(x == True)

    ########
    # ARGS #
    ########

    print('>'*30)
    print('ARGS')
    print('>'*30)
    
    print('args(1)')
    print(args(1))

    print('args([1,2,3])')
    print(args([1,2,3]))

    print('args({ARGS:(1,2,3)})')
    print(args({ARGS:(1,2,3)}))

    ############
    # CALLABLE #
    ############

    print('>'*30)
    print('CALLABLE')
    print('>'*30)

    add1=lambda x: x+1

    print('='*30)
    print('pype(1,add1)')

    x=pype(1,add1)

    print(x)
    
    assert(x == 2)

    print('='*30)
    print('pype(1,add1,add1,add1)')

    x=pype(1,add1,add1,add1)

    print(x)
    
    assert(x == 4)

    ##########
    # MIRROR #
    ##########

    print('>'*30)
    print('MIRROR')
    print('>'*30)

    print('='*30)
    print('pype(1,_)')

    x=pype(1,_)
    
    print(x)

    assert(x == True)

    print('='*30)
    print('pype(1,add1,_)')

    x=pype(1,add1,_)
    
    print(x)

    assert(x == 2)

    #############
    # INDEX ARG #
    #############

    print('>'*30)
    print('INDEX ARG')
    print('>'*30)

    print('='*30)

    print('pype(tup,_0)')

    tup=(1,2,3)

    x=pype(tup,_0)

    print(x) 

    assert(x == 1)

    print('='*30)

    print('pype(tup,_1)')

    tup=(1,2,3)

    x=pype(tup,_1)

    print(x) 

    assert(x == 2)


    #######
    # MAP #
    #######

    print('>'*30)
    print('MAP')
    print('>'*30)

    print('='*30)
    print('pype([1,2,3,4],[add1]')

    x=pype([1,2,3,4],[add1])

    print(x)

    assert(x == [add1(1),add1(2),add1(3),add1(4)])

    print('='*30)
    print('pype({1:1,2:2},[add1]')

    x=pype({1:1,2:2},[add1])

    print(x)

    assert(x == {1:add1(1),2:add1(2)})

    ##########
    # REDUCE #
    ##########

    print('>'*30)
    print('REDUCE')
    print('>'*30)

    print('='*30)
    print('pype([1,2,3],[(sm,)])')
    
    x=pype([1,2,3],[(sm,)])
    
    print(x)

    assert(x == 6)

    print('='*30)
    print('pype({1:1,2:2},[(sm,)])')
    
    x=pype({1:1,2:2},[(sm,),1])
    
    print(x)

    assert(x == 4)

    print('='*30)
    print('pype([1,1,1},[(sm,),1,[add1]])')
    
    x=pype([1,1,1],[(sm,),1,[add1]])
    
    print(x)

    assert(x == 7)
    
    #sys.exit(1)

    ###############
    # SWITCH DICT #
    ###############

    print('>'*30)
    print('SWITCH DICT')
    print('>'*30)

    print('pype(1,{1:"one",2:"two","else":"nothing"})')

    x=pype(1,{1:"one",2:"two","else":"nothing"})

    print(x)

    assert(x == "one")

    print('='*30)

    gt1=lambda x: x > 1
    lt3=lambda x: x < 3

    print('pype(1,{gt1:"greater 1", lt3:"less than three", "else":_')

    x=pype(1,{gt1:"greater 1", lt3:"less than three", "else":_})

    print(x)

    assert(x == 'less than three')

    print('pype(5,{gt1:"greater 1","else":_')

    x=pype(-5,{gt1:"greater 1","else":_})

    print(x)

    assert(x == -5)

    add2=lambda x: x+2

    print('='*30)

    print('pype(5,{gt1:"greater 1","else":add1')

    x=pype(5,{gt1:add2,"else":add1})

    print(x)

    assert(x == 7)

    print('='*30)
    
    print('pype(1,(sm,_,2))')

    x=pype(1,(sm,_,2))

    print(x)
    
    assert(x == 3)


    #########
    # INDEX #
    #########

    print('>'*30)
    print('INDEX')
    print('>'*30)

    print('='*30)

    ls=[1,2,3,4]

    print('pype(ls,(_,[0])))')

    x=pype(ls,(_,[0]))

    print(x)
    
    assert(x == 1)

    print('='*30)

    dct={1:2,3:4}

    print('pype(dct,(_,[3]))')

    x=pype(dct,(_,[3]))

    print(x)
    
    assert(x == 4)

    bigLS=[[1,2,3],[2,3,4]]

    print('='*30)

    print('pype(bigLS,(_,[0],[1]))')

    x=pype(bigLS,(_,[0],[1]))

    print(x)

    assert(x == 2)

    print('='*30)

    print('pype(ls,(_,[(sub,(len,_),1)]))')

    x=pype(ls,(_,[(sub,(len,_),1)]))

    print(x)

    assert(x == 4)

    #########
    # XEDNI #
    #########

    print('>'*30)
    print('XEDNI')
    print('>'*30)

    print('='*30)

    print('pype(1,(ls,[_]))')

    x=pype(1,(ls,[_]))

    print(x)

    assert(x == 2)

    print('='*30)

    print('pype(1,(ls,[(add,_,1)]))')

    x=pype(1,(ls,[(add,_,1)]))

    print(x)

    assert(x == 3)

    print('='*30)

    print('pype([0,1],[(ls,[_])]')

    x=pype([0,1],[(ls,[_])])

    print(x)

    assert(x == [1,2])

    print('='*30)

    print('pype([0,1],[(ls,[(add,_,1)])])')

    x=pype([0,1],[(ls,[(add,_,1)])])

    print(x)

    assert(x == [2,3])
    
    ##########
    # LAMBDA #
    ##########

    print('>'*30)
    print('LAMBDA')
    print('>'*30)

    one=lambda: 1

    print('='*30)
    
    print('pype(0,(one,))')

    x=pype(0,(one,))

    print(x)
    
    assert(x == 1)

    print('='*30)
    
    print('pype(1,(sm,(sm,_,3),2))')

    x=pype(1,(sm,(sm,_,3),2))

    print(x)
    
    assert(x == 6)

    print('='*30)
    
    print('pype(1,(sm,(sm,_,3),2))')

    x=pype(1,(sm,(sm,_,(sm,_,5)),_))

    print(x)
    
    assert(x == 8)

    print('='*30)
    
    print('pype(1,(gt,_,0))')

    x=pype(1,(gt,_,0))

    print(x)
    
    assert(x == True)

    #################
    # OBJECT LAMBDA #
    #################
    
    class CallMe:

        def __init__(self):

            self.me="me"

        def add1(self,y):

            return y+1

        def sum(self,y,z):

            return y+z

        def hi(self):

            return "hi"

    class Call:

        def __init__(self):

            pass

        def get_call_me(self):

            return CallMe()

    print('>'*30)
    print('OBJECT LAMBDA')
    print('>'*30)

    print('='*30)
    
    print('pype(CallMe(),((_,"hi"),))')

    x=pype(CallMe(),((_,"hi"),))

    print(x)

    assert(x == 'hi')

    print('='*30)

    print('pype(CallMe(),(_,"hi")')

    x=pype(CallMe(),(_,"hi"))

    print(x)

    assert(x == 'hi')

    print('='*30)

    print('pype(CallMe(),_.hi')

    print('_.hi is really {}'.format(_.hi))

    x=pype(CallMe(),_.hi)

    print(x)

    assert(x == 'hi')

    print('='*30)
    
    print('pype(CallMe(),(_,"me"))')

    x=pype(CallMe(),(_,"me"))

    print(x)

    assert(x == 'me')

    print('='*30)
    
    print('pype(CallMe(),_.me)')

    print('_.me is really {}'.format(_.me))

    x=pype(CallMe(),_.me)

    print(x)

    assert(x == 'me')

    print('='*30)
    
    print('pype(CallMe(),(_,"add1",2))')

    x=pype(CallMe(),(_,"add1",2))

    print(x)

    assert(x == 3)

    print('='*30)
    
    print('pype(CallMe(),(_,"sum",2,3))')

    x=pype(CallMe(),(_,"sum",2,3))

    print(x)

    assert(x == 5)

    print('='*30)

    print('pype(Call(),(_,"get_call_me"),(_,"add1",2))')

    x=pype(Call(),(_,"get_call_me"),(_,"add1",2))

    print(x)

    assert(x == 3)

    print('='*30)

    print('pype(Call(),_.get_call_me,(_.add1,2))')

    x=pype(Call(),_.get_call_me,(_.add1,2))

    print(x)

    assert(x == 3)

    print('='*30)

    c={'call':Call()}

    print('Call() is callable: {}'.format(is_callable(c['call'])))
    print("pype(d,_['call'].get_call_me)")
    print(_['call'].get_call_me)

    x=pype(c,_['call'].get_call_me)

    print(x)

    print('='*30)

    ls=[Call()]

    print("pype(d,_0.get_call_me)")
    print(_0.get_call_me)
    print(delam(_0.get_call_me))
    print('is_object_lambda(_0.get_call_me) {}'.format(is_object_lambda(_0.get_call_me)))

    x=pype(ls,_0.get_call_me)

    print(x)

    #sys.exit(1)
    #print('='*30)

    #print("pype({'a':1},(_,'a'))")

    #x=pype({'a':1},(_,'a'))

    #print(x)

    #assert(x == 1)

    print('>'*30)
    print('AND FILTERS')
    print('>'*30)

    print('='*30)

    print('pype([1,2,-1,-5,7],[[(gt,_,1)]])')

    x=pype([1,2,-1,-5,7],[[(gt,_,1)]])

    print(x)

    assert(x == [2,7])

    print('='*30)

    print('pype([1,2,-1,-5,7,4,3,8],[[(gt,_,1),(lt,_,6)]])')

    x=pype([1,2,-1,-5,7,4,3,8],[[(gt,_,1),(lt,_,6)]])

    print(x)

    assert(x == [2,4,3])

    print('>'*30)
    print('OR FILTERS')
    print('>'*30)

    print('='*30)

    print('pype([1,2,3,4,5,2,2,43,4,3],{(eq,_,3),(eq,_,2)})')

    x=pype([1,2,3,4,5,2,2,43,4,3],{(eq,_,3),(eq,_,2)})

    print(x)

    assert(x == [2,3,2,2,3])

    print('>'*30)
    print('DICT BUILD')
    print('>'*30)

    x=pype(1,{_:_,'add1':add1,3:4,add1:add1})

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2})

    print('='*30)
    add1=lambda x: x+1
    print("[d,{_:_,'add1':add1,3:4,add1:add1}]")
    db=[d,{_:_,'add1':add1,3:4,add1:add1}]
    #print("is_dict_build([d,{_:_,'add1':add1,3:4,add1:add1}]) {}".format(is_dict_build(db)))

    x=pype(1,[d,{_:_,'add1':add1,3:4,add1:add1}])

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2})

    print('>'*30)
    print('DICT ASSOC')
    print('>'*30)

    x=pype(1,
           {_:_,'add1':add1,3:4,add1:add1},
           [assoc,'one','more'])

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2,'one':'more'})

    print('>'*30)
    print('DICT MERGE')
    print('>'*30)

    x=pype(1,
           {_:_,'add1':add1,3:4,add1:add1},
           [merge,
            {'one':'more',
             'and':(add1,(_,['add1']))}])

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2,'and':3,'one':'more'})

    print('>'*30)
    print('DICT DISSOC')
    print('>'*30)

    x=pype({1:2,3:4,5:6},[dissoc,1,3])

    print(x)

    assert(x == {5:6})

    print('>'*30)
    print('LIST BUILD')
    print('>'*30)

    x=pype(1,[l,add1,2,add1])

    assert(x == [2,2,2])

    print(x)

    print('>'*30)
    print('LIST APPEND')
    print('>'*30)

    x=pype([1,2,3],[append,4,5,6])

    print(x)

    assert(x == [1,2,3,4,5,6])

    print('>'*30)
    print('LIST CONCAT')
    print('>'*30)

    print('='*30)

    x=pype([1,2,3],_concat(_,[4,5,6],[7,8]))

    print(x)

    assert(x == [1,2,3,4,5,6,7,8])

    print('>'*30)
    print('FOR LOOP')
    print('>'*30)

    print('='*30)

    ls1=[1,2,3]
    ls2=[2,3,4]

    print('pype(ls1,[([_],[ls2]),(add,_i,_j)])')
    x=pype(ls1,[([_],[ls2]),(add,_i,_j)])

    print(x)

    print('='*30)

    ls1=[1,2,3]
    ls2=[2,3,4]

    print('pype(ls1,[([_],[ls2]),(add,_i+_0,_j)])')
    x=pype(ls1,[([_],[ls2]),(add,_i+_0,_j)])

    print(x)


    print('>'*30)
    print('WHILE LOOP')
    print('>'*30)

    #print(_while_loop(_last > 4,
    #                  _append(_last+1),
    #                  _))
    print('pype([1],_while_loop(_last > 4,_append(_last+1),_))')
    x=pype([1],_while_loop(_last > 4,
                           _append(_last+1),
                           _))

    print(x)

    assert(x == [1,2,3,4,5])

    print('while_list_append ...')

    x=pype([1],_while_list_append(_last > 4,
                                  _last+1,
                                  _))

    print(x)

    assert(x == [1,2,3,4,5])

    print('while_range ...')

    x=pype(1,_while_range(_last > 4,
                          _last+1,
                          _))

    print(x)

    assert(x == [1,2,3,4,5])

    print('='*30)

    print('>'*30)
    print('GETTER')
    print('>'*30)

    print('='*30)
    
    print('pype([1,2,3],_[1])')

    x=pype([1,2,3],_[1])

    print(x)

    assert(x == 2)

    print('>'*30)
    print('EMBEDDED PYPE')
    print('>'*30)

    print('='*30)

    x=pype(1,[embedded_pype,add1,add1])

    print(x)

    assert(x == 3)

    print('>'*30)
    print('QUOTE')
    print('>'*30)

    print('='*30)

    add_two=lambda x,y:x+y
    x=pype(2,(add_two,_,Quote(1)))

    print('pype(2,Quote(1))')

    print(x)

    add2=lambda x: x+2
    calc=lambda x,f: x*f(x)
    
    print('='*30)

    x=pype(2,(calc,_,Quote(add2)))

    print('pype(2,(calc,_,Quote(add2)))')
    print(x)

    assert(x == 2*(2+2))
    
    print('='*30)

    ls=[{'a':1,'b':2},{'a':3,'b':4}]

    x=pype(ls,_0)

    print('pype(ls,_0)')
    print(x)


    print('>'*30)
    print('PYPEVAL')
    print('>'*30)

    print('='*30)

    lenf=PypeVal(len)

    x=pype([1,3,4,2],lenf > 5)

    print('pype([1,3,4,2],lenf > 5)')

    print(x)

    assert(x == False)

    print('='*30)

    x=pype([1,3,4,2],lenf > 2)

    print('pype([1,3,4,2],lenf > 2)')

    print(x)

    assert(x == True)

    print('='*30)

    ls=[1,2,3,4]
    lsV=PypeVal(ls)

    print(lsV[_])

    x=pype([1,3],[lsV[_]])

    print('pype([1,3],[lsV[_]])')

    print(x)

    assert(x == [2,4])

    print('>'*30)
    print('BUILD PYPE')
    print('>'*30)

    print('='*30)

    sm=lambda x,y: x+y

    pp=build_pype(add1)

    print('build_pype(add1)')
    
    x=pp(1)

    print(x)

    assert(x==2)

    print('='*30)

    pp=build_pype_multi(sm)

    print('build_pype(sm)')
    
    x=pp(1,2)

    print(x)

    assert(x==3)

    print('>'*30)
    print('DO')
    print('>'*30)

    print('='*30)

    ls=[1,452,5,6,7,23]

    x=pype(ls,_do(_.sort))

    print("pype(ls,_do(_.sort))")

    assert(x==[1, 5, 6, 7, 23, 452])

    print(x)

if __name__=='__main__':

    demo()
