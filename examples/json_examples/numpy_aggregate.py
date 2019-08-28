'''
python3 numpy_aggregate.py expenses.json

This demonstrates three ways to aggregate data - the naive python way, the pure
pype way, and the numpy aggregation way.  

THe point of this excercise is to demonstrate the expressive power of pype.
It can also serve as practical advice if you want to get a performance boost by 
bringing numpy into the picture.
'''
from pype import pype as p
from pype import _,_0,_1,_p
from pype.helpers import *
from pype import _assoc as _a
from pype import _dissoc as _d
import json
import pprint as pp
import sys
from copy import deepcopy
from statistics import mean,stdev
from pype.vals import lenf
from pype.vals import PypeVal as v
from pype.time_helpers import *
import datetime as dt
from dateutil.parser import parse
from pype.numpy_helpers import *
from collections import defaultdict

def sum_by_month_imperative(js):
    '''
    This is just a pure imperative python algorithm which sums all expenses by month.
    '''
    expenses=js['expenses'] # Extract the field from JSON.
    
    for expenseJS in expenses: # Iterate through the JSON's and add a month field.

        expenseDate=parse(expenseJS['date'])
        expenseMonth=dt.datetime(year=expenseDate.year,
                                       month=expenseDate.month,
                                       day=1)
        expenseJS['month']=expenseMonth
    
    # Create a field keyed by month strings in format YYYY-MM-DD.
    mergedByMonth=defaultdict(lambda:list())

    for expenseJS in expenses:

        month=expenseJS['month']
        monthString=month.strftime("%Y-%m-%d")

        mergedByMonth[monthString].append(expenseJS)

    # Now we do the sums of the amounts in the value lists.
    monthSums={}

    for (monthString,ls) in mergedByMonth.items():

        amounts=[js['amount'] for js in ls]
        monthSums[monthString]=sum(amounts)

    return monthSums


def sum_by_month(js):
    '''
    Line-by-line:

    _['expenses'],

    Extract the 'expenses' field from the JSON.

    [_a('month',(date_string_to_month_string,_['date']))],

    Because it is a list, add a string for month.  These date-string-to-month-string
    mappings are cached in pype.time_helpers.  If the date string is '2019-02-15',
    its month string is '2019-02-01'.  

    This gets around the object creation necessary for datetime parsing, which becomes
    a performance bottleneck for large data volume.

    (merge_ls_dct_no_key,_,'month'),

    Aggregate the JSON's by month, eliminate the 'month' key for each JSON.

    [[_['amount']]],

    The value is a dictionary keyed by the month string, with lists of JSON's as
    values.  Because each JSON contains an integer amount, we iterate through each
    list and extract this integer amount.  The result is a JSON keyed by month strings,
    with lists of integers as values. 

    [sum],

    Now, we sum these values.  
    '''
    return p( js,
              _['expenses'],
              [_a('month',(date_string_to_month_string,_['date']))],
              (merge_ls_dct_no_key,_,'month'),
              [[_['amount']]],
              [sum],
            )  


def sum_by_month_numpy(js):
    '''
    Now, we throw numpy into the mix.  

    [_a('month_int',_p(_['date'],
                       date_string_to_month_string,
                       month_string_to_int))],

    Instead of adding a month string, we add a month integer, which is an integer
    derived from the string of concatenated year,month, and day values.  '2019-02-01'
    would be turned into 20190201.  This done by cache lookups in pype.time_helpers:

    _p(_['date'],
       date_string_to_month_string,
       month_string_to_int))

    date_string_to_month_string looks up the month string, as described above.
    month_string_to_int maps this month string to an integer, as described above.

    (zip_ls,[_['month_int']],[_['amount']]),

    We create a list of tuples containing the month integer and the amount.  Notice
    that we are using two maps on the JSON list - [_['month_int']] creates a list
    of month intetegers, and [_['amount']] creates a list of amounts. zip_ls is a 
    helper that takes the zip of two lists and converts the result into a list.  

    np.array

    Cast the list in an array with two columns, the first for the month integers and
    the second for amounts.
    
    aggregate_by_key

    This is a function from pype.numpy helpers which returns three things:

    1) A matrix whose i-th row is all the values corresponding with the i-th key.
       the matrix is padded with zeros so that lists of varying length can fit into
       it.  
    2) A list of keys, where the i-th key corresponds with the i-th row of (1).
    3) A list of counts for the keys, where the i-th count is the count of the i-th
       key.

    (zip,_p( _1,
            [int_to_month_string]),
            (sum_by_row,_0)),
    
    Notice we are using zip instead of zip_ls, because the following tup_dct can 
    take a zip object, whereas numpy.array requires an explicit list.

    _p( _1,
        [int_to_month_string]),

    _1 takes the second element in the tuple produced by aggregate_by_key, which is
    the month integers. [int_to_month_string] iterates through these keys and converts
    them backs to month strings.

    (sum_by_row,_0)

    _0 is the matrix containing all the amounts, with the i-th row corresponding
    with the i-th key in _1.  sum_by_row just sums the rows of this vector, so now
    we have a zip over tuples (month string, amount sum).  

    tup_dct

    Converts these tuples into a dictionary mapping the first element of the tuple
    to the second.
    '''
    return p( js,
              _['expenses'],
              [_a('month_int',_p(_['date'],
                                 date_string_to_month_string,
                                 month_string_to_int))],
              (zip_ls,[_['month_int']],[_['amount']]),
              np.array,
              aggregate_by_key,
              (zip,_p( _1,
                       [int_to_month_string]),
                   (sum_by_row,_0)),
              tup_dct,
            )



if __name__=='__main__':

    js=p( sys.argv[1],
          open,
          _.read,
          json.loads,
        )
    js1=p(js,
          deepcopy,
          sum_by_month_imperative)
    js2=p(js,
          deepcopy,
          sum_by_month)
    js3=p(js,
          deepcopy,
          sum_by_month_numpy)
    
    print('Original JSON is:')
    pp.pprint(js)
    print('*'*30)
    print('Output of imperative implementation is:')
    pp.pprint(js1)
    print('*'*30)
    print('Output of pure pype implementation is:')
    pp.pprint(js2)
    print('*'*30)
    print('Output of numpy-aggregated pype implementation is:')
    pp.pprint(js3)
