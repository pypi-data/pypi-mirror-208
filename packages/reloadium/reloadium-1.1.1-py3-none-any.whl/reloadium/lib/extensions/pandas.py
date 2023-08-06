from typing import Any, ClassVar, List, Optional, Type

from reloadium.corium.static_anal import symbols

try:
    import pandas as pd
except ImportError:
    pass

from typing import TYPE_CHECKING

from reloadium.corium.objects import Container, Object, Variable, obj_dc

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from reloadium.vendored.dataclasses import dataclass, field

from reloadium.lib.extensions.extension import Extension


__RELOADIUM__ = True


@dataclass(**obj_dc)
class Dataframe(Variable):
    TYPE_NAME = "Dataframe"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        if type(py_obj) is pd.DataFrame:
            return True

        return False

    def compare(self, against: Object) -> bool:
        return self.py_obj.equals(against.py_obj)

    @classmethod
    def get_rank(cls) -> int:
        return 200


@dataclass(**obj_dc)
class Series(Variable):
    TYPE_NAME = "Series"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        if type(py_obj) is pd.Series:
            return True

        return False

    def compare(self, against: Object) -> bool:
        return self.py_obj.equals(against.py_obj)

    @classmethod
    def get_rank(cls) -> int:
        return 200


@dataclass
class Pandas(Extension):
    NAME = "Pandas"

    def get_objects(self) -> List[Type["Object"]]:
        return [Dataframe, Series]
