'''
python3 cyk.py

This is a pype implementation of my functional implementation of the CYK parsing
algorithm in Clojure, at https://bitbucket.org/bbbdragon/bennett-cyk-demo.  You will
find that the pype implementation implements the algorithm functionally in the same 
way that the Clojure algorithm does.  The only difference is under-the-hood.  Because
Clojure data structures are so light-weight, it can generate new structures with 
every iteration and not have any performance hits.  In this case, however, the same
table structure is being updated with each iteration - the code is functional, but
the underlying implementation does not guarantee immutability.
'''
from pype import pype as p
from pype import _,_0,_1,_2,_l
import pprint as pp
from pype.vals import PypeVal as v
from pype import _concat as _c
from pype import _assoc as _a
from pype import _dissoc as _d
from pype import _merge as _m
from pype import _p 
from pype import Quote as q
from itertools import product
from pype.helpers import *
from pype.vals import lenf

'''
In the grammar string, we define a context-free grammar.  The first symbol in each
line is the left-hand-side symbol, or lhs.  The second symbol is the first 
right-hand-side symbol, or rhs1.  The third symbol is the second right-hand-side
symbol, or rhs2.
'''
GRAMMAR_STRING='''
NP Det N
VP V NP
S NP VP
'''

def read_grammar(grammarString):
    '''
    We read the grammar string and convert it into a JSON of the form 
    {rhs1:{rhs2:lhs,...},...}

    _.splitlines,

    This splits the grammar string by line.

    {_},

    {} indicates we are filtering over a list, and including whatever elements in 
    the list evaluate as true.  Since _ is a string, and an empty string evaluates as
    false, this filters out any empty strings.

    [_.split],
    [{'lhs':_0,
      'rhs1':_1,
      'rhs2':_2}],
    
    This splits each line into tuples of 3.  The first is assigned to the 'lhs' in
    the dictionary.  The second is 'rhs1'.  The third is 'rhs2'.

    (merge_ls_dct,_,'rhs1'),

    We aggregate these dictionaries by 'rhs1', giving us a dictionary of the form
    {rhs1:[{'rhs1':rhs1,'rhs2':rhs2,'lhs':lhs},...],...}.

    [_p((merge_ls_dct,_,'rhs2'),
        [_0],
        [_['lhs']])]

    Then, we iterate through the values of the resulting dict, which are lists.  We
    aggregate these lists by rhs2.  Since this is a deterministic context-free-
    grammar, we know that we have a JSON of form 

    {rhs1:(rhs2:[{'rhs1':rhs1,'rhs2':rhs2,'lhs':lhs}],...],...}.
    
    with only one element in the embedded list.  We therefore extract the first element
    of these embedded lists with [_0], and extract the element keyed by 'lhs'.
    '''
    return p( grammarString,
              _.splitlines,
              {_},
              [_.split],
              [{'lhs':_0,
                'rhs1':_1,
                'rhs2':_2}],
              (merge_ls_dct,_,'rhs1'),
              [_p((merge_ls_dct,_,'rhs2'),
                  [_0],
                  [_['lhs']])]
            )


def range_for_span(span,fArg):
    '''
    CYK requires three sequences of numbers, the span, the begin index, and the 
    partition.  This takes a span, which is 1 to the final index of the sequence,
    and it takes a quoted fArg.  Because [(range_list,0,fArg)], produces a list of
    lists, we use the flatten_list helper to convert it into a single list.
    '''
    return p( span,
              [(range_list,0,fArg)],
              flatten_list)


def partitions(seq):
    '''
    In our strategy, we do not want to iterate over a static table, but rather
    iterate over a series of partitions.  Each partition is a JSON of the form:

    {'begin1':begin1,
     'end1':end1,
     'begin2':begin2,
     'end2':end2}

    It defines a partition of the string which the parser will evaluate to generate
    and insert new symbols.  To do this, we first evaluate the following:

    (range_list,1,_),
    
    This is a list of integers from 1 to the length of the sequence.

    (product,_,
             (range_for_span,_,q(v(stLen)-_)),
             (range_for_span,_,q(_))),

    Now, we take the Cartesian product of 3 sequences.  The first is the span range
    evaluated above, and marked by _.

    (range_for_span,_,q(v(stLen)-_)),

    This second is the range of begin1 indices.  Notice we are passing the range of
    the span, but we are also passing an q(stLen-_).  stLen-_ evaluates to a LamTup.
    TODO: explain this!.  q() means that we are quoting the expression, and do not
    want the pype interpreter to evaluate this expression in this function, but rather
    to pass it into range_for_span as an fArg, to be evaluated there.
    
    (range_for_span,_,q(_))),

    This third is the range of the partition indices.  Again, we use the quote.

    (zip_to_dicts,_,'span','begin1','partition'),

    zip_to_dicts is a helper which iterates through a sequence of tuples and builds
    a dictionary with the consecutively ordered keys.

    [_a('end1',_['begin1']+_['partition'])],

    Now that we have a list of dictionaries, we add a field, 'end1', and assign the
    result of the following expression.

    [_a('begin2',_['end1']+1)],
    [_a('end2',_['begin1']+_['span'])],

    We add 'begin2' and 'end2' in the same way.

    [_d('partition','span')],

    Since we no longer need these fields, we remove them from the dictionaries.
    '''
    stLen=len(seq)

    return p( stLen,
              (range_list,1,_),
              (product,_,
                       (range_for_span,_,q(stLen-_)),
                       (range_for_span,_,q(_))),
              (zip_to_dicts,_,'span','begin1','partition'),
              [_a('end1',_['begin1']+_['partition'])],
              [_a('begin2',_['end1']+1)],
              [_a('end2',_['begin1']+_['span'])],
              [_d('partition','span')],
            )


def init_table(seq):
    '''
    This takes a sequence and initializes a table.  The table is a JSON of form
 
    {index1:{index1:{'lhs':seq1,'tree':tree1}},
     index2:{index2:{'lhs':seq2,'tree':tree2}},
     ...}
    
    where seq1 is the first symbol in the sequence, and index1 is the index of that 
    symbol in the sequence, 0 for the first, 1 for the second, etc. tree1 is a tree
    representation of that symbol, which is a list of form [seq1].

    (zip,(range,len),_),

    Create a list of tuples containing the index and the symbol.

    [{_0:{_0:{'lhs':_1,
              'tree':_l(_1)}}}],

    _0 refers to the index, so we are creating a list of JSON's of form 

    {index1:{index1:{'lhs':seq1,'tree':tree1}}

    [(dct_merge_vals,),{}],

    dct_merge_vals merges two dictionaries that have embedded dictionaries as values.
    We are doing this as a reduce, with an empty dictionary, {}, as the starting value.
    '''
    return p( seq,
              (zip,(range,len),_),
              [{_0:{_0:{'lhs':_1,
                        'tree':_l(_1)}}}],
              [(dct_merge_vals,),{}],
            )


def get_lhs(begin1,begin2,end1,end2,table,grammar):
    '''
    This takes a table, the variables of a partition, and a grammar, and returns a 
    JSON of form {'lhs':lhs1,'tree':tree1} if there is an element in the table
    from which the grammar can derive an lhs.  

    {'rhs1':(get_or_false,_,begin1,end1),
     'rhs2':(get_or_false,_,begin2,end2)},

    get_or_false is a helper which takes a dictionary with embedded dictionaries
    and finds if the sequence of keys is present.  So, if the table is:

    {0:0:{'lhs':'Det','tree':['Det']}}

    then get_or_false(table,0,0) will return {'lhs':'Det','tree':['Det']}.  However,
    with this particular table, get_or_false(table,0,1) will return False, because
    no embedded element exists in the JSON.  

    So, we find if there is an rhs1 in the table beginning at begin1 and ending at 
    end1, and do the same thing for rhs2.  We do a dict build for scoping.

    _a('tree1',(get_or_false,_['rhs1'],'tree')),
    _a('tree2',(get_or_false,_['rhs2'],'tree')),

    If the first argument of get_or_false is False, then the function returns False.
    Otherwise, we recover the trees from rhs1 and rhs2 in the table, and add them to
    the JSON initialized above.

    _a('lhs',(get_or_false,grammar,
                           (get_or_false,_['rhs1'],'lhs'),
                           (get_or_false,_['rhs2'],'lhs'))),

    Now, we check the grammar to see if it has a rule in which the lhs of rhs1 is the
    first rhs, and the lhs of rhs2 is the second lhs.  We assign the result to 'lhs'
    in the main JSON.

    {_['lhs']:_p( _a('tree',_l(_['lhs'],_['tree1'],_['tree2'])),
                            _d('rhs1','rhs2','tree1','tree2')),
     'else':False}

    Remember, in a switch dict, if the key evaluates as True, then the corresponding
    expression is evaluated and returned.  If the grammar cannot find an lhs in the
    above statement, then 'lhs' in the main JSON will be False, and we return
    False.

    Otherwise, we add an additional field, 'tree' to the main JSON, which is a list 
    containing the lhs symbol, followed by tree1 and tree2, which are also lists.  

    Finally, we get rid of fields we don't need - 'rhs1','rhs2','tree1',and 'tree2' - 
    and return the JSON.
    '''
    return p( table,
              {'rhs1':(get_or_false,_,begin1,end1),
               'rhs2':(get_or_false,_,begin2,end2)},
              _a('tree1',(get_or_false,_['rhs1'],'tree')),
              _a('tree2',(get_or_false,_['rhs2'],'tree')),
              _a('lhs',(get_or_false,grammar,
                        (get_or_false,_['rhs1'],'lhs'),
                        (get_or_false,_['rhs2'],'lhs'))),
              {_['lhs']:_p( _a('tree',_l(_['lhs'],_['tree1'],_['tree2'])),
                            _d('rhs1','rhs2','tree1','tree2')),
               'else':False}
            )


def apply_partitions(seq,grammar):
    '''
    This is the main function to run CYK.  Notice that we create a closure function
    apply_partition in the function body.  We do this because the main iteration is a
    reduce, and a reduce takes two arguments only.  So we bind the grammar variable
    inside the closure.

    Let's go through apply_partition first.  

    (get_lhs,begin1,begin2,end1,end2,_,grammar),

    We get the lhs for the partition.

    {_:(dct_merge_vals,table,
                       {begin1:{end2:_}}),
     'else':table},

    This is a switch dict:

    {_:(dct_merge_vals,table,
                       {begin1:{end2:_}}),

    The _ key tests whether the result of the last expression is True.  If it is,
    we run dct_merge_vals on the table and a new JSON of form 

    {begin1:{end2:lhs}}

    Because dct_merge_vals adds values to the embedded dictionaries, this allows the
    table to contain a new lhs JSON, indexed by begin1 and end2.

    'else':table},

    Otherwise, return the table as-is.

    Now, we go to the main returned value:

    [(apply_partition,),init_table,partitions],

    This is a reduce of the closure function we created.  init_table is the starting
    value, applied to seq.  partitions is also called on seq, and apply_partition
    performs the reduce over these partitions.

    Basically, the reduce goes over each partition, sees if there is an lhs that can
    be added to the table, and adds it to the table if it can.  Otherwise, it just
    returns the table, and the same thing happens with the next partition.

    It is important to note that, because pype dict manipulations do not guarantee
    imutability, the reduce is not generating a new copy of the table with each 
    partition, but rather an altered version of the original table.
    '''
    def apply_partition(table,partition):

        begin1=partition['begin1']
        end1=partition['end1']
        begin2=partition['begin2']
        end2=partition['end2']

        return p( table,
                  (get_lhs,begin1,begin2,end1,end2,_,grammar),
                  {_:(dct_merge_vals,table,
                                     {begin1:{end2:_}}),
                   'else':table},
                )

    return p( seq,
              [(apply_partition,),init_table,partitions],
            )


def parse(seq,grammar):
    '''
    This is the main function.

    (get_or_false,(apply_partitions,_,grammar),
                  0,
                  lenf - 1),

    First, we run apply_partitions on seq.  Then, we check the resulting table to
    see if there is an element in the table indexed by 0 and the last index of the 
    string.  If there is, this expression returns that element, otherwise it returns
    false.

    {_:_['tree'],
     'else':'No Valid Parse'}

    Remember, _ as a key in a switch dict is evaluated for its truth value.  So if 
    the get_or_false returns False, we know the parse is unsuccessful, and we return
    'No Valid Parse'.  Otherwise, we return the tree of the parse, which will be

    ['S', ['NP', ['Det'], ['N']], ['VP', ['V'], ['NP', ['Det'], ['N']]]]
    '''
    return p( seq,
              (get_or_false,(apply_partitions,_,grammar),
                            0,
                            lenf - 1),
              {_:_['tree'],
               'else':'No Valid Parse'}
            )

 
if __name__=='__main__':

    seq=['Det','N','V','Det','N']
    grammar=read_grammar(GRAMMAR_STRING)
    p=parse(seq,grammar)

    pp.pprint(p)
