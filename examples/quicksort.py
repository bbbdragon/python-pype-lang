'''
python3 quicksort.py
'''
from pype import pype as p
from pype import _
from pype import _concat as _c
from pype.helpers import middle
from pype.vals import lenf

def quicksort(ls):

    pivot=middle(ls)

    return p( ls,
              {lenf == 0:_,
               'else':_c((quicksort,{_ < pivot}),
                         [pivot],
                         (quicksort,{_ > pivot}))},
            )

if __name__=='__main__':
            
    ls=[86,23,1,4,-1,2,5]

    print(f'Before the sort, the list is {ls}')
    print(f'The sorted list is {quicksort(ls)}') 

