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
It was then, on a particular NLP-related project, that I discovered Clojure.  Functional programming revived my enthusiasm for coding - its cleanness, its expressiveness, its elegance.  I had been using a bee-bee gun to hunt dragons, and suddenly I was given an Uzi ... no, a gatling gun!  Difficult, snarling problems that only got more angry as I pelted them with bee-bees now vanished in a quiet, peaceful, red mist.  

But if I wanted to build Clojure applications, I would have to embed Python functionality in a microservice, and make HTTP calls or use websockets.  It worked well, but I didn't like the idea of using two different languages to do two different things.  Plus, employers don't really like it when you suddenly decide to switch to a language that no one else on the team knows.  I didn't want to leave Python, because of all its great libraries, so creating my own language was out.  What to do, what to do?

So I began to explore how Python implemented certain functional programming features - reduces, maps, filters, lambdas, etc. - and was still dissatisfied.  Their syntax was cumbersome, it flooded the page, it looked awful.  It was as if Python was grudgingly throwing us a bone, but still pouted about it.  

I hate the expression "syntactic sugar".  Sugar is something you don't need.  Sugar rots your teeth.  Sugar makes you a diabetic.  You sprinkle sugar in your tea at the weekly Princeton University English Department faculty meeting, listening politely to the Dean's snippy comments about your latest novel.  The metaphor seemed to imply that more concise ways of expressing an idea were bad for you, that if you aren't thinking in terms of "for(int i=0; i <= LENGTH; i++){ ...", you aren't a real programmer.  Here's a little secret - to every programmer, every other programmer is not a real programmer.  We need, collectively, to get over it.

I didn't want "syntactic sugar".  I wanted "syntactic plutonium that ignites and in so doing shifts your productivity and awareness of the program to a new level".  

So I decided to create what I call "pseudo-macros" - syntactically valid Python expressions which are, in an of themselves, no more than meaningless lists, tuples, and dictionaries, but that, when used as arguments to a certain function, perform common FP operations.  

Over a long weekend, while my wife was consulting in Africa, I wrote pype, and I have been using it ever since.

While Pype may be challenging at first, you will soon find that it will become very easy to represent your program logic concisely and elegantly.  

If you don't think Pype is awesome, then my apologies, and you're free to not use it.  However, you are invited to suggest improvements, particularly with regards to performance.

Pype is distributed under the MIT license.

# Installation

Clone this repo and cd into the directory `pype`.  To install on your local machine, under root, run:

```
cd pype
pip3 install -e .
```

To re-install, you will need to remove the `egg-link` file in your `dist-packages` directory, as root:

```
rm /usr/local/lib/python3.6/dist-packages/pype.egg-link 
```

Now you are ready to test pype, in Python3:

```
>>> from pype import pype
>>> add1=lambda x: x+1
>>> pype(1,add1)
2
```

Now, you are ready to run the demo, which evaluates several pype expressions and shows you their output:
```
>>> from pype import demo
>>> demo()
WELCOME TO PYPE! ...
```
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
* AND filters - Taking all elements of an iterable which statisfy the AND of all truth conditions.
* OR filters - Taking all elements of an iterable which satisfy the OR of all truth conditions.
* lambdas - A shorthand for applying a function to several bound variables and accumulator-specific expressions.
* object lambdas - A shorthand for accessing methods in an object.
* indexes - Accessing values of list and dictionary accums.
* xedni's - Accessing values of bound variable lists and dictionaries, with the accums represented in the brackets.
* swtich dicts - Retruns values based on different conditions applied to the accum.
* for loops - Returns tuples of Cartesian products of iterables, or fArgs applied to these tuples.
* dictionary operations - Building dictionaries from the accum, adding key-value pairs, deleting keys from dictionaries.
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

A callable is any callable function or object in Python3.

~~~~

from pype import pype

pype(1,add1) <=> add1(1) <=> 2
~~~~

## Mirrors

`_`

A mirror simply refers to the accum passed to the expression.  It must be explicitly imported from pype.

~~~~

from pype import pype,_

pype(1,_) <=> 1
~~~~

Mirrors are instances of the `Getter` object, which will be relevant in our discussion of object lambdas, indexes, and xendis.

## Index Arg

`<_0|_1|_2|_3|_4>`

If an index arg is defined as `_n`, we access the n-th element of the accum.  The accum must be a list, tuple, or other type of sequence.  n only goes up to 4, and must be explicitly imported:
```

from pype import pype,_0

pype([1,2,3,4,5],_0) <=> [1,2,3,4,5][0] <=> 1
```

Index Args are instances of the `Getter` object, which will be relevant in our discussion of object lambdas, indexes, and xendis.

## Maps

`[fArg,+]`

Maps apply apply the sequence of fArgs to each element in the accum if it is a list, tuple, or other type of sequence, or each value of the accum if it is a dictionary or other type of mapping.

```
pype([1,2,3],[add1]) <=> [pype(1,add1),pype(2,add1),pype(3,add1)] <=> [add1(1),add1(2),add1(3)] <=> [2,3,4]
pype({3:1,4:2,5:3},[add1]) <=> {3:pype(1,add1),4:pype(2,add1),5:pype(3,add1): <=> {3:add1(1),4:add1(2),5:add1(3)} <=> {3:2,4:3,5:4}

```
If more than one fArg is specified in the map, then we apply each fArg consecutively to the accum:
```
pype([1,2,3],[add1,add1]) <=> [pype(1,add1,add1),pype(2,add1,add1),pype(3,add1,add1)] <=> [add1(add1(1)),add1(add1(2)),add1(add1(3))] <=> [3,4,5]
```

## Reduces

`[(fArg1,),<expression|fArg2>?]`

This is a reduce on an iterable accum, where `fArg1` is a binary function applied to an accumuled value and an element of the accum:
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

## Build Pype

Although this is not an fArg, it wraps a pype in a callable function:
```
from pype import build_pype

pp=build_pype(add1,add1,add1)

pp(1) <=> pype(1,add1,add1,add1) <=> 4
```

## AND Filters

`[[boolFArg,+]]`

The accum is a sequence or mapping.  If the accum is a sequence, the filter operates on all elements of the sequence, and returns a list.  If it is a mapping, the filter operates on all values of the mapping, and returns a dictionary.

The AND filter returns all values in the sequence or mapping for which all fArgs can be evaluated as true:
```
gt1=lambda x: x>1
ls=[0,-1,2,3,1,9]
pype(ls,[[gt1]]) <=> [el for el in ls if gt1(el)] <=> [el for el in ls if el > 1] <=> [2,3,9]
lt9=lambda x: x < 9
pype(ls,[[gt1,lt9]]) <=>  [el for el in ls if gt1(el) and lt9(el)]  <=> [el for el in ls if el > 1 and el < 9] <=> [2,3]
```
It is useful to note that the fArgs do not need to return truth values.  THey are simply evaluated as truth values.  That means that the map `[[_]]` means "every element in the sequence or dict which, when evaluated as a boolean, is true".  This makes this expression useful for filtering out `False` values, `None` values, `0` values, or empty sets, dictionaries, or lists:
```
ls=[2,3,4,0,[],{},set(),None,3,False]
pype(ls,[[_]]) <=> [el for el in ls if bool(el)] <=> [2,3,4,3]
```
Note there is syntactic ambiguity with a map, if, say, we wanted to apply a map of maps to a list of lists.  In such a case, the AND filter takes precedence.  If we wanted to build an expression, we would use `build_pype` instead:
```
add1ToLs=build_pype([add1])

pype([[1,2,3],[4,5,6]],[add1ToLs]) <=> [pype([1,2,3],[add1]),pype([3,4,5],[add1])] <=> [[2,3,4],[4,5,6]]
```

## OR Filters

`{hashBoolFArg,+}`

The accum is a sequence or mapping.  If the accum is a sequence, the filter operates on all elements of the sequence, and returns a list.  If it is a mapping, the filter operates on all values of the mapping, and returns a dictionary.

Because the expression uses a set, you must ensure that your fArgs are hashable - if they contain lists or dictionaries, you should wrap them using `build_pype`.

The AND filter returns all values in the sequence or mapping for which any fArgs can be evaluated as true:
```
gt1=lambda x: x>1
eq0=lambda x: x == 0
ls=[0,-1,2,3,1,9]
pype(ls,{gt1,eq0}) <=> [el for el in ls if gt1(el) or eq0(el0)] <=> [el for el in ls if el > 1 or el == 0] <=> [0,2,3,9]
```
Note that when there is only one fArg, the expression is equivalent to an AND filter.

## Lambdas 

`(<callable|object lambda>,<expression|fArg>,+)`

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
## Object Lambdas

`(mirror,string)`

An object lambda takes an object as an accum.  The string is then an attribute, either a field of the class or a member function. It evaluates in three different ways:

1. If the object lambda is not the first element of a lambda, and the string refers to a member function of the accum, then that function is called, and its value is returned:
```
pype({1:2,3:4},(_,'keys')) <=> {1:2,3:4}.keys() <=> dict_keys([1,3])

def CallMe():
  def __init__(self):
    self.me='me'
  def call(self):
    return 'hi'
  def add1(self,x):
  	return x+1
	
pype(CallMe(),(_,'call')) <=> CallMe().call() <=> 'hi'
```
2. If the object lambda is not the first element of a lambda, and the string refers to a field of the accum, then the value of that field is returned:
```
pype(CallMe(),(_,'me')) <=> CallMe().me <=> 'me'    
```
3. If the object lambda is the first element of a lambda, and the string refers to a member function of the accum, then that function is applied to the other arguments of the lambda:
```
pype(CallMe(),((_,'add1'),1)) <=> CallMe().add1(1) <=> 2
```
`Getter` and `PypeVal` objects override the `__getattr__` function to return an object lambda.  This means we can create object lambdas in the following way:
```
from pype.vals import Getter,PypeVal

_.add1 <=> (_,'add1')
_.call <=> (_,'call')
```
This makes our syntax a bit more readable:
```
pype(CallMe(),_.call) <=> pype(CallMe(),(_,'call')) <=> CallMe().call() <=> 'hi'
pype(CallMe(),(_.add1,1)) <=> pype(CallMe(),((_,'add1'),1)) <=> CallMe().add1(1) <=> 2
```
## Indexes

`(mirror,[<expression|fArg>],+)`

Or indices if you want to be a snob about it.  These take a sequence or a mapping as an accum.  If the accum is a sequence, then `[<expression|fArg>]` must evaluate to an integer.  If the accum is a mapping, it must evaluate to a key of the mapping:
```
ls=[1,2,3,4]
pype(ls,(_,[0])) <=> ls[0] <=> 1
dct={1:2,3:4}
pype(dct,(_,[3]) <=> dct[3] <=> 4
```
If there are multiple `[<expression|fArg>]`, then we evaluate them one at a time:
```
ls=[[1,2,3],[4,5,6]]
pype(ls,(_,[0],[1])) <=> ls[0][1] <=> 2
```
`Getter` and `PypeVal` objects override the `__getitem__` method to return an index:
```
from pype.vals import Getter,PypeVal

_[1] <=> (_,[1])
_[2,3] <=> (_,[2],[3])
ls=[1,2,3,4]
pype(ls,_[0]) <=> ls[0] <=> 1
ls=[[2,3,4],[1,2,3]]
pype(ls,_[1,2]) <=> ls[1][2] <=> 3
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
## Xednis

`(<sequence|mapping>,[expression|fArg],+)`

"xedni" is the word "index" spelled backwards.  The first value in the expression is a sequence or mapping, and the remaining `[expression|fArg]` expressions access an element from that value.  Multiple `[expression|fArg]` expressions apply consecutively:
```
ls=[1,2,3,4]
pype([0,3],[(ls,[_])]) <=> [ls[0],ls[3]] <=> [1,4]
ls=[[1,2,3],[4,5,6]]
pype([0,1],[(ls,[_,1]]) <=> [ls[0][1],ls[1][1]] <=> [2,5]
```
By casting the sequence or mapping in a PypeVal object, we can use the overridden `__getitem__` operator:
```
from pype.vals import PypeVal

ls=[[1,2,3],[4,5,6]]
lsV=PypeVal(ls)

lsV[_] <=> (ls,[_])

pype([0,1],[lsV[_,1]]) <=> [2,5]
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

## For Loops

`[([<fArg1|iterable1|int1>],[<fArg2|iterable2|int2>],+),<fArg3|expression3>?]`

This simulates a loop over a Cartesian product specified by `([<fArg1|iterable1|int1>],[<fArg2|iterable2|int2>],+)`.  `<fArg1|iterable1|int1>` must be an expression for an iterable or an integer, or an fArg that evaluates to an expression for an iterable or an integerThis also applies to `<fArg2|iterable2|int2>`.  If this expression is an integer, we take it as a numeric range, converting it into an iterable.  Each such expression is included in the Cartesian product.

If no `<fArg3|expression3>?` is included, then the tuples of the Cartesian product are returned.  If an expression is included, then a list, the size of the Cartesian product, is returned with that expression repeated.  If an fArg is included, then that fArg is evaluated for the elements of each tuple.  `_i` returns the first element of the tuple, `_j` returns the second element, and so on for `_k`, and `_l`.

It is much clearer if we demonstrate:
```
from itertools import product
from pype import _,_i,_j

ls=[1,2]
pype(ls,[([_],[_])]) <=> product(ls,ls) <=> [(1,1),(1,2),(2,1),(2,2)]
pype(5,[([_],[_ - 1])]) <=> product(range(5),range(5-1)) <=> [(0,-1),(0,0),...(1,-1),(1,0),(1,1)...]

pype(ls,[([_],[_]), _i + _j]) <=> [i+j for (i,j) in product(ls,ls)] <=> [1+1,1+2,2+1,2+2] <=> [2,3,3,4]

```
## List Build

`[l,<expression|fArg>,+]`

This creates a new list, eith either an expression or an evaluated fArg:
```
from pype import append

p([1,2],[l,3,_]) <=> [3,[1,2]]
```


## List Append 

`[append,<expression|fArg>,+]`

This extends a list with either an expression or an evaluated fArg:
```
from pype import append

p([1,2],[append,3,4]) <=> [1,2,3,4]
```

## List Concat 

`[append,<expression|fArg>,+]`

This concatenates two lists, either expressions or fArgs.

```
from pype import concat

p([1,2],[concat,_,[3,4]) <=> [1,2,3,4]
```

## Dict Build

`[d,<<expression1|fArg1>,<expression2|fArg2>>,+] | {<expression|hashFArg>:<expression|fArg>,+}`

This builds a dictionary.  If we use the `[d,..]` syntax, we supply key-value pairs consecutively, ensuring that the evaluation of any fArg for a key is hashable:
```
from pype import d

pype(2,[d,1, _+1,3,_+3]) <=> {1:2+1,3:2+3} <=> {1:3,3:5}
```
If the raw dictionary syntax is used, we must ensure that the dictionary does not contain the key "else", otherwise it will be evaluated as a switch dict:
```
pype(2,{_+1: _+3, _*4: _*3}) <=> {2+1:2+3, 2*4:2*3} <=> {3:5, 8:10}
```

## Dict Assoc

`[assoc,<<expression1|fArg1>,<expression2|fArg2>>,+]`

We insert one or more key-value pairs into the accum, where accum is a mapping, in the same way as Dict Build:
```
from pype import assoc

pype({1:2},[assoc,3,4,5,6]) <=> {1:2,3:4,5:6}
```

## Dict Merge
`[merge,<mapping|fArg>]`

This merges a mapping or an fArg that returns a mapping with the accum, which should also be a mapping:
```
from pype import merge

pype({1:2},[merge,{3:4}]) <=> {1:2,3:4}
```

## Dict Dissoc
`[dissoc,<expression|fArg>,+]`

This removes keys specified by `<exppression|fArg>,+` from the accum, which must be a mapping:
```
from pype import dissoc

pype({1:2,3:4},[dissoc,1]) <=> {3:4}
```

## Embedded Pype
`[_p,fArg,+]`

This embeds a pype expression in an fArg.  The accum passed to the embedding fArg is also passed to the embedded pype:
```
from pype import _p

pype([1,2,3,4,5,6],{"number greater than 3":[_p,[[_ > 3]],len], "number less than three":[_p,[[_ < 3]],len]})
<=> {"number greater than 3": 3, "number less than 3": 2}
```

# FAQ

* "Is Pype Fast"

Not really, not yet, anyway.  I'm working on trying numba decorators, caching, and redoing pype functions as AST's.  But also, ask yourself something - you're using Python.  You're not programming microprocessors for toasters in C.  Does it really matter if your program runs in 3 seconds instead of 2?

* "Is Pype Turing-Complete?"

Like I really care.  But seriously, CS shouldn't get in the way of programming.

* "What's wrong with LISP?  What's wrong with Clojure?  What's wrong with Haskell?"

Don't get me wrong, I love these languages.  They're fricking awesome.  But ... try to convince an employer to allow you to use these languages.  With pype, you can say you use Python.  

There is a good LISP library in Python called hy.  Use it if you want to.  Or use pype.

I think there are three main benefits to using pype over these languages.  First, you have the richness of Python (pandas, numpy, scikit-learn, various Neural Network libraries) at your fingertips, without having to enclose them in microservices. Second, you can embed pype into any python code you want.  Thirdly, the pseudo-macros in the language for maps, reduces, filters, etc. are actually more concise than many LISP macros.

What does this last thing mean?  When you're programing, there's the thought, and there's the code.  Most of programming is going through the mental overhead of translating thought into code.  But the problem is, you think more slowly, because you try a new idea, translate/implement, try another idea, translate/implement, until you get to the right idea and the right implementation.  And, half the time, your thinking is wrong.  

Because of succinctness, debugging reduces to two problems - getting the syntax right and getting the thought right.  You can do that, or you can program C++ at an investment bank.  It's your life.    

* "Is pype Readable?"

One way I evaluate a coding style is to write a piece of code and then revisit it several weeks later.  How easy is it to figure out what you're doing?  With C++ or Java, forget it.  I notice when I come back to something written in pype, there's very little overhead trying to re-understand something.

Maybe other developers will complain about your using pype, but don't take it personally.  Developers take about as much interest in one anothers' code as 3-year-olds take in one anothers' fingerpainting.  Besides, if they can't understand what a map, reduce, or filter is, should they really be developing?  You'll get your work done 10x faster, anyway.

You could do worse.  You probably have.  Use pype.