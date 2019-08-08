'''
python3 optimize.py
'''
py_slice=slice
import pype as pyp
from pype import is_lambda
from pype import _,_0,_1,_p
from pype import _assoc as _a
from pype import _dissoc as _d
from pype import _d as _db
from pype import _merge as _m
from pype import _l
from pype import _do
from pype import *
from pype import pype as p
from pype import pype as pype_f
from pype import LIST_ARGS
from itertools import groupby
from pype.vals import delam,hash_rec
from pype import INDEX_ARG_DICT
from functools import reduce
from inspect import signature
from collections import defaultdict
from inspect import getsource
from ast import *
import hashlib
import types
import sys
from pype.vals import LamTup
from pype import ALL_GETTER_IDS
import _operator
import builtins
import numpy as np
from functools import wraps
from copy import deepcopy
import pprint as pp
import astpretty
from inspect import currentframe
import types

NUMPY_UFUNCS=set(dir(np))
ACCUM_STORE=Name(id='accum',ctx=Store())
ACCUM_LOAD=Name(id='accum',ctx=Load())
RETURN_ACCUM=[Return(value=ACCUM_LOAD)]


def is_module(v):

    return isinstance(v,types.ModuleType)


def get_name(fArg):
    '''
    https://stackoverflow.com/questions/18425225/getting-the-name-of-a-variable-as-a-string/18425523
    '''
    callersLocalVars=currentframe().f_back.f_locals.items()
    varNames=[varName for (varName,varVal) in callersLocalVars if varVal is fArg]

    if not varNames:

        return varNames

    return varNames[0]


def get_module_alias(fArg):

    moduleName=fArg.__module__
    #print(f'{moduleName} is moduleName')
    #callersLocalVars=currentframe().f_back.f_globals.items()
    #names=[(varName,varVal) for (varName,varVal) in callersLocalVars \
    #          if isinstance(varVal,types.ModuleType)]
    #print(f'{names} is names')
    callersLocalVars=currentframe().f_back.f_locals.items()
    varNames=[varName for (varName,varVal) in callersLocalVars \
              if isinstance(varVal,types.ModuleType) \
              and varVal.__name__ == moduleName]

    if not varNames:

        return varNames

    return varNames[0]


##########
# MIRROR #
##########

def mirror_node(fArgs,accum=ACCUM_LOAD):

    return accum


############
# CALLABLE #
############

import importlib

def module_attribute(moduleStrings):

    if len(moduleStrings) == 1:

        return Name(id=moduleStrings[0],ctx=Load())

    return Attribute(value=module_attribute(moduleStrings[1:]),
                     attr=moduleStrings[0],
                     ctx=Load())


NUMPY_NAME=Name(id='np',ctx=Load())
    
def callable_node_with_args(fArg,callableArgs):

    #print('='*30)
    #print('callable node')

    fArgName=fArg.__name__

    if fArgName in NUMPY_UFUNCS:

        return Call(func=Attribute(value=NUMPY_NAME,
                                   attr=fArgName,
                                   ctx=Load()),
                    keywords=[],
                    args=callableArgs)

    #print(f'id is {fArg.__name__}')
    #print(f'moduRanle is {fArg.__module__}')

    if fArg.__module__ == '__main__':

        return Call(func=Name(id=fArgName,ctx=Load()),
                    keywords=[],
                    args=callableArgs)

    #print(f'{get_module_alias(fArg)} is get_module_alias(fArg)')

    moduleStrings=fArg.__module__.split('.')
    
    moduleStrings.reverse()

    return Call(func=Attribute(value=module_attribute(moduleStrings),
                               attr=fArgName,
                               ctx=Load()),
                keywords=[],
                args=callableArgs)

                          

def callable_node(fArg,accumLoad=ACCUM_LOAD):

    return callable_node_with_args(fArg,[accumLoad])


def replace_callable_names(fArg,node):

    return fArg


#############
# INDEX ARG #
#############

def index_arg_node(fArg,accum=ACCUM_LOAD):

    return Subscript(value=accum,
                     slice=Index(value=Num(n=INDEX_ARG_DICT[fArg])),
                     ctx=Load())


#########
# INDEX #
#########

from operator import getitem

def has_getitem(fArgs):

    #print(f'is_getter(fArgs[0]) is {is_getter(fArgs[0])}')

    if not fArgs:

        return False

    if is_callable(fArgs) and fArgs == getitem:

        return True

    if (is_list(fArgs) or is_tuple(fArgs)) and len(fArgs) > 1:

        return has_getitem(fArgs[0])

    if is_getter(fArgs):

        #print(f'{fArgs} is getter')

        return True

    return False

#########
# SLICE #
#########

def is_slice(fArg):

    return is_tuple(fArg)\
        and len(fArg) == 3\
        and fArg[0] == py_slice


def slice_node(fArg,accum):

    #print(f'computing slice for {fArg}')

    lower=optimize_rec(fArg[1],accum)
    upper=optimize_rec(fArg[2],accum)

    return Slice(lower=lower,
                 upper=upper,
                 step=None) # Include step in the syntax


#########
# INDEX #
#########

def is_index(fArg):

    return pyp.is_index(fArg) \
        or (is_tuple(fArg) \
        and len(fArg) == 3 \
        and has_getitem(fArg))


def index_val_node(val):

    if isinstance(val,int):

        val=Num(n=val)

    if isinstance(val,str):

        val=Str(s=val)

    '''
    if is_ast_name(val):

        val=val
    '''

    return val

    '''
    return Subscript(value=chain_indices(indexedObject,indices[1:]),
                     slice=Index(value=val),
                     ctx=Load())
    '''

def index_node(fArgs,accum=ACCUM_LOAD):

    #print(f'computing index node {fArgs}')
    indexedObject=fArgs[0]
    indices=fArgs[1:]

    if is_callable(fArgs[0]) and fArgs[0] == getitem:
        
        indexedObject=fArgs[1]
        indices=fArgs[2:]

    optimizedIndexedObject=optimize_rec(indexedObject,accum) # Should just be a mirror
    optimizedIndices=[optimize_rec(f,accum) if is_f_arg(f) else f[0] for f in indices]
    optimizedIndicesNodes=[index_val_node(index) for index in optimizedIndices]

    if optimizedIndicesNodes \
       and isinstance(optimizedIndicesNodes[0],Slice):

        # You need to make this more general - the syntax for indexing and slicing
        # is not coherent.

        return Subscript(value=optimizedIndexedObject,
                         slice=optimizedIndicesNodes[0],
                         ctx=Load())

    return callable_node_with_args(get_or_false,
                                   [optimizedIndexedObject]+optimizedIndicesNodes)

    #ci=chain_indices(optimizedIndexedObject,optimizedIndices)

    #print(dump(ci))

    #return ci


def replace_index_names(fArgs,node):

    #print('replace_index_names')
    #astpretty.pprint(node)

    if isinstance(node,Tuple):

        nodeIndexArgs=[el.elts[0] for el in node.elts[1:]]

    elif isinstance(node,Subscript):

        if hasattr(node.slice,'value'):

            nodeIndexArgs=[node.slice.value]

        else:

            nodeIndexArgs=[node.slice.lower,node.slice.upper]
            nodeIndexArgs=[ni for ni in nodeIndexArgs if ni is not None]

    else:

        raise Exception(f'replace index name, fArgs are {fArgs}'
                        ' node is {dump(node)}')

    indexArgs=[[el] if is_ast_name(el,fArg) \
                else replace_with_name_node_rec(fArg,el) \
                for (el,fArg) in zip(nodeIndexArgs,fArgs[1:])]

    #print(f'{nodeIndexArgs} is nodeIndexArgs')
    #print(f'{indexArgs} is indexedArgs')

    return (fArgs[0],*indexArgs)

    
##########
# LAMBDA #
##########

import ast

def is_lambda(fArg):

    if has_getitem(fArg):

        return False

    return is_tuple(fArg) \
        and len(fArg) >= 1 \
        and not is_mirror(fArg[0]) \
        and fArg[0] != py_slice \
        and is_f_arg(fArg[0])


def lambda_node(fArgs,accum=ACCUM_LOAD):
    # First element of lambda must be callable.  Replace with real fArg when you can.
    #print('*'*30)
    #print('lambda_node')
    #print(f'{fArgs} is fArgs')

    if fArgs[0].__name__ == '<lambda>':

        raise Exception(f'With fArgs[0] {fArgs[0]}, you cannot '
                        'include Python lambdas in a function defintion when '
                        'optimizing.  Redefine this using def.')

    optimizedLambdaArgs=[optimize_rec(fArg,accum) for fArg in fArgs[1:]]

    return callable_node_with_args(fArgs[0],optimizedLambdaArgs)


def replace_lambda_names(fArgs,node):

    #print('*'*30)
    #print('replace_lambda_names')
    #print(f'{fArgs} is fArgs')
    #print(f'{node} is node')
    #print(f'{has_getitem(fArgs)} is has_getitem(fArgs)')

    # You may need to parse the fArg[0]

    if isinstance(node,BinOp):

        leftArg=replace_with_name_node_rec(fArgs[1],node.left)
        rightArg=replace_with_name_node_rec(fArgs[2],node.right)

        #print(f'rightArg is {dump(rightArg) if is_ast_name(rightArg) else rightArg}')

        return (fArgs[0],leftArg,rightArg)

    if isinstance(node,UnaryOp):

        lambdaArg=node.operand if is_ast_name(node,fArgs[1]) \
                    else replace_with_name_node_rec(fArgs[1],node.operand)

        return (fArgs[0],lambdaArg)

    if isinstance(node,Compare):

        leftArg=node.left if is_ast_name(node.left,fArgs[1]) else fArgs[1]
        comparator=node.comparators[0]
        rightArg=comparator if is_ast_name(comparator,fArgs[2]) else fArgs[2]

        #print('is comparator')
        #print(f'node is {ast.dump(node)}')
        #print(f'left arg is {leftArg}')
        #print(f'right arg is {rightArg}')
        #print(f'fArgs[1] is {fArgs[1]}')

        return (fArgs[0],leftArg,rightArg)

    if isinstance(node,Tuple):
        
        lambdaArgs=[replace_with_name_node_rec(fArg,el) \
                    for (fArg,el) in zip(fArgs,node.elts)]

        return tuple(lambdaArgs)

    if isinstance(node,Subscript):

        nodeList=node.value

        if isinstance(node.slice,Slice):

            nodeList.extend([node.slice.lower,node.slice.upper])
        
        elif isinstance(node.slice,Index):

            nodeList.append(node.slice.value)

        return tuple([replace_with_name_node_rec(fArg) \
                      for (fArg,el) in zip(fArgs,nodeList)])

    return fArgs
        


##############################
# HELPERS FOR MAP AND FILTER #
##############################

LOADED_DICT_KEY=Name(id='k',ctx=Load())
LOADED_DICT_VALUE=Name(id='v',ctx=Load())
STORED_DICT_KEY=Name(id='k',ctx=Store())
STORED_DICT_VALUE=Name(id='v',ctx=Store())

def dict_comp(accum,
              mapValue,
              ifsList=[],
              loadedDictKey=LOADED_DICT_KEY,
              storedDictKey=STORED_DICT_KEY,
              storedDictValue=STORED_DICT_VALUE,
             ):

    if not is_list(ifsList):

        ifsList=[ifsList]

    return DictComp(key=loadedDictKey,
                    value=mapValue,
                    generators=[
                        comprehension(target=Tuple(elts=[storedDictKey,
                                                         storedDictValue],
                                                   ctx=Store()),
                                      iter=Call(func=Attribute(value=accum,
                                                               attr='items',
                                                               ctx=Load()),
                                                args=[],
                                                keywords=[]),
                                      is_async=False,
                                      ifs=ifsList)])


LOADED_LIST_ELEMENT=Name(id='list_element',ctx=Load())
STORED_LIST_ELEMENT=Name(id='list_element',ctx=Store())

def list_comp( accum,
               loadedListElement,
               storedListElement,
               ifsList=[]
             ):

    if not is_list(ifsList):

        ifsList=[ifsList]

    return ListComp(elt=loadedListElement,
                    generators=[comprehension(target=storedListElement,
                                              iter=accum,
                                              is_async=False,
                                              ifs=ifsList)])


#######
# MAP #
#######

def map_list_node(fArg,
                  accum=ACCUM_LOAD,
                  loadedListElement=LOADED_LIST_ELEMENT,
                  storedListElement=STORED_LIST_ELEMENT):

    #print('is map_list_node')

    if len(fArg) > 1:

        raise Exception(f'Multiple fArgs in maps deprecated.'
                        'Use separate maps instead, like [add1],[add2] ...')

    mapFArg=fArg[0]

    mapNode=optimize_rec(mapFArg,loadedListElement)
    lsComp=list_comp(accum,mapNode,storedListElement)

    #print(f'{mapNode} is mapNode')
    #print(f'{ast.dump(lsComp)} is lsComp')
    
    return lsComp


def map_dict_node(fArg,
                  accum=ACCUM_LOAD,
                  loadedDictValue=LOADED_DICT_VALUE):

    if len(fArg) > 1:

        raise Exception(f'Multiple fArgs in maps deprecated.'  
                        'Use separate maps instead.')

    mapFArg=fArg[0]
    mapValue=optimize_rec(mapFArg,loadedDictValue)

    return dict_comp(accum,mapValue)


def if_list_or_dict(accum,fArg,dict_func,list_func):

    return IfExp(test=Call(func=Name(id='is_dict',ctx=Load()),
                           args=[accum],
                           keywords=[]),
                 body=dict_func(fArg,accum),
                 orelse=list_func(fArg,accum))
           

def map_dict_or_list_node(fArg,accum=ACCUM_LOAD):

    if len(fArg) > 1:

        raise Exception(f'Multiple fArgs in maps deprecated.'  
                        'Use separate maps instead.')
    
    return if_list_or_dict(accum,fArg,map_dict_node,map_list_node)


def replace_map_names(fArgs,node):

    return [replace_with_name_node_rec(fArg,el) \
            for (el,fArg) in zip(node.elts,fArgs)]
                 
    
##############
# AND FILTER #
##############

def and_filter_f_args(fArgs):
    '''
    This is for when we change and filter from [[fArg ...]] to _f(fArg) 
    '''
    return fArgs[0]


def all_node(nodes):

    if len(nodes) < 2:

        return nodes

    return BoolOp(op=And(),
                  values=nodes)


def and_filter_list_node(fArgs,
                         accum=ACCUM_LOAD,
                         loadedListElement=LOADED_LIST_ELEMENT,
                         storedListElement=STORED_LIST_ELEMENT):

    fArgs=and_filter_f_args(fArgs)
    ifAllNode=all_node([optimize_rec(fArg,loadedListElement) for fArg in fArgs])

    #print('printing and filter list node')
    #print(ifAllNode)

    listComp=list_comp(accum,loadedListElement,storedListElement,ifAllNode)

    #astpretty.pprint(ifAllNode)

    return listComp


def and_filter_dict_node(fArgs,
                         accum=ACCUM_LOAD,
                         loadedDictValue=LOADED_DICT_VALUE):

    fArgs=and_filter_f_args(fArgs)
    ifAllNode=all_node([optimize_rec(fArg,loadedDictValue) for fArg in fArgs])

    return dict_comp(accum,loadedDictValue,ifAllNode)
    

def and_filter_list_or_dict_node(fArgs,accum=ACCUM_LOAD):

    return if_list_or_dict(accum,
                           fArg,
                           and_fitler_dict_node,
                           and_filter_list_node)


def replace_and_filter_names(fArgs,node):

    return [[replace_with_name_node_rec(fArg,el) \
             for (el,fArg) in zip(node.elts[0].elts,fArgs[0])]]


#############
# OR FILTER #
#############

def any_node(nodes):

    if len(nodes) < 2:

        return nodes

    return BoolOp(op=Or(),
                  values=nodes)


def or_filter_list_node(fArgs,
                         accum=ACCUM_LOAD,
                         loadedListElement=LOADED_LIST_ELEMENT,
                         storedListElement=STORED_LIST_ELEMENT):

    ifAnyNode=any_node([optimize_rec(fArg,loadedListElement) for fArg in fArgs])

    #print('printing and filter list node')
    #print(ifAllNode)

    listComp=list_comp(accum,loadedListElement,storedListElement,ifAnyNode)

    return listComp


def or_filter_dict_node(fArgs,
                         accum=ACCUM_LOAD,
                         loadedDictValue=LOADED_DICT_VALUE):

    #print('&'*30)
    #print(f'{ast.dump(accum)} is accum')
    ifAnyNode=any_node([optimize_rec(fArg,loadedDictValue) for fArg in fArgs])
    #dc=dict_comp(accum,loadedDictValue,ifAnyNode)
    #print(f'{ast.dump(dc)} is accum')

    return dict_comp(accum,loadedDictValue,ifAnyNode)
    

def or_filter_list_or_dict_node(fArg,accum=ACCUM_LOAD):

    '''
    print('='*30)
    print('or_filter_list_or_dict_node')
    print(f'{fArg} is fArg')
    print(f'{ast.dump(accum)} is accum')

    print('or_filter_list_or_dict_node')
    print(f'{fArg} is fArg')
    print(f'{accum} is accum')
    v=if_list_or_dict(accum,
                      fArg,
                      or_filter_dict_node,
                      or_filter_list_node)
    print(f'{v} is v')
    '''

    return if_list_or_dict(accum,
                           fArg,
                           or_filter_dict_node,
                           or_filter_list_node)


def replace_or_filter_names(fArgs,node):

    return {replace_with_name_node_rec(fArg,el) \
            for (el,fArg) in zip(node.elts[0].elts,fArgs[0])}


###############
# SWITCH_DICT #
###############

def chain_if_else(switchDictList,elseFArg):
    # Using tail recursion here.
    if not switchDictList:

        return elseFArg

    condition,statement=switchDictList[0]

    return IfExp(test=condition,
                 body=statement,
                 orelse=chain_if_else(switchDictList[1:],elseFArg))
    

def switch_dict_node(fArg,accum=ACCUM_LOAD):
    # For now, equality checking in switch dict will not be used.  Too inconvenient to
    # parse.
    switchDictList=[(optimize_rec(k,accum),optimize_rec(v,accum)) \
                    for (k,v) in fArg.items() if k != 'else']
    elseFArg=optimize_rec(fArg['else'],accum)
    
    return chain_if_else(switchDictList,elseFArg)


def replace_dict_names(fArgs,nodes):

     nodePairs=zip(nodes.keys,nodes.values)

     return {replace_with_name_node_rec(k,nk):replace_with_name_node_rec(v,nv) \
             for ((k,v),(nk,nv)) in zip(fArgs.items(),nodePairs)}


replace_switch_dict_names=replace_dict_names
   

##############
# DICT ASSOC #
##############

def dict_assoc_node_old(fArgs,accum=ACCUM_LOAD):

    keys=fArgs[1::2]
    fArgs=fArgs[2::2]
    assignList=[]

    for (key,fArg) in zip(keys,fArgs):

        optimizedFArg=optimize_rec(fArg)
        keyNode=parse_literal(key)
        indexNode=Index(value=keyNode)
        assignNode=Assign(targets=[Subscript(value=accum,
                                             slice=indexNode,
                                             ctx=Store())],
                          value=optimizedFArg)

        assignList.append(assignNode)

    return assignList


def dict_assoc_node(fArgs,accum=ACCUM_LOAD):

    key=fArgs[1]
    fArg=fArgs[2]
    keyNode=parse_literal(key)
    optimizedFArg=optimize_rec(fArg)

    if len(fArgs) == 3:

        return callable_node_with_args(dct_assoc,[accum,keyNode,optimizedFArg])

    return callable_node_with_args(dct_assoc,
                                   [dict_assoc_node(fArgs[2::],accum),
                                    keyNode,
                                    optimizedFArg])


def replace_dict_assoc_names(fArgs,node):

    keys=fArgs[1::2]
    fArgs=fArgs[2::2]

    if isinstance(node,List):

        nodes=node.elts[2::2]

    elif isinstance(node,Call):

        nodes=node.args[1::2]

    else:

        raise Exception(f'unacceptable node type {node} for dict assoc')

    #print('*'*30)
    #print(f'{fArgs} is fArgs')
    #print(f'{[ast.dump(n) for n in nodes]} is nodes')

    nameReplacedFArgs=[replace_with_name_node_rec(fArg,n)\
                       for (fArg,n) in zip(fArgs,nodes)]

    #print(f'{nameReplacedFArgs} is nameReplacedFArgs')

    nameReplacedPairs=[v for pr in zip(keys,nameReplacedFArgs) for v in pr]

    return _a(*nameReplacedPairs)


##############
# DICT MERGE #
##############

def dict_merge_node(fArgs,
                    accum=ACCUM_LOAD,
                   ):

    fArg=fArgs[1]
    optimizedFArg=optimize_rec(fArg,accum)

    return callable_node_with_args(dct_merge,
                                   [accum,
                                    optimizedFArg])



def replace_dict_merge_names(fArgs,node):
    
    #print('&'*30)
    #print('replace_dict_merge_names')
    #print(f'{ast.dump(node)} is node')

    fArgs=fArgs[1:]

    #print(f'{fArgs} is fArgs')

    if isinstance(node,List):

        nodes=node.elts

    elif isinstance(node,Call):

        nodes=node.args

    else:

        raise Exception(f'unacceptable node type {node} for dict merge')

    #print(f'{[ast.dump(n) for n in nodes]} is nodes')

    nameReplacedFArgs=[replace_with_name_node_rec(fArg,n)\
                       for (fArg,n) in zip(fArgs,nodes)]

    #print(f'{_m(*nameReplacedFArgs)} is nameReplacedFArgs')
    #nameReplacedPairs=[v for pr in zip(keys,nameReplacedFArgs) for v in pr]

    return _m(*nameReplacedFArgs)


##########################
# HELPERS FOR LIST FARGS #
##########################

def get_nodes_for_list_f_arg(node):

    if isinstance(node,List):

        return node.elts[1:]

    elif isinstance(node,Call):

        return node.args

    else:

        raise Exception(f'unacceptable node type {node} for dict dissoc')


def build_list_f_arg(fArgs,node,f):

    fArgs=fArgs[1:]
    nodes=get_nodes_for_list_f_arg(node)
    nameReplacedFArgs=[replace_with_name_node_rec(fArg,n)\
                       for (fArg,n) in zip(fArgs,nodes)]

    return f(*nameReplacedFArgs)


###############
# DICT DISSOC #
###############
   
def dict_dissoc_node(fArgs,accum=ACCUM_LOAD):

    key=fArgs[-1]
    keyNode=parse_literal(key)

    if len(fArgs) == 2:

        return callable_node_with_args(dct_dissoc,[accum,keyNode])

    return callable_node_with_args(dct_dissoc,
                                   [dict_dissoc_node(fArgs[:-1],accum),
                                    keyNode])


def replace_dict_dissoc_names(fArgs,node):

    return build_list_f_arg(fArgs,node,_d)
    

##############
# LIST BUILD #
##############

def list_build_node(fArgs,accum=ACCUM_LOAD):

    fArgs=fArgs[1:]
    optimizedFArgs=[optimize_rec(fArg,accum) for fArg in fArgs]
    
    return List(elts=optimizedFArgs,
                ctx=Load())


def replace_list_build_names(fArgs,node):

    return build_list_f_arg(fArgs,node,_l)


##############
# DICT BUILD #
##############

def dict_build_node(fArg,accum=ACCUM_LOAD):

    #print('&'*30)
    #print('dict_build_node')
    #pp.pprint(fArg)
    #print([optimize_rec(v,accum) for v in list(fArg.values())])

    if is_explicit_dict_build(fArg):

        if len(fArg) >= 3:

            keys=fArg[1::2]
            vals=fArg[2::2]

        else:

            keys=fArg[1]
            vals=[accum]
    
    else:

        keys=fArg.keys()
        vals=fArg.values()

    keys=[optimize_rec(k,accum) for k in keys]
    vals=[optimize_rec(v,accum) for v in vals]

    #print('keys:')
    #print([ast.dump(k) for k in keys])
    #print('values:')
    #print([v for v in vals])

    return Dict(keys=keys,values=vals,ctx=Load())


def replace_dict_build_names(fArg,node):

    if is_explicit_dict_build(fArg):

        return build_list_f_arg(fArg,node,_db)

    return replace_dict_names(fArg,node)

#replace_dict_build_names=replace_dict_names


#################
# EMBEDDED PYPE #
#################

def embedded_pype_chain(fArgs,accum):

    if len(fArgs) == 1:

        return optimize_rec(fArgs[0],accum)

    return optimize_rec(fArgs[0],embedded_pype_chain(fArgs[1:],accum))

    
def embedded_pype_node(fArgs,accum=ACCUM_LOAD):

    fArgs=fArgs[1:]
    
    #print('&'*30)
    #print('embedded_pype_node')
    #print(fArgs)
    #pp.pprint(fArg)
    #print([optimize_rec(v,accum) for v in list(fArg.values())])

    fArgs.reverse()

    pypeChain=embedded_pype_chain(fArgs,accum)

    #astpretty.pprint(pypeChain)

    #print('keys:')
    #print([ast.dump(k) for k in keys])
    #print('values:')
    #print([v for v in vals])

    return pypeChain


def replace_embedded_pype_names(fArgs,node):

    #print('&'*30)
    #print('replace_embedded_pype_names')
    
    fArgs=fArgs[1:]

    #print(f'{fArgs} is fArgs')
    #print(f'{ast.dump(node)} is node')

    nodeArgs=node.args

    #print(f'{nodeArgs} is nodeArgs')

    replaced=[replace_with_name_node_rec(fArg,n) \
              for (fArg,n) in zip(fArgs,nodeArgs)]
    
    #print(f'{_p(*replaced)} is _p(*replaced)')

    return _p(*replaced)


######
# DO #
######

def do_lambda_node(node):

    return Lambda(args=arguments(args=[arg(arg='do_lambda_arg', annotation=None)], 
                                 vararg=None, 
                                 kwonlyargs=[], 
                                 kw_defaults=[], 
                                 kwarg=None, 
                                 defaults=[]),
                  body=node)


DO_LAMBDA_ARG=Name(id='do_lambda_arg',ctx=Load())

def do_node(fArgs,accum=ACCUM_LOAD):

    fArg=fArgs[1]
    optimizedNode=optimize_rec(fArg,DO_LAMBDA_ARG)
    lambdaNode=do_lambda_node(optimizedNode)
    callNode=callable_node_with_args(do_func,
                                     [accum,
                                      lambdaNode])

    #print(f'{callNode} is callNode')

    return callNode


def replace_do_names(fArgs,node):

    fArg=fArgs[1]
    node=node.args[0]
    replacedFArg=replace_with_name_node_rec(fArg,node)

    return _do(replacedFArg)


#############
# AST NAMES #
#############

def is_ast_name(node,fArg=None):

    isCallable=False if fArg is None else is_callable(fArg)

    return isinstance(node,Name) \
        and node.id not in ALL_GETTER_IDS \
        and not isCallable
      

def ast_name_node(node,accumNode):

    return node


def replace_ast_name(fArg,node):

    #print('replace_ast_name')

    return node


OPTIMIZE_PAIRS=[(is_callable,callable_node),
                (is_ast_name,ast_name_node),
                (is_mirror,mirror_node),
                (is_index_arg,index_arg_node),
                (is_lambda,lambda_node),
                (is_slice,slice_node),
                (is_index,index_node),
                (is_map,map_dict_or_list_node),
                #(is_map,{list:map_list_node,
                #         dict:map_dict_node,
                #         'default':map_dict_or_list_node}),
                #(is_and_filter,{list:and_filter_list_node,
                #                dict:and_filter_dict_node,
                #                'default':and_filter_list_or_dict_node}),
                (is_or_filter,or_filter_list_or_dict_node),
                #(is_or_filter,{list:or_filter_list_node,
                #                dict:or_filter_dict_node,
                #                'default':or_filter_list_or_dict_node}),
                (is_switch_dict,switch_dict_node),
                (is_dict_assoc,dict_assoc_node),
                (is_dict_dissoc,dict_dissoc_node),
                (is_dict_merge,dict_merge_node),
                (is_list_build,list_build_node),
                (is_dict_build,dict_build_node),
                (is_embedded_pype,embedded_pype_node),
                (is_do,do_node),
               ]

REPLACE_PAIRS=[(is_lambda,replace_lambda_names),
               (is_map,replace_map_names),
               (is_callable,replace_callable_names),
               #(is_and_filter,replace_and_filter_names),
               #(is_index,replace_index_names),
               (is_switch_dict,replace_switch_dict_names),
               (is_dict_assoc,replace_dict_assoc_names),
               (is_dict_dissoc,replace_dict_dissoc_names),
               (is_dict_merge,replace_dict_merge_names),
               (is_list_build,replace_list_build_names),
               (is_dict_build,replace_dict_build_names),
               (is_embedded_pype,replace_embedded_pype_names),
               (is_do,replace_do_names),
              ]


def assign_node_to_accum(node,accum=ACCUM_STORE):

    return Assign(targets=[accum],value=node)



def parse_literal(fArg):

    #print('='*30)
    #print('parse_literal')
    
    if fArg is None:

        return None

    if isinstance(fArg,str):

        return Str(s=fArg)

    if isinstance(fArg,int) or isinstance(fArg,float):

        return Num(n=fArg)

    if isinstance(fArg,dict):

        keyValuePairs=[(parse_literal(k),parse_literal(v)) for (k,v) in fArg.items()]
        
        return Dict( keys=[k for (k,v) in keyValuePairs],
                     values=[v for (k,v) in keyValuePairs],
                     ctx=Load())

    if isinstance(fArg,list):

        ls=List( elts=[parse_literal(el) for el in fArg],
                 ctx=Load())
        #print(dump(ls))

        return ls

    if isinstance(fArg,set):

        return Set( elts=[parse_literal(el) for el in fArg],
                    ctx=Load())

    if is_ast_name(fArg):

        return fArg

    # I have no idea why I did this.

    return Name(id=get_name(fArg),ctx=Load())


def optimize_rec(fArg,accumNode=ACCUM_LOAD):#,evalType=None):

    #print('>'*30)
    #print('optimize_rec')
    #print(fArg)

    fArg=delam(fArg)
    optimizers=[opt_f for (evl_f,opt_f) in OPTIMIZE_PAIRS if evl_f(fArg)]
    evalType=type(fArg)# if evalType is None else evalType

    if not optimizers:

        return parse_literal(fArg)

    #print(f'{optimizers} is optimizers')

    optimizer=optimizers[-1]
    
    #print(f'{optimizer} is optimizer')

    # TODO - either get rid of this or implement it properly
    if is_dict(optimizer):

        #print(f'optimizer is dict')
        #print(f'{evalType} is evalType')

        if evalType in optimizer:

            #print(f'{optimizers} is optimizers')
            #print(f'{evalType} is evalType')
            #print(f'{optimizer} is optimizer')

            optimizer=optimizer[evalType]

        else:

            optimizer=optimizer['default']

    #print('returning:')
    #print(optimizer(fArg,accumNode))

    return optimizer(fArg,accumNode)



def optimize_f_args(fArgs,fArgTypes,startNode):

    assignList=[assign_node_to_accum(startNode)]

    for fArg,fArgType in zip(fArgs,fArgTypes):

        opt=optimize_rec(fArg,ACCUM_LOAD)#,fArgType)
        
        if is_list(opt):

            assignList.extend(opt)

        else:

            assignNode=assign_node_to_accum(opt)

            assignList.append(assignNode)

    #print('*'*30)
    #print('optimize_f_args')
    #print(f'{fArgs} is fArgs')
    #print([dump(a) for a in assignList])

    return assignList


def is_pype_return(body,aliases):

    return isinstance(body[-1],Return) \
        and isinstance(body[-1].value,Call)\
        and body[-1].value.func.id in aliases


def aliases_for_pype(glbls):
    '''
    This searches through the global namespace of a function to find any aliases for
    the pype function.  Helps when pype is given another name, as in:

    from pype import pype as p
    '''
    #print(f'{p} is pype')
    #print(f'{pype_f} is pype')

    return set([alias for (alias,f) in glbls.items() \
                if glbls[alias] == pype_f \
                and is_callable(f)])


def pype_with_f_arg_and_tree(accum,*fArgs):

    #print('='*30)
    #print('pype_with_f_arg_and_tree')
    #successiveFArgs=[list(fArgs[:i+1]) for i in range(len(fArgs))]
    successiveEvals=[]
    
    for fArg in fArgs:

        accum=pype_f(accum,fArg)

        #print('accum is')
        #pp.pprint(accum)

        successiveEvals.append(deepcopy(accum))

    #successiveEvals=[pype_f(accum,*successive) for successive in successiveFArgs]
    fArgTypes=[type(evl) for evl in successiveEvals]

    #print('successiveEvals')
    #pp.pprint(successiveEvals)
    #print(f'{fArgTypes} is fArgTypes')

    return successiveEvals[-1],list(fArgs),fArgTypes


IMPORT_PYPE=ImportFrom(module='pype.optimize', 
                       names=[alias(name='pype_with_f_arg_and_tree', 
                                    asname=None)])

class PypeCallReplacer(NodeVisitor):

    def __init__(self,aliases):

        self.pypeAliases=aliases
        self.accumNode=None
        self.fArgsNode=None

    def visit_FunctionDef(self,node):

        args=node.args.args
        body=node.body

        #print(f'{self.pypeAliases} is pype aliases')

        if is_pype_return(body,self.pypeAliases):

            node.body[-1].value.func.id='pype_with_f_arg_and_tree'
            #print('replacing pype call')
            node.body=[IMPORT_PYPE]+node.body
            self.accumNode=body[-1].value.args[0]
            self.fArgsNodes=body[-1].value.args[1:]

        node.decorator_list=[]
        node=fix_missing_locations(node)

        self.generic_visit(node)


class PypeTreeReplacer(NodeVisitor):

    def __init__(self,fArgAssigns,aliases):

        self.fArgAssigns=fArgAssigns
        self.pypeAliases=aliases

    
    def visit_FunctionDef(self,node):

        body=node.body
        
        if is_pype_return(body,self.pypeAliases):
        
            node.body=body[:-1]+self.fArgAssigns+RETURN_ACCUM

        node.decorator_list=[]
        node=fix_missing_locations(node)

        self.generic_visit(node)



'''
class FArgCallReplacer(NodeVisitor):

    def __init__(self,glbls):

        self.glbls=glbls


    def visit_FunctionDef(self,node):

        body=node.body
        
        if isinstance(body[-1],Return):

            fArgNodes=body[-1].value.args[1:]
            newNodes=[]

            for fArgNode in fArgNodes:

                if isinstance(fArgNode,Call):

                    print(f'{ast.dump(fArgNode)} is fArgNode')
                    exp=Expression(body=fArgNode)
                    evalExp=eval(compile(exp,
                                         filename='<ast>',
                                         mode='eval'),
                                 self.glbls)
                    
                    if is_list(evalExp) \
                       and len(evalExp) >= 1 \
                       and is_string(evalExp[0]) \
                       and evalExp[0] in LIST_ARGS:

                        pass

                    #newNodes.append(newFArgNode)

                    print(f'{evalExp} is evalExp')

        node.decorator_list=[]
        node=fix_missing_locations(node)

        self.generic_visit(node)
'''

'''
def align_node_with_fargs(fArgs,node):

    if not (isinstance(node,Call) or isinstance(node,List)):

        return node

    ls=get_nodes_for_list_f_arg(node)
    
    for (i,fArg) in enumerate(fArgs):

        if is_list(fArg) \
           and len(fArg) >= 1 \
           and is_string(fArg[0]) \
           and fArg[0] in LIST_ARGS:

           subNodes=ls[i:len(fArg)]
'''           


def replace_literal_container_names(fArgs,node):

    if isinstance(node,Dict):

        keyNodes=node.keys
        valNodes=node.values
        replacedKeys=[replace_with_name_node_rec(fArgKey,keyNode) \
                      for (fArgKey,keyNode) in zip(fArgs.keys(),keyNodes)]
        replacedValues=[replace_with_name_node_rec(fArgVal,valNode) \
                        for (fArgVal,valNode) in zip(fArgs.values(),valNodes)]
        
        return {k:v for (k,v) in zip(replacedKeys,replacedValues)}

    if isinstance(node,List):

        elts=node.elts

        return [replace_with_name_node_rec(fArg,node) \
                for (fArg,node) in zip(fArgs,elts)]

    if isinstance(node,Set):
        
        elts=node.elts

        return {replace_with_name_node_rec(fArg,node) \
                for (fArg,node) in zip(fArgs,elts)}

    if isinstance(node,Tuple):

        elts=node.elts

        return tuple([replace_with_name_node_rec(fArg,node) \
                      for (fArg,node) in zip(fArgs,elts)])

    return fArgs


def replace_with_name_node_rec(fArg,node):
    '''
    When we call pype_with_f_arg_and_tree, there is a problem - in the fArg,
    variables in the scope of the function are actually their literals.  So
    for example, if we had an fArg _+x, and x=1 on the first evaluation, we
    get _+1.  The function is then parsed accordingly.

    What we want to do is take the first fArg of the function, and replace
    any literal with a Name node.  This will encourage the recompiler to include
    the variable name instead of the first evaluated literal.
    '''
    #print('='*30)
    #print('replace_with_name_node')

    #print('node is')
    #print(node)

    #print('fArg is')
    #print(fArg)

    isLamTup=is_lam_tup(fArg)
    isFArg=is_f_arg(fArg)

    if is_ast_name(node) \
       and not isFArg \
       and not isLamTup \
       and not isinstance(fArg,PypeVal):

        return node

    fArg=delam(fArg)

    # Here, we ensure that we get names in dict, tuple, list, and set literals.

    if not isFArg:
        
        fArg=replace_literal_container_names(fArg,node)

    #pp.pprint(f'fArg is {fArg}')
    #astpretty.pprint(node)
    evls=[f(fArg,node) for (evl_f,f) in REPLACE_PAIRS if evl_f(fArg)]
    fArg=evls[-1] if evls else fArg
    #print('replaced:')
    #if is_dict(fArg) and 2 in fArg:
    #    print(f'{ast.dump(fArg[2])}')
    #pp.pprint(fArg)
    #print('='*30)

    if isLamTup:

        fArg=LamTup(fArg)

    return fArg


def replace_with_name_node(fArgs,nodes):

    return [replace_with_name_node_rec(fArg,node) \
            for (fArg,node) in zip(fArgs,nodes)]


def add_main_modules(mod,glbls):

    for name in dir(mod):

        attr=getattr(mod,name)
        modName=''

        if is_callable(attr):

            modName=attr.__module__

        if is_module(attr):

            modName=attr.__name__

        if modName:

            #print(f'importing {modName}')

            glbls[modName]=__import__(modName)

    return glbls


FUNCTION_CACHE={}

#import astpretty
#import pprint as pp

def optimize(pype_func,verbose=False):

    originalFuncName=pype_func.__name__
    glbls=pype_func.__globals__
    aliases=aliases_for_pype(glbls)
    src=getsource(pype_func)
    moduleName=pype_func.__module__
    mod=__import__(moduleName)
    #print(f'{mod} is moduleName')
    glbls[moduleName]=mod
    glbls=add_main_modules(mod,glbls)

    @wraps(pype_func)
    def optimized(*args):

        if originalFuncName in FUNCTION_CACHE:

            return FUNCTION_CACHE[originalFuncName](*args)

        '''
        First pass, replace pype call with pype_with_f_arg_and_tree, so we
        can get the fArgs without having to explicitly parse them from the 
        tree.
        '''
        tree=parse(src)
        callReplacer=PypeCallReplacer(aliases)
        recompiledReplacerNamespace={}
        #fArgReplacer=FArgCallReplacer(glbls)

        if verbose:

            print('*'*30)
            print('parse tree before')
            astpretty.pprint(tree)
            print('*'*30)

        callReplacer.visit(tree)
        #print('after callReplacer.visit')
        #print(f'{ast.dump(tree)}')

        #fArgReplacer.visit(tree)
        #print('*'*30)
        #pp.pprint(optimize.__globals__)
        #print('*'*30)

        exec(compile(tree,
                     filename='<ast>',
                     mode='exec'),
             glbls,
             recompiledReplacerNamespace)

        recompiled_pype_func=recompiledReplacerNamespace[originalFuncName]
        v,fArgs,fArgTypes=recompiled_pype_func(*args)

        '''
        Second pass, we find anywhere where the pype expression has a reference
        to a variable in the scope of the function, and replace it with a Name.
        Otherwise, it gets evaluated as a literal.
        '''
        if callReplacer.fArgsNodes is not None:

            #print('fArgs is')
            #pp.pprint(fArgs)
            #print('callReplacer.fArgsNodes is ')
            #print(callReplacer.fArgsNodes)

            fArgs=replace_with_name_node(fArgs,
                                         callReplacer.fArgsNodes)
            
            #print('fArgs With Replaced Name')
            #pp.pprint(fArgs)
        '''
        Third pass, we parse the original source and convert the original 
        returned pype call into fArg calls.
        '''
        replaceTree=optimize_f_args(fArgs,fArgTypes,callReplacer.accumNode)
        #print(f'{replaceTree} is replaceTree')
        recompiledReplacerNamespace={}
        tree=parse(src)
        treeReplacer=PypeTreeReplacer(replaceTree,aliases)

        treeReplacer.visit(tree)

        if verbose:
            
            print('*'*30)
            print('parse tree after')
            astpretty.pprint(tree)
            print('*'*30)
            #pp.pprint(astunparse.dump(tree))

        exec(compile(tree,
                     filename='<ast>',
                     mode='exec'),
             glbls,
             recompiledReplacerNamespace)

        #pp.pprint(recompiledReplacerNamespace)

        recompiled_pype_func=recompiledReplacerNamespace[originalFuncName]
        '''
        This is extremely dangerous, but the alternative is to add a flag to the
        function, checking if it's been compiled.  What we are doing here is
        taking the global namespace of pype_func, and replacing that pype_func with
        recompiled_pype_func, so that any calls to pype_func will automatically call
        recompiled_pype_func.
        '''

        FUNCTION_CACHE[originalFuncName]=recompiled_pype_func

        #glbls[originalFuncName]=recompiled_pype_func
        #setattr(mod,originalFuncName,recompiled_pype_func)

        #print(f'successfully recompiled {recompiled_pype_func}')
        #print(f'recomiled {originalFuncName} in globals: {glbls[originalFuncName]}')
        #print(f'{pype_func.__module__} is module')
        #print('*'*30)

        '''
        Still, we don't want to waste the first function call, so we return the value
        of the first function call.  
        '''
        return v

    return optimized


def time_func(func):

    originalFuncName=func.__name__

    def timed(*args):

        t0=tm.time()
        v=func(*args)
        print(f'time to run {originalFuncName}: {tm.time() - t0}')

        return v

    return timed


def concat(ls):

    return ls+[0]

def sm(x,y): return x+y

'''
'''

import numpy as np
from pype.helpers import *
import pype.helpers
from pype.vals import lenf

@optimize
def calc16(dctLS):

    return p( dctLS,
              [_a(3,1,5,6)],
            )


@optimize
def calc15(ls):

    return p( ls,
              [[_+1]],
            )

from pype import _assoc_p as _ap

@optimize
def calc17(n):

    return p( n,
              #{'x':_+1,
              # 'y':_*3},
              _db('x',_+1,'y',_*3),
              _a('z',_p(_['x']+_['y'],_*5)),
            )


from pype import _merge as _m

def change_list(ls):

    ls.append(1000)


@optimize
def calc18(ls):

    x=5

    return p( ls,
              _do(change_list),
              #_m({2:x}),
              #_d(2,3,12)),
              #{_>2},
             )

if __name__=='__main__':

    #pass
    #print(calc([1]))
    #print(calc([2]))
    #print(calc3([2,4]))
    #print(calc3([2,4]))
    #print(calc6([[1,2],3,4]))
    #print(calc7([1,2,4,5]))
    #print(calc8([1,2,4,5]))
    #print(calc8([1,2,4,5]))
    #print(calc9([1,2,4,5]))
    #print(calc9([1,2,4,5]))
    #print(caloc10({1:2,4:5}))
    #print(calc10({1:2,4:5}))
    #print(calc11({1:2,4:5}))
    #print(calc11({1:2,4:5}))
    #print(calc12([1,2,3,4,5,6]))
    #print(calc12([1,2,3,4,5,6])) 
    #print(calc13([[1,2],[3,4],[5,6]])) 
    #print(calc13([[1,2],[3,4],[5,6]])) 
    #print(calc14({'a':[1,2,3],'b':[2,2,3,4],'c':[3]}))
    #print(calc14({'a':[1,2,3],'b':[2,2,3,4],'c':[3]}))
    #print(calc15([[1,2,3],[4,5,6]]))
    #print(calc15([[1,2,3],[4,5,6]]))
    #print(calc16([{1:2,3:4}]))
    #print(calc16([{1:2,3:4}]))
    #print(calc17(3))
    #print(calc17(3))
    print(calc18([1,2,3,4]))
    print(calc18([1,2,3,4]))
    #print(calc18([5,8,1,2,3]))
