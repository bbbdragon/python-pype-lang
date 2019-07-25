from operator import *

is_tuple=lambda x: isinstance(x,tuple)
is_dict=lambda x: isinstance(x,dict)
is_list=lambda x: isinstance(x,list)
is_set=lambda x: isinstance(x,set)
is_slice=lambda x: isinstance(x,slice)

def hash_rec(el):

    #print('*'*30)
    #print('hash_rec')
    #print(el)

    if is_set(el) or is_list(el) or is_tuple(el):

        #print('{} is set'.format(el))

        return hash(str([hash_rec(x) for x in el]))

    if is_dict(el):

        #print('{} is dict'.format(el))

        return hash(str({hash_rec(k):hash_rec(v) for (k,v) in el.items()}))

    #print(hash(el))
    #print('returning')

    return hash(el)


class LamTup(object):
    '''
    This takes tuple expressions and overrides operators for them.
    '''
    def __init__(self,*tup):

        if not tup:

            raise Exception('LamTup.__init__: tup needs to have one '
                            'or more values')

        self._tup_=tup

    def __str__(self):

        return 'L'+str(self._tup_)

    def __repr__(self):

        return self.__str__()


    def __getitem__(self,val):

        # We rewrite and return acceptable expressions.

        if (is_tuple(val) or is_list(val)):

           if len(val) > 1:

               # We are making this definition recursive, since I do not want to 
               # evaluate two different structures for indexing.
               # The first is _[0][0], the second is _[0,0], which should both
               # after delam parse as ((('_pype_mirror_',), [0]), [0])

               return LamTup(self.__getitem__(val[:-1]),[val[-1]])

           else:

               return LamTup(self.val(),[val[0]])

        elif is_slice(val):

            return LamTup(getitem,self.val(),(slice,val.start,val.stop))

        return LamTup(self.val(),[val])


    def __getattr__(self,val):

        return LamTup(self.val(),val)


    def __hash__(self):

        return hash(str(self._tup_))

    def val(self):

        if len(self._tup_) == 1:

            return self._tup_[0]

        return tuple(self._tup_)

    # Unary Arithmetic

    def __neg__(self):

        return LamTup(neg,self.val())

    # Binary Arithmetic 

    def __add__(self,other):

        return LamTup(add,self.val(),other)

    def __radd__(self,other):

        return LamTup(add,other,self.val())

    def __sub__(self,other):

        return LamTup(sub,self.val(),other)

    def __rsub__(self,other):

        return LamTup(sub,other,self.val())


    def __mul__(self,other):

        return LamTup(mul,self.val(),other)

    def __rmul__(self,other):

        return LamTup(mul,other,self.val())


    def __floordiv__(self,other):

        return LamTup(floordiv,self.val(),other)

    def __rfloordiv__(self,other):

        return LamTup(floordiv,other,self.val())

    def __truediv__(self,other):

        return LamTup(truediv,self.val(),other)

    def __rtruediv__(self,other):

        return LampTup(truediv,other,self.val())

    def __mod__(self,other):

        return LamTup(mod,self.val(),other)

    def __rmod__(self,other):

        return LamTup(mod,other,self.val())

    def __pow__(self,other):

        return LamTup(pow,self.val(),other)

    def __rpow__(self,other):

        return LamTup(pow,other,self.val())

    # Comparators

    def __eq__(self,other):

        return LamTup(eq,self.val(),other)

    def __ne__(self,other):

        return LamTup(ne,self.val(),other)

    def __lt__(self,other):

        return LamTup(lt,self.val(),other)

    def __le__(self,other):

        return LamTup(le,self.val(),other)

    def __gt__(self,other):

        return LamTup(gt,self.val(),other)

    def __ge__(self,other):

        return LamTup(ge,self.val(),other)

    # Boolean operators

    def __not__(self):

        return LamTup(not_,self.val())

    def __and__(self,other):

        return LamTup(and_,self.val(),other)

    def __ror__(self,other):

        return LamTup(or_,self.val(),other)

    def __or__(self,other):

        return LamTup(or_,self.val(),other)

    def __xor__(self,other):

        return LamTup(xor,self.val(),other)

    '''
    def __contains__(self,other):

        return LamTup(contains,self.val(),other)
    '''

    def __rshift__(self,other):

        return LamTup(contains,other,self.val())

    def __rrshift__(self,other):

        return LamTup(contains,self.val(),other)

class PypeVal(LamTup):

    def __init__(self,*val):

        if not val:

            raise Exception('PypeVal.__init__: no value to initialize')

        if len(val) > 2:

            raise Exception('PypeVal.__init__: you need to provide only one value')

        self._tup_=(val[0],)

    def __str__(self):

        return 'PV'+str(self._tup_)


class Getter(PypeVal):
    '''
    The getter returns itself only for 'val'.  This is for unique objects.
    '''
    def val(self):

        return self

    def __str__(self):

        return 'G'+str(self._tup_)

is_pype_val=lambda x:isinstance(x,PypeVal)
is_getter=lambda x:isinstance(x,Getter)
is_lam_tup=lambda x: isinstance(x,LamTup) and not is_pype_val(x) and not is_getter(x)

def delam(expr):

    #print('*'*30)
    #print('delam')
    #print('{} is expr'.format(expr))

    if is_lam_tup(expr):

        #print('is lam tup')

        return delam(expr.val())

    if is_dict(expr):

        #print('{} is dict'.format(expr))

        # This allows lam tups to appear as keys, but then be evaluated as
        # lambdas in switch dicts and dict builds.

        return {k:delam(v) for (k,v) in expr.items()}

    if is_list(expr):

        return [delam(el) for el in expr]

    if is_tuple(expr):

        #print('is tuple')

        return tuple([delam(el) for el in expr])

    '''
    if is_set(expr):

        print('*'*30)
        print(expr)
        print([el for el in expr])

        return set([delam(el) for el in expr])
    '''

    return expr


class Quote(object):

    def __init__(self,v):

        self.v=v

    def val(self):

        #print('evaluating quote')

        return self.v
        
    def __str__(self):

        return 'Q('+str(self.v)+')'


def l(*args):

    return PypeVal((*args,))

lenf=PypeVal(len)
empty=lambda ls: len(ls) == 0
empty_1=lambda tup: len(tup[1]) == 0
single=lambda ls: len(ls) == 1
single_1=lambda tup: len(tup[1]) == 1

singlef=PypeVal(single)
emptyf=PypeVal(empty)
quote=lambda v: Quote(v)

def not_empty(v):

    return len(v) != 0


