import sys
from pype import *
from pype.helpers import *
from pype.vals import *
from pype import _,_0,_1,_i,_j
from pype import _l
from pype import _concat as _c
from pype import _append as _ap
from pype import _do

def demo():

    print("WELCOME TO PYPE!")
    print("Here are several pype expressions, with their values.  We hope that "
          "this will give you an idea of the full range of what pype can do.")
    print("In the printout, the >>> separates the topics of this tour.")
    print("The === sign encoloses two values: an optional variable definition, "
          "the expression, and right below it the evaluation of that expression. "
          "The *** sign demonstrates an equality between two expressions." )
    print("="*30)

    call_me=lambda : 1
    add1=lambda x: x+1
    sm=lambda x,y: x+y

    ##################
    # CHECKING FARGS #
    ##################

    print('>'*30)
    print('CHECKING FARGS')
    print('Here we will give you an idea of what fArgs look like.')
    print('>'*30)

    print('='*30)
    print('is_callable(call_me)')

    x=is_callable(call_me)

    print(x)

    assert(x == True)

    print('='*30)
    print('is_mirror(_)')

    x=is_f_arg(call_me)

    print(x)

    assert(x == True)

    print('='*30)
    print('is_map([add1,add1])')

    x=is_map([add1,add1])

    print(x)

    assert(x == True)

    print('='*30)
    print('is_map([add1,add1,_])')

    x=is_map([add1,add1,_])

    print(x)

    assert(x == True)

    sm=lambda x,y: x+y

    print('='*30)
    print('is_reduce([(sm,)])')

    x=is_reduce([(sm,)])

    print(x)

    assert(x == True)

    print('='*30)
    print('is_reduce([(sm,),1])')

    x=is_reduce([(sm,),1])

    print(x)

    assert(x == True)

    print('='*30)
    print('is_switch_dict({1:2,3:4,"else":5})')

    x=is_switch_dict({1:2,3:4,'else':5})

    print(x)

    assert(x == True)

    print('='*30)
    print('is_lambda((add1,_))')

    x=is_lambda((add1,_))

    print(x)

    assert(x == True)

    print('='*30)
    print('is_index((_,[2]))')

    x=is_index((_,[2]))

    print(x)

    assert(x == True)

    print('='*30)
    print('is_index((_,[2],[3],[4]))')

    x=is_index((_,[2]))

    print(x)

    assert(x == True)

    '''
    ########
    # ARGS #
    ########

    print('>'*30)
    print('ARGS')
    print('>'*30)
    
    print('args(1)')
    print(args(1))

    print('args([1,2,3])')
    print(args([1,2,3]))

    print('args({ARGS:(1,2,3)})')
    print(args({ARGS:(1,2,3)}))
    '''

    ############
    # CALLABLE #
    ############

    print('>'*30)
    print('CALLABLE')
    print('Callables are the first and most commonly used type of fArg')
    print('Here you will learn how to use callables on the initial value, '
          'or the "accum".')
    print('>'*30)

    add1=lambda x: x+1

    print('='*30)
    print('pype(1,add1)')

    x=pype(1,add1)

    print(x)
    
    assert(x == 2)

    print('='*30)
    print('pype(1,add1,add1,add1)')

    x=pype(1,add1,add1,add1)

    print(x)
    
    assert(x == 4)

    ##########
    # MIRROR #
    ##########

    print('>'*30)
    print('MIRROR')
    print("The mirror fArg is an identity function, and it evaluates to the accum. "
          "Remember, the accum is simply the preceeding value, either the first "
          "value given to the pype function or the previously evaluated fArg.")
    print('>'*30)

    print('='*30)
    print('pype(1,_)')

    x=pype(1,_)
    
    print(x)

    assert(x == True)

    print('='*30)
    print('pype(1,add1,_)')

    x=pype(1,add1,_)
    
    print(x)

    assert(x == 2)

    #############
    # INDEX ARG #
    #############

    print('>'*30)
    print('INDEX ARG')
    print("The index fArg is a shorthand for different elements of a list or other "
          "object that can be retrieved using [].  So _0 of the accum is the first "
          "element, _1 is the second element, _2 is the third element, etc.  Index "
          "args go from _0 to _4, with _last referring to the last element of the "
          "list.")
          
    print('>'*30)

    print('='*30)

    print('tup=(1,2,3)')
    print('pype(tup,_0)')

    tup=(1,2,3)

    x=pype(tup,_0)

    print(x) 

    assert(x == 1)

    print('='*30)

    print('tup=(1,2,3)')
    print('pype(tup,_1)')

    tup=(1,2,3)

    x=pype(tup,_1)

    print(x) 

    assert(x == 2)


    #######
    # MAP #
    #######

    print('>'*30)
    print('MAP')
    print("The map fArg evaluates an fArg for an iterable accum.  If the accum is "
          "list-like, the map evaluates the enclosing fArg on each element of the "
          "list.  If the accum is dict-like, the map evaluates the enclosing fArg on "
          "each *value* of the list.")
         
    print('>'*30)

    print('*'*15)
    print('add1=lambda x:x+1')
    print('pype([1,2,3,4],[add1]')

    x=pype([1,2,3,4],[add1])

    assert(x == [add1(1),add1(2),add1(3),add1(4)])

    print(x)

    print('='*30)
    print('add1=lambda x:x+1')
    print('pype([1,2,3,4],[add1]) == [add1(1),add1(2),add1(3),add1(4)]')
    print(x == [add1(1),add1(2),add1(3),add1(4)])

    print('='*30)
    print('add1=lambda x:x+1')
    print('pype({1:1,2:2},[add1]')

    x=pype({1:1,2:2},[add1])

    print(x)

    assert(x == {1:add1(1),2:add1(2)})

    print('*'*15)
    print('add1=lambda x:x+1')
    print('pype({1:1,2:2},[add1]) == {1:add1(1),2:add1(2)}')
    print(pype({1:1,2:2},[add1]) == {1:add1(1),2:add1(2)})

    ##########
    # REDUCE #
    ##########

    print('>'*30)
    print('REDUCE')
    print("The reduce fArg performs a reduce on the accum, and comes in three "
          "variations, which we will explore here.  If the accum is list-like, the "
          "reduce will iterate over each element of the accum.  If it is dict-like, "
          "the reduce will iterate over each value of the accum.")
    print('>'*30)

    print('='*30)
    print('sm=lambda x,y:x+y')
    print('pype([1,2,3],[(sm,)])')
    
    x=pype([1,2,3],[(sm,)])
    
    print(x)

    assert(x == 6)

    print('='*30)
    print('sm=lambda x,y:x+y')
    print('pype([1,2,3],[(sm,)]) == 3 + 2 + 1')

    print(pype([1,2,3],[(sm,)]) == 3 + 2 + 1)

    print('='*30)
    print('sm=lambda x:x+1')
    print('pype({1:1,2:2},[(sm,)])')
    
    x=pype({1:1,2:2},[(sm,)])
    
    print(x)

    assert(x == 3)

    print('*'*15)
    print('sm=lambda x,y:x+y')
    print('pype({1:1,2:2},[(sm,),]) == 1 + 2')
    print(pype({1:1,2:2},[(sm,),]) == 1 + 2)


    print('='*30)
    print('Now, the reduce has a starting value of 3')
    print('sm=lambda x,y:x+y')
    print('pype([1,1,1],[(sm,),3])')
    
    x=pype([1,1,1],[(sm,),3])
    
    print(x)

    assert(x == 6)

    print('*'*15)
    print('sm=lambda y,x:x+y')
    print('pype([1,1,1],[(sm,),3]) == 3 + 1 + 1 + 1')

    print(pype([1,1,1],[(sm,),1]) == 3 + 1 + 1 + 1)

    print('='*30)
    print("Now, the reduce has a starting value of 3, but we perform a transformation"
          " on the accum, [add1], before performing the reduce.")
    print('add1=lambda x:x+1')
    print('sm=lambda x,y:x+y')
    print('pype([1,1,1],[(sm,),3,[add1]])')
    
    x=pype([1,1,1],[(sm,),3,[add1]])
    
    print(x)

    assert(x == 9)

    print('*'*15)
    print('add1=lambda x:x+1')
    print('sm=lambda x:x+1')
    print('pype([1,1,1],[(sm,),3,[add1]]) == 3 + 2 + 2 + 2')

    print(pype([1,1,1],[(sm,),3,[add1]]) == 3 + 2 + 2 + 2)

    ###############
    # SWITCH DICT #
    ###############

    print('>'*30)
    print('SWITCH DICT')
    print("The switch dict is a dictionary with an 'else' key.  Please read the "
          "README.md for exact defails, but this should give you an idea of how it "
          "works.")
    print('>'*30)

    print('='*30)
    print("If the accum matches one of the keys exactly, we return the value for "
          "that key.")
    print('pype(1,{1:"one",2:"two","else":"nothing"})')

    x=pype(1,{1:"one",2:"two","else":"nothing"})

    print(x)

    assert(x == "one")

    print('*'*15)
    print('pype(1,{1:"one",2:"two","else":"nothing"}) == "one"')
    print(pype(1,{1:"one",2:"two","else":"nothing"}) == "one")

    print('='*30)
    print("If the accum does not match one of the keys exactly, and there are no "
          "fArgs in the dictionary keys, we return the 'else' value.")
    print('pype(1,{1:"one",2:"two","else":"nothing"})')

    x=pype(34,{1:"one",2:"two","else":"nothing"})

    print(x)

    assert(x == "nothing")

    
    print('='*30)
    print("Now, we are going to add some fArgs.  Remember, these fArgs are PypeVal "
          "expressions, which means they are hashable by the Python interpreter and "
          "are evaluated by the pype interpreter.")

    print('pype(1,{_ > 1:"greater 1", _ < 3:"less than three", "else":_})')

    x=pype(1,{_ > 1:"greater 1", _ < 3:"less than three", "else":_})

    print(x)

    assert(x == 'less than three')

    print('*'*15)
    print('pype(1,{_ > 1:"greater 1", _ < 3:"less than three", "else":_}) == "less than three"')

    print('='*30)
    print("If the value does not evaluate true for any fArgs, and is not equal to any "
          "of the keys, we return the 'else' value.")
    print('pype(-5,{_ > 1:"greater 1","else":_})')

    x=pype(-5,{_ > 1:"greater 1","else":_})

    print(x)

    assert(x == -5)

    print('='*30)
    print("If an fArg is in the matching value, we evaluate that fArg on the value.")

    add2=lambda x: x+2

    print('add2=lambda x: x+2')
    print('pype(5,{_ > 1:"greater 1","else":add1}')

    x=pype(5,{_ > 1:add2,"else":add1})

    print(x)

    assert(x == 7)

    print('='*30)
    
    print('pype(1,(sm,_,2))')

    x=pype(1,(sm,_,2))

    print(x)
    
    assert(x == 3)

    #########
    # INDEX #
    #########

    print('>'*30)
    print('INDEX')
    print('>'*30)

    print('='*30)

    print("Here we demonstrate the index feature, which can be used with a mirror, an "
          "index arg, or any other Getter object.")
    ls=[1,2,3,4]
    print('ls=[1,2,3,4]')
    print('pype(ls,_[0]))')

    x=pype(ls,_[0])

    print(x)
    
    assert(x == 1)

    print('='*30)
    print("This can also be used to access dictionaries by keys.")

    dct={1:2,3:4}
    print('dct={1:2,3:4}')
    print('pype(dct,_[3]))')

    x=pype(dct,_[3])

    print(x)
    
    assert(x == 4)

    '''
    Here I'm having a bit of trouble, need to fix.
    sys.exit(1)
    
    print('='*30)
    print("Now, we are going to demonstrate how to access elements of embedded lists.")
    bigLS=[[1,2,3],[2,3,4]]
    print('bigLS=[[1,2,3],[2,3,4]]')
    print('pype(bigLS,(_,[0],[1]))')

    x=pype(bigLS,_[0][1])

    print(x)

    assert(x == 2)

    print('='*30)

    print('pype(ls,(_,[(sub,(len,_),1)]))')

    x=pype(ls,(_,[(sub,(len,_),1)]))

    print(x)

    assert(x == 4)
    '''
    #########
    # XEDNI #
    #########

    print('>'*30)
    print('XEDNI')
    print('>'*30)

    print('='*30)

    print('pype(1,(ls,[_]))')

    x=pype(1,(ls,[_]))

    print(x)

    assert(x == 2)

    print('='*30)

    print('pype(1,(ls,[(add,_,1)]))')

    x=pype(1,(ls,[(add,_,1)]))

    print(x)

    assert(x == 3)

    print('='*30)

    print('pype([0,1],[(ls,[_])]')

    x=pype([0,1],[(ls,[_])])

    print(x)

    assert(x == [1,2])

    print('='*30)

    print('pype([0,1],[(ls,[(add,_,1)])])')

    x=pype([0,1],[(ls,[(add,_,1)])])

    print(x)

    assert(x == [2,3])
    
    ##########
    # LAMBDA #
    ##########

    print('>'*30)
    print('LAMBDA')
    print('>'*30)

    one=lambda: 1

    print('='*30)
    
    print('pype(0,(one,))')

    x=pype(0,(one,))

    print(x)
    
    assert(x == 1)

    print('='*30)
    
    print('pype(1,(sm,(sm,_,3),2))')

    x=pype(1,(sm,(sm,_,3),2))

    print(x)
    
    assert(x == 6)

    print('='*30)
    
    print('pype(1,(sm,(sm,_,3),2))')

    x=pype(1,(sm,(sm,_,(sm,_,5)),_))

    print(x)
    
    assert(x == 8)

    print('='*30)
    
    print('pype(1,(gt,_,0))')

    x=pype(1,(gt,_,0))

    print(x)
    
    assert(x == True)

    #################
    # OBJECT LAMBDA #
    #################
    
    class CallMe:

        def __init__(self):

            self.me="me"

        def add1(self,y):

            return y+1

        def sum(self,y,z):

            return y+z

        def hi(self):

            return "hi"

    class Call:

        def __init__(self):

            pass

        def get_call_me(self):

            return CallMe()

    print('>'*30)
    print('OBJECT LAMBDA')
    print('>'*30)

    print('='*30)
    
    print('pype(CallMe(),((_,"hi"),))')

    x=pype(CallMe(),((_,"hi"),))

    print(x)

    assert(x == 'hi')

    print('='*30)

    print('pype(CallMe(),(_,"hi")')

    x=pype(CallMe(),(_,"hi"))

    print(x)

    assert(x == 'hi')

    print('='*30)

    print('pype(CallMe(),_.hi')

    print('_.hi is really {}'.format(_.hi))

    x=pype(CallMe(),_.hi)

    print(x)

    assert(x == 'hi')

    print('='*30)
    
    print('pype(CallMe(),(_,"me"))')

    x=pype(CallMe(),(_,"me"))

    print(x)

    assert(x == 'me')

    print('='*30)
    
    print('pype(CallMe(),_.me)')

    print('_.me is really {}'.format(_.me))

    x=pype(CallMe(),_.me)

    print(x)

    assert(x == 'me')

    print('='*30)
    
    print('pype(CallMe(),(_,"add1",2))')

    x=pype(CallMe(),(_,"add1",2))

    print(x)

    assert(x == 3)

    print('='*30)
    
    print('pype(CallMe(),(_,"sum",2,3))')

    x=pype(CallMe(),(_,"sum",2,3))

    print(x)

    assert(x == 5)

    print('='*30)

    print('pype(Call(),(_,"get_call_me"),(_,"add1",2))')

    x=pype(Call(),(_,"get_call_me"),(_,"add1",2))

    print(x)

    assert(x == 3)

    print('='*30)

    print('pype(Call(),_.get_call_me,(_.add1,2))')

    x=pype(Call(),_.get_call_me,(_.add1,2))

    print(x)

    assert(x == 3)

    print('='*30)

    c={'call':Call()}

    print('Call() is callable: {}'.format(is_callable(c['call'])))
    print("pype(d,_['call'].get_call_me)")
    print(_['call'].get_call_me)

    x=pype(c,_['call'].get_call_me)

    print(x)

    print('='*30)

    ls=[Call()]

    print("pype(d,_0.get_call_me)")
    print(_0.get_call_me)
    print(delam(_0.get_call_me))
    print('is_object_lambda(_0.get_call_me) {}'.format(is_object_lambda(_0.get_call_me)))

    x=pype(ls,_0.get_call_me)

    print(x)

    #sys.exit(1)
    #print('='*30)

    #print("pype({'a':1},(_,'a'))")

    #x=pype({'a':1},(_,'a'))

    #print(x)

    #assert(x == 1)

    '''
    print('>'*30)
    print('AND FILTERS')
    print('>'*30)

    print('='*30)

    print('pype([1,2,-1,-5,7],[[(gt,_,1)]])')

    x=pype([1,2,-1,-5,7],[[(gt,_,1)]])

    print(x)

    assert(x == [2,7])

    print('='*30)

    print('pype([1,2,-1,-5,7,4,3,8],[[(gt,_,1),(lt,_,6)]])')

    x=pype([1,2,-1,-5,7,4,3,8],[[(gt,_,1),(lt,_,6)]])

    print(x)

    assert(x == [2,4,3])
    '''
    print('>'*30)
    print('OR FILTERS')
    print('>'*30)

    print('='*30)

    print('pype([1,2,3,4,5,2,2,43,4,3],{(eq,_,3),(eq,_,2)})')

    x=pype([1,2,3,4,5,2,2,43,4,3],{(eq,_,3),(eq,_,2)})

    print(x)

    assert(x == [2,3,2,2,3])

    print('>'*30)
    print('DICT BUILD')
    print('>'*30)

    x=pype(1,{_:_,'add1':add1,3:4,add1:add1})

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2})

    print('='*30)
    add1=lambda x: x+1
    print("[d,{_:_,'add1':add1,3:4,add1:add1}]")
    db=[d,{_:_,'add1':add1,3:4,add1:add1}]
    #print("is_dict_build([d,{_:_,'add1':add1,3:4,add1:add1}]) {}".format(is_dict_build(db)))

    x=pype(1,[d,{_:_,'add1':add1,3:4,add1:add1}])

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2})

    print('>'*30)
    print('DICT ASSOC')
    print('>'*30)

    x=pype(1,
           {_:_,'add1':add1,3:4,add1:add1},
           [assoc,'one','more'])

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2,'one':'more'})

    print('>'*30)
    print('DICT MERGE')
    print('>'*30)

    x=pype(1,
           {_:_,'add1':add1,3:4,add1:add1},
           [merge,
            {'one':'more',
             'and':(add1,(_,['add1']))}])

    print(x)

    assert(x == {1:1,'add1':2,3:4,2:2,'and':3,'one':'more'})

    print('>'*30)
    print('DICT DISSOC')
    print('>'*30)

    x=pype({1:2,3:4,5:6},[dissoc,1,3])

    print(x)

    assert(x == {5:6})

    print('>'*30)
    print('LIST BUILD')
    print('>'*30)

    x=pype(1,_l(add1,2,add1))

    assert(x == [2,2,2])

    print(x)

    print('>'*30)
    print('LIST APPEND')
    print('>'*30)

    x=pype([1,2,3],_ap(4,5,6))

    print(x)

    assert(x == [1,2,3,4,5,6])

    print('>'*30)
    print('LIST CONCAT')
    print('>'*30)

    print('='*30)

    x=pype([1,2,3],_c(_,[4,5,6],[7,8]))

    print(x)

    assert(x == [1,2,3,4,5,6,7,8])

    print('>'*30)
    print('FOR LOOP')
    print('>'*30)

    print('='*30)

    ls1=[1,2,3]
    ls2=[2,3,4]

    print('pype(ls1,[([_],[ls2]),(add,_i,_j)])')
    x=pype(ls1,[([_],[ls2]),(add,_i,_j)])

    print(x)

    print('='*30)

    ls1=[1,2,3]
    ls2=[2,3,4]

    print('pype(ls1,[([_],[ls2]),(add,_i+_0,_j)])')
    x=pype(ls1,[([_],[ls2]),(add,_i+_0,_j)])

    print(x)

    print('='*30)

    print('>'*30)
    print('GETTER')
    print('>'*30)

    print('='*30)
    
    print('pype([1,2,3],_[1])')

    x=pype([1,2,3],_[1])

    print(x)

    assert(x == 2)

    print('>'*30)
    print('EMBEDDED PYPE')
    print('>'*30)

    print('='*30)

    x=pype(1,[embedded_pype,add1,add1])

    print(x)

    assert(x == 3)

    print('>'*30)
    print('QUOTE')
    print('>'*30)

    print('='*30)

    add_two=lambda x,y:x+y
    x=pype(2,(add_two,_,Quote(1)))

    print('pype(2,Quote(1))')

    print(x)

    add2=lambda x: x+2
    calc=lambda x,f: x*f(x)
    
    print('='*30)

    x=pype(2,(calc,_,Quote(add2)))

    print('pype(2,(calc,_,Quote(add2)))')
    print(x)

    assert(x == 2*(2+2))
    
    print('='*30)

    ls=[{'a':1,'b':2},{'a':3,'b':4}]

    x=pype(ls,_0)

    print('pype(ls,_0)')
    print(x)


    print('>'*30)
    print('PYPEVAL')
    print('>'*30)

    print('='*30)

    lenf=PypeVal(len)

    x=pype([1,3,4,2],lenf > 5)

    print('pype([1,3,4,2],lenf > 5)')

    print(x)

    assert(x == False)

    print('='*30)

    x=pype([1,3,4,2],lenf > 2)

    print('pype([1,3,4,2],lenf > 2)')

    print(x)

    assert(x == True)

    print('='*30)

    ls=[1,2,3,4]
    lsV=PypeVal(ls)

    print(lsV[_])

    x=pype([1,3],[lsV[_]])

    print('pype([1,3],[lsV[_]])')

    print(x)

    assert(x == [2,4])

    print('>'*30)
    print('BUILD PYPE')
    print('>'*30)

    print('='*30)

    sm=lambda x,y: x+y

    pp=build_pype(add1)

    print('build_pype(add1)')
    
    x=pp(1)

    print(x)

    assert(x==2)

    print('='*30)

    pp=build_pype_multi(sm)

    print('build_pype(sm)')
    
    x=pp(1,2)

    print(x)

    assert(x==3)

    print('>'*30)
    print('DO')
    print('>'*30)

    print('='*30)

    ls=[1,452,5,6,7,23]

    x=pype(ls,_do(_.sort))

    print("pype(ls,_do(_.sort))")

    assert(x==[1, 5, 6, 7, 23, 452])

    print(x)

if __name__=='__main__':

    demo()
