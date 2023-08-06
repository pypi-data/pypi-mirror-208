from pathlib import Path
import sys
import threading
from types import CodeType, FrameType, ModuleType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, cast

from reloadium.corium import lll1111l1l111111Il1l1, ll1llll11111llllIl1l1, public, l1l11lll11l111llIl1l1, lll111l11l11lll1Il1l1
from reloadium.corium.ll1l111l1lll111lIl1l1 import l1llll11ll1l11l1Il1l1, lll11llll11l111lIl1l1
from reloadium.corium.ll1llll11111llllIl1l1 import ll1l11l1llllll1lIl1l1, l1lll11ll1ll111lIl1l1, llll111llll11ll1Il1l1
from reloadium.corium.llllll1l11ll1l11Il1l1 import ll1llllll1lllll1Il1l1
from reloadium.corium.l11lllllll11llllIl1l1 import l11lllllll11llllIl1l1
from reloadium.corium.lll11ll1lll1ll1lIl1l1 import l1l1l1l1ll1ll1l1Il1l1
from reloadium.corium.l11lll11l1l11lllIl1l1 import ll1l1l1111ll1l1lIl1l1, l1l1l11l1111l1l1Il1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True

__all__ = ['lll1111lllll111lIl1l1', 'l11l11l11lll1ll1Il1l1', 'lllll111l11ll1llIl1l1']


ll1l1ll1111l1111Il1l1 = l11lllllll11llllIl1l1.l1l1lll1l1l11ll1Il1l1(__name__)


class lll1111lllll111lIl1l1:
    @classmethod
    def l1ll1ll11l1lll1lIl1l1(ll11l11ll1l11lllIl1l1) -> Optional[FrameType]:
        l1l1l11ll1111lllIl1l1: FrameType = sys._getframe(2)
        l1ll1lll11llllllIl1l1 = next(lll111l11l11lll1Il1l1.l1l1l11ll1111lllIl1l1.l11ll1lll1l11111Il1l1(l1l1l11ll1111lllIl1l1))
        return l1ll1lll11llllllIl1l1


class l11l11l11lll1ll1Il1l1(lll1111lllll111lIl1l1):
    @classmethod
    def lll111lll11ll1l1Il1l1(ll1l1l1lll11l11lIl1l1, ll1l1ll11lll1lllIl1l1: List[Any], l11l1111l1111ll1Il1l1: Dict[str, Any], ll11111l11ll1ll1Il1l1: List[ll1l1l1111ll1l1lIl1l1]) -> Any:  # type: ignore
        with l1lll11ll1ll111lIl1l1():
            assert ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1ll1ll11lll1lllIl1l1
            l1l1l11ll1111lllIl1l1 = ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1ll1ll11lll1lllIl1l1.l1l1l1ll1llllll1Il1l1.l11111lll1ll1111Il1l1()
            l1l1l11ll1111lllIl1l1.llllll1lllllll1lIl1l1()

            l1lll11l11l11l11Il1l1 = ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l11l11lll1l11ll1Il1l1.llllll1l111l1111Il1l1(l1l1l11ll1111lllIl1l1.ll1ll1l1111l1lllIl1l1, l1l1l11ll1111lllIl1l1.l1lllll11ll1l111Il1l1.l111ll1llll1llllIl1l1())
            assert l1lll11l11l11l11Il1l1
            l111llllll1l1111Il1l1 = ll1l1l1lll11l11lIl1l1.l1ll1ll11l1lll1lIl1l1()

            for llll11ll11l1l1l1Il1l1 in ll11111l11ll1ll1Il1l1:
                llll11ll11l1l1l1Il1l1.l1ll111ll1lll1l1Il1l1()

            for llll11ll11l1l1l1Il1l1 in ll11111l11ll1ll1Il1l1:
                llll11ll11l1l1l1Il1l1.ll11ll1111l111l1Il1l1()


        l1ll1lll11llllllIl1l1 = l1lll11l11l11l11Il1l1(*ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1);        l1l1l11ll1111lllIl1l1.l1ll1llll11l1l11Il1l1.additional_info.pydev_step_stop = l111llllll1l1111Il1l1  # type: ignore

        return l1ll1lll11llllllIl1l1

    @classmethod
    async def l11l1111l11ll1llIl1l1(ll1l1l1lll11l11lIl1l1, ll1l1ll11lll1lllIl1l1: List[Any], l11l1111l1111ll1Il1l1: Dict[str, Any], ll11111l11ll1ll1Il1l1: List[l1l1l11l1111l1l1Il1l1]) -> Any:  # type: ignore
        with l1lll11ll1ll111lIl1l1():
            assert ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1ll1ll11lll1lllIl1l1
            l1l1l11ll1111lllIl1l1 = ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1ll1ll11lll1lllIl1l1.l1l1l1ll1llllll1Il1l1.l11111lll1ll1111Il1l1()
            l1l1l11ll1111lllIl1l1.llllll1lllllll1lIl1l1()

            l1lll11l11l11l11Il1l1 = ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l11l11lll1l11ll1Il1l1.llllll1l111l1111Il1l1(l1l1l11ll1111lllIl1l1.ll1ll1l1111l1lllIl1l1, l1l1l11ll1111lllIl1l1.l1lllll11ll1l111Il1l1.l111ll1llll1llllIl1l1())
            assert l1lll11l11l11l11Il1l1
            l111llllll1l1111Il1l1 = ll1l1l1lll11l11lIl1l1.l1ll1ll11l1lll1lIl1l1()

            for llll11ll11l1l1l1Il1l1 in ll11111l11ll1ll1Il1l1:
                await llll11ll11l1l1l1Il1l1.l1ll111ll1lll1l1Il1l1()

            for llll11ll11l1l1l1Il1l1 in ll11111l11ll1ll1Il1l1:
                await llll11ll11l1l1l1Il1l1.ll11ll1111l111l1Il1l1()


        l1ll1lll11llllllIl1l1 = await l1lll11l11l11l11Il1l1(*ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1);        l1l1l11ll1111lllIl1l1.l1ll1llll11l1l11Il1l1.additional_info.pydev_step_stop = l111llllll1l1111Il1l1  # type: ignore

        return l1ll1lll11llllllIl1l1


class lllll111l11ll1llIl1l1(lll1111lllll111lIl1l1):
    @classmethod
    def lll111lll11ll1l1Il1l1(ll1l1l1lll11l11lIl1l1) -> Optional[ModuleType]:  # type: ignore
        with l1lll11ll1ll111lIl1l1():
            assert ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1ll1ll11lll1lllIl1l1
            l1l1l11ll1111lllIl1l1 = ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1ll1ll11lll1lllIl1l1.l1l1l1ll1llllll1Il1l1.l11111lll1ll1111Il1l1()

            l11ll1l1lll1ll1lIl1l1 = Path(l1l1l11ll1111lllIl1l1.l1ll11ll1llll11lIl1l1.f_globals['__spec__'].origin).absolute()
            l1l1l11l111l11l1Il1l1 = l1l1l11ll1111lllIl1l1.l1ll11ll1llll11lIl1l1.f_globals['__name__']
            l1l1l11ll1111lllIl1l1.llllll1lllllll1lIl1l1()
            llll1ll111l1llllIl1l1 = ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.llll111l111l1111Il1l1.l1ll1l11ll11llllIl1l1(l11ll1l1lll1ll1lIl1l1)

            if ( not llll1ll111l1llllIl1l1):
                ll1l1ll1111l1111Il1l1.ll11l1111111l1llIl1l1('Could not retrieve src.', ll1ll11lll1lll1lIl1l1={'file': l1l1l1l1ll1ll1l1Il1l1.lll1l1ll1lll11llIl1l1(l11ll1l1lll1ll1lIl1l1), 
'fullname': l1l1l1l1ll1ll1l1Il1l1.l1l1l11l111l11l1Il1l1(l1l1l11l111l11l1Il1l1)})

            assert llll1ll111l1llllIl1l1

        try:
            llll1ll111l1llllIl1l1.ll1l11lllll111l1Il1l1()
            llll1ll111l1llllIl1l1.l111111l1l111111Il1l1(l1ll11111111l11lIl1l1=False)
            llll1ll111l1llllIl1l1.lll11111111lll11Il1l1(l1ll11111111l11lIl1l1=False)
        except ll1l11l1llllll1lIl1l1 as l111ll1l11l111l1Il1l1:
            l1l1l11ll1111lllIl1l1.llll1ll1l111l111Il1l1(l111ll1l11l111l1Il1l1)
            return None

        import importlib.util

        lllll111111111llIl1l1 = l1l1l11ll1111lllIl1l1.l1ll11ll1llll11lIl1l1.f_locals['__spec__']
        ll1ll11l1llll1l1Il1l1 = importlib.util.module_from_spec(lllll111111111llIl1l1)

        llll1ll111l1llllIl1l1.l1l11l11ll1l1l1lIl1l1(ll1ll11l1llll1l1Il1l1)
        return ll1ll11l1llll1l1Il1l1


lll11llll11l111lIl1l1.l11ll1l1l1llll1lIl1l1(l1llll11ll1l11l1Il1l1.ll1l11111l1l111lIl1l1, l11l11l11lll1ll1Il1l1.lll111lll11ll1l1Il1l1)
lll11llll11l111lIl1l1.l11ll1l1l1llll1lIl1l1(l1llll11ll1l11l1Il1l1.l1l1ll1111lll1l1Il1l1, l11l11l11lll1ll1Il1l1.l11l1111l11ll1llIl1l1)
lll11llll11l111lIl1l1.l11ll1l1l1llll1lIl1l1(l1llll11ll1l11l1Il1l1.ll1ll1l1ll1l1l1lIl1l1, lllll111l11ll1llIl1l1.lll111lll11ll1l1Il1l1)
