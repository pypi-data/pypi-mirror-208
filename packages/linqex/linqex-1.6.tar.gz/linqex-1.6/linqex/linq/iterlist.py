from linqex._typing import *
from linqex.abstract.iterable import AbstractEnumerable
from linqex.build.iterlistbase import EnumerableListBase

from typing import Dict, List, Callable, Union as _Union, NoReturn, Optional, Tuple, Type, Generic, overload, Self
from collections.abc import Iterable

def EnumerableListCatch(enumerableList:"EnumerableList", iterable:Optional[List[_TV]], *keyHistoryAdd:_Key, oneValue:bool=False) -> Optional["EnumerableList[_TV]"]:
    if iterable is None:
        return None
    else:
        newEnumerableList = EnumerableList(iterable)
        newEnumerableList._main = enumerableList._main
        newEnumerableList._orderby = enumerableList._orderby
        newEnumerableList.keyHistory = enumerableList.keyHistory.copy()
        if keyHistoryAdd != ():
            if isinstance(keyHistoryAdd[0], (list, tuple)) and len(enumerableList.keyHistory) != 0:
                if isinstance(enumerableList.keyHistory[-1], (list, tuple)):
                    newEnumerableList.keyHistory[-1].extend(keyHistoryAdd[0])
                else:
                    newEnumerableList.keyHistory.extend(keyHistoryAdd)
            else:
                newEnumerableList.keyHistory.extend(keyHistoryAdd)
        newEnumerableList._oneValue = oneValue
        return newEnumerableList

def EnumerableListToValue(enumerableListOrValue:_Union["EnumerableList[_TV2]",_TV]) -> _TV:
    if isinstance(enumerableListOrValue, EnumerableList):
        return enumerableListOrValue.ToValue
    else:
        return enumerableListOrValue

class EnumerableList(AbstractEnumerable, Iterable[_TV], Generic[_TV]):
    
    def __init__(self, iterable:List[_TV]=None):
        self.iterable:List[_TV] = EnumerableListBase(EnumerableListToValue(iterable)).Get()
        self.keyHistory:list = list()
        self._main:EnumerableList = self
        self._orderby:list = list()
        self._oneValue:bool = False

    def __call__(self, iterable:List[_TV]=None):
        self.__init__(iterable)

    def Get(self, *key:int) -> _Union["EnumerableList[_TV]",_TV]:
        iterable = EnumerableListBase(self.iterable).Get(*key)
        if isinstance(iterable,list):
            return EnumerableListCatch(self, iterable, key)
        else:
            return iterable
    
    def GetKey(self, value:_TV) -> int:
        return EnumerableListBase(self.iterable).GetKey(EnumerableListToValue(value))
    
    def GetKeys(self) -> "EnumerableList[int]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).GetKeys())
    
    def GetValues(self) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).GetValues())
    
    def GetItems(self) -> "EnumerableList[Tuple[int,_TV]]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).GetItems())
    
    def Copy(self) -> "EnumerableList[_TV]":
        return EnumerableList(EnumerableListBase(self.iterable).Copy())



    def Take(self, count:int) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).Take(count))
    
    def TakeLast(self, count:int) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).TakeLast(count))
    
    def Skip(self, count:int) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).Skip(count))
    
    def SkipLast(self, count:int) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).SkipLast(count))
    
    def Select(self, selectFunc:Callable[[_TV],_TFV]=lambda value: value) -> "EnumerableList[_TFV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).Select(selectFunc))
    
    def Distinct(self, distinctFunc:Callable[[_TV],_TFV]=lambda value: value) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).Distinct(distinctFunc))
    
    def Except(self, exceptFunc:Callable[[_TV],_TFV]=lambda value: value, *value:_TV) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).Except(exceptFunc, *map(EnumerableListToValue, value)))

    def Join(self, iterable: List[_TV2], 
        innerFunc:Callable[[_TV],_TFV]=lambda value: value, 
        outerFunc:Callable[[_TV2],_TFV]=lambda value: value, 
        joinFunc:Callable[[_TV,_TV2],_TFV2]=lambda inValue, outValue: (inValue, outValue),
        joinType:JoinType=JoinType.INNER
    ) -> "EnumerableList[_TFV2]":
        return EnumerableList(EnumerableListBase(self.iterable).Join(EnumerableListToValue(iterable), innerFunc, outerFunc, joinFunc, joinType))
      
    def OrderBy(self, orderByFunc:Callable[[_TV],_Union[Tuple[_TFV],_TFV]]=lambda value: value, desc:bool=False) -> "EnumerableList[_TV]":
        self._orderby.clear()
        self._orderby.append((orderByFunc, desc))
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).OrderBy((orderByFunc, desc)))

    def ThenBy(self, orderByFunc:Callable[[_TV],_Union[Tuple[_TFV],_TFV]]=lambda value: value, desc:bool=False) -> "EnumerableList[_TV]":
        self._orderby.append((orderByFunc, desc))
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).OrderBy(*self._orderby))
        
    def GroupBy(self, groupByFunc:Callable[[_TV],_Union[Tuple[_TFV],_TFV]]=lambda value: value) -> "EnumerableList[Tuple[_Union[Tuple[_TFV],_TFV], List[_TV]]]":
        return EnumerableList(EnumerableListBase(self.iterable).GroupBy(groupByFunc))

    def Reverse(self) -> "EnumerableList[_TV]":
        return EnumerableListCatch(self,EnumerableListBase(self.iterable).Reverse())
        
    def Zip(self, iterable:List[_TV2], zipFunc:Callable[[_TV,_TV2],_TFV]=lambda inValue, outValue: (inValue, outValue)) -> "EnumerableList[_TFV]":
        return EnumerableList(EnumerableListBase(self.iterable).Zip(EnumerableListToValue(iterable), zipFunc))



    def Where(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> "EnumerableList[_TV]":
        items = dict(EnumerableListBase(self.iterable).Where(conditionFunc))
        return EnumerableListCatch(self, list(items.values()), list(items.keys()))
    
    def OfType(self, *type:Type) -> "EnumerableList[_TV]":
        items = dict(EnumerableListBase(self.iterable).OfType(*type))
        return EnumerableListCatch(self, list(items.values()), list(items.keys()))
    
    def First(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> Optional["EnumerableList[_TV]"]:
        firstValue = EnumerableListBase(self.iterable).First(conditionFunc)
        if firstValue is None:
            return None
        else:
            return EnumerableListCatch(self, [firstValue[1]], firstValue[0], oneValue=True)
    
    def Last(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> Optional["EnumerableList[_TV]"]:
        lastValue = EnumerableListBase(self.iterable).Last(conditionFunc)
        if lastValue is None:
            return None
        else:
            return EnumerableListCatch(self, [lastValue[1]], lastValue[0], oneValue=True)
        
    def Single(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> Optional["EnumerableList[_TV]"]:
        singleValue = EnumerableListBase(self.iterable).Single(conditionFunc)
        if singleValue is None:
            return None
        else:
            return EnumerableListCatch(self, [singleValue[1]], singleValue[0], oneValue=True)



    def Any(self, conditionFunc:Callable[[_TV],bool]=lambda value: value) -> bool:
        return EnumerableListBase(self.iterable).Any(conditionFunc)
    
    def All(self, conditionFunc:Callable[[_TV],bool]=lambda value: value) -> bool:
        return EnumerableListBase(self.iterable).All(conditionFunc)
    
    def SequenceEqual(self, iterable:List[_TV2]) -> bool:
        return EnumerableListBase(self.iterable).SequenceEqual(EnumerableListToValue(iterable))



    def Accumulate(self, accumulateFunc:Callable[[_TV,_TV],_TFV]=lambda temp, nextValue: temp + nextValue) -> "EnumerableList[_TFV]":
        return EnumerableList(EnumerableListBase(self.iterable).Accumulate(accumulateFunc))

    def Aggregate(self, aggregateFunc:Callable[[_TV,_TV],_TFV]=lambda temp, nextValue: temp + nextValue) -> _TFV:
        return EnumerableListBase(self.iterable).Aggregate(aggregateFunc)



    def Count(self, value:_TV) -> int:
        return EnumerableListBase(self.iterable).Count(value)

    @property
    def Lenght(self) -> int:
        return EnumerableListBase(self.iterable).Lenght()
    
    def Sum(self) -> Optional[_TV]:
        return EnumerableListBase(self.iterable).Sum()
        
    def Avg(self) -> Optional[_TV]:
        return EnumerableListBase(self.iterable).Avg()
        
    def Max(self) -> Optional[_TV]:
        return EnumerableListBase(self.iterable).Max()
        
    def Min(self) -> Optional[_TV]:
        return EnumerableListBase(self.iterable).Min()

    @overload
    def Set(self): ...
    @overload
    def Set(self, value:_Value): ...
    def Set(self, value=...):
        if value is ...:
            self.Set(self.iterable)
        else:
            value = EnumerableListToValue(value)
            if len(self.keyHistory) == 0:
                self._main.Clear()
                self._main.Concat(value)
            else:
                keyHistory = list(filter(lambda k: not isinstance(k, list),self.keyHistory[:len(self.keyHistory)-1]))
                if isinstance(self.ToKey, list):
                    key = keyHistory[-1]
                    keyHistory = keyHistory[:len(keyHistory)-1]
                    if isinstance(key, list):
                        return None
                else:
                    key = self.ToKey
                self._main.Get(*keyHistory).Update(key, value)
                self.iterable = value

    def Add(self, value:_Value):
        EnumerableListBase(self.iterable).Add(EnumerableListToValue(value))

    def Prepend(self, value:_Value):
        EnumerableListBase(self.iterable).Prepend(EnumerableListToValue(value))

    def Insert(self, key:int, value:_Value):
        EnumerableListBase(self.iterable).Insert(key, EnumerableListToValue(value))

    def Update(self, key:int, value:_Value):
        EnumerableListBase(self.iterable).Update(key, EnumerableListToValue(value))

    def Concat(self, *iterable:List[_TV2]):
        EnumerableListBase(self.iterable).Concat(*map(EnumerableListToValue, iterable))

    def Union(self, *iterable:List[_TV2]):
        EnumerableListBase(self.iterable).Union(*map(EnumerableListToValue, iterable))

    @overload
    def Delete(self): ...
    @overload
    def Delete(self, *key:int): ...
    def Delete(self, *key):
        if key == ():
            if isinstance(self.ToKey, (list,tuple)):
                key = self.ToKey
            else:
                key = [self.ToKey]
            self._main.Get(*filter(lambda k: not isinstance(k, (list,tuple)),self.keyHistory[:len(self.keyHistory)-1])).Delete(*key)
        else:
            EnumerableListBase(self.iterable).Delete(*key)

    def Remove(self, *value:_TV):
        EnumerableListBase(self.iterable).Remove(*map(EnumerableListToValue, value))

    def RemoveAll(self, *value:_TV):
        EnumerableListBase(self.iterable).RemoveAll(*map(EnumerableListToValue, value))

    def Clear(self):
        EnumerableListBase(self.iterable).Clear()



    def Loop(self, loopFunc:Callable[[_TV],NoReturn]=lambda value: print(value)):
        EnumerableListBase(self.iterable).Loop(loopFunc)



    @property
    def ToKey(self) -> int:
        if self.keyHistory == []:
            return None
        else:
            return self.keyHistory[-1]
    
    @property
    def ToValue(self) -> _Union[List[_TV],_TV]:
        if len(self.iterable) == 1 and self._oneValue:
            return self.GetValues().iterable[0]
        else:
            return self.ToList
    
    @property
    def ToDict(self) -> Dict[int,_TV]:
        return EnumerableListBase(self.iterable).ToDict()
    
    @property
    def ToList(self) -> List[_TV]:
        return EnumerableListBase(self.iterable).ToList()



    @property
    def IsEmpty(self) -> bool:
        return EnumerableListBase(self.iterable).IsEmpty()

    def ContainsByKey(self, *key:int) -> bool:
        return EnumerableListBase(self.iterable).ContainsByKey(*key)

    def Contains(self, *value:_TV) -> bool:
        return EnumerableListBase(self.iterable).Contains(*map(EnumerableListToValue, value))



    def __neg__(self) -> "EnumerableList[_TV]":
        return EnumerableList(EnumerableListBase(self.Copy().iterable).__neg__())
    
    def __add__(self, iterable:List[_TV]) -> "EnumerableList[_Union[_TV,_TV2]]":
        return EnumerableList(EnumerableListBase(self.Copy().iterable).__add__(EnumerableListToValue(iterable)))
    
    def __iadd__(self, iterable:List[_TV]) -> Self:
        EnumerableListBase(self.iterable).__iadd__(EnumerableListToValue(iterable))
        return self

    def __sub__(self, iterable:List[_TV]) -> "EnumerableList[_Union[_TV,_TV2]]":
        return EnumerableList(EnumerableListBase(self.Copy().iterable).__sub__(EnumerableListToValue(iterable)))
    
    def __isub__(self, iterable:List[_TV]) -> Self:
        EnumerableListBase(self.iterable).__isub__(EnumerableListToValue(iterable))
        return self

    

    def __eq__(self, iterable:List[_TV]) -> bool:
        return EnumerableListBase(self.iterable).__eq__(EnumerableListToValue(iterable))

    def __ne__(self, iterable:List[_TV]) -> bool:
        return EnumerableListBase(self.iterable).__ne__(EnumerableListToValue(iterable))
    
    def __contains__(self, value:_Value) -> bool:
        return EnumerableListBase(self.iterable).__contains__(EnumerableListToValue(value))



    def __bool__(self) -> bool:
        return EnumerableListBase(self.iterable).__bool__()
    
    def __len__(self) -> int:
        return EnumerableListBase(self.iterable).__len__()
    
    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, str(self.iterable))



    def __iter__(self) -> Iterable[Tuple[int,_TV]]:
        return EnumerableListBase(self.GetValues().ToValue).__iter__()
    
    def __getitem__(self, key:int) -> _TV:
        return EnumerableListBase(self.iterable).__getitem__(key)
    
    def __setitem__(self, key:int, value:_Value):
        return EnumerableListBase(self.iterable).__setitem__(key, EnumerableListToValue(value))

    def __delitem__(self, key:int):
        return EnumerableListBase(self.iterable).__delitem__(key)



    @staticmethod
    def Range(start:int, stop:int, step:int=1) -> "EnumerableList[int]":
        return EnumerableList(EnumerableListBase.Range(start, stop, step))
    @staticmethod
    def Repeat(value:_TV, count:int) -> "EnumerableList[_TV]":
        return EnumerableList(EnumerableListBase.Repeat(value, count))



__all__ = ["AbstractEnumerable", "EnumerableList"]
