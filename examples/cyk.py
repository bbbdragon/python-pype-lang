'''
python3 cyk.py

This is a pype implementation of my functional implementation of the CYK parsing
algorithm in Clojure, at https://bitbucket.org/bbbdragon/bennett-cyk-demo.  It 
demonstrates that an algorithm which has traditionally been implemented as a series
of loops over a static table can be implemented functionally.  

The algorithm is described in full at: https://en.wikipedia.org/wiki/CYK_algorithm

The pype implementation implements the algorithm functionally in the same way that 
the Clojure algorithm does.  The only difference is under-the-hood.  

Because Clojure data structures are so light-weight, it can generate new structures 
with every iteration and not have any performance hits.  In this case, however, the 
same table structure is being updated with each iteration - the code is functional, but
the underlying implementation does not guarantee immutability.
'''
from pype import pype as p
from pype import _,_0,_1,_2,_l as tup
import pprint as pp
from pype.vals import PypeVal as v
from pype import _concat as _c
from pype import _assoc as a
from pype import _dissoc as d
from pype import _d as db
from pype import _merge as _m
from pype import _p as ep
from pype import Quote as q
from pype.optimize import optimize
from itertools import product
from pype.vals import lenf
from pype.helpers import *
from pype import _iff,_if,_iffp
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

@optimize
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

    [(merge_ls_dct,_,'rhs2')],

    This performs the same merge on the embeded dictionaries, producing a JSON of
    form: {rhs1:{rhs2:[{'rhs1':rhs1,'rhs2':rhs2,'lhs':lhs}],...},...}

    [[_0]]

    Since rhs1 and rhs2 are keys to single-element lists, we extract the first element
    from this list, so now our JSON is:{rhs1:{rhs2:{'rhs1':rhs1,'rhs2':rhs2,
    'lhs':lhs},...},...}

    [[_.lhs]],

    Now, we want to extract only the 'lhs' from the JSON keyed by rhs1 and rhs2, 
    producing a JSON of the form: {rhs1:{rhs2:lhs,...},...}.

    One thing to note is that this only applies to deterministic Context-Free 
    grammars, which allow only one parse for a string.  This is the case with
    programming languages, but is not the case for Natural Languages. 
    '''
    return p( grammarString,
              _.splitlines,
              {_},
              [_.split],
              [{'lhs':_0,
                'rhs1':_1,
                'rhs2':_2}],
              (merge_ls_dct,_,'rhs1'),
              [(merge_ls_dct,_,'rhs2')],
              [[_0]],
              [[_.lhs]],
            )


@optimize
def partitions(seq):
    '''
    In our strategy, we do not want to iterate over a static table, but rather
    iterate over a series of partitions.  Each partition is a JSON of the form:

    {'begin1':begin1,
     'end1':end1,
     'begin2':begin2,
     'end2':end2}

    It defines a partition of the string which the parser will evaluate to generate
    and insert new symbols.  To do this, we build a dict with the span, or length
    of the partition:

              db('spans',(range_list,1,_)), # span

    Then, we build a list of i1Begin indices:

              a('iBegin1s',ep(_.spans,
                              [(range_list,0,stLen-_)],
                              flatten_list)),

    And finally, a list of partitions, which will define where the first part of the 
    partition begins and the second part ends:

              a('partitions',ep(_.spans,
                                [(range_list,0,_)],
                                flatten_list)),

    Let's take the cartesian product of these three lists, giving us a tuple of 
    (span, iBegin1, partition):

              (cartesian,_.spans,_.iBegin1s,_.partitions),

    Cast the tuple to a dictionary:

              (zip_to_dicts,_,'span','i1Begin','partition'),

    And now we fill in i1End, i2Begin, and i2End.

              [a('i1End',_.i1Begin + _.partition)],
              [a('i2Begin',_.i1End + 1)],
              [a('i2End',_.i1Begin + _.span)],

    Delete the 'partition' field, but keep the 'span' field:

              [d('partition')],

    Get rid of any combinations where i2End is less than i2Begin, and remove 
    repeating partition JSON's:

              {_.i2Begin <= _.i2End},
              unique_dcts,

    Finally, sort this list of JSON's.  First, we sort it by 'span', so that the 
    shortest JSON's appear first.  Then, sort it by i1Begin.  This means that the
    first partitions in the list will be over two symbols:

              (sort_by_keys,_,'span','i1Begin'),

    The end result looks like this:

    [{'i1Begin': 0, 'i1End': 0, 'i2Begin': 1, 'i2End': 1, 'span': 1},
    {'i1Begin': 1, 'i1End': 1, 'i2Begin': 2, 'i2End': 2, 'span': 1},
    {'i1Begin': 2, 'i1End': 2, 'i2Begin': 3, 'i2End': 3, 'span': 1},
    {'i1Begin': 3, 'i1End': 3, 'i2Begin': 4, 'i2End': 4, 'span': 1},
    {'i1Begin': 0, 'i1End': 0, 'i2Begin': 1, 'i2End': 2, 'span': 2},
    {'i1Begin': 0, 'i1End': 1, 'i2Begin': 2, 'i2End': 2, 'span': 2},
    ...
    {'i1Begin': 3, 'i1End': 3, 'i2Begin': 4, 'i2End': 7, 'span': 4},
    {'i1Begin': 3, 'i1End': 4, 'i2Begin': 5, 'i2End': 7, 'span': 4},
    {'i1Begin': 3, 'i1End': 5, 'i2Begin': 6, 'i2End': 7, 'span': 4},
    {'i1Begin': 3, 'i1End': 6, 'i2Begin': 7, 'i2End': 7, 'span': 4}]
    '''
    stLen=len(seq)

    return p( stLen,
              db('spans',(range_list,1,_)), # span
              a('iBegin1s',ep(_.spans,
                              [(range_list,0,stLen-_)],
                              flatten_list)),
              a('partitions',ep(_.spans,
                                [(range_list,0,_)],
                                flatten_list)),
              (cartesian,_.spans,_.iBegin1s,_.partitions),
              (zip_to_dicts,_,'span','i1Begin','partition'),
              [a('i1End',_.i1Begin + _.partition)],
              [a('i2Begin',_.i1End + 1)],
              [a('i2End',_.i1Begin + _.span)],
              [d('partition')],
              {_.i2Begin <= _.i2End},
              unique_dcts,
              (sort_by_keys,_,'span','i1Begin'),
            )


@optimize
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
                        'tree':tup(_1)}}}],

    _0 refers to the index, so we are creating a list of JSON's of form 

    {index1:{index1:{'lhs':seq1,'tree':tree1}}

              [(dct_merge_vals,),{},_],

    dct_merge_vals merges two dictionaries that have embedded dictionaries as values.
    We are doing this as a reduce, with an empty dictionary, {}, as the starting value.
    '''
    return p( seq,
              (zip,(range,len),_),
              [{_0:{_0:{'lhs':_1,
                        'tree':tup(_1)}}}],
              [(dct_merge_vals,),{},_],
            )


@optimize
def get_lhs(begin1,begin2,end1,end2,table,grammar):
    '''
    This takes a table, the variables of a partition, and a grammar, and returns a 
    JSON of form {'lhs':lhs1,'tree':tree1} if there is an element in the table
    from which the grammar can derive an lhs.  

              {'rhs1':_[begin1,end1],
               'rhs2':_[begin2,end2]},

    If the sequence of keys is present in the dictionary, we return the element keyed
    by those keys.  Otherwise, we return False.

    {0:0:{'lhs':'Det','tree':['Det']}}

    then p(table,_[0,0]) will return {'lhs':'Det','tree':['Det']}.  However,
    with this particular table, p(table,_[0,1]), will return False, because
    no embedded element exists in the JSON.  We store 'rhs1' and 'rhs2' in a dict build
    because we are going to reference them in the next two lines - this how we can
    use dict builds for scoping.

              a('lhs',(get_or_false,grammar,
                                     _.rhs1.lhs,
                                     _.rhs2.lhs)),

    get_or_false has the same functionality as the indexing.  However, we use it 
    because the alternative expression:

    _a('lhs',v(grammar)[_['rhs1','lhs'],_['rhs2','lhs']),
    
    is a lot uglier.

    Now, we check the grammar to see if it has a rule in which the lhs of rhs1 is the
    first rhs, and the lhs of rhs2 is the second lhs.  We assign the result to 'lhs'
    in the main JSON.

              _iff(_.lhs,ep(a('tree',tup(_.lhs,
                                          _.rhs1.tree,
                                          _.rhs2.tree)),
                            d('rhs1','rhs2'))),

    _iff returns a switch dict: {_:fArg,'else':False}.

    Remember, in a switch dict, if the key evaluates as True, then the corresponding
    expression is evaluated and returned.  If the grammar cannot find an lhs in the
    above statement, then 'lhs' in the main JSON will be False, and we return
    False.

    Otherwise, we add an additional field, 'tree' to the main JSON, which is a list 
    containing the lhs symbol, followed by the trees for rhs1 and rhs 2, which are 
    also lists.  

    Finally, we get rid of 'rhs1','rhs2', which we don't need and return the JSON.
    '''
    return p( table,
              {'rhs1':_[begin1,end1],
               'rhs2':_[begin2,end2]},
              a('lhs',(get_or_false,grammar,
                                     _.rhs1.lhs,
                                     _.rhs2.lhs)),
              _iff(_.lhs,ep(a('tree',tup(_.lhs,
                                          _.rhs1.tree,
                                          _.rhs2.tree)),
                            d('rhs1','rhs2'))),
            )


@optimize
def apply_partition_from_grammar(table,partition,grammar):
    '''
    This applies a partition if there is a grammar rule that allows us to generate
    a new lhs.  After unpacking partition, we get a new lhs from the table, using the 
    grammar:

              (get_lhs,i1Begin,
                       i2Begin,
                       i1End,
                       i2End,
                       _,
                       grammar),

    If we are unsuccessful, then this will be False.  In the following swtich dict:

                  {_:(dct_merge_vals,table,
                                     {i1Begin:{i2End:_}}),
                   'else':table},

    The _: term means that the result of get_lhs is not False.  If it is, we return
    the table as-is.  If it is not, then we build a dictionary around the returned 
    value - {i1Begin:{i2End:_} - and then merge it into the table.
    '''
    i1Begin=partition['i1Begin']
    i1End=partition['i1End']
    i2Begin=partition['i2Begin']
    i2End=partition['i2End']
    
    return p( table,
              (get_lhs,i1Begin,
                       i2Begin,
                       i1End,
                       i2End,
                       _,
                       grammar),
                  {_:(dct_merge_vals,table,
                                     {i1Begin:{i2End:_}}),
                   'else':table},
                )


@optimize
def apply_partitions(seq,grammar):
    '''
    This is the main function to run CYK.  Notice that we create a closure function
    apply_partition in the function body.  We do this because the main iteration is a
    reduce, and a reduce takes two arguments only.  So we bind the grammar variable
    inside the closure.

    First, we want to use a closure to wrap apply_partion_from_grammar:

    def apply_partition(tb,prt):

        return apply_partition_from_grammar(tb,prt,grammar)

    We do this because the reduce only accepts functions with two arguments, the
    first for the accumulator, and the second for the next item.  Therefore,
    we want a function, apply_partition, where grammar is bound to grammar
    in the scope of the apply_partitions function.

    Now, we go to the main returned value:

              [(apply_partition,),init_table,partitions],

    First, this is the syntax for a reduce.  Let's go through it ...

    init_table returns the starting value of the table from seq:

    {0: {0: {'lhs': 'Det', 'tree': ['Det']}},
     1: {1: {'lhs': 'N', 'tree': ['N']}},
     2: {2: {'lhs': 'V', 'tree': ['V']}},
     3: {3: {'lhs': 'Det', 'tree': ['Det']}},
     4: {4: {'lhs': 'N', 'tree': ['N']}}}

    partitions generates the partition JSON's which the reduce will iterate through.

    apply_partition is the function that takes a table at a given state, takes a
    partition, and tries to update that table, depending on whether there is a 
    grammar rule that can generate a new lhs from that partition.  

    It is important to note that, because pype dict manipulations do not guarantee
    imutability, the reduce is not generating a new copy of the table with each 
    partition, but rather an altered version of the original table.
    '''
    def apply_partition(tb,prt):

        return apply_partition_from_grammar(tb,prt,grammar)

    return p( seq,
              [(apply_partition,),init_table,partitions],
            )


@optimize
def parse(seq,grammar):
    '''
    This is the main function.

    Let's walk through the returned value:

              (get_or_false,(apply_partitions,_,grammar),
                            0,
                            len - 1),

    First, we run apply_partitions on seq, as described above.  Apply partitions will
    return a table, as described above.  We want to know if there is a sequence
    of rules that can generate a parse for the entire string.  If there is, then
    for a string of five symbols, the table will contain an element at 0 and 4, 
    meaning there is a tree spanning elements 0 to 4.  If this is true, then the 
    string is grammatical.  

    get_or_false looks at the element of the table starting at 0 and ending at 
    the length of the sequence - 1.  The starting element is shown by the 0, and the
    finishing element is defined by 'len - 1', or "the length of seq minus 1".  

    Note that, because the function is optimized, we do not use the PypeVal 
    lenf instead, the optimizer makes the the necessary changes.  

    If there is no element in this table, the statement will return False.

              {_:_.tree,
               'else':'No Valid Parse'}

    The {_: evaluates if the get_or_false is False.  If it is False, then we return
    a string saying 'No Valid Parse'.  Otherwise, we return the tree, which will be

    ['S', ['NP', ['Det'], ['N']], ['VP', ['V'], ['NP', ['Det'], ['N']]]]
    '''
    return p( seq,
              (get_or_false,(apply_partitions,_,grammar),
                            0,
                            len - 1),
              {_:_.tree,
               'else':'No Valid Parse'}
            )

 
if __name__=='__main__':

    seq=['Det','N','V','Det','N']
    grammar=read_grammar(GRAMMAR_STRING)
    p=parse(seq,grammar)

    pp.pprint(p)
