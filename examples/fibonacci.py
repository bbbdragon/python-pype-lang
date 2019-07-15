'''
python3 fibonacci.py
'''
from pype import pype as p
from pype import _,_p,_0,_1,_l
from pype import _append as _ap
from pype.helpers import middle
from pype.vals import lenf
from pype.vals import PypeVal as v

def fib(n):
    '''
    Here is an example of the recursive fibonacci sequence, and a demonstration of
    how to use dict builds as scopes for the succeeding expressions.
    
    Line-by-line:

    {_ <= 1:_,
     'else':_p({'fib1':(fib,_-1),
                'fib2':(fib,_-2)},
                _['fib1']+_['fib2'])}

    This is a switch dict, as we see because it has the 'else' key.  

    _ <= 1:_,

    If n is less or equal to 1, return n.

    'else':_p({'fib1':(fib,_-1),
               'fib2':(fib,_-2)},
               _['fib1']+_['fib2'])}

    _p means we are building an embedded pype.  The first dictionary assigns fib(n-1) to
    'fib1', and the second assigns fib(n-2) to 'fib2'.  

    _['fib1']+_['fib2']

    This adds the two values in the previous dict build.  
    '''
    return p( n,
              {_ <= 1:_,
               'else':_p({'fib1':(fib,_-1),
                          'fib2':(fib,_-2)},
                         _['fib1']+_['fib2'])}
            )


if __name__=='__main__':
            
    print(f'Fibonacci')

    for i in range(10):

        print(f'Fibonacci of {i} is {fib(i)}')

