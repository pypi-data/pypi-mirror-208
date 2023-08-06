from linqex._typing import *
from linqex.abstract.iterablebase import AbstractEnumerableBase
from linqex.build.iterlistbase import EnumerableListBase

from typing import Dict, List, Callable, Union as _Union, NoReturn, Optional, Tuple, Type, Generic, Self
from collections.abc import Iterable
import itertools

class EnumerableItemBase(EnumerableListBase, Iterable[Tuple[int,_TV]], Generic[_TK,_TV]):
        
    def __init__(self, iterable:Optional[List[_TV]]=None):
        super().__init__(iterable)

    def Get(self, *key:int) -> _Union[List[_TV],_TV]:
        return super().Get(*key)
    
    def GetKey(self, value:_TV) -> int:
        return super().GetKey(value)
    
    def GetKeys(self) -> List[int]:
        return super().GetKeys()
    
    def GetValues(self) -> List[_TV]:
        return super().GetValues()
    
    def GetItems(self) -> List[Tuple[int,_TV]]:
        return super().GetItems()
    
    def Copy(self) -> List[_TV]:
        return super().Copy()



    def Take(self, count:int) -> List[_TV]:
        return super().Take(count)
    
    def TakeLast(self, count:int) -> List[_TV]:
        return super().TakeLast(count)
    
    def Skip(self, count:int) -> List[_TV]:
        return super().Skip(count)
    
    def SkipLast(self, count:int) -> List[_TV]:
        return super().SkipLast(count)

    def Select(self, selectFunc:Callable[[int,_TV],_TFV]=lambda key, value: value) -> List[_TFV]:
        return list(map(selectFunc, self.GetKeys(), self.GetValues()))
    
    def Distinct(self, distinctFunc:Callable[[int,_TV],_TFV]=lambda key, value: value) -> List[_TV]:
        newIterable = self.Copy()
        indexStep = 0
        for key, value in self.GetItems():
            if EnumerableItemBase(EnumerableItemBase(newIterable).Select(distinctFunc)).Count(distinctFunc(key, value)) > 1:
                EnumerableItemBase(newIterable).Delete(key-indexStep)
                indexStep += 1
        return newIterable
    
    def Except(self, exceptFunc:Callable[[int,_TV],_TFV]=lambda key, value: value, *value:_TV) -> List[_TV]:
        newIterable = EnumerableItemBase()
        for k, v in self.GetItems():
            if not exceptFunc(k, v) in value:
                newIterable.Add(k, v)
        return newIterable.Get()

    def Join(self, iterable: List[_TV2], 
        innerFunc:Callable[[int,_TV],_TFV]=lambda key, value: value, 
        outerFunc:Callable[[int,_TV2],_TFV]=lambda key, value: value, 
        joinFunc:Callable[[int,_TV,int,_TV2],_TFV2]=lambda inKey, inValue, outKey, outValue: (inValue, outValue),
        joinType:JoinType=JoinType.INNER
    ) -> List[_TFV2]:
        def innerJoin(innerIterable:List[_TV], outerIterable:List[_TV2], newIterable:EnumerableItemBase[Tuple[_TV,_TV2]]):
            nonlocal outerFunc, innerFunc
            for inKey, inValue in EnumerableItemBase(innerIterable).GetItems():
                outer = EnumerableItemBase(outerIterable).Where(lambda outKey, outValue: outerFunc(outKey, outValue) == innerFunc(inKey, inValue))
                if outer != []:
                    for out in outer:
                        newIterable.Add(-1,(inKey, inValue, out[0], out[1]))
        def leftJoin(innerIterable:List[_TV], outerIterable:List[_TV2], newIterable:EnumerableItemBase[Tuple[_TV,Optional[_TV2]]]):
            nonlocal outerFunc, innerFunc
            for inKey, inValue in EnumerableItemBase(innerIterable).GetItems():
                outer = EnumerableItemBase(outerIterable).Where(lambda outKey, outValue: outerFunc(outKey, outValue) == innerFunc(inKey, inValue))
                if outer is None:
                    newIterable.Add(-1,(inKey, inValue, None, None))
                else:
                    newIterable.Add((inKey, inValue, outer[0], outer[1]))
        def rightJoin(innerIterable:List[_TV], outerIterable:List[_TV2], newIterable:EnumerableItemBase[Tuple[_TV2,Optional[_TV]]]):
            nonlocal outerFunc, innerFunc
            for outKey, outValue in EnumerableItemBase(outerIterable).GetItems():
                inner = EnumerableItemBase(innerIterable).First(lambda inKey, inValue: outerFunc(outKey, outValue) == innerFunc(inKey, inValue))
                if inner is None:
                    newIterable.Add(-1,(None, None, outKey, outValue))
                else:
                    newIterable.Add(-1,(inner[0], inner[1], outKey, outValue))
        newIterable = EnumerableItemBase()
        if joinType == JoinType.INNER:
            joinTypeFunc = innerJoin
        elif joinType == JoinType.LEFT:
            joinTypeFunc = leftJoin
        elif joinType == JoinType.RIGHT:
            joinTypeFunc = rightJoin
        joinTypeFunc(self.Get(), iterable, newIterable)
        return newIterable.Select(lambda key, value: joinFunc(value[0], value[1], value[2], value[3]))         
      
    def OrderBy(self, *orderByFunc:Tuple[Callable[[int,_TV],_Union[Tuple[_TFV],_TFV]],_Desc]) -> List[_TV]:
        if orderByFunc == ():
            orderByFunc = ((lambda key, value: value))
        iterable = self.GetItems()
        orderByFunc = list(reversed(orderByFunc))
        for func, desc in orderByFunc:
            iterable = sorted(iterable, key=lambda x: func(x[0], x[1]), reverse=desc)
        return list(zip(*iterable))[1]
        
    def GroupBy(self, groupByFunc:Callable[[int,_TV],_Union[Tuple[_TFV],_TFV]]=lambda value: value) -> List[Tuple[_Union[Tuple[_TFV],_TFV], List[_TV]]]:
        iterable = EnumerableItemBase(self.OrderBy((groupByFunc, False))).GetItems()
        iterable = itertools.groupby(iterable, lambda items: groupByFunc(items[0], items[1]))
        return [(keys, list(zip(*list(group)))[1]) for keys, group in iterable]
    
    def Reverse(self) -> List[_TV]:
        return super().Reverse()
          
    def Zip(self, iterable:List[_TV2], zipFunc:Callable[[int,_TV,int,_TV2],_TFV]=lambda inKey, inValue, outKey, outValue: (inValue, outValue)) -> List[_TFV]:
        newIterable = EnumerableItemBase(list(zip(self.GetValues(), EnumerableItemBase(iterable).GetKeys(), EnumerableItemBase(iterable).GetValues())))
        return newIterable.Select(lambda key, value: zipFunc(key, value[0], value[1], value[2]))



    def Where(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> List[Tuple[int,_TV]]:
        result = list()
        for index, value in self.GetItems():
            if conditionFunc(index, value):
                result.append((index, value))
        return result
    
    def OfType(self, *type:Type) -> List[Tuple[int,_TV]]:
        return self.Where(lambda key, value: isinstance(value,type))
    
    def First(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> Optional[Tuple[int,_TV]]:
        for index, value in self.GetItems():
            if conditionFunc(index, value):
                return (index,value)
        return None
    
    def Last(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> Optional[Tuple[int,_TV]]:
        result = self.Where(conditionFunc)
        if len(result) == 0:
            return None
        else:
            return result[-1]
        
    def Single(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: True) -> Optional[Tuple[int,_TV]]:
        result = self.Where(conditionFunc)
        if len(result) != 1:
            return None
        else:
            return result[0]



    def Any(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: value) -> bool:
        result = False
        for key, value in self.GetItems():
            if conditionFunc(key, value):
                result = True
                break
        return result
    
    def All(self, conditionFunc:Callable[[int,_TV],bool]=lambda key, value: value) -> bool:
        result = True
        for key, value in self.GetItems():
            if not conditionFunc(key, value):
                result = False
                break
        return result
 
    def SequenceEqual(self, iterable:List[_TV2]) -> bool:
        return super().SequenceEqual(iterable)



    def Accumulate(self, accumulateFunc:Callable[[_TV,int,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> List[_TFV]:
        firstTemp:bool = True
        def FirstTemp(temp):
            nonlocal firstTemp
            if firstTemp:
                firstTemp = False
                return temp[1]
            else:
                return temp
        if not self.IsEmpty():
            result = [self.GetValues()[0]]
            result.extend(list(itertools.accumulate(self.GetItems(), lambda temp, next: accumulateFunc(FirstTemp(temp), next[0], next[1])))[1:])
            return result
        else:
            return []

    def Aggregate(self, accumulateFunc:Callable[[_TV,int,_TV],_TFV]=lambda temp, key, nextValue: temp + nextValue) -> _TFV:
        return self.Accumulate(accumulateFunc)[-1]



    def Count(self, value:_TV) -> int:
        return super().Count(value)
        
    def Lenght(self) -> int:
        return super().Lenght()
    
    def Sum(self) -> Optional[_TV]:
        return super().Sum()
        
    def Avg(self) -> Optional[_TV]:
        return super().Avg()
        
    def Max(self) -> Optional[_TV]:
        return super().Max()
        
    def Min(self) -> Optional[_TV]:
        return super().Min()



    def Add(self, key:Optional[int], value:_Value):
        if key is None:
            super().Add(value)
        else:
            self.Insert(key, value)

    def Prepend(self, key:Optional[int], value:_Value):
        if key is None:
            super().Prepend(value)
        else:
            self.Insert(key, value)

    def Insert(self, key:_Key, value:_Value):
        super().Insert(key, value)

    def Update(self, key:int, value:_Value):
        super().Update(key, value)

    def Concat(self, *iterable:List[_Value]):
        super().Concat(*iterable)

    def Union(self, *iterable:List[_Value]):
        super().Union(*iterable)

    def Delete(self, *key:int):
        super().Delete(*key)

    def Remove(self, *value:_TV):
        super().Remove(*value)

    def RemoveAll(self, *value:_TV):
        super().RemoveAll(*value)

    def Clear(self):
        super().Clear()



    def Loop(self, loopFunc:Callable[[int,_TV],NoReturn]=lambda value: print(value)):
        for key, value in self.GetItems():
            loopFunc(key, value)



    def ToDict(self) -> Dict[int,_TV]:
        return super().ToDict()

    def ToList(self) -> List[_TV]:
        return super().ToList()



    def IsEmpty(self) -> bool:
        return super().IsEmpty()

    def ContainsByKey(self, *key:int) -> bool:
        return super().ContainsByKey(*key)

    def Contains(self, *value:_TV) -> bool:
        return super().Contains(*value)



    def __neg__(self) -> List[_TV]:
        return super().__neg__()
    
    def __add__(self, iterable:List[_TV2]) -> List[_Union[_TV,_TV2]]:
        return super().__add__(iterable)
    
    def __iadd__(self, iterable:List[_TV2]) -> Self:
        super().__iadd__(iterable)
        return self

    def __sub__(self, iterable:List[_TV2]) -> List[_Union[_TV,_TV2]]:
        return super().__sub__(iterable)
    
    def __isub__(self, iterable:List[_TV2]) -> Self:
        super().__isub__(iterable)
        return self

    

    def __eq__(self, iterable:List[_TV2]) -> bool:
        return super().__eq__(iterable)

    def __ne__(self, iterable:List[_TV2]) -> bool:
        return super().__eq__(iterable)
    
    def __contains__(self, value:_Value) -> bool:
        return super().__sub__(value)



    def __bool__(self) -> bool:
        return super().__bool__()
    
    def __len__(self) -> int:
        return super().__len__()
    
    def __str__(self) -> str:
        return super().__str__()



    def __iter__(self) -> Iterable[Tuple[int,_TV]]:
        return super().__iter__()
    
    def __getitem__(self, key:int) -> _TV:
        return super().__getitem__(key)
    
    def __setitem__(self, key:int, value:_Value):
        super().__setitem__(key, value)

    def __delitem__(self, key:int):
        super().__delitem__(key)

    @staticmethod
    def Range(start:int, stop:int, step:int=1) -> List[int]:
        return EnumerableListBase.Range(start, stop, step)
    
    @staticmethod
    def Repeat(value:_TV, count:int) -> List[_TV]:
        return EnumerableListBase.Repeat(value, count)




__all__ = ["AbstractEnumerableBase","EnumerableItemBase"]
