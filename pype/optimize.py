from ast import *
from pype import is_lambda
from pype import _,_0,_1,_p
from pype import _assoc as _a
from pype import _dissoc as _d
from pype import _merge as _m
from pype import _l
from pype import *
from itertools import groupby
from pype.vals import delam,hash_rec
from pype import INDEX_ARG_DICT
from functools import reduce
from inspect import signature
from collections import defaultdict
from inspect import source
from ast import *
import hashlib
import types
'''
OPTIMIZE

One of the original drawbacks of pype for data-intensive applications was its
performance.  For example, on a 16gb Ubuntu machine with 8 cores, where we define:

ls=[1]*10000

the following expression takes 6.9 seconds to run:

pype(ls,[{'n':_}],[_a('n1',_['n']+1)])

What is going on here?  There is the first mapping, which iterates through ls
and builds a dictionary.  Every time the mapping visits an element of ls, the statement
{'n':_} is interpreted by the pype interpreter.  Ditto for the second fArg.

How can we solve this?  In the old days, I'd write two functions:

fArg1=lambda ls: [{'n':el} for el in ls]

def augment_dict(d):
 d[n1]=d['n']+1
 return d

fArg2=lambda ls: [augment_dict(d) for d in ls]

pype(ls,fArg1,fArg2)

You can see that I'm converting pype fArgs into lambda functions which bypass the 
interpreter in favor of more efficient structures such as list comprehensions.  However,
it is easy to do this programmatically.  

So the first solution is to iterate through the fArgs of a pype call, identify them,
and call a function that converts the pype expression into a lambda, as we can see 
above.  This is done by the function optimize_rec - it looks at the delammed fArg,
sees if it matches any fArg types, and runs the corresponding function to convert that
expression into a lambda.  

This is what the function optimize_pype does.  Anything in fArgs that can be converted
into a lambda is converted.  Consecutive callables in the fArgs list are then fused
together using stack_funcs.  This way, something like [fArg1,fArg2,fArg3,fArg4] can 
be converted into [lambda1,fArg3,lambda2], assuming that fArg1, fArg2, and fArg4 can
be converted into lambdas.  We want to fuse callables together so that the pype 
interpreter has less work to do passing the accum to consecutive fArgs.    

However, this is rather invonvenient, especially with older pype projects.  Plus, I 
really would like pype to stand on its own two feet as a truly performant language,
capable of production code, or at least as capable as Python.

If we have access to the abstract syntax tree (AST) of a function, we could perform
the following operation:

* if f has source and can be converted into an AST, then for all pype calls in f:

  * recompile the fArg AST expressions

  * optimize the fArgs using optimize_rec

  * fuse the callables of the fArgs together

  * if not all callables can be fused together:

    *  we recompile each fArg from the AST, run optimize_rec on this expression, and 
       replace fArg expressions with lambdas in the AST, allthewhile updating the 
       namespace with these new functions.
    * we recompile f from the updated AST and namespace

  * if all of the callables can be fused together into a single callable c:

      * we can replace the pype expression pype(accum,fArg1,fArg2,...) with c(accum)
        in the AST
      * if accum matches the arguments of the encolosing function, and there is only
        one pype call, and that call is in the return, and there is no code
        in between the function definition and the returned pype call, then we return
        c.
      * otherwise, we return the original function, c(accum) where the pype expressions
        used to be

  * any function called in f whose AST can be retrieved from source is recursively 
    optimized.

This can be done by the decorator @optimize.  Simply put this decorator on the main
pype function, and let the optimizer do the work.  For example, let's have two
functions:

def sum(tup):
  return pype(tup,_0+_1)

def calc(ls):
  return pype(ls,(zip,_,_[1:]),[sum])

For if ls has 10,000 elements, calc(ls) will take 3.6 seconds.  Now, let's decorate it:

from pype.optimize import optimize 

@optimize
def calc(ls):
  return pype(ls,(zip,_,_[1:]),[sum])

Just for fun, what is going on here?

* We see that calc has source, so we generate the AST tree, or calc_AST.
* We look into calc_AST and see it has one pype call, with two fArgs, (zip,_,_[1:]) and
  [sum].  The first can be converted into a lambda, lambdaZip, and the second can
  be converted into a map, lambdaMap.  
* But wait, lambdaMap contains a function which can be turned into an AST as well.  
* We see that this has a pype call with 1 fArg, a lamTup expression.  We convert this
  into a lambda, lambdaTup.  So we replace _0+_1 with lambdaTup in the AST, and sm
  now looks like:

  def sm(ls):
   return pype(ls,lambdaTup)

* Except wait, the accum in the pype expression of sm is the same as the arguments of 
  sm, and there's no code in the function body except for the return pype expression.
  So, in mapZip in calc_AST, we replace sm wiith lambdaTup, so that now, calc looks
  like:

  def calc(ls):
   return pype(ls,lambdaZip,[lambdaTup])

* We know that maps can be reduced to lambdas, so now we replace [lambdaTup] with
  lambdaMap:

  def calc(ls):
    return pype(ls,lambdaZip,lambdaMap)

* But we also see that lambdaZip and lambdaMap are two consecutive callables, so we can
  fuse them together into lambdaStacked:

  def calc(ls):
    return pype(ls,lambdaStacked)

* But, just like with sm, the arguments of the function match thoe of pype, and there
  is no code in between them, so we just assume that calc == lambdaStacked.  

Now, it calc(ls) takes 70 milliseconds instead of 3.8 seconds. The first expression
went from 6.9 seconds to 80 milliseconds.  

That's an improvement of several orders of magnitude.

Compilation time rarely exceeds 5 milliseconds.

Purdy kewellll ...
'''
###########
# HELPERS #
###########

def call_or_val(x,f):
    '''
    Similar to eval_or_val.  Return f(x) if f is callable, otherwise just f.
    '''
    return f(x) if is_callable(f) else f


def call_or_val_if_none(x,f):
    '''
    Similar to eval_or_val.  Return f(x) if f is callable, otherwise just f.
    '''
    return x if f is None else f(x) if is_callable(f) else f


def stack_funcs(funcs):
    '''
    Creates a callable from a list of callables.  If there is more than one
    callable, we wrap the callables in a reduce.
    '''
    if len(funcs) == 1:

        return funcs[0]

    else:

        return lambda x: reduce(lambda h,f: f(h),
                                 funcs[1:],
                                 funcs[0](x))


def all_callable(optimizedFArg):
    '''
    When we have a list of fArgs that we've optimized, we can build a callable
    putting them together in some way only if everything in the fArg has
    successfully been converted into callables.  Otherwise, we need a different
    strategy, returning something resembling the original fArg.  
    '''
    return all([is_callable(l) for l in optimizedFArg])


def is_optimized(optimizedFArg):
    '''
    We know that something is optimized if it is either a callable or a constant,
    non-fArg value.
    '''
    return is_callable(optimizedFArg) or not is_f_arg(optimizedFArg)


def all_optimized(optimizedFArg):
    '''
    This is for cases like lambda expressions where you may have non-fArg values.
    For example an expression like:

    (add,1,(add,_,_))

    (add,_,_) can be converted into a callable, but 1 is not an fArg, so we should
    just leave it as such.  
    '''
    return all([is_optimized(l) for l in optimizedFArg])


##################
# MAIN OPTIMIZER #
##################

def optimize_rec(fArg):
    '''
    This iterates through OPTIMIZE_PAIRS, which is a list of tuples 
    [(is_f_arg,optimize_f_arg),...] where is_f_arg is a boolean that identifies 
    the fArg type and optimize_f_arg is a function that converts the fArg into a 
    callable with one argument, or f(x).  

    We do this by going through OPTIMIZE_PAIRS, finding the last boolean to 
    evaluate as True.  Then, we take its corresponding optimize function and 
    apply this to fArg.  

    If there are no matches, we return the original fArg.  We do this to ensure
    that fArgs that are not covered by this module can still be interpreted.

    Because optimize_rec is called in the optimize functions, this function is
    recursive.  

    Also notice that the decorator optimize is called on any callable fArgs, to 
    see whether the function contains any pype expressions that can be optimized.
    '''
    fArg=delam(fArg)
    evals=[(evl_f(fArg),opt_f) for (evl_f,opt_f) in OPTIMIZE_PAIRS]
    opt_fs=[opt_f for (evl,opt_f) in evals if evl]

    if opt_fs:

        opt_f=opt_fs[-1](fArg)

        return opt_f

    return fArg


def optimize_f_args(fArgs):
    '''
    This helper calls optimize_rec on a list of fArgs.
    '''
    return [optimize_rec(a) for a in fArgs]


def get_f_from_optimized(optimizedFArg):
    '''
    If all fArgs in optimizedFargs are callable, then we return the first element
    if there is only one element, otherwise we call stack_funcs on the list.
    '''
    if len(optimizedFArg) == 1:

        return optimizedFArg[0]

    else:

        return stack_funcs(optimizedFArg)


'''
OPTIMIZERS

The grand strategy of each optimizer function is to run optimize_rec recursively
on the fArg structure.  If everything in the fArg structure has successfully been
converted into a callable, then we can compose a new callable around that.

For example, let's say I can convert fArg1,fArg2, and fArg3 into callables f1,
f2, and f3.  This means that I can take a lambda expression:

(fArg1,fArg2,fArg3)

and convert it into a function f1(f2(x),f3(x)).  But if fArg3 cannot be turned into
a callable, then I return:

(f1,f2,fArg3).
'''

#############
# INDEX ARG #
#############

def optimize_index_arg(fArg):
    '''
    The returned function is gets the integer from INDEX_ARG_DICT keyed by the 
    fArg (_0,_1,_last, etc.).  Index args are some of the most commonly used pype
    expressions, so we do these first.
    '''
    def ind_arg(ctnr):

        return ctnr[INDEX_ARG_DICT[fArg]]

    return ind_arg


##########
# MIRROR #
##########

def optimize_mirror(fArg):
    '''
    As the mirror is just the identity function, we return the identity function.
    '''
    return lambda x:x


##########
# LAMBDA #
##########

def optimize_lambda(fArg):
    '''
    If we have successfully converted every embedded fArg into a callable,
    we return a callable composed of these functions.  However, if there is at
    least one non-callable in the converted lambda, then we return that 
    lambda expression, with whatever we callables we could find (see above 
    example).  
    '''
    f=optimize_rec(fArg[0])
    lambdaArgs=fArg[1:]
    optimizedLambdaArgs=optimize_f_args(lambdaArgs)
    
    if is_callable(f) and all_optimized(optimizedLambdaArgs):
       
        #print('optimize_lambda')
        #print(f'{fArg}')
 
        return lambda x: f(*[call_or_val(x,g) for g in optimizedLambdaArgs])

        #print(f'{f},{signature(f)}')

        #return f

    return (f,*optimizedLambdaArgs)


#######
# MAP #
#######

def optimize_map(fArg):
    '''
    This optimizes a map of fArgs.  If all fArgs are callable, we fuse them into
    a single callable, f, using get_f_from_optimized.  Then, we return a callable
    that runs a list comprehension of f on each element of the list.

    If this is unsuccessful, we return a list of the optimized fArgs.

    This was a particularly dramatic improvement.
    '''
    optimizedFArg=optimize_f_args(fArg)
    
    if all_callable(optimizedFArg):

        f=get_f_from_optimized(optimizedFArg)

        def mp(ctnr):

            if is_dict(ctnr):

                return {k:f(v) for (k,v) in ctnr.items()}

            return [f(el) for el in ctnr]

        return mp

    else:

        return optimizedFArg


#########
# INDEX #
#########

def optimize_index(fArg):
    '''
    If we successfully optimize the indexed element and the indices, we
    return a reduce which iterates through the indices and gets us the element.
    
    Otherwise, we return the original structure, with whatever optimized fArgs
    exist.
    '''
    indexed=optimize_rec(fArg[0])
    indices=[optimize_rec(f[0]) for f in fArg[1:]]
    
    return lambda x: reduce(lambda h,index:h[index(x)] \
                                           if is_callable(index) else h[index],
                            indices,
                            call_or_val(x,indexed))

##############
# AND FILTER #
##############

def optimize_and_filter(fArg):
    '''
    First, tries to optimize all fArgs in the filter.  If not all fArgs can be
    optimized, it returns a and-filter expression [[fArg1,fArg2,...]].  If all 
    fArgs can be optimized, it returns a callable which iterates through a list,
    including only elements for which all fArgs evaluate as True.
    '''
    fArg=fArg[0]  # Unpack the list: [[fArg1,...]] => [fArg1,...]
    optimizedFArg=optimize_f_args(fArg)

    if all_callable(optimizedFArg):
 
        return lambda ls: [el for el in ls if all([f(el) for f in optimizedFArg])]

    else:

        return [optimizedFArg]



#################
# EMBEDDED PYPE #
#################

def optimize_embedded_pype(fArg):
    '''
    We find if we successfully optimized all fArgs in fArg, and if so we
    return a single callable from those optimized fArgs.  Otherwise, we
    return another embedded pype with the partially optimized fArg.  
    '''
    optimizedFArg=optimize_f_args(fArg[1:])

    if all_callable(optimizedFArg):

        return stack_funcs(optimizedFArg)
    
    return _p(optimizedFArg)


#################
# OBJECT LAMBDA #
#################

def optimize_object_lambda(fArg):
    '''
    We evaluate obj, get the attribute in fArg[1], and then see if we can
    optimize any of the other fArgs.  If we have failed to optimize fArg[1]
    and all otherFArgs, we return the object lambda as is.
    '''
    firstFArg=optimize_rec(fArg[0])
    obj=lambda x: call_or_val(x,firstFArg)
    obj_f=lambda x: getattr(obj(x),fArg[1])
    otherFArgs=optimize_f_args(f[2:])

    if is_callable(firstFArg) and all_optimized(otherFArgs):

        return lambda x: obj_f(x,*[call_or_val(x,f) for f in otherFArgs])

    return (fArg[0],fArg[1],*otherFArgs)


##############
# LIST BUILD #
##############

def optimize_list_build(fArgs):
    '''
    If we successfully optimize everything in the list build, then we return
    a lambda that runs a list comprehension on it.  Otherwise, we return another
    list build fArg.
    '''
    fArgs=[optimize_rec(fArg) for fArg in fArgs[1:]]

    if all_optimized(fArgs):

        return lambda x: [call_or_val(x,fArg) for fArg in fArgs]

    return _l(*fArgs)


##########
# REDUCE #
##########

def optimize_reduce(fArgs):
    '''
    We want to optimize three types of reduce statements:

    1) [(reduceF,)], where the reduceF acts on the accumulator as a starting value.
       
       Equivalent to reduce(reduceF,accum).

    2) [(reduceF,),startVal], where the reduceF acts on the accumulator with a
       different starting value, possibly an fArg.

       If startVal is an fArg, this is equivalent to:
 
       reduce(reduceF,accum,startVal(accum)).

       If startVal is not an fArg, this is equivalent to:

       reduce(reduceF,accum,startVal)

    3) [(reduceF,),startVal,accumExpression], where the reduceF acts on an accumulator,
       which is first transformed by accumExpression, with a start value.  This is 
       equivalent to pype(...,accumExpression,[(reduceF,),startFArg],...), or:

       reduce(reduceF,accumExpression(accum),startVal)

       If startVal is an fArg, this is equivalent to:

       reduce(reduceF,accumExpression(accum),startVal(accumExpression(accum)))

    We only return a lambda if:

    1) reduceF is optimizeable to a callable.
    2) If there is a startFArg, it must be optimized to a callable or not an fArg.
    3) If there is an accumExpression, it must be optimized to a callable.
    '''
    reduceF=optimize_rec(fArgs[0][0])
    # startFArg is the data structure that accumulates the reduce.
    startFArg=optimize_rec(fArgs[1]) if len(fArgs) > 1 else None
    # accumExpression is a transformation applied to accum before
    # we run the reduce.
    accumExpression=optimize_rec(fArgs[2]) if len(fArgs) == 3 else None

    if is_callable(reduceF):

        # [(reduceF,)]
        # reduce(reduceF,accum)
        if not startFArg:

            return lambda accum: reduce(reduceF,accum)

        if is_callable(startFArg):

            # [(reduceF,),startFArg,accumExpression]
            # reduce(reduceF,
            #        accumExpression(accum),
            #        startFArg(accumExpression(accum)))
            if accumExpressionCallable:

                return lambda accum: reduce(reduceF,
                                            accumExpression(accum),
                                            startFArg(accum))

            # [(reduceF,),startFArg]
            # reduce(reduceF,
            #        startFArg(accum))
            return lambda accum: reduce(reduceF,
                                        accum,
                                        startFArg(accum))

        # [(reduceF,),startFArg]
        # reduce(reduceF,startFArg)
        elif is_optimized(startFArg):

            return lambda accum: reduce(reduceF,accum,startFArg)

    # Return an fArg for the reduce.
    return [el for el in [(reduceF,),startFArg,accumExpression] if el]



'''
DICTIONARY OPERATIONS

Here, our grand strategy is to take a dictionary, put it into a list of key-value
pairs, optimize those key-value pairs. If we are successful, then we return a 
lambda that returns this dict.  Otherwise, we rebuild the original dict.  

We must remember that since lambdas can break the hashing requirements for 
dictionary keys, we cannot rebuild dicts with optimized lambdas - we must use the 
original lamtups instead.
'''

##############
# DICT BUILD #
##############

def unpack_and_optimize(fArg):
    '''
    Helper function to run delam on the keys of a dict (not permissible with 
    dictionary comprehentions) and produce a list of optimized key-value pairs.
    '''
    unpackedFArg=[(k,v) for (k,v) in fArg.items()]
    optimizedFArg=[(optimize_rec(k),optimize_rec(v)) for (k,v) in unpackedFArg]

    return unpackedFArg,optimizedFArg


def all_pairs_optimized(optimizedFArg):
    '''
    Convenience method to go through optimized key-value pairs and ensure they're
    optimized.
    '''
    return all_optimized([k for (k,v) in optimizedFArg]) \
       and all_optimized([v for (k,v) in optimizedFArg])


def rebuild_unoptimized_dict(unpackedFArg,optimizedFArg):
    '''
    Otherwise, we rebuild the original fArg, making sure
    that we re-include lamtups as keys rather than delamm-ed lamtups.  
    '''
    return {fArgK if is_lam_tup(fArgK) else optK:optV \
            for ((fArgK,fArgV),(optK,optV)) in zip(optimizedFarg,unpackedFArg)}

     
def optimize_dict_build(fArg):
    '''
    First, we unpack the dict into key-value pairs.  Then, we optimzie these pairs.
    If all keys and values are successfully optimized, we return a lambda which
    computes the dict build.  Otherwise, we rebuild the original fArg, making sure
    that we re-include lamtups as keys rather than delamm-ed lamtups.  
    '''
    unpackedFArg,optimizedFArg=unpack_and_optimize(fArg)

    if all_pairs_optimized(optimizedFArg):

        return lambda x: {call_or_val(x,k):call_or_val(x,v) \
                          for (k,v) in optimizedFArg}

    return rebuild_unoptimized_dict(optimizedFArg,unpackedFArg)
    

###############
# SWITCH DICT #
###############

def optimize_switch_dict(fArg):
    '''
    Similar to optimize_dict_build.  We go through the dictionary, optimizing keys
    and values.  If all keys and values are optimized (or constant), we return
    a function that evaluates the switch dict.  Otherwise, we just return the 
    switch dict with whatever keys or values could be optimized.
    '''
    unpackedFArg,optimizedFArg=unpack_and_optimize(fArg)

    if not all_pairs_optimized(optimizedFArg):

        return rebuild_unoptimized_dict(optimizedFArg,unpackedFArg)

    is_in=lambda x: not is_container(x) and x in optimizedFArg
    
    def evl_switch_dict(x):

        evls=[(bool(call_or_val(x,k)),v) for (k,v) in optimizedFArg]
        evlsTrue=[(k,v) for (k,v) in evls if is_bool(k) and k]
        v=evlsTrue[-1][1] if evlsTrue else optimizedFArg['else']

        return call_or_val(x,v)

    return lambda x: call_or_val(x,optimizedFArg[x]) if is_in(x) \
                    else evl_switch_dict(x)


##############
# DICT ASSOC #
##############

def optimize_dict_assoc(fArg):
    '''
    We first optimize the keys and fArgs.  If this is successfull, then we build
    a function d_assoc which executes the dict assoc.  Otherwise, we return the 
    original dict assoc object.
    '''
    keys=optimize_f_args(fArg[1::2])
    fArgs=optimize_f_args(fArg[2::2])

    if not all_optimized(keys) nor  all_optimized(fArgs):

        return _a(*[val for pair in zip(keys,fArgs) for val in pair])

    def dassoc(x):

        for key,fArg in zip(keys,fArgs):
            
            x[call_or_val(x,key)]=call_or_val(x,fArg)
            
            return x

    return dassoc


###############
# DICT DISSOC #
###############

def optimize_dict_dissoc(fArgs):
    '''
    We try and optimize all elements of a dict dissoc.  If we are successful,
    we return a function that executes the dict dissoc.  Otherwise, we return
    the original dict dissoc fArg.
    '''
    fArgs=optimize_f_args(fArgs[1:])

    if not all_optimized(fArgs):

        return _d(*fArgs)

    def dict_dissoc(x):

        for fArg in fArgs:

            del x[call_or_val(x,fArg)]

            return x

    return dict_dissoc


##############
# DICT MERGE #
##############

def optimize_dict_merge(fArg):
    '''
    We try to optimize the fArg, which we know is a dict.  We do not call optimize_rec
    on this fArg because we need to confirm that the dictionary is fully optimized.
    '''
    optimizedDict=optimize_rec(fArg[1])

    if not is_dict(optimizedDict):

        raise Exception('accidentally did a dict_merge on a switch dict')

    unpackedFArg,optimizedFArg=unpack_and_optimize(optimizedDict)

    if not all_pairs_optimized(optimizedFArg):

        return _m(rebuild_unoptimized_dict(optimizedFArg,unpackedFArg))

    def dict_merge(x):

        for (k,v) in fArg.items():

            x[call_or_val(x,k)]=call_or_val(x,v)

        return x

    return dict_merge


'''
MAIN OPTIMIZATION

Here, we are making extensive use of AST syntax trees.
'''
#############################
# MAIN OPTIMIZATION HELPERS #
#############################

def hash_optimized(evls):
    '''
    This is to build names for callables generated from optimize_rec.  We hash
    whatever fArgs we have found, and return them in the format optimize_HASH.
    This is for insertion into the namespace.  If, in the process of modifying the 
    AST, we build a callable and don't include the name of the callable and the callable
    in the namespace, the compilation will fail.
    '''
    m=hashlib.sha224()

    if is_list(evls):

        for evl in evls:

            m.update(str(evl).encode('utf-8'))

    else:

        m.update(str(evls).encode('utf-8'))

    return f'optimized_{m.hexdigest()}'


def fuse_pype_args(pypeArgs):
    '''
    This takes the optimized arguments of pype, being [accum,fArg1,fArg2,fArg3].
    We group the fArgs by whether they are callable.  Every contiguous group of 
    callable fArgs gets turned into a single callable and put into newPypeArgs with
    its new name, computed by hash_optimized.  Otherwise, we just insert the fArg 
    with a False.  pypeArgs has the format [(False,AST(accum)),(identifier1,callable1),
    (False,AST(fArg2))...], where 'False' indicates that the tuple is either the accum
    or an unoptimized fArg and AST indicates the AST representation fo the pype arg.
    '''
    newPypeArgs=[pypeArgs[0]] # This is already a tuple, (False,accum).

    for isCallable,g in groupby(pypeArgs[1:],lambda x:is_callable(x[1])):

        if isCallable:

            # x is a tuple (identifier,fArg), where identifier is False if the fArg
            # was not successfully optimized.
            funcs=[x[1] for x in g]
            # Identifier will be the hash of all the identifiers for the optimized
            # functions.
            identifier=hash_optimized([x[0] for x in g])

            # stack_funcs wraps contiguous callables in a reduce.
            newPypeArgs.append((identifier,stack_funcs(funcs)))

        else:

            newPypeArgs.extend(grp)

    return newPypeArgs


def convert_pype_args_to_optimized(args):
    '''
    We take a first pass at the pype args, consisitning of [AST(accum),AST(fArg1),
    AST(fArg2),...], and produce [(False,AST(accum)),(identifier1,callable1),
    (False,fArg2)...], where 'False' indicates that the element represents the accum
    or an unsuccessfully optimized pype arg.
    '''
    newPypeArgs=[(False,args[0])]

    for fArg in args[1:]:

        # We evaluate the expression into a Python-interpretable fArg.
        expr=Expression(fArg)
        evl=eval(compile(expr,filename='<ast>',mode='eval'))
        # Then we try and optimize it.
        optimized=optimize_rec(evl)

        # If we are successful, append its identifier and the function.
        if is_callable(optimized):

            identifier=hash_optimized(evl)

            newPypeArgs.append((identifier,optimized))

        # Otherwise, just put 'False' and the original fArg.
        else:

            newPypeArgs.append((False,fArg))

    return newPypeArgs


def optimize_pype_args(args,namespace):
    '''
    This is the meat of the optimization.  We presume that args are the args of a 
    pype call, in the format [AST(accum),AST(fArg1),AST(fArg2),...], where AST
    indicates an AST representation.  We want to build a new list of args for the 
    pype call, consisting of [AST(accum),AST(callable1),AST(fArg) ...] where callable1
    is a successfully optimized fArg, and the updated namespace..
    '''
    # We don't want to optimize the AST for the accum.
    newPypeArgs=convert_pype_args_to_optimized(args)
    newPypeArgs=fuse_pype_args(newPypeArgs)
    # Now, let's take our Pype args, which will either be (False,AST(fArg or accum)),
    # if the optimization was unsuccessful, or (identifier,callable1) if the
    # optimization was.   
    finalPypeArgs=[]

    for (identifier,fArg) in newFArgs:

        # The optimization was unsuccessful, meaning we just add AST(fArg or accum)
        # to finalPypeArgs.
        if not identifier:

            finalPypeArgs.append(fArg)
        
        # The optimization was successful, which means we build an AST Name expression
        # for the new callable, and insert that callable into the namespace.
        else:

            optimizedNode=Name(id=identifier,ctx=Load())
            namespace[identifier]=fArg            

            finalPypeArgs.append(optimizedNode)

    return finalPypeArgs,namespace


def aliases_for_pype(glbls):
    '''
    This searches through the global namespace of a function to find any aliases for
    the pype function.  Helps when pype is given another name, as in:

    from pype import pype as p
    '''
    return set([alias for (alias,f) in glbls.items() \
                if glbls[alias] == glbls['pype'] \
                and is_callable(f)])

    

#########################
# PYPE ARG NODE VISITOR #
#########################

class PypeArgOptimizer(NodeVisitor):
    '''
    This finds pype calls in the AST, identified by pype aliases, and runs optimizations
    on their arguments.

    I use NodeVisitor instead of NodeTransformer because I had a few issues which I
    didn't want to deal with.
    '''
    def __init__(self,pypeAliases):
        '''
        We need pypeAliases to identify the pype calls in the syntax tree.
        '''
        self.namespace={}
        self.pypeAliases=pypeAliases


    def visit_FunctionDef(self,node):
        '''
        Since this is called inside a decorator, optimize, we want to get rid of 
        that decorator's information in the AST.
        '''
        node.decorator_list=[]
        
        node=fix_missing_locations(node)

        self.generic_visit(node)


    def visit_Call(self,node):
        '''
        When we find a pype call inside the function, we perform the optimization on
        the pype args, and update the namespace.  We deal with two situations:

        1) In the case where we've reduced the pype args to the accum and a single 
        callable, as in [AST(accum),AST(callable1)], we don't need pype anymore, so
        we just replace the pype call with AST(callable1(accum)).

        2) Otherwise, we keep keep the pype call, as in AST(pype(accum,fArg1,callable1,
        ...).
        '''
        if node.func.id in self.pypeAliases:

            newPypeArgs,self.namespace=optimize_pype_args(node.args,self.namespace)
        
            # newPypeArgs[1].id in self.namespace means that this is a callable that
            # has been generated by optimize_pype_args, and it is the only callable.
            if len(newPypeArgs) == 2 and newPypeArgs[1].id in self.namespace:

                optimizedName=newPypeArgs[1] # We mean the ast.Name object.
                # We swap out the pype call with the optimized function.
                node.func=optimizedName
                # And the accum becomes the only argument to this function.
                node.args=[newFArgs[0]]
                node=fix_missing_locations(node)

            # Otherwise, keep the pype call with the modified fArgs.
            else:

                node.args=newPypeArgs
                node=fix_missing_locations(node)
        
        self.generic_visit(node)

###########
# INLINER #
###########

def is_inlineable(args,body):
    '''
    Investigates the arguments and body of the FuncDef AST to see if:
    
    1) There is no code between the return statement and the function definition.
    2) The returned value is a function call with a single argument.
    3) The id of the function argument matches the id of the argument in the returned
       function call.  
    '''
    return len(args) == 1 \
        and len(body) == 1 \
        and isinstance(body[0],Return) \
        and len(body[0].value.args) == 1 \
        and isinstance(body[0].value.args[0],Name) \
        and args[0].arg == body[0].value.args[0].id


class Inliner(NodeVisitor):
    '''
    If, in our pype optimization, we end up with a function which is inlineable,
    such as:

    def f1(x):
     return pype(x,callable1)

    We instead just want to turn this into callable1.  The arguments of f1 and the
    accum of the pype call match, there is only one callable in the fArgs, so let's
    just make f1 callable1.  This can give us a 10 millisecond improvement in 
    performance for large arrays (30k ...).
    '''
    def __init__(self,namespace):
        '''
        We need the namespace to reference the function.  If we find an inlineable
        function, we put it in self.inlined_function.
        '''
        self.namespace=namespace
        self.inlined_function=None

    def visit_FunctionDef(self,node):
        '''
        Looks at the function from the FunctionDef, and determines if there is 
        an inlineable function embedded in it.  If so, it populates 
        self.inlined_function.
        '''
        args=node.args.args
        body=node.body

        if is_inlineable(args,body):

            # We found an inlineable function.
            inlinedFunctionID=body[0].value.func.id
            self.inlined_function=self.namespace[inlinedFunctionID]

        self.generic_visit(node)


############################
# MAIN OPTIMIZER DECORATOR #
############################

def recompile(tree,mainFunctionName,globalNamespace,localNamespace):
    '''
    This takes a tree for a function identified by mainFunctionName, and
    recompiles it.  This function should be found in the localNamespace,
    so we return the compiled function there.
    '''
    c=compile(tree,filename='<ast>',mode='exec')

    exec(c,globalNamespace,localNamespace)

    return localNamespace[mainFunctionName]


def optimize(func):
    '''
    Intended to be used as a decorator, but can be called directly on the function.

    Our grand strategy is:

    1) If func is a builtin function, return it.
    2) If func has no source, return it.
    3) Extract the source from func.
    4) Get an AST from the source.
    5) Run a PypeArgOptimizer on it.
    4) If we can extract an inlined function, return the inlined function.
    5) Otherwise, rebuild the tree and return the recompiled function.
    '''
    # We don't want to even try running this on builtin functions.
    if isinstance(func,types.BuiltinFunctionType):

        return func

    # Let's see if the function has source code ...
    try:

        source=getsource(func)

    # No?  Just return the function
    except Exception as e:

        return func

    # Parse it into an AST.
    tree=parse(source)
    # Grab our pype aliases.
    aliases=aliases_for_pype(func.__globals__)
    # And let's optimize.
    pypeArgOpt=PypeArgOptimizer(aliases)

    pypeArgOpt.visit(tree)

    # Let's see if we can inline the function.
    inline=Inliner(pypeArgOpt.namespace)

    inline.visit(tree)

    if inline.inlined_function is not None:

        return inline.inlined_function

    # Otherwise, let's just returned the recompiled tree.
    recompiled_f=recompile(tree,
                           func.__name__,
                           func.__globals__,
                           pypeArgOpt.namespace)

    return recompiled_f


'''
OPTIMIZE PAIRS

This global variable is essential for optimize_rec.  Notice that every callable can
be optimized using optimize.  This means that placing the optimize decorator on any
function recursively optimizes all pype calls in that function or any callable in
that function.  So, for example, if I had:

def sm(tup):
 return pype(tup,_0+_1)

@optimize
def calc(ls):
 return pype(ls,(zip,_,_[1:]),[sm])

both calc and sm would be optimized.  

I am hoping to add tuples to this as I continue to optimize different fArg types.
Ideally, I would like all of pype to be optimized, so that the optimize decorator
would be redundant.  The pype interpeter would be used for testing and debugging only.
'''
OPTIMIZE_PAIRS=[(is_callable,optimize),
                (is_mirror,optimize_mirror),
                (is_index_arg,optimize_index_arg),
                (is_lambda,optimize_lambda),
                (is_index,optimize_index),
                (is_map,optimize_map),
                (is_and_filter,optimize_and_filter),
                (is_implicit_dict_build,optimize_dict_build),
                (is_switch_dict,optimize_switch_dict),
                (is_embedded_pype,optimize_embedded_pype),
                (is_object_lambda,optimize_object_lambda),
                (is_dict_assoc,optimize_dict_assoc),
                (is_dict_dissoc,optimize_dict_dissoc),
                (is_list_build,optimize_list_build),
                (is_reduce,optimize_reduce),
             ]

