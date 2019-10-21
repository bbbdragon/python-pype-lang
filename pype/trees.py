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
from pype.optimize_helpers import *
from pype.optimize_nodes import *
from itertools import groupby
from pype.vals import delam,hash_rec,is_bookmark,NameBookmark
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
import builtins
from pype.optimize_nodes import *
'''
This module contains the AST tree transformations necessary to run the optimizer.
'''
###########
# HELPERS #
###########

def is_pype_return(node,aliases):

    if is_list(node):

        node=node[-1]

    return isinstance(node,Return) \
        and isinstance(node.value,Call)\
        and node.value.func.id in aliases


def is_pype_call(node,aliases):

    return isinstance(node,Call)\
        and node.func.id in aliases


def is_name_bookmark(node):

    return isinstance(node,Call) \
        and isinstance(node.func,Attribute) \
        and node.func.attr=='NameBookmark'


def pype_return_f_args(accum,*fArgs):
    '''
    FArgs is a tuple, but we want it to be a list - it's just neater.
    '''
    return list(fArgs)


######################
# NO RETURN REPLACER #
######################

class NoReturnReplacer(NodeVisitor):
    '''
    If the function ends with a pype call, but no 'return', then we put in a return.
    This helps with conciseness, since 'return' takes up a lot of uneccessary 
    space.
    '''
    def __init__(self,aliases):

        self.aliases=aliases

    def visit_FunctionDef(self,node):

        # print(f'in functionDef')

        args=node.args.args
        body=node.body
        lastNode=body[-1]

        # print(f'{body} is body')
        # print(f'{ast.dump(lastNode)} is lastNode')
        
        if isinstance(lastNode,Expr):

            lastNode=lastNode.value

            if is_pype_call(lastNode,self.aliases):

                returnNode=Return(lastNode)
                node.body[-1]=returnNode
        
                node=fix_missing_locations(node)
                node.decorator_list=[]

        self.generic_visit(node)


#################
# NAME REPLACER # 
#################

class NameReplacer(NodeTransformer):
    '''
    This finds any name and converts it into a NameBookmark object, so when the fArgs
    are returned by pype_return_fargs, they contain NameBookmark objects.
    '''
    def __init__(self,nameSpace=set([])):

        self.nameSpace=set([el for el in nameSpace])

    def visit_Name(self,node):

        self.generic_visit(node)

        newNode=node

        if node.id in self.nameSpace:

            #print(f'visiting node {ast.dump(node)}')
            #print(f'{str(self.nameSpace)[:20]} is namespace')

            name=node.id
            newNode=Call(func=Attribute(value=PYPE_VALS_NODE,
                                        attr='NameBookmark',
                                        ctx=Load()),
                         args=[Str(s=name)], 
                         keywords=[])
            
            #newNode=fix_missing_locations(newNode)
            #node=fix_missing_locations(node)

            #print(f'node is now {ast.dump(newNode)}')

        return newNode


#####################
# PYPE VAL REPLACER #
#####################

class PypeValReplacer(NodeVisitor):
    '''
    This finds any instance of a binop in the parse tree, and replaces the first 
    element with a PypeVal for that element.  This allows us to get rid of explicit
    PypeVal declarations in optimized code, so instead of v(len)+1 you can now just
    do len + 1, but again, only in optimized code.

    Because of how delam works, this does not create a problem for the NameBookmarks
    since PypeVals are delam-ed recursively, so v(v(v(1))) evaluates as 1, and
    v(NameBookmark("a")) evaluates as NameBookmark("a").
    '''
    def visit_BinOp(self,node):

        leftNode=node.left
        rightNode=node.right

        if not (is_name_bookmark(leftNode) and is_name_bookmark(rightNode)):
        
            newLeftNode=Call(func=Attribute(value=PYPE_VALS_NODE,
                                            attr='PypeVal',
                                            ctx=Load()),
                             args=[leftNode], 
                             keywords=[])
            node.left=newLeftNode
            node.decorator_list=[]
            node=fix_missing_locations(node)

        #print(f'{ast.dump(node)} is node')

        self.generic_visit(node)


######################
# CALL NAME REPLACER #
######################

def get_body_names(el,names=[]):
    '''
    Recursively retrieve names from function body.
    '''
    if is_list(el):

        for v in el:

            get_body_names(v,names)

    elif isinstance(el,Assign):

        targets=el.targets
        
        for target in targets:

            get_body_names(target,names)

    elif isinstance(el,Name):

        names.append(el.id)

    elif isinstance(el,Tuple):

        for v in el.elts:

            get_body_names(v,names)

def pype_return_f_args(accum,*fArgs):
    '''
    FArgs is a tuple, but we want it to be a list - it's just neater.
    '''
    return list(fArgs)


IMPORT_OPTIMIZE=ImportFrom(module='pype', 
                           names=[alias(name='optimize', asname=None)], 
                           level=0)
PYPE_RETURN_F_ARGS=Attribute(value=Name(id='optimize',ctx=Load()),
                             attr='pype_return_f_args',
                             ctx=Load())

def get_body_names(el,names=[]):
    '''
    Recursively retrieve names from function body.
    '''
    if is_list(el):

        for v in el:

            get_body_names(v,names)

    elif isinstance(el,Assign):

        targets=el.targets
        
        for target in targets:

            get_body_names(target,names)

    elif isinstance(el,Name):

        names.append(el.id)

    elif isinstance(el,Tuple):

        for v in el.elts:

            get_body_names(v,names)



class CallNameReplacer(NodeVisitor):
    '''
    This class does two things - first, it changes the returned pype call to 
    pype_return_f_args, a function that returns only the fArgs.  As well, it 
    changes any variable in the local namespace into a NameBookmark object, so it is 
    not evaluated by the interpreter as a specific value.  This NameBookmark object
    is later converted into a Name object.

    I chose the NameBookmark strategy because the simultaneous iteration-mapping
    of fArg elements with nodes on the tree doesn't support pype macros such as 
    _if.  So you'd have to right a simultaneous traversal for each macro.  Instead
    I evaluate the macros with pype_return_f_args, and then parse the fArgs directly
    without any reference to the original tree.

    To illustrate this, let's say we have a macro which is:

    def _if(condition,result):

      return {condition:result,
              'else':_}

    In the call:

    y=2

    return p(x,_if(_ > 2,_+y))

    Under the old pair-traversal strategy, I'd get a parse of the _if statement, 
    and I would need to write both a fArg-to-tree conversion and a replace-name 
    conversion for this particular case.  This is messy and leads to a lot of
    code bloat.

    So here, we replace the call with a function that returns:

    [{_ > 2: _ + NameBookmark('y'),
      'else':_}]

    When the fArg parser finds a NameBookmark object, it replaces it with a Name
    object.  
    '''
    def __init__(self,aliases):

        self.pypeAliases=aliases
        self.nameSpace=set()
        self.accumNode=None

    def visit_FunctionDef(self,node):
        '''
        We are at the function definition.  First, we update the namesSpace
        with all local variables.  This means that using global constants isn't
        permitted in the optimizer - you have to explicitly put them in the 
        function scope.
        '''
        bodyNames=[]
        get_body_names(node.body,bodyNames)
        #print(f'{bodyNames} is bodyNames')
        #bodyNames=[target.id for line in node.body if isinstance(line,Assign) \
        #             for target in line.targets]
        argNames=[arg.arg for arg in node.args.args]
        self.nameSpace|=set(bodyNames+argNames)

        '''
        Is there a pype return at the end of the function definition?

        TODO - do this for all pype calls inside a function, which means the 
        accum-assign strategy needs to be replaced.
        '''
        if is_pype_return(node.body,self.pypeAliases):
            # Set the accum node
            self.accumNode=node.body[-1].value.args[0]
            # Insert an import of pype.optimize into the node body.
            node.body=[IMPORT_OPTIMIZE]+node.body
            # Change the function call from pype to pype_return_f_args, which only
            # returns the fArgs.
            node.body[-1].value.func=PYPE_RETURN_F_ARGS
            # Now, we look for any Name instance in the FArg and replace it with
            # a NameBookMark. Feed resulting nodes into newFArgsNodes.
            fArgsNodes=node.body[-1].value.args[1:]
            newFArgsNodes=[NameReplacer(self.nameSpace).visit(fArgNode) \
                           for fArgNode in fArgsNodes]
            # The new fArgsNodes have NameBookmark anywhere there is a local variable
            # referenced.  So we replace the fArgs in the function body with this.
            node.body[-1].value.args[1:]=newFArgsNodes

        node.decorator_list=[]
        node=fix_missing_locations(node)

        self.generic_visit(node)


#################
# FARG REPLACER #
#################

class FArgReplacer(NodeVisitor):
    '''
    This takes a series of sub-trees in fArgAssigns and the original parse tree.
    It then applies these assignments to the function return.

    TODO - get rid of the accum assigns.
    '''
    def __init__(self,fArgAssigns,aliases):

        self.fArgAssigns=fArgAssigns
        self.pypeAliases=aliases

    def visit_FunctionDef(self,node):

        if is_pype_return(node.body,self.pypeAliases):
        
            # Whereas originally node.body[-1] just contains the return,
            # now we replace it with the funciton body up to the return,
            # plus the accum assigns, plus the return accum.
            node.body=node.body[:-1]+self.fArgAssigns+RETURN_ACCUM

        node.decorator_list=[]
        node=fix_missing_locations(node)

        self.generic_visit(node)
