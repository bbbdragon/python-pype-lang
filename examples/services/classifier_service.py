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
from flask import Flask,request,jsonify
from pype import pype as p
from pype import _,_0,_1,_p
from pype import _assoc as _a
from pype import _dissoc as _d
from pype import _do
from statistics import mean,stdev
from pype.vals import lenf
from sklearn.ensemble import RandomForestClassifier as Classifier
from sklearn.feature_extraction.text import TfidfVectorizer as Vectorizer
import sys
import csv

'''
We have to use lambda to define the read function because pype functions can't yet 
deal with keyword args.
'''
read=lambda f: csv.reader(f,delimiter='|')


def train_classifier(texts,y):
    '''
    Here is a perfect example of the "feel it ... func it" philosophy:

    The pype call uses the function arguments and function body to specify 
    three variables, texts, a list of strings, y, a list of floats, and vectorizer,
    a scikit-learn object that vectorizes text.  This reiterates the adivce that you
    should use the function body and function arguments to declare your scope,
    whenever you can.  

    Line-by-line, here we go:

    {'vectorizer':vectorizer.fit,
     'X':vectorizer.transform},

    We build a dict, the first element of which is the fit vectorizer.  Luckily, the
    'fit' function returns an instance of the trained vectorizer, so we do not need to
    use _do.  This vectorizer is then assigned to 'vectorizer'.  Because iterating
    through dictionaries in Python3.6 preserves the order of the keys in which they 
    were declared, we can apply the fit function to the vectorizer on the texts, 
    assign that to the 'vectorizer' key.  We need this instance of the vectorizer to
    run the classifier for unknown texts.

    After this, we apply the 'transform' to convert the texts into a training matrix
    keyed by 'X', whose rows are texts and whose columns are words. 

    _a('classifier',(Classifier().fit,_['X'],y)),

    Finally, we can build a classifier.  _a, or _assoc, means we are adding a 
    key-value pair to the previous dictionary.  This will be a new instance of our
    Classifier, which is trained through the fit function on the text-word matrix 'X'
    and the labels vector y.

    _d('X'),

    Since we don't need the X matrix anymore, we delete it from the returned JSON,
    which now only contains 'vectorizer' and 'classifier', the two things we will
    need to classify unknown texts.
    '''
    vectorizer=Vectorizer()

    return p( texts,
              {'vectorizer':vectorizer.fit,
               'X':vectorizer.transform},
              _a('classifier',(Classifier().fit,_['X'],y)),
              _d('X'),
            )


'''
We train the model in a global variable containing our vectorizer and classifier.  

This use of global variables is only used for microservices, by the way.

Here is a line-by-line description:

sys.argv[1],
open,

Open the file.

read,

We build a csv reader with the above-defined 'read' function, which builds a csv reader
with a '|' delimiter.  I chose this delimeter because the texts often have commas. 

list,

Because csv.reader is a generator, it cannot be accessed twice, so I cast it to a list.  This list is a list of 2-element lists, of the form [label,text], where label is a 
string for the label ('1' or '-1'), and text is a string for the training text.  So an
example of this would be ['1','free herbal viagra buy now'].  

(train,[_1],[(float,[_0])])

This is a lambda which calls the 'train' function on two arguments, the first being 
a list of texts, the second being a list of numerical labels.

We know that the incoming argument is a list of 2-element lists, so [_1] is a map, 
which goes through this list - [] - and builds a new list containing only the second
element of each 2-element list, referenced by _1.  

With the first elements of the 2-element lists, we must extract the first element and
cast it to a float.  In [(float,[_0])], the [] specifies a map over the list of 
2-element lists.  (float,_0) specifies we are accessing the first element of the 
2-element list ('1' or '-1'), and calls the float function on it, to cast it to a 
float.  If we do not cast it to a float, sklearn will not be able to process it as
a label.       
'''
MODEL=p( sys.argv[1],
         open,
         read,
         list,
         (train_classifier,[_1],[(float,_0)]),
       )

app = Flask(__name__)

@app.route('/classify',methods=['POST'])
def classify():
    '''
    This is the function that is run on a JSON containing one field, 'texts', which
    is a list of strings.  This function will return a list of JSON's containing the
    label for that text given by the classifier (1 or -1), and the original text.
    Notice that, in this routing, we need access to 'texts' in (zip,_,texts).  

    Line-by-line:

    global MODEL

    We need this to refer to the model we trained at the initialization of the 
    microservice.  

    texts=request.get_json(force=True)['texts']

    This extracts the 'texts' list from the json embedded in the request.  

    MODEL['vectorizer'].transform,

    This uses the vectorizer to convert the list of strings in texts to a text-word
    matrix that can be fed into the classifier.

    MODEL['classifier'].predict,

    This runs the prediction on the text-word matrix, producing an array of 1's and
    -1's, where 1 indicates that the classification is positive (it is spam), and -1
    indicates that the classification is negative (it is not spam).

    (zip,_,texts),

    We know that the n-th label produced by the classifier is for the n-th string in
    texts, so we zip them together to produce an iterable of tuples (label,text).  

    [{'label':_0,
      'text':_1,
      'description':{_0 == 1: 'not spam',
                     'else':'spam'}}],

    Here, we are performing a mapping over the (label,text) tuples produced by the 
    zip.  For each tuple, we build a dictionary with three items.  The first is the
    label, which is numberic, either 1.0 or -1.0.  The second is the actual text
    string.  

    However, to help the user, we also include a description of what the label means:

    'description':{_0 == 1: 'not spam',
                   'else':'spam'}

    The value is a switch dict.  Since _0 is a Getter object, it overrides the == 
    operator to produce a LamTup, which Python will accept, but which the pype 
    interpreter will run as an expression.  _0 == 1 simply means, "the first element
    of the (label,text) tuple, label, is 1.  If this is true, 'description is set to
    'not spam'. Otherwise, it is set to 'spam'.  

    jsonify

    This just turns the resulting JSON, a list of dicitonaries, into something that can
    be returned to the client over HTTP.  
    '''
    global MODEL

    texts=request.get_json(force=True)['texts']

    return p( texts,
              MODEL['vectorizer'].transform,
              MODEL['classifier'].predict,
              (zip,_,texts),
              [{'label':_0,
                'text':_1,
                'description':{_0 == 1: 'not spam',
                               'else':'spam'}}],
              jsonify)


if __name__=='__main__':

    app.run(host='0.0.0.0',port=10004,debug=True)
