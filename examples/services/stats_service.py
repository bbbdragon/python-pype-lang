'''
Shows how pype can be seamlessly integrated into Flask services to build microservices.
'''
from flask import Flask,request,Response,jsonify
from pype import pype as p
from statistics import mean,stdev
from pype.vals import lenf

app = Flask(__name__)

@app.route('/mean_sum_and_std',methods=['POST'])
def mean_and_std():

    return p( request.get_json(force=True),
              _['numbers'],
              {'mean':mean,
               'std':{lenf <= 2:'Not computed',
                      'else':stdev},
               'sum':sum},
              jsonify)


if __name__=='__main__':

    app.run(host='0.0.0.0',port=10004,debug=True)
