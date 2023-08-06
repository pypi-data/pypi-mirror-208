from linqex._typing import *
from linqex.abstract.iterable import AbstractEnumerable
from linqex.build.iterdictbase import EnumerableDictBase
from linqex.linq.iterlist import EnumerableList, EnumerableListCatch

from typing import Dict, List, Callable, Union as _Union, NoReturn, Optional, Tuple, Type, Generic, overload, Self
from collections.abc import Iterable

def EnumerableDictCatch(enumerableDict:"EnumerableDict", iterable:Optional[Dict[_TK,_TV]], *keyHistoryAdd:_Key, oneValue:bool=False) -> Optional["EnumerableDict[_TK,_TV]"]:
    if iterable is None:
        return None
    else:
        newEnumerableDict = EnumerableDict(iterable)
        newEnumerableDict._main = enumerableDict._main
        newEnumerableDict.keyHistory = enumerableDict.keyHistory.copy()
        if keyHistoryAdd != ():
            if isinstance(keyHistoryAdd[0], (list, tuple)) and len(enumerableDict.keyHistory) != 0:
                if isinstance(enumerableDict.keyHistory[-1], (list, tuple)):
                    newEnumerableDict.keyHistory[-1].extend(keyHistoryAdd[0])
                else:
                    newEnumerableDict.keyHistory.extend(keyHistoryAdd)
            else:
                newEnumerableDict.keyHistory.extend(keyHistoryAdd)
        newEnumerableDict._oneValue = oneValue
        return newEnumerableDict

def EnumerableDictToValue(enumerableDictOrValue:_Union["EnumerableDict[_TK,_TV]",_TV]) -> _TV:
    if isinstance(enumerableDictOrValue, EnumerableDict):
        return enumerableDictOrValue.ToValue
    else:
        return enumerableDictOrValue

class EnumerableDict(AbstractEnumerable, Iterable[Tuple[_TK,_TV]], Generic[_TK,_TV]):
    
    def __init__(self, iterable:Dict[_TK,_TV]=None):
        self.iterable:Dict[_TK,_TV] = EnumerableDictBase(EnumerableDictToValue(iterable)).Get()
        self.keyHistory:list = list()
        self._main:EnumerableDict = self
        self._orderby:list = list()
        self._oneValue:bool = False

    def __call__(self, iterable:Dict[_TK,_TV]=None):
        self.__init__(iterable)

    def Get(self, *key:_TK) -> _Union["EnumerableDict[_TK,_TV]",_TV]:
        iterable = EnumerableDictBase(self.iterable).Get(*key)
        if isinstance(iterable,dict):
            return EnumerableDictCatch(self, iterable, key)
        else:
            return iterable
    
    def GetKey(self, value:_TV) -> _TK:
        return EnumerableDictBase(self.iterable).GetKey(EnumerableDictToValue(value))
    
    def GetKeys(self) -> EnumerableList[_TK]:
        return EnumerableListCatch(self, EnumerableDictBase(self.iterable).GetKeys())
    
    def GetValues(self) -> EnumerableList[_TV]:
        return EnumerableListCatch(self, EnumerableDictBase(self.iterable).GetValues())
    
    def GetItems(self) -> EnumerableList[Tuple[_TK,_TV]]:
        return EnumerableListCatch(self, EnumerableDictBase(self.iterable).GetItems())
    
    def Copy(self) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDict(EnumerableDictBase(self.iterable).Copy())



    def Take(self, count:int) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).Take(count))
    
    def TakeLast(self, count:int) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).TakeLast(count))
    
    def Skip(self, count:int) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).Skip(count))
    
    def SkipLast(self, count:int) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).SkipLast(count))
    
    def Select(self, 
        selectFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value,
        selectFuncByKey:Callable[[_TK,_TV],_TFK]=lambda key, value: key
    ) -> "EnumerableDict[_TFK,_TFV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).Select(selectFunc, selectFuncByKey))
    
    def Distinct(self, distinctFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).Distinct(distinctFunc))
    
    def Except(self, exceptFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value, *value:_TV) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).Except(exceptFunc, *map(EnumerableDictToValue, value)))

    def Join(self, iterable: Dict[_TK2,_TV2], 
        innerFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value, 
        outerFunc:Callable[[_TK2,_TV2],_TFV]=lambda key, value: value, 
        joinFunc:Callable[[_TK,_TV,_TK2,_TV2],_TFV2]=lambda inKey, inValue, outKey, outValue: (inValue, outValue),
        joinFuncByKey:Callable[[_TK,_TV,_TK2,_TV2],_TFK2]=lambda inKey, inValue, outKey, outValue: inKey,
        joinType:JoinType=JoinType.INNER
    ) -> "EnumerableDict[_TFK2,_TFV2]":
        return EnumerableDict(EnumerableDictBase(self.iterable).Join(EnumerableDictToValue(iterable), innerFunc, outerFunc, joinFunc, joinFuncByKey, joinType))
      
    def OrderBy(self, orderByFunc:Callable[[_TK,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value, desc:bool=False) -> "EnumerableDict[_TK,_TV]":
        self._orderby.clear()
        self._orderby.append((orderByFunc, desc))
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).OrderBy((orderByFunc, desc)))

    def ThenBy(self, orderByFunc:Callable[[_TK,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value, desc:bool=False) -> "EnumerableDict[_TK,_TV]":
        self._orderby.append((orderByFunc, desc))
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).OrderBy(*self._orderby))
        
    def GroupBy(self, groupByFunc:Callable[[_TK,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value) -> "EnumerableDict[_Union[Tuple[_TFV],_TFV], Dict[_TK,_TV]]":
        return EnumerableDict(EnumerableDictBase(self.iterable).GroupBy(groupByFunc))

    def Reverse(self) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDictCatch(self,EnumerableDictBase(self.iterable).Reverse())
        
    def Zip(self, iterable:Dict[_TK2,_TV2], 
        zipFunc:Callable[[_TK,_TV,_TK2,_TV2],_TFV]=lambda inKey, inValue, outKey, outValue: (inValue, outValue),
        zipFuncByKey:Callable[[_TK,_TV,_TK2,_TV2],_TFK]=lambda inKey, inValue, outKey, outValue: inKey
    ) -> "EnumerableDict[_TFK,_TFV]":
        return EnumerableDict(EnumerableDictBase(self.iterable).Zip(EnumerableDictToValue(iterable), zipFunc))



    def Where(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> "EnumerableDict[_TK,_TV]":
        items = dict(EnumerableDictBase(self.iterable).Where(conditionFunc))
        return EnumerableDictCatch(self, items, list(items.keys()))
    
    def OfType(self, *type:Type) -> "EnumerableDict[_TK,_TV]":
        items = dict(EnumerableDictBase(self.iterable).OfType(*type))
        return EnumerableDictCatch(self, items, list(items.keys()))
    
    def OfTypeByKey(self, *type:Type) -> "EnumerableDict[_TK,_TV]":
        items = dict(EnumerableDictBase(self.iterable).OfTypeByKey(*type))
        return EnumerableDictCatch(self, items, list(items.keys()))

    def First(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> Optional["EnumerableDict[_TK,_TV]"]:
        firstValue = EnumerableDictBase(self.iterable).First(conditionFunc)
        if firstValue is None:
            return None
        else:
            return EnumerableDictCatch(self, {None:firstValue[1]}, firstValue[0], oneValue=True)
    
    def Last(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> Optional["EnumerableDict[_TK,_TV]"]:
        lastValue = EnumerableDictBase(self.iterable).Last(conditionFunc)
        if lastValue is None:
            return None
        else:
            return EnumerableDictCatch(self, {None:lastValue[1]}, lastValue[0], oneValue=True)
        
    def Single(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> Optional["EnumerableDict[_TK,_TV]"]:
        singleValue = EnumerableDictBase(self.iterable).Single(conditionFunc)
        if singleValue is None:
            return None
        else:
            return EnumerableDictCatch(self, {None:singleValue[1]}, singleValue[0], oneValue=True)



    def Any(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: value) -> bool:
        return EnumerableDictBase(self.iterable).Any(conditionFunc)
    
    def All(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: value) -> bool:
        return EnumerableDictBase(self.iterable).All(conditionFunc)
    
    def SequenceEqual(self, iterable:Dict[_TK2,_TV2]) -> bool:
        return EnumerableDictBase(self.iterable).SequenceEqual(EnumerableDictToValue(iterable))



    def Accumulate(self, accumulateFunc:Callable[[_TV,_TK,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> "EnumerableList[_TFV]":
        return EnumerableDict(EnumerableDictBase(self.iterable).Accumulate(accumulateFunc))

    def Aggregate(self, accumulateFunc:Callable[[_TV,_TK,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> _TFV:
        return EnumerableDictBase(self.iterable).Aggregate(accumulateFunc)



    def Count(self, value:_TV) -> int:
        return EnumerableDictBase(self.iterable).Count(value)

    @property
    def Lenght(self) -> int:
        return EnumerableDictBase(self.iterable).Lenght()
    
    def Sum(self) -> Optional[_TV]:
        return EnumerableDictBase(self.iterable).Sum()
        
    def Avg(self) -> Optional[_TV]:
        return EnumerableDictBase(self.iterable).Avg()
        
    def Max(self) -> Optional[_TV]:
        return EnumerableDictBase(self.iterable).Max()
        
    def Min(self) -> Optional[_TV]:
        return EnumerableDictBase(self.iterable).Min()

    @overload
    def Set(self): ...
    @overload
    def Set(self, value:_Value): ...
    def Set(self, value=...):
        if value is ...:
            self.Set(self.iterable)
        else:
            value = EnumerableDictToValue(value)
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

    def Add(self, key:_Key, value:_Value):
        EnumerableDictBase(self.iterable).Add(key,EnumerableDictToValue(value))

    def Update(self, key:_TK, value:_Value):
        EnumerableDictBase(self.iterable).Update(key, EnumerableDictToValue(value))

    def Concat(self, *iterable:Dict[_TK2,_TV2]):
        EnumerableDictBase(self.iterable).Concat(*map(EnumerableDictToValue, iterable))

    def Union(self, *iterable:Dict[_TK2,_TV2]):
        EnumerableDictBase(self.iterable).Union(*map(EnumerableDictToValue, iterable))

    @overload
    def Delete(self): ...
    @overload
    def Delete(self, *key:_TK): ...
    def Delete(self, *key):
        if key == ():
            if isinstance(self.ToKey, (list,tuple)):
                key = self.ToKey
            else:
                key = [self.ToKey]
            self._main.Get(*filter(lambda k: not isinstance(k, (list,tuple)),self.keyHistory[:len(self.keyHistory)-1])).Delete(*key)
        else:
            EnumerableDictBase(self.iterable).Delete(*key)

    def Remove(self, *value:_TV):
        EnumerableDictBase(self.iterable).Remove(*map(EnumerableDictToValue, value))

    def RemoveAll(self, *value:_TV):
        EnumerableDictBase(self.iterable).RemoveAll(*map(EnumerableDictToValue, value))

    def Clear(self):
        EnumerableDictBase(self.iterable).Clear()



    def Loop(self, loopFunc:Callable[[_TK,_TV],NoReturn]=lambda key, value: print(key,value)):
        EnumerableDictBase(self.iterable).Loop(loopFunc)



    @property
    def ToKey(self) -> _TK:
        if self.keyHistory == []:
            return None
        else:
            return self.keyHistory[-1]
    
    @property
    def ToValue(self) -> _Union[Dict[_TK,_TV],_TV]:
        if len(self.iterable) == 1 and self._oneValue:
            return self.GetValues().iterable[0]
        else:
            return self.ToDict
    
    @property
    def ToList(self) -> List[_TV]:
        return EnumerableDictBase(self.iterable).ToList()
    
    @property
    def ToDict(self) -> Dict[_TK,_TV]:
        return EnumerableDictBase(self.iterable).ToDict()
    


    @property
    def IsEmpty(self) -> bool:
        return EnumerableDictBase(self.iterable).IsEmpty()

    def ContainsByKey(self, *key:_TK) -> bool:
        return EnumerableDictBase(self.iterable).ContainsByKey(*key)

    def Contains(self, *value:_TV) -> bool:
        return EnumerableDictBase(self.iterable).Contains(*map(EnumerableDictToValue, value))



    def __neg__(self) -> "EnumerableDict[_TK,_TV]":
        return EnumerableDict(EnumerableDictBase(self.Copy().iterable).__neg__())
    
    def __add__(self, iterable:Dict[_TK2,_TV2]) -> "EnumerableDict[_Union[_TK,_TK2],_Union[_TV,_TV2]]":
        return EnumerableDict(EnumerableDictBase(self.Copy().iterable).__add__(EnumerableDictToValue(iterable)))
    
    def __iadd__(self, iterable:Dict[_TK2,_TV2]) -> Self:
        EnumerableDictBase(self.iterable).__iadd__(EnumerableDictToValue(iterable))
        return self

    def __sub__(self, iterable:Dict[_TK2,_TV2]) -> "EnumerableDict[_Union[_TK,_TK2],_Union[_TV,_TV2]]":
        return EnumerableDict(EnumerableDictBase(self.Copy().iterable).__sub__(EnumerableDictToValue(iterable)))
    
    def __isub__(self, iterable:Dict[_TK2,_TV2]) -> Self:
        EnumerableDictBase(self.iterable).__isub__(EnumerableDictToValue(iterable))
        return self
    
    

    def __eq__(self, iterable:Dict[_TK2,_TV2]) -> bool:
        return EnumerableDictBase(self.iterable).__eq__(EnumerableDictToValue(iterable))

    def __ne__(self, iterable:Dict[_TK2,_TV2]) -> bool:
        return EnumerableDictBase(self.iterable).__ne__(EnumerableDictToValue(iterable))
    
    def __contains__(self, value:_Value) -> bool:
        return EnumerableDictBase(self.iterable).__contains__(EnumerableDictToValue(value))



    def __bool__(self) -> bool:
        return EnumerableDictBase(self.iterable).__bool__()
    
    def __len__(self) -> int:
        return EnumerableDictBase(self.iterable).__len__()
    
    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, str(self.iterable))



    def __iter__(self) -> Iterable[Tuple[_TK,_TV]]:
        return EnumerableDictBase(self.GetItems().ToValue).__iter__()
    
    def __getitem__(self, key:_TK) -> _TV:
        return EnumerableDictBase(self.iterable).__getitem__(key)
    
    def __setitem__(self, key:_TK, value:_Value):
        return EnumerableDictBase(self.iterable).__setitem__(key, EnumerableDictToValue(value))

    def __delitem__(self, key:_TK):
        return EnumerableDictBase(self.iterable).__delitem__(key)



__all__ = ["AbstractEnumerable", "EnumerableDict"]
