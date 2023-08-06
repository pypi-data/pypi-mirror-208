from contextlib import contextmanager
import os
from pathlib import Path
import sys
from threading import Thread, Timer
import types
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union

from reloadium.lib.extensions.extension import Extension
from reloadium.corium.objects import Action, Container, Object, Variable, obj_dc
from reloadium.corium.static_anal import symbols

if TYPE_CHECKING:
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass(**obj_dc)
class OrderedType(Variable):
    TYPE_NAME = "OrderedType"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        import graphene.utils.orderedtype

        if isinstance(py_obj, graphene.utils.orderedtype.OrderedType):
            return True

        return False

    def compare(self, against: Object) -> bool:
        if self.py_obj.__class__.__name__ != against.py_obj.__class__.__name__:
            return False

        left = dict(self.py_obj.__dict__)
        left.pop("creation_counter")

        right = dict(self.py_obj.__dict__)
        right.pop("creation_counter")

        ret = left == right
        return ret

    @classmethod
    def get_rank(cls) -> int:
        return 200


@dataclass
class Graphene(Extension):
    NAME = "Graphene"

    def __post_init__(self) -> None:
        super().__post_init__()

    def get_objects(self) -> List[Type[Object]]:
        return [OrderedType]
