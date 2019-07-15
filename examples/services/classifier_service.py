'''
python3 classifier_service.py data.csv

This service runs a scikit-learn classifier on data provided by the csv file data.csv.

The idea of this is a simple spam detector.  In the file, you will see a number, 1 or
-1, followed by a pipe, followed by a piece of text.  The text is designed to be a 
subject email, and the number its label: 1 for spam and -1 for not spam.  

The service loads the csv file, trains the classifier, and then waits for you to 
send it a list of texts via the 'classify' route.  This service can be tested using:

./test_classifier_service.sh
'''
from flask import Flask,request,Response,jsonify
from pype import pype as p
from pype import _,_0,_1,_p
from pype import _assoc as _a
from pype import _do
from statistics import mean,stdev
from pype.vals import lenf
from sklearn.ensemble import RandomForestClassifier as Classifier
from sklearn.feature_extraction.text import TfidfVectorizer as Vectorizer
import sys
import csv

# We have to enclose the read function because pype functions can't yet deal with
# keyword args.
 
read=lambda f: csv.reader(f,delimiter='|')


def train(js):
    '''
    Here is a perfect example of the "feel it ... func it" philosophy:

    We didn't want to include the training process in the definition of MODEL because
    of scoping issues, so we build our own scope in a function.

    Notice we are depending on Python3.6's ordering of the dictionary to ensure that
    the vectorizer is fit, then the data vectors are generated.
    '''
    vectorizer=Vectorizer()

    return p( js['texts'],
              {'vectorizer':vectorizer.fit,
               'X':vectorizer.transform},
              _a('classifier',(Classifier().fit,_['X'],js['y'])),
            )

'''
We train the model in a global variable.
'''
MODEL=p( sys.argv[1],
         open,
         read,
         list,
         {'y':_p( [_0],
                  [float]),
          'texts':[_1]},
         train,
       )

app = Flask(__name__)

@app.route('/classify',methods=['POST'])
def classify():

    global MODEL

    js=request.get_json(force=True)

    return p( js,
              _['texts'],
              MODEL['vectorizer'].transform,
              MODEL['classifier'].predict,
              (zip,_,js['texts']),
              [{'label':_0,
                'text':_1}],
              jsonify)


if __name__=='__main__':

    app.run(host='0.0.0.0',port=10004,debug=True)
