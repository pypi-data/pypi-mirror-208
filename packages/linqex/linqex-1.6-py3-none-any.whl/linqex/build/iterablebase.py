from linqex._typing import *
from linqex.abstract.iterablebase import AbstractEnumerableBase
from linqex.build.iterdictbase import EnumerableDictBase
from linqex.build.iterlistbase import EnumerableListBase
from linqex.build.iteritembase import EnumerableItemBase

from typing import Dict, List, Union, Generic


class EnumerableBase(Generic[_TK,_TV]):
    def __new__(cls, iterable:Union[List[_TV],Dict[_TK,_TV]]):
        return cls.Iterable(iterable)
    @classmethod
    def Iterable(cls, iterable:Union[List[_TV],Dict[_TK,_TV]]) -> Union[EnumerableItemBase[_TV], EnumerableDictBase[_TK,_TV]]:
        if isinstance(iterable, list):
            return cls.Item(iterable)
        elif isinstance(iterable, dict):
            return cls.Dict(iterable)
        else:
            raise TypeError("Must be list or dict, not {}".format(str(type(iterable))[8,-2]))

    @classmethod
    def Item(cls, iteritem:List[_TV]=None) -> EnumerableItemBase[_TV]:
        if iteritem is None:
            iteritem:List[_TV]=list()
        return EnumerableItemBase(iteritem)

    @classmethod
    def List(cls, iterlist:List[_TV]=None) -> EnumerableListBase[_TV]:
        if iterlist is None:
            iterlist:List[_TV]=list()
        return EnumerableListBase(iterlist)

    @classmethod
    def Dict(cls, iterdict:Dict[_TK,_TV]=None) -> EnumerableDictBase[_TK,_TV]:
        if iterdict is None:
            iterdict:Dict[_TK,_TV]=dict()
        return EnumerableDictBase(iterdict)



__all__ = ["AbstractEnumerableBase", "EnumerableListBase", "EnumerableItemBase", "EnumerableDictBase", "EnumerableBase"]
