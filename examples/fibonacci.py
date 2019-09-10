'''
python3 fibonacci.py

This section demonstrates how you can use dictionaries to build scopes for the following
functions, and certain helpers for your PypeVal expressions to make them more readable.
'''
from pype import pype as p
from pype import _,_p,_0,_1,_l
from pype import _if
from pype import _append as _ap
from pype.helpers import middle
from pype.vals import lenf,l
from pype.vals import PypeVal as v

def fib1(n):
    '''
    Here is an example of the recursive fibonacci sequence, and a demonstration of
    how to use dict builds as scopes for the succeeding expressions.
    
    Line-by-line:

    {_ <= 1:_,
     'else':_p({'fib1':(fib,_-1),
                'fib2':(fib,_-2)},
                _.fib1+_.fib2)}

    This is a switch dict, as we see because it has the 'else' key.  

    _ <= 1:_,

    If n is less or equal to 1, return n.

    'else':_p({'fib1':(fib,_-1),
               'fib2':(fib,_-2)},
               _.fib1+_.fib2)}

    _p means we are building an embedded pype.  The first dictionary assigns fib(n-1) to
    'fib1', and the second assigns fib(n-2) to 'fib2'.  

    _.fib1+_.fib2

    This adds the two values in the previous dict build.  
    '''
    return p( n,
              {_ <= 1:_,
               'else':_p({'fib1':(fib1,_-1),
                          'fib2':(fib1,_-2)},
                         _.fib1+_.fib2)}
            )


def fib2(n):
    '''
    Notice here we have a more concise description, using the l helper from pype.vals.
    We use this because we want the expression in 'else' to be passed over by the 
    Python interpreter, but evaluated by the pype interpreter.  Therefore, we need 
    to turn this into a PypeVal.  As we know, PypeVals override their operators to 
    produce LamTups, which are hashable objects that contain a pype-interpretable
    expression.  For example, the expression:

    _ <= 1

    is evaluated by the interpreter as:

    L(<built-in function le>, G('_pype_mirror_',), 1)

    This is because _ is a PypeVal, whose operator is overridden to produce a LamTup.

    LamTups are hashable, so they can be used as set elements and dictionary keys.

    In the pype interpreter, when a LamTup is encountered, a function delam is run to 
    extract a lambda expression:

    delam(_ <= 1) => delam(L(<built-in function le>, G('_pype_mirror_',), 1)) =>
    (<built-in function le>, G('_pype_mirror_',), 1)

    We can see that the pype interpreter can now evaluate the final expression:

    p(0,_ <= 1) <=> p(0,(<built-in function le>, G('_pype_mirror_',), 1)) <=> True

    However, in the case of Lambda expressions, the double parentheses makes this
    very awkward: 

    v((fib2,_-1)) + (fib2,_-2)

    So the l helper builds a PypeVal which encloses this tuple:

    l(fib2,_-1) + (fib2,_-2)
    '''
    return p( n,
              {_ <= 1:_,
               'else':l(fib2,_-1) + (fib2,_-2)})


def fib3(n):
    '''
    Finally, we have the most concise implementation.  _if(cond,expr) returns a switch
    dict:

    {cond:expr,
     'else':_}
    '''
    return p( n,
              _if(_ > 1,l(fib2,_-1) + (fib2,_-2)))


if __name__=='__main__':
            
    print(f'Dict Build Fibonacci')

    for i in range(10):

        print(f'Fibonacci of {i} is {fib1(i)}')

    print(f'Pure Fibonacci')

    for i in range(10):

        print(f'Fibonacci of {i} is {fib2(i)}')

    print(f'Pure Fibonacci (Concise)')

    for i in range(10):

        print(f'Fibonacci of {i} is {fib3(i)}')

