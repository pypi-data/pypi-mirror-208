from linqex._typing import *
from linqex.abstract.iterablebase import AbstractEnumerableBase

from typing import Dict, List, Callable, Union as _Union, NoReturn, Optional, Tuple, Type, Generic, Self
from numbers import Number
from collections.abc import Iterable
import itertools

class EnumerableListBase(AbstractEnumerableBase, Iterable[_TV], Generic[_TV]):
    
    def __init__(self, iterable:Optional[List[_TV]]=None):
        if iterable is None:
            iterable:List[_TV] = list()
        if isinstance(iterable, list):
            self.iterable:List[_TV] = iterable
        elif isinstance(iterable, (tuple, set)):
            self.iterable:List[_TV] = list(iterable)
        else:
            raise TypeError("Must be tuple, set and list, not {}".format(str(type(iterable))[8,-2]))

    def Get(self, *key:int) -> _Union[List[_TV],_TV]:
        iterable = self.iterable
        for k in key:
            if  k < len(iterable):
                iterable = iterable[k]
            else:
                raise IndexError(k)
        return iterable
    
    def GetKey(self, value:_TV) -> int:
        return self.iterable.index(value)
    
    def GetKeys(self) -> List[int]:
        return list(range(len(self.Get())))
    
    def GetValues(self) -> List[_TV]:
        return self.Get()
    
    def GetItems(self) -> List[Tuple[int,_TV]]:
        return list(enumerate(self.Get()))
    
    def Copy(self) -> List[_TV]:
        return self.Get().copy()



    def Take(self, count:int) -> List[_TV]:
        return self.Get()[:count]
    
    def TakeLast(self, count:int) -> List[_TV]:
        return self.Skip(self.Lenght()-count)
    
    def Skip(self, count:int) -> List[_TV]:
        return self.Get()[count:]
    
    def SkipLast(self, count:int) -> List[_TV]:
        return self.Take(self.Lenght()-count)
    
    def Select(self, selectFunc:Callable[[_TV],_TFV]=lambda value: value) -> List[_TFV]:
        return list(map(selectFunc,self.Get()))
    
    def Distinct(self, distinctFunc:Callable[[_TV],_TFV]=lambda value: value) -> List[_TV]:
        newIterable = self.Copy()
        indexStep = 0
        for key, value in self.GetItems():
            if EnumerableListBase(EnumerableListBase(newIterable).Select(distinctFunc)).Count(distinctFunc(value)) > 1:
                EnumerableListBase(newIterable).Delete(key-indexStep)
                indexStep += 1
        return newIterable
    
    def Except(self, exceptFunc:Callable[[_TV],_TFV]=lambda value: value, *value:_TV) -> List[_TV]:
        newIterable = EnumerableListBase()
        for v in self.Get():
            if not exceptFunc(v) in value:
                newIterable.Add(v)
        return newIterable.Get()

    def Join(self, iterable: List[_TV2], 
        innerFunc:Callable[[_TV],_TFV]=lambda value: value, 
        outerFunc:Callable[[_TV2],_TFV]=lambda value: value, 
        joinFunc:Callable[[_TV,_TV2],_TFV2]=lambda inValue, outValue: (inValue, outValue),
        joinType:JoinType=JoinType.INNER
    ) -> List[_TFV2]:
        def innerJoin(innerIterable:List[_TV], outerIterable:List[_TV2], newIterable:EnumerableListBase[Tuple[_TV,_TV2]]):
            nonlocal outerFunc, innerFunc
            for inValue in innerIterable:
                outer = EnumerableListBase(outerIterable).Where(lambda outValue: outerFunc(outValue) == innerFunc(inValue))
                if outer != []:
                    for out in outer:
                        newIterable.Add((inValue, out[1]))
        def leftJoin(innerIterable:List[_TV], outerIterable:List[_TV2], newIterable:EnumerableListBase[Tuple[_TV,Optional[_TV2]]]):
            nonlocal outerFunc, innerFunc
            for inValue in innerIterable:
                outer = EnumerableListBase(outerIterable).First(lambda outValue: outerFunc(outValue) == innerFunc(inValue))
                if outer is None:
                    newIterable.Add((inValue, None))
                else:
                    newIterable.Add((inValue, outer[1]))
        def rightJoin(innerIterable:List[_TV], outerIterable:List[_TV2], newIterable:EnumerableListBase[Tuple[_TV2,Optional[_TV]]]):
            nonlocal outerFunc, innerFunc
            for outValue in outerIterable:
                inner = EnumerableListBase(innerIterable).First(lambda inValue: outerFunc(outValue) == innerFunc(inValue))
                if inner is None:
                    newIterable.Add((None, outValue))
                else:
                    newIterable.Add((inner[1], outValue))
        newIterable = EnumerableListBase()
        if joinType == JoinType.INNER:
            joinTypeFunc = innerJoin
        elif joinType == JoinType.LEFT:
            joinTypeFunc = leftJoin
        elif joinType == JoinType.RIGHT:
            joinTypeFunc = rightJoin
        joinTypeFunc(self.Get(), iterable, newIterable)
        return newIterable.Select(lambda value: joinFunc(value[0], value[1]))         
      
    def OrderBy(self, *orderByFunc:Tuple[Callable[[_TV],_Union[Tuple[_TFV],_TFV]],_Desc]) -> List[_TV]:
        if orderByFunc == ():
            orderByFunc = ((lambda value: value, False))
        iterable = self.Get()
        orderByFunc:list = list(reversed(orderByFunc))
        for func, desc in orderByFunc:
            iterable = sorted(iterable, key=func, reverse=desc)
        return list(iterable)
        
    def GroupBy(self, groupByFunc:Callable[[_TV],_Union[Tuple[_TFV],_TFV]]=lambda value: value) -> List[Tuple[_Union[Tuple[_TFV],_TFV], List[_TV]]]:
        iterable = self.OrderBy((groupByFunc, False))
        iterable = itertools.groupby(iterable, groupByFunc)
        return [(keys, list(group)) for keys, group in iterable]

    def Reverse(self) -> List[_TV]:
        return list(reversed(self.Get()))
        
    def Zip(self, iterable:List[_TV2], zipFunc:Callable[[_TV,_TV2],_TFV]=lambda inValue, outValue: (inValue, outValue)) -> List[_TFV]:
        newIterable = EnumerableListBase(list(zip(self.GetValues(), EnumerableListBase(iterable).GetValues())))
        return newIterable.Select(lambda value: zipFunc(value[0], value[1]))



    def Where(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> List[Tuple[int,_TV]]:
        result = list()
        for index, value in self.GetItems():
            if conditionFunc(value):
                result.append((index, value))
        return result
    
    def OfType(self, *type:Type) -> List[Tuple[int,_TV]]:
        return self.Where(lambda value: isinstance(value,type))
    
    def First(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> Optional[Tuple[int,_TV]]:
        for index, value in self.GetItems():
            if conditionFunc(value):
                return (index,value)
        return None
    
    def Last(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> Optional[Tuple[int,_TV]]:
        result = self.Where(conditionFunc)
        if len(result) == 0:
            return None
        else:
            return result[-1]
        
    def Single(self, conditionFunc:Callable[[_TV],bool]=lambda value: True) -> Optional[Tuple[int,_TV]]:
        result = self.Where(conditionFunc)
        if len(result) != 1:
            return None
        else:
            return result[0]



    def Any(self, conditionFunc:Callable[[_TV],bool]=lambda value: value) -> bool:
        result = False
        for value in self.Get():
            if conditionFunc(value):
                result = True
                break
        return result
    
    def All(self, conditionFunc:Callable[[_TV],bool]=lambda value: value) -> bool:
        result = True
        for value in self.Get():
            if not conditionFunc(value):
                result = False
                break
        return result
    
    def SequenceEqual(self, iterable:List[_TV2]) -> bool:
        if self.Lenght() != len(iterable):
            return False
        for value in self.Get():
            if not value in iterable:
                return False
        return True



    def Accumulate(self, accumulateFunc:Callable[[_TV,_TV],_TFV]=lambda temp, nextValue: temp + nextValue) -> List[_TFV]:
        return list(itertools.accumulate(self.Get(), lambda temp, next: accumulateFunc(temp, next)))

    def Aggregate(self, accumulateFunc:Callable[[_TV,_TV],_TFV]=lambda temp, nextValue: temp + nextValue) -> _TFV:
        return self.Accumulate(accumulateFunc)[-1]




    def Count(self, value:_TV) -> int:
        return self.GetValues().count(value)
        
    def Lenght(self) -> int:
        return len(self.Get())
    
    def Sum(self) -> Optional[_TV]:
        if self.OfType(Number):
            return sum(self.Get())
        else:
            return None
        
    def Avg(self) -> Optional[_TV]:
        if self.OfType(Number):
            return sum(self.Get()) / self.Lenght()
        else:
            return None
        
    def Max(self) -> Optional[_TV]:
        if self.OfType(Number):
            return max(self.Get())
        else:
            return None
        
    def Min(self) -> Optional[_TV]:
        iterable = self.GetValues()
        if self.OfType(Number):
            return min(iterable)
        else:
            return None



    def Add(self, value:_Value):
        self.Get().append(value)

    def Prepend(self, value:_Value):
        newIterable = [value]
        self.Clear()
        self.Concat(newIterable)

    def Insert(self, key:_Key, value:_Value):
        self.Get().insert(key, value)

    def Update(self, key:int, value:_Value):
        self.Get()[key] = value

    def Concat(self, *iterable:List[_Value]):
        for i in iterable:
            self.Get().extend(i)

    def Union(self, *iterable:List[_Value]):
        if not iterable in [(),[]]:
            iterable:list = list(iterable)
            newIterable = EnumerableListBase()
            filter = dict(self.Where(lambda v: v in iterable[0]))
            EnumerableListBase(filter).Loop(lambda v: newIterable.Add(v))
            iterable.pop(0)
            self.Clear()
            self.Concat(newIterable.Get())
            self.Union(*iterable)

    def Delete(self, *key:int):
        i = 0
        for k in sorted(key):
            k -= i
            self.Get().pop(k)
            i += 1

    def Remove(self, *value:_TV):
        for v in value:
            self.Get().remove(v)

    def RemoveAll(self, *value:_TV):
        for v in value:
            while True:
                if self.Contains(v):
                    self.Remove(v)
                else:
                    break

    def Clear(self):
        self.Get().clear()



    def Loop(self, loopFunc:Callable[[_TV],NoReturn]=lambda value: print(value)):
        for value in self.Get():
            loopFunc(value)



    def ToDict(self) -> Dict[int,_TV]:
        return dict(self.GetItems())

    def ToList(self) -> List[_TV]:
        return self.Get()



    def IsEmpty(self) -> bool:
        return self.Get() in [[],{}]

    def ContainsByKey(self, *key:int) -> bool:
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



    def __neg__(self) -> List[_TV]:
        newIterable = EnumerableListBase(self.Copy())
        return newIterable.Reverse()
    
    def __add__(self, iterable:List[_TV2]) -> List[_Union[_TV,_TV2]]:
        newIterable = EnumerableListBase(self.Copy())
        newIterable.Concat(iterable)
        return newIterable.Get()
    
    def __iadd__(self, iterable:List[_TV2]) -> Self:
        self.Concat(iterable)
        return self
    
    def __sub__(self, iterable:List[_TV2]) -> List[_Union[_TV,_TV2]]:
        newIterable = EnumerableListBase(self.Copy())
        newIterable.Union(iterable)
        return newIterable.Get()
    
    def __isub__(self, iterable:List[_TV2]) -> Self:
        self.Union(iterable)
        return self

    

    def __eq__(self, iterable:List[_TV2]) -> bool:
        return self.SequenceEqual(iterable)

    def __ne__(self, iterable:List[_TV2]) -> bool:
        return not self.SequenceEqual(iterable)
    
    def __contains__(self, value:_Value) -> bool:
        return self.Contains(value)



    def __bool__(self) -> bool:
        return not self.IsEmpty()
    
    def __len__(self) -> int:
        return self.Lenght()
    
    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, str(self.iterable))



    def __iter__(self) -> Iterable[_TV]:
        return iter(self.GetValues())
    
    def __getitem__(self, key:int) -> _TV:
        return self.Get(key)
    
    def __setitem__(self, key:int, value:_Value):
        self.Update(key, value)

    def __delitem__(self, key:int):
        self.Delete(key)

    @staticmethod
    def Range(start:int, stop:int, step:int=1) -> List[int]:
        return list(range(start,stop,step))
    @staticmethod
    def Repeat(value:_TV, count:int) -> List[_TV]:
        return list(itertools.repeat(value, count))



__all__ = ["AbstractEnumerableBase", "EnumerableListBase"]
