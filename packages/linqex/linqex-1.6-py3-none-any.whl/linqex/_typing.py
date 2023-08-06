from typing import Any, TypeVar, ClassVar

_Key = str
_Value = Any
_Desc = bool

_TK = TypeVar('_TK')
_TV = TypeVar('_TV')

_TK2 = TypeVar('_TK2')
_TV2 = TypeVar('_TV2')

_TFV = TypeVar('_TFV')
_TFK = TypeVar('_TFK')
_TFV2 = TypeVar('_TFV2')
_TFK2 = TypeVar('_TFK2')

class JoinType:
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

__all__ = ["_Key", "_Value", "_Desc", "_TK", "_TV", "_TK2", "_TV2", "_TFV", "_TFK", "_TFV2", "_TFK2", "JoinType"]