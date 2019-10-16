# Pype

## What and Why?

In the winter of 2017, I was a run-of-the-mill Python Data-Scientist/Code Monkey/Script Kiddie, rocking pandas, scikit-learn, numpy, and scipy.  I began to get bored of Python's imperative style, especially a particularly nasty anti-pattern that appears across many Python scripts and Jupyter notebooks.  What happens is, I'm applying a whole bunch of operations to a single variable:
```
df=pd.read_csv('something.csv')
df=df[columnList]
df.dropna()
...
result=get_result_finally(df)
```
It was then, on a particular NLP-related project, that I discovered Clojure, and its ->> macro.  Functional programming was something extremely powerful for me.  I felt as if I switched from a bee-bee gun to an Uzi ... no, a gatling gun.  Before FP, difficult, snarling problems only got angrier as I shot at them.  Now, with the pull of a trigger, they vanished into a peaceful, quiet, red mist.  

But I found another dilemna.  Switching languages in the office is a big no-no, and even if I wanted to use Clojure I still needed Python's extremely mature libraries, embedded in microservices that the main Clojure app called through HTTP.  So I started to code functionally in Python.  Here's how pype came about.

I realized that a series of transformations on a data structure could be implemented in Python as a reduce, so I could build a function, pype, to take a starting value and apply functions to it in succession:
```
from functools import reduce

def pype(accum,*fArgs):

  return reduce(lambda accum,f:f(accum),fArgs)
  
add1=lambda x: x+1
mult5=lambda x:x*5
pype(2,add1,mult5)
15
```
Then, I realized I could do manipulations of dictionaries and lists, so long as I defined the arguments as lambdas.  Let's say I had the following list:
```
ls=[{"name":"bob","age":32},{"name":"susan","age":25},{"name":"joe","age":23},{"name":"mike","age":23}]
```
Let's say I wanted to build a dictionary whose keys were ages rounded down to 10 and whose values were lists of names - in other words, who was in their twenties, thrities, etc.  This would look like `{30:["bob"],20:["susan","joe","mike"]}`.  In imperative Python, using defaultdict I could do this as:
```
from collections import defaultdict

aggregation=defaultdict(lambda:list())

for js in ls:

  age,name=js['age'],js['name']
  roundedTo10=int(age/10)
  aggregation[roundedTo10].append(name)
```
Using the original pype function, it would be:
```
from functools import reduce

def add_to_ls_dct(dct,js):

  age,name=js['age'],js['name']
  
  dct[age].append(name)
  
  return dct


pype( ls,
      lambda ls:[{*js,'age':int(js['age']/10)} for js in ls],
      lambda ls:reduce(add_to_ls_dct,ls,{}),
      lambda dct:{k:[js['name'] for js in v] for (k,v) in dct.items()}
     )
```
Now, we are starting to get functional, but we are not quite at pype yet.  First, I'm noticing that the first expression is a map over every JSON in ls.  So, I could write a function called round_age:
```
from functools import reduce

...

def round_age(js):

  js['age']=int(js['age']/10)
  
  return js
  

pype( ls,
      lambda ls:[round_age(js) for js in ls],
      lambda ls:reduce(add_to_ls_dct,ls,defaultdict(lambda:list())),
      lambda dct:{k:[js['name'] for js in v] for (k,v) in dct.items()}
     )
```
But at this point, the Python notation on the lambda was just a bit too verbose.  So I told the pype function that, whenever it saw a function in square brackets, it would apply that function to every element of the previous iterable structure:
```
pype( ls,
      [round_age],
      lambda ls:reduce(add_to_ls_dct,ls,defaultdict(lambda:list())),
      lambda dct:{k:v['name'] for (k,v) in dct.items()}
     )
```
But wait, why did round_age have to be its own function?  Maybe I could automate the dictionary alteration, by using something similar to Clojure's assoc.  So I built an expression called _assoc, which would associate a key in the dictionary to a value:
```
from pype import _assoc as _a

js={"name":"bob"}

pype(js,
     _a('age',42)) => {"name":"bob","age":42})
```
This _assoc takes the dictionary and adds a key-value pair into that dictionary.  If the key is already in the dictionary, the value is overwritten with the new vale.  So let's re-define round_age to only do the calculation:
```
def round_age(js):

  return int(js['age']/10)
 
pype( ls,
      [_a('age',round_age)],
      lambda ls:reduce(add_to_ls_dct,ls,defaultdict(lambda:list())),
      lambda dct:{k:v['name'] for (k,v) in dct.items()}
     )
```
round_age applies to every JSON in ls.  But what if we just wanted round_age to take an integer as a value?  We'd need a notation to access a value of the JSON by key:
```
def round_age(age):

  return int(age/10)
 
pype( ls,
      [_a('age',(round_age,_['age']))],
      lambda ls:reduce(add_to_ls_dct,ls,defaultdict(lambda:list())),
      lambda dct:{k:[js['name'] for js in v] for (k,v) in dct.items()}
     )
```
Now, the expression _a('age',(round_age,_['age'])) says, "extract the 'age' value from the JSON, evaluate round_age on it, and assign the resulting value to 'age' in the JSON.  But wait, why even enclose the numerical computation in a function?  Could we just specify it in this new language?
```
pype( ls,
      [_a('age',(int,_['age']/10))],
      lambda ls:reduce(add_to_ls_dct,ls,defaultdict(lambda:list())),
      lambda dct:{k:[js['name'] for js in v] for (k,v) in dct.items()}
     )
```
We have overridden the / operator to produce an expression which is interpretable by pype.  So we have pypified the map entirely.  Let's move onto the reduce.  We want to build a dictionary which aggregates every user by the decade of their age.  First, we define a function to perform the reduce on a defaultdict: 
```
def add_age_to_dct(dct,js):

  dct[js['age']].append(js['name'])
  
  return dct
  
pype( ls,
      [_a('age',(int,_['age']/10)],
      [(add_age_to_dct,),defaultdict(lambda:list())],
      lambda dct:{k:[js['name'] for js in v] for (k,v) in dct.items()}
     )
```
[(add_to_ls_dct,),defaultdict(lambda:list()] means, we iterate over the jsons, and build a dictionary using add_to_ls_dct.  Because the dictionary is a defaultdict, it will automatically add a list to a key that hasn't been inserted yet.  Luckily, however, I've written a library of helpers for these aggregation operations, merge_ls_dct_no_key.  This deletes a key from the JSON, and uses that value as a key in the new dictionary:
```
from pype.helpers import merge_ls_dct_no_key

pype( ls,
      [_a('age',(int,_['age']/10))],
      (merge_ls_dct_no_key,_,'age'),
      lambda dct:{k:[js['name'] for js in v] for (k,v) in dct.items()}
     )
```
_ refers to the previous value, and is sort of an "identity function", or placeholder for merge_ls_dct_no_key, since this function takes two arguments.

In the final step, we want to iterate through every JSON in the list values, and extract the 'name' value.  We can do this by running another map.  When a map runs on a dictionary we apply the expression to the values.  For clarity, we could use the build_pype function to loop through the list and extract the name value from the JSON:
```
from pype.helpers import merge_ls_dct_no_key
from pype import build_pype as bp

names=bp([_['name']])

pype( ls,
      [_a('age',(int,_['age']/10))],
      (merge_ls_dct_no_key,_,'age'),
      [names]
     )
```
In [_['name']], the enclosing square brackets mean "go through the list and apply the enclosing expression".  We know that this is a list of JSON's, each with a 'name' field, so we extract that field using _['name'].  However, I've recently gotten rid of the AND filter, so now you can use [[]] to iterate through lists embedded in dictionaries:
```
pype( ls,
      [_a('age',(int,_['age']/10))],
      (merge_ls_dct_no_key,_,'age'),
      [[_['name']]]
     )
```
Or if you really wanted to get crazy:
```
pype( ls,
      (merge_ls_dct_no_key,[_a('age',(int,_['age']/10)],'age'),
      [[_['name']]]
     )
```
It was this process that turned pype from a simple reduce function into something much more expressive.

You may say this is "syntactic sugar".  I hate the expression "syntactic sugar".  Sugar is something you don't need.  Sugar rots your teeth.  Sugar makes you a diabetic.  You sprinkle sugar in your tea at the weekly Princeton University English Department faculty meeting, listening politely to the Dean's passive-aggressive comments about your latest novel.  The metaphor seemed to imply that more concise ways of expressing an idea were bad for you, that if you aren't thinking in terms of "for(int i=0; i <= LENGTH; i++){ ...", you aren't a real programmer.  Here's a little secret - to every programmer, every other programmer is not a real programmer.  We need, collectively, to get over it.

I didn't want "syntactic sugar".  Sugar doesn't change things deeply, make you see things differently.  No, motherfucker, I wanted "syntactic plutonium".    

So I decided to create what I call "pseudo-macros", or "fArgs" - syntactically valid Python expressions which are, in an of themselves, no more than meaningless native Python data structures - lists, tuples, and dictionaries, mostly - but that, when used as arguments to a certain function, perform common FP operations.

This also is why pype can't be called a real programming language.  A pype expression compiles in python, but is then interpreted to run code, so the strategy for interpretation is to examine, with if-thens, the structure and content of the data structure.  Later, I added a just-in-time optimizer which could eventually convert a function returning a pype expression into a function returning the result of a series of native Python expressions, by using AST.   

Pype is distributed under the MIT license.

# Requirements

Pype uses Python3.6 or above.

# Installation

## Using Pip3

You can install pype simply by typing:
```
pip3 python-pype-lang
```
Ensure you are running under root if you do not have proper permissions.  

## From Source

Clone this repo, and cd into `python-pype-lang`.  To install on your local machine, under root, run:

```
cd pype
pip3 setup.py install
```
To re-install, you will need to run the following script from `python-pype-lang`:
```
./reinstall_from_source.sh
```
which will execute, under sudo, the following commands:
```
pip3 uninstall pype
pip3 setup.py install
```
To re-install, you may need to remove the `egg-link` file in your `dist-packages` directory, as root:
```
rm /usr/local/lib/python3.6/dist-packages/pype.egg-link 
```
Now you are ready to test pype in Python3:
```
>>> from pype import pype
>>> add1=lambda x: x+1
>>> mult2=lambda x: x*2
>>> pype(1,add1,mult2)
4
```
# Examples

Before wading into the documentation, it may be a good idea to look at the `examples` directory to get a feel for how pype really works.  Everything is explained blow-by-blow, and I'd recommend you start programming by copy-pasting some of these examples.

A full tour of the language is available in `examples/tour.py`, which runs major types of pype expressions and explains the results.  It is best to start here.

Other examples demonstrate how to implement recursion in pype, and how to build simple microservices in the language, including Machine Learning services:

* recursive quicksort - `examples/quicksort.py`
* recursive Fibonacci - `examples/fibonacci.py`
* purely functional implementation of the CYK parsing algorithm - `examples/cyk.py`
* JSON aggregation - `examples/json_examples/aggregations.py` This script will familiarize you with useful JSON manipulations that Pype excels at. `examples/json_examples/numpy_aggregate.py` demonstrates how to use the numpy_helpers
library to get a performance boost by doing aggregation and computation with numpy.
* statistics service - `examples/services/stats_service.py` This script runs a Flask service that computes the sum, mean, and standard deviation of a group of numbers.  First, you must install `examples/services/service_requirements.txt`.  After the server is run, it can be tested with `examples/services/test_stats_service.sh`.  
* classifier service - `examples/services/classifier_service.py` This script runs a Flask service that runs a Random Forest classifier.  It is useful if you want to deploy lightweight machine learning microservices.  First, you must install `examples/services/service_requirements.txt`.  After the server is run, it can be tested with `examples/services/test_classifier_service.sh`. 
To run any of these files from a command line, just type in the quoted command at the beginning of the file.  For example, `quicksort.py` can be run by typing:
```
python3 quicksort.py
```
In addition, there is an example of a Docker container, described in `examples/services/Dockerfile`, which will run the classifier service.  Assuming you have docker on your machine, you can run this with the script `examples/services/run_docker.sh`.  This means that you can readily deploy a pype microservice whenever you want, wherever you want.  You can test it with `test_classifier_service.sh`.

# FAQ

* "Is Pype Fast"

Interpreted pype isn't very fast.  Optimized pype runs as fast as regular Python, because it is.  But also, ask yourself something - you're using Python.  You're not programming microprocessors for toasters in C.  Does it really matter if your program runs in 3 seconds instead of 2?

* "Is Pype Turing-Complete?"

Like I really fucking care.  But seriously, CS shouldn't get in the way of programming.

* "What's wrong with LISP?  What's wrong with Clojure?  What's wrong with Haskell?"

Don't get me wrong, I love these languages.  They're awesome.  But ... try to convince an employer to allow you to use these languages.  With pype, you can say you use Python.  

There is a good LISP library in Python called hy, although seems to have some perfomance issues.  Pype will never be Lisp, ever.  To paraphrase the Zefiro Anejo motto, "hasta el repl, es una obra de arte".  Lisp is a work of art.  Lisp is Mozart.  Use it if you can.  Or use pype.

I think there are three main benefits to using pype over these .  First, you have the richness of Python (pandas, numpy, scikit-learn, various Neural Network libraries) at your fingertips, without having to enclose them in microservices. Second, you can embed pype into any python code you want.  Thirdly, I've found that the expressions for maps, reduces, filters, etc. are actually more concise than many LISP or Clojure expressions.

Why is conciseness valuable?  When you're programing, there's the thought, and there's the code.  Most of programming is going through the mental overhead of translating thought into code.  More verbose languages require more overhead.  But the problem is, you think more slowly, because you try a new idea, translate/implement, try another idea, translate/implement, until you get to the right idea and the right implementation.  And, half the time, your thinking is wrong.  

Because of the implementation's succinctness, debugging pype reduces to two problems - getting the syntax right and getting the thought right.  In other words, it's the difference between thinking for 15 minutes and coding for 18 hours or coding for 30 minutes and thinking for 24 hours.  Or you can program C++ at an investment bank.  It's your life.    

* "Is pype readable?"

One way I evaluate a coding style is to write a piece of code and then revisit it several weeks later.  How easy is it to figure out what you're doing?  With C++ or Java, forget it.  I notice when I come back to something written in pype, there's very little overhead trying to re-understand something.

Maybe other developers will complain about your using pype, but don't take it personally.  Office developers take about as much interest in one anothers' code as 3-year-olds take in one anothers' fingerpainting.  Besides, if they can't understand what a map, reduce, or filter is, should they really be developing?  You'll get your work done 10x faster, anyway, so the bosses will love you - or fire you for being too productive.

But this isn't an advertisement.  I genuinely do not care if you use pype or not - it works for me, not so well for others.  And, in huge amounts, the hyper-concise notation can get you lost.  See below on how to make your code maintainable.  

* "Can I build microservices in pype?"

Heck yes you can!  I just told you about the Dockerfile, gosh!!!  Pype was designed for rapid (and rabid) implementation of microservices.  You can see several examples of microservices in the `examples/services` directory.  Since pype excells at transforming JSON's, a routing funciton can simply take the request JSON, make the necessary transformations, and send it back.  When you apply the `optimize` decorator, you'll find that these services are both performant and scalable.  The small Dockerfile lets you Dockerize a service to deploy on AWS Fargate and other production-type server environments.  

By the way, optimized pype and gunicorn are best of friends.  Vote for Pedro.

* "Can you dynamically generate pype code"

Theoretically, yes, you can, because fArgs are just native Python, so you could generate your fArgs programmatically somehow, and then feed them to pype as varargs.  The real question is, can you use pype itself to generate these expressions.  At this point, I am not sure.  I am working on a "quote" fArg, which prevents the fArg from being evaluated by the interpreter.  This is necessary for situations where you have functions that pass other functions as arguments - pype as described above would evaluate those functions on the accum first.  But I have not tried this.  I'm not a world-moving genius like John McCarthy (although my Mom's name is McCarthy, so I guess her side of the family isn't all cops, salesmen, and real estate dealers), but more to the point, pype arose naturally out of my need to write programs faster, rather than a theoretical concern, so I went at the things I needed and wanted before the things that were theoretically important.    

# Overview

The main function in pype is called `pype`, and it consists of two sets of parameters, the start value and the fArgs:

`def pype(startVal,*fArgs): ...
`

The start value is the initial value, which we call "accum", and the fArgs are consecutive operations on this value.  So, if we had a function `add1=lambda x: x+1`, we could perform functional composition on the starting value, where `<=>` means "is functionally equivalent to":

`pype(1,add1,add1,add1) <=> add1(add1(add1(1))) <=> 4`

This is nothing special, and can be implemented with a reduce.  However, it turns out that an fArg can be a wide range of expressions, as long as they are syntactic Python3 according to the interpreter.  I was able to implement the following types of operations:

* mirrors - an identity function which returns the accum.
* index args - when the accum is a sequence, accessing any of the first 4 values of the accum.
* maps - Appyling an fArg to each element of an iterable.
* reduces - Taking an iterable, which applies an fArg to update an accumulated value.
* filters - Taking all elements of an iterable which statisfy the conditions.
* lambdas - A shorthand for applying a function to several bound variables and accumulator-specific expressions.
* indexes - Accessing values of list and dictionary accums.
* swtich dicts - Retruns values based on different conditions applied to the accum.
* dictionary operations - Building dictionaries from the accum, adding key-value pairs, deleting keys from dictionaries.
* do expressions - For classes with methods that do not return a value, we can run the code and then return the object.
* list operations - Building lists from the accum, appending items, extending items, concatenation.
* embedded pypes - Specifying pypes within an fArg.

In addition, there are two types of objects, Getter and PypeVal, which convert basic Python expressions into fArgs, which can then be interpreted by pype.

# fArgs

Here we define the fArgs according to a grammar.  We use the following notation:

* `fArg` is any fArg specified below.
* `fArg,+` means "one or more fArgs, seperated by commas".
* `fArg,*` means "zero or more fArgs, seperated by commas".
* `fArg?` means "zero or one fArgs".
* `fArg1`,`fArg2`, etc. refer to the first, second, third fArgs.
* `|` means an OR.
* `<` and `>` bracket an expression, so `<x|y>` means "x or y".
* `hashFArg` means "an fArg which is hashable (not containing a list or dictionary)".
* `boolFArg` means "an fArg which is evaluated as a truth value."
* `hashBoolFArg` is an fArg that is both a `boolFArg` and a `hashFArg`.
* `accum` refers to the starting value of a pype function, if the fArg is the first, or the result of the last application of the fArg.
* `expression` refers to a syntactically evaluable Python expression or variable.
* We refer to lists as `[...]`, tuples as `(...)`, and dictionaries as `{...}`.
* We refer to fArgs by their names.
* `<=>` means "functionally equivalent to/gives the same result", so `pype(1,add1) <=> add1(1)` means "`pype(1,add1)` is functionally equivalent to `add1(1)`".

## Callables

A callable is any callable function or callable object in Python3.

~~~~
from pype import pype

add1=lambda x:x+1

pype(1,add1) <=> add1(1) <=> 2
~~~~

## Mirrors

`_`

A mirror simply refers to the accum passed to the expression.  It must be explicitly imported from pype, since it overrides the `_` placeholder in Python3.  If you would like to use both, you can import `__`, a double-underscore, but I find the single underscore is much cleaner.

~~~~

from pype import pype,_,__

pype(1,_) <=> 1
pype(1,__) <=> 1
~~~~

Mirrors are instances of the `Getter` object, which will be relevant in our discussion of object lambdas, indexes, and xendis.

## Index Arg

`<_0|_1|_2|_3|_4|_last>`

If an index arg is defined as `_n`, we access the n-th element of the accum.  The accum must be a list, tuple, or other type of sequence.  n only goes up to 4, and must be explicitly imported:
```
from pype import pype,_0

pype([1,2,3,4,5],_0) <=> [1,2,3,4,5][0] <=> 1
```
The `_last` index arg accesses the last element of the sequence:
```
pype([1,2,3,4,5],_last)
```
Index Args are instances of the `Getter` object, which will be relevant in our discussion of object lambdas, indexes, and xendis.

Currently, pype does not allow you to create your own index-arg, and should just be used as a shorthand for often-used list and tuple access expressions.

## Maps

`[fArg]`

Maps apply apply the fArg to each element in the accum if it is a list, tuple, or other type of sequence, or each value of the accum if it is a dictionary or other type of mapping.

```
pype([1,2,3],[add1]) <=> [pype(1,add1),pype(2,add1),pype(3,add1)] <=> [add1(1),add1(2),add1(3)] <=> [2,3,4]
pype({3:1,4:2,5:3},[add1]) <=> {3:pype(1,add1),4:pype(2,add1),5:pype(3,add1)} <=> {3:add1(1),4:add1(2),5:add1(3)} <=> {3:2,4:3,5:4}
```
If you would like to apply a mapping to both the keys and values, you can use the helper function `dct_items` in `pype.helpers`, which gets the items of a dictionary:
```
from pype.helpers import dct_items

def key_value_string(keyValuePair):
  return f'key is {keyValuePair[0]}, value is {keyValuePair[1]}'
  
pype({3:1,4:2,5:3},dct_items,[key_value_string]) <=> ['key is 3, value is 1','key is 4, value is 2','key is 5, value is 3'] 
```
## Reduces

`[(fArg1,),<expression|fArg2>,<expression|fArg3>]`

This is a reduce on an iterable accum, where `fArg1` is a binary function applied to an accumuled value and an element of the accum, `<expression|fArg2>` is the starting value, and `<expression|fArg3>` is the iterable:
```
sm=lambda accumulatedValue,element: accumulatedValue+element

pype([1,2,3],[(sm,)]) <=> 1 + 2 + 3 <=> 6
```
If the accum is a sequence, then `fArg` is applied to the elements of that sequence.  If accum is a mapping, `fArg` is applied to the values of that mapping.

`<expression|fArg2>` refers to the optioonal starting value.  If it is an expression, then that expression is the starting value:

```
pype([1,2,3],[(sm,),6]) <=> 12 + 1 + 2 + 3 <=> 18
```

If it is `fArg2` then this `fArg` is first evaluated and then given as the starting value:
```
pype([1,2,3],[(sm,),len]) <=> len([1,2,3]) + 1 + 2 + 3 <=> 3 + 1 + 2 + 3 <=> 9
```
## Filters

`{hashBoolFArg}`

The accum is a sequence or mapping.  If the accum is a sequence, the filter operates on all elements of the sequence, and returns a list.  If it is a mapping, the filter operates on all values of the mapping, and returns a dictionary.

Because the expression uses a set, you must ensure that your fArgs are hashable - if they contain lists or dictionaries, you should wrap them using `build_pype`.

The filter returns all values in the sequence or mapping for which any fArgs can be evaluated as true:
```
gt1=lambda x: x>1
eq0=lambda x: x == 0
ls=[0,-1,2,3,1,9]
pype(ls,{gt1},{eq0}) <=> [el for el in ls if gt1(el) or eq0(el0)] <=> [el for el in ls if el > 1 or el == 0] <=> [0,2,3,9]
```
Note that when there is only one fArg, the expression is equivalent to an AND filter.

## Lambdas 

`(<callable|fArg>,<expression|fArg>,+)`

Lambdas replace the cumbersome syntax of lambdas in Python3.  The first element of a lambda is a callable or an object lambda which returns a callable.  The other elements are arguments to this callable.  If these arguments are fArgs, they are evaluated against the accum:
```
sm=lambda x,y:x+y
pype(1,(sm,_,3)) <=> sm(1,3)
pype(1,(sm,(sm,_,3),_)) <=> sm(pype(1,(sm,_,3)),pype(1,_)) <=> sm(sm(1,3),1) <=> sm(4,1) <=> 5
```
The fact that lambdas can contain other fArgs makes them very expressive.  Imagine if we wanted to take a list, copy it, add 1 to each element of the copy, and concatenate that copy with the original list, and then concatenate that with a list of zeroes which is as long as the original list, and then multiply every element of that list by 3.  Using imperative Python3, this would be:
```
from operator import add # we use this instead of the '+' sign
ls1=[1,2,3,4]
ls2=[el+1 for el in ls]
ls3=[0]*len(ls1)
x=ls1 + ls2 + ls3
y=[el*3 for el in x]
```
Let's do it in pype:
```
from operator import mul # the '*' operator

pype([1,2,3,4],
    (add,_,(add,[add1],(mul,[0],len))),
	[(mul,3,_)]) 
```
It's still a bit unclear, because `add` is binary.  Also, notice that lambdas replicate Polish notation in Lisp - (+ 1 1), etc.  And we can do this quite well with functions in the operator module.  However, `_` is a `Getter` object, and most Python operators, when applied to `Getter` and `PypeVal` objects, will evaluate as lambdas.  This is done by the Python interpreter, so that lambdas are always given as fArgs to the pype:
```
_ + 1 <=> (add,_,1)
pype(3,_ + 1) <=> pype(3,(add,_,1)) <=> 4
_ * 3 <=> (mul,_,3)
pype(3, _ * 3) <=> pype(3,(mul,_,3)) <=> 9
pype([1,2,3],lenf * 3) <=> pype([1,2,3],(mul,len,3)) <=> 9
```
So we can rewrite the above as:
```
lenf=PypeVal(len)

pype([1,2,3,4],
      _ + [add1] + [0] * lenf, 
      [_ * 3])
```
## Indexes

`idx=[<<expression|fArg>+]|.expression|fArg>`
`_idx`

Or indices if you want to be a snob about it.  These take a sequence or a mapping as an accum.  If the accum is a sequence, then each `<expression|fArg>` must evaluate to an integer.  If the accum is a mapping, it must evaluate to a key of the mapping:
```
ls=[1,2,3,4]
pype(ls,_[0]) <=> ls[0] <=> 1
dct={1:2,3:4}
pype(dct,_[3]) <=> dct[3] <=> 4
```
If there are multiple `[<expression|fArg>]`, then we evaluate them one at a time:
```
ls=[[1,2,3],[4,5,6]]
pype(ls,_[0,1])) <=> ls[0][1] <=> 2
```
If the indexed object is a dictionary and the key is not in the dictionary, the expression evaluates as False.  Similarly,
if the indexed object is a list and the index is too high for the list, the expression evaluates as False.  This imitates Clojure's returning nil when an indexed element is not found in a container:
```
ls=[[1,2,3],[4,5,6]]
pype(ls,_[3,1])) <=> ls[3][1] <=> False
```
```
dct={1:2,3:{4:5}}
pype(dct,_[3,4])) <=> dct[3][4] <=> 5
pype(dct,_[3,6])) <=> dct[3][6] <=> False
```
Splices are also available, although they do not evaluate as indexes:
```
ls=[0,1,2,3]
pype(ls,_[:2]) <=> [0,1]
```
And, fArgs are permitted as well:
```
from pype.vals import PypeVal

lenf=PypeVal(len)
ls=[1,2,3,4]
pype(ls,_[lenf - 1]) <=> ls[len(ls) - 1] <=> ls[4 - 1] <=> ls[3]
```
You can also use dot notation for more legibility:
```
d={'a':1,'b':2}

pype(d,_.a) => 1
pype(d,_.b) => 2
```
Also note that indexing is used to access fields of objects:
```
class Obj:
  def __init__(self,val):
    self.val=val
    
o=Obj(1)

pype( o,
      _.val) => 1 
```
### Indices and Callables
When the index returns a callable, there are two possibilities.  If the index is the first element of a lambda expression, then the callable is called on the arguments of a lambda:
```
funcs={'sum':sum,'add1':add1}

pype( funcs,
      (_.sum,1,2)) => 3 
```
If the index is anywhere else, the callable will be evaluated on the accum:
```
def add_to_a(dct):
   dct['a']+=1
   return dct
   
d={'sum':sum,'add_to_a':add_to_a,'a':1,'b':2}

pype( d,
      (_.sum,ep(_.add_to_a,_.a),_.b)) => 4
```
This functionality is useful when you want to call a list of functions on the same data structure:
```
funcs=[add1,add2,add3,add4]
x=1
pype( funcs,
      [(_,x)]) => [2,3,4,5] 
```
It is also useful when you want to call an object method, and this object method is not in the first position of the lambda, the method gets called on the accum:
```
class Obj:
  def __init__(self,val):
    self.val=val
  def add1():
    return self.val+1
o=Obj(1)

pype( o,
      _.add1) => 2 
```
Or when it is in the first position of a lambda:
```
class Obj:
  def __init__(self,val):
    self.val=val
  def add1():
    return self.val+1
  def add(x):
    return self.val + x
    
o=Obj(1)

pype( o,
      (_.add,2)) => 3 
```

## Xednis

`<sequence|mapping>.[<expression|fArg>+]`

"xedni" is the word "index" spelled backwards.  The first value in the expression is a sequence or mapping, and the remaining `[expression|fArg]` expressions access an element from that value.  Multiple `[expression|fArg]` expressions apply consecutively:
```
ls=[1,2,3,4]
lsV=PypeVal(ls)
pype([0,3],[lsV[_]]) <=> [ls[0],ls[3]] <=> [1,4]
ls=[[1,2,3],[4,5,6]]
pype([0,1],[lsV[_,1]]) <=> [ls[0][1],ls[1][1]] <=> [2,5]
```
## Switch Dicts

`{<hashFArg|expression>:<fArg|expression>,+,'else':<fArg|expression>}`

These mimic the swtich/case statements in many languages.  Here's how they work:

1. The swtich dict has keys, each one of which is either a hashable fArg or an expression, and one of which must be 'else'.
2. If the accum is equal to a key that is an expression, then we select that value.
3. If the accum is not equal to a key that is an expression, then every key that is an fArg is evaluated against the accum.  We select the value corresponding to the last fArg to be evaluated as true.
4. If neither (2) nor (3) are successful, we select the value corresponding with "else".
5. Once we select a value from (2), (3), or (4), we return that value if it is an expression, or evaluate it against the accum if it is an fArg.

This will make more sense if we demonstrate it:
```
pype(1,{1:"one",2:"two","else":"Nothing"}) <=> "one"
pype(2,{1:"one",2:"two","else":"Nothing"}) <=> "two"
pype(3,{1:"one",2:"two","else":"Nothing"}) <=> "nothing"

pype(3, {_ > 2: "greater than two", 2: "two", "else" : _}) <=> pype(3, {(gt,_,2): "greater than two", 2: "two", "else" : _}) <=> "greater than two"
pype(2, {_ > 2: "greater than two", 2: "two", "else" : _}) <=> pype(2, {(gt,_,2): "greater than two", 2: "two", "else" : _}) <=> "two"
pype(4, {_ > 2: "greater than two", 2: "two", "else" : _}) <=> pype(4, {(gt,_,2): "greater than two", 2: "two", "else" : _}) <=> 4
```
We evaluate every fArg key in order, so only the value for the last evaluated fArg is returned:
```
pype(3, {_ > 2: "greater than two", _ < 4 : "less than four", "else" : _}) <=> "less than four"
```
### Switch Dict Macros
There are several functions which return a switch dict that follows a given, commonly used pattern:
```
_if(cond,expr) => {cond:expr,'else':_}
_iff(cond,expr) => {cond:expr,'else':False}
_ifp(cond,*fArgs) => {cond:_p(*fArgs),'else':_}
_iffp(cond,*fArgs) => {cond:_p(*fArgs),'else':False}
```
## Do expression

`_do(objectCallable)`

This is for instances where objects have methods that change the object, but do not return a value.  `pandas` has a lot of these, such as `dropna`:

```
import pandas as pd
... here df is a pandas dataframe ...
value=df.dropna()

print(value) <=> None
```
So, `_do` runs the function and returns the object.  Note that the object must be the accum:
```
pype(df,_do(_.dropna)) <=> df after we run dropna on it.
```

## List Build

`_l(<expression|fArg>,+)`

This creates a new list, eith either an expression or an evaluated fArg:
```
from pype import _l

p([1,2],_l(_0+8,_1+10)]) <=> [9,20]
```
These are often used when we want to transform the keys and values of a dictionary, in conjunction with index args, `dct_items` and `tup_dct`, the last of which builds a dictionary from a list of tuples or 2-element lists:
```
from python.helpers import dct_items,tup_dct

pype({1:2,3:4},
     dct_items,
     [_l(_0+5,_1+10)],
     tup_dct) 
<=> {6:20,8:40}
```

## List Append 

`_append(<expression|fArg>,+])`

This extends a list with either an expression or an evaluated fArg:
```
from pype import _append

p([1,2],_append(3,4)) <=> [1,2,3,4]
```

## List Concat 

`_concat([<expression|fArg>,+])`

This concatenates two lists, either expressions or fArgs.

```
from pype import _concat

p([1,2],_concat(_,[3,4]) <=> [1,2,3,4]
```

## Dict Build

`_d(<<expression1|fArg1>,<expression2|fArg2>>,*) | {<expression|hashFArg>:<expression|fArg>,+}`

This builds a dictionary.  If we use the `_d(..)` syntax, we supply key-value pairs consecutively, ensuring that the evaluation of any fArg for a key is hashable:
```
from pype import _d as db

pype(2,db(1,_+1,3,_+3)) <=> {1:2+1,3:2+3} <=> {1:3,3:5}
```
If you only have one fArg expression in the build expression, that fArg will be the key for the accum in the new dictionary:
```
pype(2,db('two')) <=> pype(2,db('two',_)) <=> {'two':2}
```
If the raw dictionary syntax is used, we must ensure that the dictionary does not contain the key "else", otherwise it will be evaluated as a switch dict:
```
pype(2,{_+1:_+3,_*4:_*3}) <=> {2+1:2+3, 2*4:2*3} <=> {3:5, 8:10}
```

## Dict Assoc

`_assoc(<<expression1|fArg1>,<expression2|fArg2>>,+)`

We insert one or more key-value pairs into the accum, where accum is a mapping, in the same way as Dict Build:
```
from pype import _assoc as a

pype({1:2},a(3,4,5,6)) <=> {1:2,3:4,5:6}
```

A commonly used shorthand for assoc is `_a` - `import _assoc as _a`.
## Dict Merge
`_merge(<mapping|fArg>)`

This merges a mapping or an fArg that returns a mapping with the accum, which should also be a mapping:
```
from pype import _merge

pype({1:2},_merge({3:4})) <=> {1:2,3:4}
```
A commonly used shorthand for assoc is `_m` - `import _merge as _m`.
## Dict Dissoc
`_dissoc(<expression|fArg>,+)`

This removes keys specified by `<exppression|fArg>,+` from the accum, which must be a mapping:
```
from pype import _dissoc as d

pype({1:2,3:4},d(1)) <=> {3:4}
```
A commonly used shorthand for assoc is `_d` - `import _dissoc as _d`, although this overrides the `_d` for dict builds, so be careful.  I like to use `_db` for dict build, and `_d` for `dissoc`.  

## Embedded Pype
`_p(fArg,+)`

This embeds a pype expression in an fArg.  The accum passed to the embedding fArg is also passed to the embedded pype:
```
from pype import _p as ep

pype([1,2,3,4,5,6],{"number greater than 3":ep({_ > 3},len), "number less than three":ep({_ < 3},len])})
<=> {"number greater than 3": 3, "number less than 3": 2}
```

## Quotes
`Quote(<fArg|expression>)`

Sometimes you may have functions that take other functions as arguments.  Lets say you had:
```
def add1(x):
  return x+1
  
def apply_func(ls,f):
  return [f(el) for el in ls]
```
There is a problem with the following statement:
```
pype( ls,
      (apply_func,_,add1))
```
`add1` would be applied to ls, rather than being passed as an argument to `apply_func` as it should.  To fix this, we enclose it in a Quote object:
```
from pype.vals import Quote as q
pype( ls,
      (apply_func,_,q(add1)))
```
Ideally, I would like Quote to work on any fArg, so that we could do things like dynamic code injections - getting into LISP macro territory.
# Other Features

## PypeVals

You have noticed expressions such as `_ > 3` can appear in strange places, such as keys for dictionaries.  That is because pype overrides the operators and translates this expression into a data structure called a LamTup, which can then be evaluated as an fArg. To do this, however, at least one element in the expression must be a PypeVal.  `_` is a PypeVal, for instance, as is `_0`, as are many other things.  A PypeVal overrides most of the operators for expressions and then generates a LamTup, which the interpreter evaluates.  So that means that an expression must have a PypeVal in it for this to happen.  You can convert variables into PypeVals by simply declaring a PypeVal instance around them:
```
from pype.vals import PypeVal as v

lists=[[1,2,3,4],
       [4,5,6],
       [2,3],
       [1,2,3,4,5,6,7,8,9]]

pype(lists,{v(len) > 3}) 
<=> [[1,2,3,4],
     [4,5,6],
     [1,2,3,4,5,6,7,8,9]]
```
By the way, this use of `len` as a PypeVal is so common that it is included in `pype.vals` as `lenf`.

The only unfortunate exception is boolean operators and `in` expressions, which cannot be overriden by Python.  Instead, use the `~` operator for NOT, the `&` operator for AND, the `|` operator for OR, and the `>>` operator for `in`.  Because of operator precedence, you will need to enclose these statements in parentheses, but this is a small inconvenience:
```
pype(lists,{(lenf > 3) & (lenf < 5)}) 
<=> [[1,2,3,4],
     [4,5,6]]
```
## `build_pype`

This builds a callable function from a pype expression.  It is especially useful for embedded maps, as de saw above:
```
from pype import build_pype as bp

value_multiply=bp([_['value'],_*10])

dctLS=[{'name':'car','value':2000},
       {'name':'apple','value':3},
       {'name':'orange','value':5},
       {'name':'cherry','value':1}]

pype(dctLS,value_multiply) <=> [20000,30,50,10]
```
Right now I am deprecating this feature, as it tends to clutter your code.

## Pype Helpers

`pype.helpers` is a module containing many helpful operations on lists and dictionaries.  We have already seen `dct_values` and `tup_dct`, but there are several others that are useful, only a few of which we will cover here (most of the functions are one-liners, so you can just browse the code to learn all of them).

### `tup_ls_dct`

This takes a list of key-value tuples and builds a dictionary of the form `{k1:[el1,..],...}`, where list elements are all values that correspond with a single key:
```
tup_ls_dct([(1,2),(1,3),(4,5),(4,8),(4,9)]) => {1:[2,3],4:[5,8,9]}
```

### `merge_ls_dct(dctLS,key)`

`dctLS` is a list of dictionaries, and `key` is a key that is in all these dictionaries.  It returns an aggregation of the dictionaries by key:
```
merge_ls_dct([{'name':'bobo','payment':20},{'name':'bob','payment':30},{'name':'bob','payment':50},{'name':'susan','payment':10}],'name')
=> {'bobo':[{'name':'bobo','payment':20}],
    'bob':[{'name':'bob','payment':30},{'name':'bob','payment':50}],
    'susan':[{'name':'susan','payment':10}])
```

`merge_ls_dct_no_key` does the same thing, except it deletes the key from the dictionaries.  This is helpful especially when sending out large lists of JSON's via HTTP - where string processing can become a performance bottleneck:
```
merge_ls_dct_no_key([{'name':'bobo','payment':20},
                     {'name':'bob','payment':30},
		     {'name':'bob','payment':50},
		     {'name':'susan','payment':10}],
		     'name')
=> {'bobo':[{'payment':20}],
    'bob':[{'payment':30},{'payment':50}],
    'susan':[{'payment':10}])
```
The usefulness of these two functions becomes more apparent when we show them with pype:
```
from pype import pype
from pype.helpers import merge_ls_dct_no_key

dctLS=[{'name':'bobo','payment':20},
       {'name':'bob','payment':30},
       {'name':'bob','payment':50},
       {'name':'susan','payment':10}]
       
pype(dctLs,
     (merge_dct_ls,_,'name'),
     [_['payment']]) 
<=> {'bobo':[20],'bob':[30,50],'susan':[10])
```
### `sort_by_key(ls,key,rev=False)`

This sorts a list of dictionaries by the key provided.  `rev` is just the `reverse` variable in `sorted`:
```
dctLS=[{'name':'bobo','payment':20},
       {'name':'bob','payment':30},
       {'name':'bob','payment':50},
       {'name':'susan','payment':10}]

sort_by_key(dctLS,'payment') =>
[{'name':'susan','payment':10},
 {'name':'bobo','payment':20},
 {'name':'bob','payment':30},
 {'name':'bob','payment':50}]
```
### `sort_by_index(ls,index,rev=False)`

In this case, `ls` is a list of tuples or lists, and `index` is just an integer for the index:
```
ls=[(1,4),(-1,5),(2,3)]
    
sort_by_index(ls,0) => [(-1,5),(1,4),(2,3)]
sort_by_index(ls,1) => [(2,3),(1,4),(-1,5)]
```
# Optimization

Pype is interpreted, which means that a pype call goes through the list of fArgs, identifies the type of fArg it is, and then evaluates this.  You will quickly find that this can be a serious performance bottleneck in long lists or dictionaries.  To address this, I built a decorator, `optimize`, which evaluates pype only once, and then rebuilds the function using abstract syntax trees.  Because these AST's prefer the most optimized Python operations on collections (dict and list comprehensions), this can often lead to a performance boost of 1-2 orders of magnitude.

I would recommend you apply the optimize decorator to all your pype functions - and soon I plan to take out the pype interpreter entirely, as now there are two implementations of pype - the interpreter and the optimizer.    

Currently, `optimize` only runs on the returned pype call in a function:

```
from pype import pype
from pype.optimize import optimize

@optimize
def optimized(ls):
  return pype(ls,
              [_+3],
	      [_*4])
```
As of today, optimized pype only covers a subset of fArg types:

* callables
* mirrors
* index args
* filters
* lambdas
* indices
* maps
* reduces
* switch dicts
* dict assocs
* dict dissocs
* dict merges
* list builds
* dict builds
* do expressions
* embedded pypes
* quotes

The optimizer is a work in progress, so it is best to first ensure your program runs in interpreted pype, and apply the `optimize` decorator to each function, testing along the way.

One nice thing about the optimizer is that you don't have to explicitly declare PypeVals when you want to override operators.  For example, the function:
```
import PypeVal as v

def double_len(ls):

  return p( ls,
            v(len)*2) 
```
can be written as:
```
@optimize
def double_len(ls):

  return p( ls,
            len*2) 
```
You will find examples of how this can de-clutter your code in `examples/quicksort.py` and `examples/fibonnaci.py` - for example, one implementation of quicksort contains the following code:
```
@optimize
def qs3_opt(ls):
    pivot=middle(ls)

    return p( ls,
              _if(len,(qs3,{_ < pivot}) + [pivot] + (qs3,{_ > pivot}))
            )
```
`(qs3,{_ < pivot}) + [pivot] + (qs3,{_ > pivot})` contains no explicit PypeVal declarations.  We can can see that this gives us an incredible amount of expressive power.
# Tips for Good Pype

## Style

I don't know why, but I always found the traditional writing order of Chinese, from top-to-bottom, somehow very beautiful.  Pype reflects this (and perhaps, subconsciously, my admiration for the elegant simplicity of Classical Chinese art), because it encourages you to always separate your fArgs by line:
```
from pype import pype as p

def process_list(ls):
 return p(ls,
          [_+1],
	  {_ > 2},
	  len,
	 )
```
The real value of this, though, is that debugging is much easier, because all you need to do is put `#` before each line, and evaluate the expression fArg by fArg.
```
from pype import pype as p

def process_list(ls):
 return p(ls,
          [_+1],
	  #{_ > 2},
	  #len,
	 )
```
By the way, while we are on the topic of Chinese writing - in "The Karate Kid", the scrolls for "rule number 1: use karate for defense only, never for attack" actually read, in Chinese, "kong shou wu xian shou", which means, literally, "empty kand (karate) not first hand" - or, "karate is not the first hand".  So much more eloquent and concise than the English.  A pype programmer is an office drone on the outside, theoretically writing in Python.  But, like a martial arts master, although they humbly go through the world and have infinite patience for the fumblings and bloated code of others, they never provoke, they never antagoinze, but they always leave behind little amounts of virtuous kickassery in a world of wrongness.   

## Feel it? Fuck it ... func it!

By "fuck it" I mean, in the Big Lubowsky sense, "fuck it ...", "don't worry about it".  The contributors of the pype repository do not in any way encourage innappropriate sexual behavior with your own code.  So don't get any ideas, you pathetic dork.  

Generally, the process of pype programming starts with a large pype expression - in fact, concisely defining program logic is pype's superpower.  As the expression gets longer, you move functionality to other funcitons.  But it's very important to keep each function small, no more than 10-20 lines or so, so you see the entire program logic. 

I do not subscribe to the philosophy of "let the function do its own work", that if a function is only called once, it shouldn't be a function.  That leads to functions that are dozens of lines, which are a nightmare to deal with.  I think a function's primary purpose is to compartmentalize a thought, and expand that thought once you're ready.  The optimizer's upcoming inliner will make remove any performance problems that come from this.

## Scoping
Because the Python interpreter doesn't allow you to refer to unnamed variables, pype doesn't have an equivalent of `let` in Clojure, where you can create scopes on the fly.  To compensate for this I often used dict builds to define an accum which was, in fact, a scope for the succeeding fArg:
```
from pype import pype as p
from pype.val import lenf

def ls_times_itself(ls):
 return p(ls,
 	  [_+2],
	  {_ < 4},
          {'newLen':lenf*2,
	   'ls':_},
	  _.ls*_.newLen,
	 )
```
Pretty awesome, but be careful - it leads to a lot of bloat.  When you can, define your variables in the function body before the pype expression:
```
from pype import pype as p

def ls_times_itself(ls):
 sz=len(ls)*2
 return p(ls,
          [_+2],
	  {_ < 4},
	  _*sz,
         )
```
Much cleaner.

## Mixing Python and Pype
The whole point of Pype is to allow you to program functionally while not having to give up Python's awesome libraries.  So when and where you want, mix mix mix.

For hyper-fast numerical processing, I often find writing functions in imperative numpy and then using pype to define the overall program logic is the most effective.  But I'd like to add a module of numpy helpers.

## Loops within loops
After getting rid of the AND filter, [[]] can now be used to run loops on embedded lists or dictionaries:
```
ls=[[1,2,3,3],[2,2]]

p(ls,[[_+1]]) <=> [[2,3,4,4],[3,3]]
```
You can also use `build_pype`, but this actually makes your code quite messy quite fast: 
```
from pype import build_pype as bp

ls=[[1,2,3,3],[2,2]]
add1=bp([_+1])

p(ls,[add1]) <=> [[2,3,4,4],[3,3]]
```
When you are doing two embedded loops, [[]] is fine.  However, after this, I'd recommend enclosing the embedded functionality in a new function or build_pype:
```
ls=[[[1,2],[3,3]],[[2,2]]]

pype(ls,[[[_+1]]]) <=> [[[2,3],[4,4]],[[3,3]]]
```
Concise but confusing, so you might want to just "feel and func this":
```
inner_add1=bp([_+])

pype(ls,[[inner_add1]])
```
## Immutability

Unfortunately, for performance reasons, we cannot ensure immutability.  This is because many of the dictionary operations act on the original dictionary passed to pype, rather than a copy of it.  Unlike the ultra-light lists and dictionaries of Clojure, Python simply cannot remain performant while creating new dictionaries or lists with every expression.  Therefore, if you are going to call pype more than once on the same data structure, you should use a deepcopy to ensure you are working on the same data.
```
from copy import deepcopy

js1={....}
js2=deepcopy(js1)

val1=some_pype_func(js1)
val2=some_other_pype_func(js2)
```
Howevwer, pype's natural habitat is a microservice, so you're going to see/write a lot of code like this:
```
from pype import pype as p
from pype import _d as db # dict build
from flask import request, jsonify

@app.route('/add',methods=['POST'])
def add():

   return p( request.get_json(force=True),
             _.numbers,
	     sum,
	     db('sum'),
	     jsonify,
	   )  
```
Within the scope of the routing function, you're not going to need a lot of immutability anyway.
# Conclusion

You could do worse.  You probably have.  Use pype.
