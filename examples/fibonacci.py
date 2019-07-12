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
    return p( n,
              {_ <= 1:_,
               'else':v((fib,_-1))+(fib,_-2)},
            )



if __name__=='__main__':
            
    print(f'Fibonacci')

    for i in range(10):

        print(f'Fibonacci of {i} is {fib(i)}')

