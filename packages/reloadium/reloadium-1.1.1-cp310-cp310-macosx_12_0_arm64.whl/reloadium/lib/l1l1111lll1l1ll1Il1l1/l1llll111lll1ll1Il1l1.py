from abc import ABC
from contextlib import contextmanager
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Generator, List, Optional, Tuple, Type

from reloadium.corium.l11lllllll11llllIl1l1 import l1ll1ll1111ll111Il1l1, l11lllllll11llllIl1l1
from reloadium.corium.llll1l11ll111lllIl1l1 import l1ll1111l111l11lIl1l1, l11lllll1l1ll111Il1l1
from reloadium.corium.l11lll11l1l11lllIl1l1 import ll1l1l1111ll1l1lIl1l1, l1l1l11l1111l1l1Il1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field

    from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1ll11l11ll1l1llIl1l1 import l1l1111l1ll11l1lIl1l1
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class l1l1lll1l1ll1ll1Il1l1:
    l1ll11l11ll1l1llIl1l1: "l1l1111l1ll11l1lIl1l1"

    l1l111l1ll1llll1Il1l1: ClassVar[str] = NotImplemented
    llll1l1ll11ll1llIl1l1: bool = field(init=False, default=False)

    lllll1l1llllll11Il1l1: l1ll1ll1111ll111Il1l1 = field(init=False)

    def __post_init__(ll11l11ll1l11lllIl1l1) -> None:
        ll11l11ll1l11lllIl1l1.lllll1l1llllll11Il1l1 = l11lllllll11llllIl1l1.l1l1lll1l1l11ll1Il1l1(ll11l11ll1l11lllIl1l1.l1l111l1ll1llll1Il1l1)
        ll11l11ll1l11lllIl1l1.lllll1l1llllll11Il1l1.llllll111111lll1Il1l1('Creating extension')
        ll11l11ll1l11lllIl1l1.l1ll11l11ll1l1llIl1l1.l1ll1111ll1l111lIl1l1.l1ll11ll1llll1l1Il1l1.lll1ll1ll11ll1llIl1l1(ll11l11ll1l11lllIl1l1.l1l1ll1lll11ll11Il1l1())

    def l1l1ll1lll11ll11Il1l1(ll11l11ll1l11lllIl1l1) -> List[Type[l11lllll1l1ll111Il1l1]]:
        l1ll1lll11llllllIl1l1 = []
        llll1l11ll111lllIl1l1 = ll11l11ll1l11lllIl1l1.l11ll111l11lllllIl1l1()
        for ll1111lllllll1llIl1l1 in llll1l11ll111lllIl1l1:
            ll1111lllllll1llIl1l1.l1ll111l1lll1l1lIl1l1 = ll11l11ll1l11lllIl1l1.l1l111l1ll1llll1Il1l1

        l1ll1lll11llllllIl1l1.extend(llll1l11ll111lllIl1l1)
        return l1ll1lll11llllllIl1l1

    def l1llll1ll1lll1llIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        ll11l11ll1l11lllIl1l1.llll1l1ll11ll1llIl1l1 = True

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> None:
        pass

    @classmethod
    def l111l1l11llll11lIl1l1(ll1l1l1lll11l11lIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> bool:
        if ( not hasattr(ll1ll11l1llll1l1Il1l1, '__name__')):
            return False

        l1ll1lll11llllllIl1l1 = ll1ll11l1llll1l1Il1l1.__name__.split('.')[0].lower() == ll1l1l1lll11l11lIl1l1.l1l111l1ll1llll1Il1l1.lower()
        return l1ll1lll11llllllIl1l1

    @contextmanager
    def llll1ll111lll1llIl1l1(ll11l11ll1l11lllIl1l1) -> Generator[None, None, None]:
        yield 

    def l11l1111ll11l1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        pass

    def l11111l11l11l11lIl1l1(ll11l11ll1l11lllIl1l1, l11ll1ll11l1l11lIl1l1: Exception) -> None:
        pass

    def l111l1lll1l1l111Il1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str, ll11l11ll1l11ll1Il1l1: bool) -> Optional[ll1l1l1111ll1l1lIl1l1]:
        return None

    async def l1lll1ll1l11ll11Il1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str) -> Optional[l1l1l11l1111l1l1Il1l1]:
        return None

    def lll1lll1lll111llIl1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str) -> Optional[ll1l1l1111ll1l1lIl1l1]:
        return None

    async def llllll11l1111111Il1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str) -> Optional[l1l1l11l1111l1l1Il1l1]:
        return None

    def ll11ll11111ll1l1Il1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path) -> None:
        pass

    def lll11llll1ll111lIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path) -> None:
        pass

    def l11l1ll1l1ll11llIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path, l111l11ll111llllIl1l1: List[l1ll1111l111l11lIl1l1]) -> None:
        pass

    def __eq__(ll11l11ll1l11lllIl1l1, ll1llll1ll1l1ll1Il1l1: Any) -> bool:
        return id(ll1llll1ll1l1ll1Il1l1) == id(ll11l11ll1l11lllIl1l1)

    def l11ll111l11lllllIl1l1(ll11l11ll1l11lllIl1l1) -> List[Type[l11lllll1l1ll111Il1l1]]:
        return []

    def l1ll1ll11l11ll1lIl1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType, ll11ll11l1llll1lIl1l1: str) -> bool:
        l1ll1lll11llllllIl1l1 = (hasattr(ll1ll11l1llll1l1Il1l1, '__name__') and ll1ll11l1llll1l1Il1l1.__name__ == ll11ll11l1llll1lIl1l1)
        return l1ll1lll11llllllIl1l1


@dataclass(repr=False)
class ll11lll1111111llIl1l1(ll1l1l1111ll1l1lIl1l1):
    l1llll111lll1ll1Il1l1: l1l1lll1l1ll1ll1Il1l1

    def __repr__(ll11l11ll1l11lllIl1l1) -> str:
        return 'ExtensionMemento'


@dataclass(repr=False)
class l1l1llll11l1l1llIl1l1(l1l1l11l1111l1l1Il1l1):
    l1llll111lll1ll1Il1l1: l1l1lll1l1ll1ll1Il1l1

    def __repr__(ll11l11ll1l11lllIl1l1) -> str:
        return 'AsyncExtensionMemento'
