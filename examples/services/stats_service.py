'''
Shows how pype can be seamlessly integrated into Flask services to build microservices.
'''
from flask import Flask,request,jsonify
from pype import pype as p
from pype import _
from statistics import mean,stdev
from pype.vals import lenf

app = Flask(__name__)

@app.route('/mean_sum_and_std',methods=['POST'])
def mean_sum_and_std():
    '''
    Line-by-line:

    request.get_json(force=True),

    Boilerplate to extract the JSON from the request.

    _['numbers'],

    Extract the 'numbers' field from the JSON.

    {'mean':mean,
     'sum':sum,
      'std':{lenf <= 2:'Not computed',
             'else':stdev}}

    This is a dict build.  Since the last argument is a list of numbers, we can
    call the mean function on this list of numbers, and assign it to the key 'mean'.
    We do the same with the sum function.  

    The standard deviation, however, requires at least 3 values.  Therefore we have
    a switch dict which tests if the list has at least 3 numbers.  Remember, lenf is
    a PypeVal, whose operators are overriden to produce a LamTup.  This will be 
    compilable by the Python interpreter, but the pype interpreter will evaluate it
    as an expression.  It simply means, "the length of the list of numbers is less or
    equal to 2", in which case we return a message 'Not computed'.  Otherwise, we
    run the stdev function on the list of numbers, and assign it to 'std'.  

    jsonify

    This converts the resulting JSON into a response that Flask can return to the 
    client.  
    '''
    return p( request.get_json(force=True),
              _['numbers'],
              {'mean':mean,
               'sum':sum,
               'std':{lenf <= 2:'Not computed',
                      'else':stdev},},
              jsonify)


if __name__=='__main__':

    app.run(host='0.0.0.0',port=10004,debug=True)
