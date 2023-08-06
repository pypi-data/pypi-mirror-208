from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, List

from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1llll111lll1ll1Il1l1 import l1l1lll1l1ll1ll1Il1l1
from reloadium.corium.llll1l11ll111lllIl1l1 import l1ll1111l111l11lIl1l1
from reloadium.corium.lll111l11l11lll1Il1l1 import ll111llll1l1llllIl1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class lll11l11l111l1llIl1l1(l1l1lll1l1ll1ll1Il1l1):
    l1l111l1ll1llll1Il1l1 = 'PyGame'

    l1ll1111l1ll11llIl1l1: bool = field(init=False, default=False)

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, l1111l111lll1l11Il1l1: types.ModuleType) -> None:
        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(l1111l111lll1l11Il1l1, 'pygame.base')):
            ll11l11ll1l11lllIl1l1.ll111l1l1ll1l111Il1l1()

    def ll111l1l1ll1l111Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        import pygame.display

        llll1l1l11lll11lIl1l1 = pygame.display.update

        def lll11111lllll1llIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> None:
            if (ll11l11ll1l11lllIl1l1.l1ll1111l1ll11llIl1l1):
                ll111llll1l1llllIl1l1.l1l1l1ll1l11lll1Il1l1(0.1)
                return None
            else:
                return llll1l1l11lll11lIl1l1(*ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1)

        pygame.display.update = lll11111lllll1llIl1l1

    def lll11llll1ll111lIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path) -> None:
        ll11l11ll1l11lllIl1l1.l1ll1111l1ll11llIl1l1 = True

    def l11l1ll1l1ll11llIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path, l111l11ll111llllIl1l1: List[l1ll1111l111l11lIl1l1]) -> None:
        ll11l11ll1l11lllIl1l1.l1ll1111l1ll11llIl1l1 = False

    def l11111l11l11l11lIl1l1(ll11l11ll1l11lllIl1l1, l11ll1ll11l1l11lIl1l1: Exception) -> None:
        ll11l11ll1l11lllIl1l1.l1ll1111l1ll11llIl1l1 = False
