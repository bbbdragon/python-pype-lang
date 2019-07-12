'''
python3 by_month_aggregation.py expenses.json

This script demonstrates how to aggregate jsons using pype.  It takes a list of 
expenses, each with a name, amount, and date.  First, it aggregates them by name,
and takes the mean and standard deviation.  Then it aggregates them by name and date,
computing the same statistics.  Finally, it aggregates them by name and month, 
computing the same statistics.  

The point of this demo is to show how easily pype can manipulate JSON's, such that the
entirety of a program can be seen as one giant JSON manipulation.
'''
from pype import pype as p
from pype import _,_0,_1,_p
from pype.helpers import merge_ls_dct_no_key
from pype import _assoc as _a
from pype import _dissoc as _d
import json
import pprint as pp
import sys
from copy import deepcopy
from statistics import mean,stdev
from pype.vals import lenf
from pype.vals import PypeVal as v
import datetime as dt
from dateutil.parser import parse

def describe_aggregation(js):
    '''
    Here, we are taking a dictionary of form {key1:[expenseJSON1,expenseJSON2,...],
    ...}, where key1 is a string, for the user id or month, expenseJSON is a json 
    containing the amount and date.  For each user, we extract the amounts, compute 
    the mean and standard deviation on these amounts, and deleting the amounts, 
    returning a dictionary of form {'expenses':[expenseJSON1,expenseJSON2,...],
    'mean':mean1,'standard_deviation':standard_deviation1}.

    Here is a description of the function, line-by-line:

    [{'expenses':_,
      'amounts':[_['amount']]}],
    
    The square brackets [] indicate we are performing a map.  When we do this on 
    dictionaries, we perform the map on the values of that dictionary, which are 
    lists of expenseJSON's associated with each key. The returned value is a 
    dicitonary with the same keys, but with the evaluated expression for each key.

    The {} without the 'else' key indicates we are building a dictionary for each list.
    The 'expenses' field is a copy of the list. 'amounts' is a list of 'amount' fields
    for each expenseJSON.  

    [_a('mean',(mean,_['amounts']))],

    Again, we are mapping over the returned dictionary, but in this case the values
    are now the dicts we have built in the last expression.  Therefore, we can add
    fields to this dict using _a, or _assoc.  In this case, we want to add a field
    called 'mean', which is the mean of 'amounts' in the dictionary.

    [_a('standard_deviation',_p( _['amounts'],
                                {lenf <= 2: 0,
                                 'else':stdev}))],

    This is a bit more complex.  We are mapping over the dictionary returned from
    the last expression, adding another field called 'standard_deviation'.  However,
    because the standard deviation cannot be computed on two or less values, we need
    to test the number of values in 'amounts'.  _p means we are embedding a pype 
    expression, that will be evaluated on the accumulated value.  _['amounts'] 
    extracts the 'amounts' field, which is a list of numbers.  Then, we test
    whether that list has two elements or less.  'lenf' is a PypeVal, an object whose
    operators are overridden to produce an object called a LamTup.  This prevents the
    Python interpreter from trying to evaluate the expression, and allows the pype
    interpreter to evaluate it.  PypeVals are formed on any python variable or
    literal, and most operators applied to a PypeVal produce a LamTup.  

    If 'amounts' has less than two elements, we return 0.  Otherwise, we return
    the standard deviation, or 'stdev' applied to 'amounts'.  

    Also note that the last expression is called a "switch dict", which is 
    distinguished by a dict build by having the key 'else'.  

    [_d('amounts')],

    Again, we are iterating over the values of the dictionary, which are dictionaries
    containing 'expenses', 'amounts', 'mean', and 'standard_deviation' fields.  
    However, we created the 'amounts' field so we could feed it to 'mean' and 'stdev'.
    We don't need it in the final output.  So we use _d, or _dissoc, to delete it 
    from the dictionary.  

    This is a common pype pattern - create a JSON to imitate a variable scope, and 
    then get rid of any variables you don't want or need.
    '''
    return p( js,
               [{'expenses':_,
               'amounts':[_['amount']]}],
              [_a('mean',(mean,_['amounts']))],
              [_a('standard_deviation',_p( _['amounts'],
                                           {lenf <= 2: 0,
                                            'else':stdev}))],
              [_d('amounts')],
            )


def aggregate_by_name(js):
    '''
    We take a json of the form {'expenses':[expenseJSON1,expenseJSON2,...]}, where
    expenseJSON1 is a dictionary of the form {'user':user1,'amount':amount1,
    'date':date1}, where user1 is a string for the user id, amount is an integer, and
    date1 is a date string of the form 'YYYY-MM-DD'.  We use 'merge_ls_dct_no_key'
    to delete the 'user' key from the embedded JSON's, since it's redundant.

    Here we go, line by line:

    (merge_ls_dct_no_key,_,'user'),

    We are taking a list of expenseJSON's, and building a dict from the 'user' field
    of these expenseJSON's, with a list of expenseJSON's associated with each user.
    
    However, unlike 'merge_ls_dct', this function deletes the 'user' key from the
    expenseJSON in the list, since it is already in the key. 

    describe_aggregation,

    We run 'describe_aggregation on the resulting dictionary.
    '''
    return p( js['expenses'],
              (merge_ls_dct_no_key,_,'user'),
              describe_aggregation,
            )


def aggregate_by_name_and_date(js):
    '''
    We take a json of the form {'expenses':[expenseJSON1,expenseJSON2,...]}, where
    expenseJSON1 is a dictionary of the form {'user':user1,'amount':amount1,
    'date':date1}, where user1 is a string for the user id, amount is an integer, and
    date1 is a date string of the form 'YYYY-MM-DD'.  We return a JSON of form:
    {user1:{date1:[{'amount',amount1},...]},...}, where amount1 is an amount.

    Line for line:

    (merge_ls_dct_no_key,_,'user'),

    This operation was described above.

    [(merge_ls_dct_no_key,_,'date')],

    [] indicates a map, so that we are merging the lists in the resulting dictionary
    by key, in this case date.  The result will be a list of jsons with only the 
    'amount' field.  

    [describe_aggregation],

    We are running 'describe_aggregation' on each of these dictionaries.  
    '''
    return p( js['expenses'],
              (merge_ls_dct_no_key,_,'user'),
              [(merge_ls_dct_no_key,_,'date')],
              [describe_aggregation],
            )


def get_month(date):
    '''
    Helper to extract month from datetime object.
    '''
    return dt.datetime(year=date.year,month=date.month,day=1)


def date_to_str(date):
    '''
    Format datetime object to string.
    '''
    return f'{date.year:04d}-{date.month:02d}-{date.day:02d}'


def aggregate_by_month(js):
    '''
    Here, we are doing the same thing as 'aggregate_by_name_and_date', only instead
    of the date we are aggregating by the month.  This means we need to convert the 
    date string into a datetime object, get the month, and convert the month back into
    a date string.  

    Line for line:

    [_a('date',(parse,_['date']))],

    For every expenseJSON object, we override the date string keyed by 'date' with
    a datetime object.

    [_a('month',(get_month,_['date']))],

    Now, because date is now a datetime object, for every date, we can get the month, 
    as a datetime object.  

    [_d('date')],

    We don't need the 'date' field anymore, so we throw it out - it clutters the final
    description.  

    [_a('month',(date_to_str,_['month']))],

    Since the 'month' field as a datetime object also clutters the final description,
    and since all we care about is whether it matches other months exactly, we 
    convert it back to a string.  

    (merge_ls_dct_no_key,_,'user'),
    [(merge_ls_dct_no_key,_,'date')],
    [describe_aggregation],

    Aggregate by user, by month, and describe the aggregation.  
    '''
    return p( js['expenses'],
              [_a('date',(parse,_['date']))],
              [_a('month',(get_month,_['date']))],
              [_d('date')],
              [_a('month',(date_to_str,_['month']))],
              (merge_ls_dct_no_key,_,'user'),
              [(merge_ls_dct_no_key,_,'month')],
              [describe_aggregation],
              
            )
  

if __name__=='__main__':

    js=p( sys.argv[1],
          open,
          _.read,
          json.loads)
    '''
    For performance, pype doesn't strictly make the object immutable.  Therefore,
    if you want to run different functions on the same object, it is best to do
    a deepcopy beforehand.  
    '''
    js1=deepcopy(js)
    js2=deepcopy(js)
    js3=deepcopy(js)

    print("Printing JS before Aggregation")

    print("Aggregating by Name")

    aggregatedByName=aggregate_by_name(js1)

    pp.pprint(aggregatedByName)

    print("Aggregating by Name and Date")

    aggregatedByNameAndDate=aggregate_by_name_and_date(js2)

    pp.pprint(aggregatedByNameAndDate)

    aggregatedByMonth=aggregate_by_month(js3)

    pp.pprint(aggregatedByMonth)
