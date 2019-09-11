'''
python3 quicksort.py
'''
from pype import _if
from pype import pype as p
from pype import _
from pype import _concat as _c
from pype.helpers import middle
from pype.vals import lenf,l
from pype.optimize import optimize

def qs1(ls):
    '''
    Here is a verbose implementation of recursive quicksort.  Here's the blow-by-blow:
    
    pivot=middle(ls)

    This just takes the middle element of the list, if there is one.

    {lenf == 0:_,

    This is a switch dict which returns the ls if it is empty.

    'else':_c((qs1,{_ < pivot}),
              [pivot],
              (qs1,{_ > pivot}))},

    otherwise it calls quicksort recursively on everything below and above the pivot, 
    and concatenates the results with the pivot in the middle.  _c is the list 
    concatenation operator.

    (qs1,{_ < pivot})

    {_ < pivot} is a filter for ls, taking everything below the pivot, and recursively
    calling quicksort on this sub-list.

    [pivot] is just a list with pivot as its only element.

    {_ > pivot} is a filter for ls, taking everything above the pivot, and recursively
    calling quicksort on this sub-list.
    '''
    pivot=middle(ls)

    return p( ls,
              {lenf == 0:_,
               'else':_c((qs1,{_ < pivot}),
                         [pivot],
                         (qs1,{_ > pivot}))},
            )

def qs2(ls):
    '''
    This is a super-concise implementation of quicksort, but has the exact same
    functionality as quicksort1.  Two differences:

    {len:...
    
    Since the keys of a swtich dict are evaluated as booleans, the len function
    evaluates as bool(len(ls)).  So if the list is empty, as in len([]), this will 
    evaluate as 0, and bool(0) will be evaluated as False.  If the list is not empty,
    then the expression will be evaluated as True.  So, if the list is not empty,
    we run quicksort recursively ...

    'else':_}

    ... otherwise we return the empty list.

    l(qs2,{_ < pivot}) + [pivot] + (quicksort2,{_ > pivot}),

    We have a list concatenation, but it is implemented in a slightly different way.

    First, we cannot do:

    (qs2,{_ < pivot}) + [pivot] + (quicksort2,{_ > pivot}),

    This is because the resulting expression would not compile, since Python does not
    allow tuples to be added to lists.  We need to "trick" the Python interpreter into
    building an expression which is compileable in Python, hashable, and interpretable
    by Pype.  When a PypeVal is used adjacent to an overriden operator, it creates a
    LamTup, which the pype interpreter can evaluate.

    l is a shorthand for declaring a PypeVal for a lambda expression:

    l(qs2,{_ < pivot}) <=> PypeVal((qs2,{_ < pivot})) 

    Because this is a PypeVal, it overrides the + operator, which can be used to 
    concatenate lists.  So, if we wanted a printout of the PypeVal expression:

    l(qs2,{_ < pivot}) + [pivot]

    it would be, assuming pivot = 5: 

    L(<built-in function add>, 
      (<function qs2 at 0x7fdd3eb30f28>, 
        {L(<built-in function lt>, G('_pype_mirror_',), 5)}), 
        [5])

    In other words, call quicksort2 on every element in the list under 5, and 
    concatenate the resulting list to [5].

    The full printout for the expression would be:

    L(<built-in function add>, 
      (<built-in function add>, 
        (<function qs2 at 0x7fdd3eb30ea0>, 
          {L(<built-in function lt>, G('_pype_mirror_',), 5)}), 
          [5]), 
       (<function qs2 at 0x7fdd3eb30ea0>, 
         {L(<built-in function gt>, G('_pype_mirror_',), 5)}))

    Concatenate two lists: the first is the result of calling qs2 on every 
    element under 5 and concatenating it to [5], and the second is the result of
    calling quicksort on every element above 5.
    '''
    pivot=middle(ls)

    return p( ls,
              {len:l(qs2,{_ < pivot}) + [pivot] + (qs2,{_ > pivot}),
               'else':_},
            )


def qs3(ls):
    '''
    Here we show how to use the pype macro _if, which returns a switch dict.  So if
    we had a switch dict:

    {len:1+_,
     'else':_}

    we could restate this as:

    _if(len,_+1)

    Pype macros return evaluable pype expressions when evaluated, but keep the code
    more concise.  
    '''
    pivot=middle(ls)

    return p( ls,
              _if(len,l(qs3,{_ < pivot}) + [pivot] + (qs3,{_ > pivot}))
            )


@optimize
def qs3_opt(ls):
    '''
    This is an implementation of qs3, but with one small difference - notice that we
    do not explicitly generate a (qs3,{_ < pivot}).  This is because the optimizer
    automatically handles this case by inserting a PypeVal into the syntax tree when
    it finds a binary operator.  
    '''
    pivot=middle(ls)

    return p( ls,
              _if(len,(qs3_opt,{_ < pivot}) + [pivot] + (qs3_opt,{_ > pivot}))
            )

'''
@optimize
def qs3_opt(ls):

    pivot=middle(ls)

    return p( ls,
              _if(len,(qs3_opt,{_ < pivot}) + [pivot] + (qs3_opt,{_ > pivot}))
            )
'''

if __name__=='__main__':
            
    ls=[86,23,1,4,-1,2,5]

    print(f'Before the sort, the list is {ls}')
    print(f'The sorted list is for verbose recursive quicksort is {qs1(ls)}') 
    print(f'The sorted list is for concise recursive quicksort is {qs2(ls)}') 
    print('The sorted list is for concise recursive quicksort with macros '
          f'is {qs3(ls)}') 
    print('The sorted list is for concise recursive quicksort with macros '
          f'and optimization is {qs3_opt(ls)}') 

