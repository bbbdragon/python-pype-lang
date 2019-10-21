#################
# TYPE CHECKING #
#################

is_tuple=lambda x: isinstance(x,tuple)
is_dict=lambda x: isinstance(x,dict)
is_list=lambda x: isinstance(x,list)
is_mapping=lambda x: isinstance(x,dict)
is_bool=lambda x: isinstance(x,bool)
is_object=lambda x: isinstance(x,object)
is_string=lambda x: isinstance(x,str)
is_set=lambda x: isinstance(x,set)
is_int=lambda x: isinstance(x,int)
is_slice=lambda x: isinstance(x,slice)
is_getter=lambda x: isinstance(x,Getter)
is_pype_val=lambda x: isinstance(x,PypeVal)
is_getter=lambda x: isinstance(x,Getter)
is_lam_tup=lambda x: isinstance(x,LamTup) and not is_pype_val(x) and not is_getter(x)
is_iterable=lambda x: isinstance(x,Iterable)
is_mapping=lambda x: isinstance(x,Mapping)
is_hashable=lambda x: isinstance(x,Hashable)
is_ndarray=lambda x: isinstance(x,np.ndarray)
is_sequence=lambda x: isinstance(x,Sequence) or is_ndarray(x)
is_container=lambda x: isinstance(x,Container)
is_float=lambda x: isinstance(x,float)
is_integer=lambda x: isinstance(x,int)
key=lambda x: tup[0]
val=lambda x: tup[1]
slc=lambda ls,start,stop: ls[start:stop]

def is_callable(fArg):

    return callable(fArg)
