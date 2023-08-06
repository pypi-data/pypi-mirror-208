from linqex._typing import *
from linqex.abstract.iterablebase import AbstractEnumerableBase

from typing import Dict, List, Callable, Union as _Union, NoReturn, Optional, Tuple, Type, Generic, Self
from numbers import Number
from collections.abc import Iterable
import itertools

class EnumerableDictBase(AbstractEnumerableBase, Iterable[Tuple[_TK,_TV]], Generic[_TK,_TV]):
    
    def __init__(self, iterable:Optional[Dict[_TK,_TV]]=None):
        if iterable is None:
            iterable:Dict[_TK,_TV] = dict()
        if isinstance(iterable, dict):
            self.iterable:Dict[_TK,_TV] = iterable
        elif isinstance(iterable, list):
            self.iterable:Dict[_TK,_TV] = dict(iterable)
        else:
            raise TypeError("Must be dict, not {}".format(str(type(iterable))[8,-2]))

    def Get(self, *key:_TK) -> _Union[Dict[_TK,_TV],_TV]:
        iterable = self.iterable
        for k in key:
            if  k in EnumerableDictBase(iterable).GetKeys():
                iterable = iterable[k]
            else:
                raise KeyError(k)
        return iterable
    
    def GetKey(self, value:_TV) -> _TK:
        return {v: k for k, v in self.GetItems()}[value]
    
    def GetKeys(self) -> List[_TK]:
        return list(self.Get().keys())
    
    def GetValues(self) -> List[_TV]:
        return list(self.Get().values())
    
    def GetItems(self) -> List[Tuple[_TK,_TV]]:
        return list(self.Get().items())
    
    def Copy(self) -> Dict[_TK,_TV]:
        return self.Get().copy()



    def Take(self, count:int) -> Dict[_TK,_TV]:
        return dict(self.GetItems()[:count])
    
    def TakeLast(self, count:int) -> Dict[_TK,_TV]:
        return self.Skip(self.Lenght()-count)
    
    def Skip(self, count:int) -> Dict[_TK,_TV]:
        return dict(self.GetItems()[count:])
    
    def SkipLast(self, count:int) -> Dict[_TK,_TV]:
        return self.Take(self.Lenght()-count)
    
    def Select(self, 
        selectFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value, 
        selectFuncByKey:Callable[[_TK,_TV],_TFK]=lambda key, value: key
    ) -> Dict[_TFK,_TFV]:
        return dict(list(map(lambda key, value: (selectFuncByKey(key,value), selectFunc(key,value)), self.GetKeys(), self.GetValues())))
    
    def Distinct(self, distinctFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value) -> Dict[_TK,_TV]:
        newIterable = self.Copy()
        for key, value in self.GetItems():
            if EnumerableDictBase(EnumerableDictBase(newIterable).Select(distinctFunc)).Count(distinctFunc(key, value)) > 1:
                EnumerableDictBase(newIterable).Delete(key)
        return newIterable
    
    def Except(self, exceptFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value, *value:_TV) -> Dict[_TK,_TV]:
        newIterable = EnumerableDictBase()
        for k, v in self.GetItems():
            if not exceptFunc(k,v) in value:
                newIterable.Add(k,v)
        return newIterable.Get()

    def Join(self, iterable: Dict[_TK2,_TV2], 
        innerFunc:Callable[[_TK,_TV],_TFV]=lambda key, value: value, 
        outerFunc:Callable[[_TK2,_TV2],_TFV]=lambda key, value: value, 
        joinFunc:Callable[[_TK,_TV,_TK2,_TV2],_TFV2]=lambda inKey, inValue, outKey, outValue: (inValue, outValue),
        joinFuncByKey:Callable[[_TK,_TV,_TK2,_TV2],_TFK2]=lambda inKey, inValue, outKey, outValue: inKey,
        joinType:JoinType=JoinType.INNER
    ) -> Dict[_TFK2,_TFV2]:
        def innerJoin(innerIterable:Dict[_TK,_TV], outerIterable:Dict[_TK2,_TV2], newIterable:List[Tuple[_TK,_TV,_TK2,_TV2]]):
            nonlocal outerFunc, innerFunc
            for inKey, inValue in EnumerableDictBase(innerIterable).GetItems():
                outer = EnumerableDictBase(outerIterable).Where(lambda outKey, outValue: outerFunc(outKey,outValue) == innerFunc(inKey, inValue))
                if outer != []:
                    for outKey, outValue in outer:
                        newIterable.append((inKey, inValue, outKey, outValue))
        def leftJoin(innerIterable:Dict[_TK,_TV], outerIterable:Dict[_TK2,_TV2], newIterable:List[Tuple[_TK,_TV,_TK2,_TV2]]):
            nonlocal outerFunc, innerFunc
            for inKey, inValue in EnumerableDictBase(innerIterable).GetItems():
                outer = EnumerableDictBase(outerIterable).First(lambda outKey, outValue: outerFunc(outKey, outValue) == innerFunc(inKey, inValue))
                if outer is None:
                    newIterable.append((inKey, inValue, None, None))
                else:
                    newIterable.append((inKey, inValue, outer[0], outer[1]))
        def rightJoin(innerIterable:Dict[_TK,_TV], outerIterable:Dict[_TK2,_TV2], newIterable:List[Tuple[_TK,_TV,_TK2,_TV2]]):
            nonlocal outerFunc, innerFunc
            for outKey, outValue in EnumerableDictBase(outerIterable).GetItems():
                inner = EnumerableDictBase(innerIterable).First(lambda inKey, inValue: outerFunc(outKey, outValue) == innerFunc(inKey, inValue))
                if inner is None:
                    newIterable.append((None, None, outKey, outValue))
                else:
                    newIterable.append((inner[0], inner[1], outKey, outValue))        
        newIterable:List[Tuple[_TK,_TV,_TK2,_TV2]] = []
        if joinType == JoinType.INNER:
            joinTypeFunc = innerJoin
        elif joinType == JoinType.LEFT:
            joinTypeFunc = leftJoin
        elif joinType == JoinType.RIGHT:
            joinTypeFunc = rightJoin
        joinTypeFunc(self.Get(), iterable, newIterable)
        joinKeys = list(map(lambda value: joinFuncByKey(value[0], value[1], value[2], value[3]), newIterable))
        joinValues = list(map(lambda value: joinFunc(value[0], value[1], value[2], value[3]), newIterable))
        joinItems = list(zip(joinKeys, joinValues))
        return dict(joinItems)        
      
    def OrderBy(self, *orderByFunc:Tuple[Callable[[_TK,_TV],_Union[Tuple[_TFV],_TFV]],_Desc]) -> Dict[_TK,_TV]:
        if orderByFunc == ():
            orderByFunc = ((lambda key, value: value, False))
        iterable = self.GetItems()
        orderByFunc = list(reversed(orderByFunc))
        for func, desc in orderByFunc:
            iterable = sorted(iterable, key=lambda x: func(x[0], x[1]), reverse=desc)
        return dict(iterable)
        
    def GroupBy(self, groupByFunc:Callable[[_TK,_TV],_Union[Tuple[_TFV],_TFV]]=lambda key, value: value) -> Dict[_Union[Tuple[_TFV],_TFV], Dict[_TK,_TV]]:
        iterable = EnumerableDictBase(self.OrderBy((groupByFunc, False))).GetItems()
        iterable = itertools.groupby(iterable, lambda items: groupByFunc(items[0], items[1]))
        return {keys : dict(group) for keys, group in iterable}

    def Reverse(self) -> Dict[_TK,_TV]:
            return dict(zip(reversed(self.GetKeys()),reversed(self.GetValues())))
        
    def Zip(self, iterable:Dict[_TK2,_TV2], 
        zipFunc:Callable[[_TK,_TV,_TK2,_TV2],_TFV]=lambda inKey, inValue, outKey, outValue: (inValue, outValue),
        zipFuncByKey:Callable[[_TK,_TV,_TK2,_TV2],_TFK]=lambda inKey, inValue, outKey, outValue: inKey
    ) -> Dict[_TFK,_TFV]:
        newIterable = EnumerableDictBase(dict(zip(self.GetKeys(),list(zip(self.GetValues(), EnumerableDictBase(iterable).GetItems())))))
        return newIterable.Select(lambda key, value: zipFunc(key, value[0], value[1][0], value[1][1]), lambda key, value: zipFuncByKey(key, value[0], value[1][0], value[1][1]))



    def Where(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> List[Tuple[_TK,_TV]]:
        result = list()
        for key, value in self.GetItems():
            if conditionFunc(key, value):
                result.append((key, value))
        return result
    
    def OfType(self, *type:Type) -> List[Tuple[_TK,_TV]]:
        return self.Where(lambda key, value: isinstance(value,type))
    
    def OfTypeByKey(self, *type:Type) -> List[Tuple[_TK,_TV]]:
        return self.Where(lambda key, value: isinstance(key,type))
    
    def First(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> Optional[Tuple[_TK,_TV]]:
        for key, value in self.GetItems():
            if conditionFunc(key, value):
                return (key,value)
        return None
    
    def Last(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> Optional[Tuple[_TK,_TV]]:
        result = self.Where(conditionFunc)
        if len(result) == 0:
            return None
        else:
            return result[-1]
        
    def Single(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: True) -> Optional[Tuple[_TK,_TV]]:
        result = self.Where(conditionFunc)
        if len(result) != 1:
            return None
        else:
            return result[0]



    def Any(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: value) -> bool:
        result = False
        for key, value in self.GetItems():
            if conditionFunc(key, value):
                result = True
                break
        return result
    
    def All(self, conditionFunc:Callable[[_TK,_TV],bool]=lambda key, value: value) -> bool:
        result = True
        for key, value in self.GetItems():
            if not conditionFunc(key, value):
                result = False
                break
        return result
    
    def SequenceEqual(self, iterable:Dict[_TK2,_TV2]) -> bool:
        if self.Lenght() != len(iterable):
            return False
        for key, value in self.GetItems():
            if key in iterable.keys():
                if not iterable[key] == value:
                    return False
            else:
                return False
        return True



    def Accumulate(self, accumulateFunc:Callable[[_TV,_TK,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> Dict[_TK,_TFV]:
        firstTemp:bool = True
        def FirstTemp(temp):
            nonlocal firstTemp
            if firstTemp:
                firstTemp = False
                return temp[1]
            else:
                return temp
        if not self.IsEmpty():
            result = dict([self.GetItems()[0]])
            result.update(dict(zip(self.GetKeys()[1:], list(itertools.accumulate(self.GetItems(), lambda temp, next: accumulateFunc(FirstTemp(temp), next[0], next[1])))[1:])))
            return result
        else:
            return {}
        
    def Aggregate(self, accumulateFunc:Callable[[_TV,_TK,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> _TFV:
        return EnumerableDictBase(self.Accumulate(accumulateFunc)).GetValues()[-1]



    def Count(self, value:_TV) -> int:
        return self.GetValues().count(value)
        
    def Lenght(self) -> int:
        return len(self.Get())
    
    def Sum(self) -> Optional[_TV]:
        if self.OfType(Number):
            return sum(self.GetValues())
        else:
            return None
        
    def Avg(self) -> Optional[_TV]:
        if self.OfType(Number):
            return sum(self.GetValues()) / self.Lenght()
        else:
            return None
        
    def Max(self) -> Optional[_TV]:
        if self.OfType(Number):
            return max(self.GetValues())
        else:
            return None
        
    def Min(self) -> Optional[_TV]:
        if self.OfType(Number):
            return min(self.GetValues())
        else:
            return None




    def Add(self, key:_Key, value:_Value):
        self.Get()[key] = value

    def Update(self, key:_TK, value:_Value):
        if key in self.GetKeys():
            self.Get()[key] = value
        else:
            raise KeyError(key)

    def Concat(self, *iterable:Dict[_TK2,_TV2]):
        for i in iterable:
            self.Get().update(i)

    def Union(self, *iterable:Dict[_TK2,_TV2]):
        if not iterable in [(),[]]:
            iterable:list = list(iterable)
            newIterable = EnumerableDictBase()
            filter = dict(self.Where(lambda k, v: v in iterable[0].values() and k in iterable[0].keys()))
            EnumerableDictBase(filter).Loop(lambda k, v: newIterable.Add(k, v))
            iterable.pop(0)
            self.Clear()
            self.Concat(newIterable.Get())
            self.Union(*iterable)

    def Delete(self, *key:_TK):
        for k in key:
            self.Get().pop(k)

    def Remove(self, *value:_TV):
        for v in value:
            self.Get().pop(self.First(lambda k, val: val == v)[0])

    def RemoveAll(self, *value:_TV):
        for v in value:
            while True:
                if self.Contains(v):
                    self.Remove(v)
                else:
                    break

    def Clear(self):
        self.Get().clear()



    def Loop(self, loopFunc:Callable[[_TK,_TV],NoReturn]=lambda key, value: print(key,value)):
        for key, value in self.GetItems():
            loopFunc(key, value)



    def ToDict(self) -> Dict[_TK,_TV]:
        return self.Get()

    def ToList(self) -> List[_TV]:
        return self.GetValues()



    def IsEmpty(self) -> bool:
        return self.Get() in [[],{}]
    
    def ContainsByKey(self, *key:_TK) -> bool:
        iterable = self.GetKeys()
        for k in key:
            if not k in iterable:
                return False
        return True
    
    def Contains(self, *value:_TV) -> bool:
        iterable = self.GetValues()
        for v in value:
            if not v in iterable:
                return False
        return True



    def __neg__(self) -> Dict[_TK,_TV]:
        newIterable = EnumerableDictBase(self.Copy())
        return newIterable.Reverse()
    
    def __add__(self, iterable:Dict[_TK2,_TV2]) -> Dict[_Union[_TK,_TK2],_Union[_TV,_TV2]]:
        newIterable = EnumerableDictBase(self.Copy())
        newIterable.Concat(iterable)
        return newIterable.Get()

    def __iadd__(self, iterable:Dict[_TK2,_TV2]) -> Self:
        self.Concat(iterable)
        return self
    
    def __sub__(self, iterable:Dict[_TK2,_TV2]) -> Dict[_Union[_TK,_TK2],_Union[_TV,_TV2]]:
        newIterable = EnumerableDictBase(self.Copy())
        newIterable.Union(iterable)
        return newIterable.Get()
    
    def __isub__(self, iterable:Dict[_TK2,_TV2]) -> Self:
        self.Union(iterable)
        return self

    

    def __eq__(self, iterable:Dict[_TK2,_TV2]) -> bool:
        return self.SequenceEqual(iterable)

    def __ne__(self, iterable:Dict[_TK2,_TV2]) -> bool:
        return not self.SequenceEqual(iterable)
    
    def __contains__(self, value:_Value) -> bool:
        return self.Contains(value)



    def __bool__(self) -> bool:
        return not self.IsEmpty()
    
    def __len__(self) -> int:
        return self.Lenght()
    
    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, str(self.iterable))



    def __iter__(self) -> Iterable[Tuple[_TK,_TV]]:
        return iter(self.GetItems())
    
    def __getitem__(self, key:_TK) -> _TV:
        return self.Get(key)
    
    def __setitem__(self, key:_TK, value:_Value):
        if key in self.Get():
            self.Update(key, value)
        else:
            self.Add(key, value)

    def __delitem__(self, key:_TK):
        self.Delete(key)



__all__ = ["AbstractEnumerableBase","EnumerableDictBase"]
