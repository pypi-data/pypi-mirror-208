from linqex._typing import *
from linqex.abstract.iterable import AbstractEnumerable
from linqex.build.iteritembase import EnumerableItemBase
from linqex.linq.iterlist import EnumerableList, EnumerableListCatch

from typing import Dict, List, Callable, Union as _Union, NoReturn, Optional, Tuple, Type, Generic, overload, Self
from collections.abc import Iterable

def EnumerableItemCatch(enumerableItem:"EnumerableItem", iterable:Optional[List[_TV]], *keyHistoryAdd:_Key, oneValue:bool=False) -> Optional["EnumerableItem[_TV]"]:
    if iterable is None:
        return None
    else:
        newEnumerableItem = EnumerableItem(iterable)
        newEnumerableItem._main = enumerableItem._main
        newEnumerableItem._orderby = enumerableItem._orderby
        newEnumerableItem.keyHistory = enumerableItem.keyHistory.copy()
        if keyHistoryAdd != ():
            if isinstance(keyHistoryAdd[0], (list, tuple)) and len(enumerableItem.keyHistory) != 0:
                if isinstance(enumerableItem.keyHistory[-1], (list, tuple)):
                    newEnumerableItem.keyHistory[-1].extend(keyHistoryAdd[0])
                else:
                    newEnumerableItem.keyHistory.extend(keyHistoryAdd)
            else:
                newEnumerableItem.keyHistory.extend(keyHistoryAdd)
        newEnumerableItem._oneValue = oneValue
        return newEnumerableItem

def EnumerableItemToValue(enumerableItemOrValue:_Union["EnumerableItem[_TV]",List[_TV]]) -> List[_TV]:
    if isinstance(enumerableItemOrValue, EnumerableItem):
        return enumerableItemOrValue.ToValue
    else:
        return enumerableItemOrValue

class EnumerableItem(EnumerableList, Iterable[Tuple[int,_TV]], Generic[_TK,_TV]):
    
    def __init__(self, iterable:List[_TV]=None):
        self.iterable:List[_TV] = EnumerableItemBase(EnumerableItemToValue(iterable)).iterable
        self.keyHistory:list = list()
        self._main:EnumerableItem = self
        self._orderby:list = list()
        self._oneValue:bool = False

    def __call__(self, iterable:List[_TV]=None):
        self.__init__(iterable)

    def Get(self, *key:int) -> _Union["EnumerableItem[_TV]",_TV]:
        iterable = EnumerableItemBase(self.iterable).Get(*key)
        if isinstance(iterable,list):
            return EnumerableItemCatch(self, iterable, key)
        else:
            return iterable
    
    def GetKey(self, value:_TV) -> int:
        return EnumerableItemBase(self.iterable).GetKey(EnumerableItemToValue(value))
    
    def GetKeys(self) -> EnumerableList[int]:
        return EnumerableListCatch(self,EnumerableItemBase(self.iterable).GetKeys())
    
    def GetValues(self) -> EnumerableList[_TV]:
        return EnumerableListCatch(self,EnumerableItemBase(self.iterable).GetValues())
    
    def GetItems(self) -> EnumerableList[Tuple[int,_TV]]:
        return EnumerableListCatch(self,EnumerableItemBase(self.iterable).GetItems())
    
    def Copy(self) -> "EnumerableItem[_TV]":
        return EnumerableItem(EnumerableItemBase(self.iterable).Copy())



    def Take(self, count:int) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).Take(count))
    
    def TakeLast(self, count:int) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).TakeLast(count))
    
    def Skip(self, count:int) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).Skip(count))
    
    def SkipLast(self, count:int) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).SkipLast(count))
    
    def Select(self, selectFunc:Callable[[int,_TV],_TFV]=lambda key, value: value) -> "EnumerableItem[_TFV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).Select(selectFunc))
    
    def Distinct(self, distinctFunc:Callable[[int,_TV],_TFV]=lambda key, value: value) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).Distinct(distinctFunc))
    
    def Except(self, exceptFunc:Callable[[int,_TV],_TFV]=lambda key, value: value, *value:_TV) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).Except(exceptFunc, *map(EnumerableItemToValue, value)))

    def Join(self, iterable: List[_TV2], 
        innerFunc:Callable[[int,_TV],_TFV]=lambda key, value: value, 
        outerFunc:Callable[[int,_TV2],_TFV]=lambda key, value: value, 
        joinFunc:Callable[[int,_TV,int,_TV2],_TFV2]=lambda inKey, inValue, outKey, outValue: (inValue, outValue),
        joinType:JoinType=JoinType.INNER
    ) -> "EnumerableItem[_TFV2]":
        return EnumerableItem(EnumerableItemBase(self.iterable).Join(EnumerableItemToValue(iterable), innerFunc, outerFunc, joinFunc, joinType))
      
    def OrderBy(self, orderByFunc:Callable[[int,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value, desc:bool=False) -> "EnumerableItem[_TV]":
        self._orderby.clear()
        self._orderby.append((orderByFunc, desc))
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).OrderBy((orderByFunc, desc)))

    def ThenBy(self, orderByFunc:Callable[[int,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value, desc:bool=False) -> "EnumerableItem[_TV]":
        self._orderby.append((orderByFunc, desc))
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).OrderBy(*self._orderby))
        
    def GroupBy(self, groupByFunc:Callable[[int,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value) -> "EnumerableItem[Tuple[_Union[Tuple[_TFV],_TFV], List[_TV]]]":
        return EnumerableItem(EnumerableItemBase(self.iterable).GroupBy(groupByFunc))

    def Reverse(self) -> "EnumerableItem[_TV]":
        return EnumerableItemCatch(self,EnumerableItemBase(self.iterable).Reverse())
        
    def Zip(self, iterable:List[_TV2], zipFunc:Callable[[int,_TV,int,_TV2],_TFV]=lambda inKey, inValue, outKey, outValue: (inValue, outValue)) -> "EnumerableItem[_TFV]":
        return EnumerableItem(EnumerableItemBase(self.iterable).Zip(EnumerableItemToValue(iterable), zipFunc))



    def Where(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> "EnumerableItem[_TV]":
        items = dict(EnumerableItemBase(self.iterable).Where(conditionFunc))
        return EnumerableItemCatch(self, list(items.values()), list(items.keys()))
    
    def OfType(self, *type:Type) -> "EnumerableItem[_TV]":
        items = dict(EnumerableItemBase(self.iterable).OfType(*type))
        return EnumerableItemCatch(self, list(items.values()), list(items.keys()))
    
    def First(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> Optional["EnumerableItem[_TV]"]:
        firstValue = EnumerableItemBase(self.iterable).First(conditionFunc)
        if firstValue is None:
            return None
        else:
            return EnumerableItemCatch(self, [firstValue[1]], firstValue[0], oneValue=True)
    
    def Last(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> Optional["EnumerableItem[_TV]"]:
        lastValue = EnumerableItemBase(self.iterable).Last(conditionFunc)
        if lastValue is None:
            return None
        else:
            return EnumerableItemCatch(self, [lastValue[1]], lastValue[0], oneValue=True)
        
    def Single(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> Optional["EnumerableItem[_TV]"]:
        singleValue = EnumerableItemBase(self.iterable).Single(conditionFunc)
        if singleValue is None:
            return None
        else:
            return EnumerableItemCatch(self, [singleValue[1]], singleValue[0], oneValue=True)



    def Any(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: value) -> bool:
        return EnumerableItemBase(self.iterable).Any(conditionFunc)
    
    def All(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: value) -> bool:
        return EnumerableItemBase(self.iterable).All(conditionFunc)
    
    def SequenceEqual(self, iterable:List[_TV2]) -> bool:
        return EnumerableItemBase(self.iterable).SequenceEqual(EnumerableItemToValue(iterable))



    def Accumulate(self, accumulateFunc:Callable[[_TV,int,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> "EnumerableItem[_TFV]":
        return EnumerableItem(EnumerableItemBase(self.iterable).Accumulate(accumulateFunc))

    def Aggregate(self, aggregateFunc:Callable[[_TV,int,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> _TFV:
        return EnumerableItemBase(self.iterable).Aggregate(aggregateFunc)



    def Count(self, value:_TV) -> int:
        return EnumerableItemBase(self.iterable).Count(value)

    @property
    def Lenght(self) -> int:
        return EnumerableItemBase(self.iterable).Lenght()
    
    def Sum(self) -> Optional[_TV]:
        return EnumerableItemBase(self.iterable).Sum()
        
    def Avg(self) -> Optional[_TV]:
        return EnumerableItemBase(self.iterable).Avg()
        
    def Max(self) -> Optional[_TV]:
        return EnumerableItemBase(self.iterable).Max()
        
    def Min(self) -> Optional[_TV]:
        return EnumerableItemBase(self.iterable).Min()

    @overload
    def Set(self): ...
    @overload
    def Set(self, value:_Value): ...
    def Set(self, value=...):
        super().Set(value)

    def Add(self, key:Optional[int], value:_Value):
        EnumerableItemBase(self.iterable).Add(key, EnumerableItemToValue(value))

    def Prepend(self, key:Optional[int], value:_Value):
        EnumerableItemBase(self.iterable).Prepend(key, EnumerableItemToValue(value))

    def Insert(self, key:int, value:_Value):
        EnumerableItemBase(self.iterable).Insert(key, EnumerableItemToValue(value))

    def Update(self, key:int, value:_Value):
        EnumerableItemBase(self.iterable).Update(key, EnumerableItemToValue(value))

    def Concat(self, *iterable:List[_TV2]):
        EnumerableItemBase(self.iterable).Concat(*map(EnumerableItemToValue, iterable))

    def Union(self, *iterable:List[_TV2]):
        EnumerableItemBase(self.iterable).Union(*map(EnumerableItemToValue, iterable))

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
            EnumerableItemBase(self.iterable).Delete(*key)

    def Remove(self, *value:_TV):
        EnumerableItemBase(self.iterable).Remove(*map(EnumerableItemToValue, value))

    def RemoveAll(self, *value:_TV):
        EnumerableItemBase(self.iterable).RemoveAll(*map(EnumerableItemToValue, value))

    def Clear(self):
        EnumerableItemBase(self.iterable).Clear()



    def Loop(self, loopFunc:Callable[[int,_TV],NoReturn]=lambda key, value: print(value)):
        EnumerableItemBase(self.iterable).Loop(loopFunc)



    @property
    def ToKey(self) -> int:
        return super().ToKey
    
    @property
    def ToValue(self) -> _Union[List[_TV],_TV]:
        return super().ToValue
    
    @property
    def ToDict(self) -> Dict[int,_TV]:
        return EnumerableItemBase(self.iterable).ToDict()
    
    @property
    def ToList(self) -> List[_TV]:
        return EnumerableItemBase(self.iterable).ToList()



    @property
    def IsEmpty(self) -> bool:
        return EnumerableItemBase(self.iterable).IsEmpty()

    def ContainsByKey(self, *key:int) -> bool:
        return EnumerableItemBase(self.iterable).ContainsByKey(*key)

    def Contains(self, *value:_TV) -> bool:
        return EnumerableItemBase(self.iterable).Contains(*map(EnumerableItemToValue, value))



    def __neg__(self) -> "EnumerableItem[_TV]":
        return EnumerableItem(EnumerableItemBase(self.Copy().iterable).__neg__())
    
    def __add__(self, iterable:List[_TV]) -> "EnumerableItem[_Union[_TV,_TV2]]":
        return EnumerableItem(EnumerableItemBase(self.Copy().iterable).__add__(EnumerableItemToValue(iterable)))
    
    def __iadd__(self, iterable:List[_TV]) -> Self:
        EnumerableItemBase(self.iterable).__iadd__(EnumerableItemToValue(iterable))
        return self

    def __sub__(self, iterable:List[_TV]) -> "EnumerableItem[_Union[_TV,_TV2]]":
        return EnumerableItem(EnumerableItemBase(self.Copy().iterable).__sub__(EnumerableItemToValue(iterable)))
    
    def __isub__(self, iterable:List[_TV]) -> Self:
        EnumerableItemBase(self.iterable).__isub__(EnumerableItemToValue(iterable))
        return self

    

    def __eq__(self, iterable:List[_TV]) -> bool:
        return EnumerableItemBase(self.iterable).__eq__(EnumerableItemToValue(iterable))

    def __ne__(self, iterable:List[_TV]) -> bool:
        return EnumerableItemBase(self.iterable).__ne__(EnumerableItemToValue(iterable))
    
    def __contains__(self, value:_Value) -> bool:
        return EnumerableItemBase(self.iterable).__contains__(EnumerableItemToValue(value))



    def __bool__(self) -> bool:
        return EnumerableItemBase(self.iterable).__bool__()
    
    def __len__(self) -> int:
        return EnumerableItemBase(self.iterable).__len__()
    
    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, str(self.iterable))



    def __iter__(self) -> Iterable[Tuple[int,_TV]]:
        return EnumerableItemBase(self.GetItems().ToValue).__iter__()
    
    def __getitem__(self, key:int) -> _TV:
        return EnumerableItemBase(self.iterable).__getitem__(key)
    
    def __setitem__(self, key:int, value:_Value):
        return EnumerableItemBase(self.iterable).__setitem__(key, EnumerableItemToValue(value))

    def __delitem__(self, key:int):
        return EnumerableItemBase(self.iterable).__delitem__(key)



    @staticmethod
    def Range(start:int, stop:int, step:int=1) -> "EnumerableItem[int]":
        return EnumerableItem(EnumerableItemBase.Range(start, stop, step))
    @staticmethod
    def Repeat(value:_TV, count:int) -> "EnumerableItem[_TV]":
        return EnumerableItem(EnumerableItemBase.Repeat(value, count))



__all__ = ["AbstractEnumerable", "EnumerableItem"]
