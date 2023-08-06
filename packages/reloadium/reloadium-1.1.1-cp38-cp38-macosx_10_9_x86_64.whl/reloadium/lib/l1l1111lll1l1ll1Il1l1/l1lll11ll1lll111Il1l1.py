import sys
from contextlib import contextmanager
from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type

from reloadium.corium.lll111l11l11lll1Il1l1 import ll111llll1l1llllIl1l1
from reloadium.lib.environ import env
from reloadium.corium.ll1llll11111llllIl1l1 import l1lll11ll1ll111lIl1l1
from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1l111llllllll1lIl1l1 import l11111l11111l111Il1l1
from reloadium.corium.llll1l11ll111lllIl1l1 import l1l111ll11111l1lIl1l1, l11lllll1l1ll111Il1l1, l1111lll11l1l11lIl1l1, lllll111lllllll1Il1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass
else:
    from reloadium.vendored.dataclasses import dataclass


__RELOADIUM__ = True


@dataclass
class l1l1l11lll1lll11Il1l1(l11111l11111l111Il1l1):
    l1l111l1ll1llll1Il1l1 = 'FastApi'

    l11l111111ll11l1Il1l1 = 'uvicorn'

    @contextmanager
    def llll1ll111lll1llIl1l1(ll11l11ll1l11lllIl1l1) -> Generator[None, None, None]:
        yield 

    def l11ll111l11lllllIl1l1(ll11l11ll1l11lllIl1l1) -> List[Type[l11lllll1l1ll111Il1l1]]:
        return []

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, l1111l111lll1l11Il1l1: types.ModuleType) -> None:
        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(l1111l111lll1l11Il1l1, ll11l11ll1l11lllIl1l1.l11l111111ll11l1Il1l1)):
            ll11l11ll1l11lllIl1l1.llllll1ll111l11lIl1l1()

    @classmethod
    def l111l1l11llll11lIl1l1(ll1l1l1lll11l11lIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> bool:
        l1ll1lll11llllllIl1l1 = super().l111l1l11llll11lIl1l1(ll1ll11l1llll1l1Il1l1)
        l1ll1lll11llllllIl1l1 |= ll1ll11l1llll1l1Il1l1.__name__ == ll1l1l1lll11l11lIl1l1.l11l111111ll11l1Il1l1
        return l1ll1lll11llllllIl1l1

    def llllll1ll111l11lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        ll111l1l1l1llll1Il1l1 = '--reload'
        if (ll111l1l1l1llll1Il1l1 in sys.argv):
            sys.argv.remove('--reload')
