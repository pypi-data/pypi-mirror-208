import types
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union, cast

from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1llll111lll1ll1Il1l1 import l1l1lll1l1ll1ll1Il1l1
from reloadium.lib import l11l111l1l11l111Il1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class l111ll111l1ll11lIl1l1(l1l1lll1l1ll1ll1Il1l1):
    l1l111l1ll1llll1Il1l1 = 'Multiprocessing'

    def __post_init__(ll11l11ll1l11lllIl1l1) -> None:
        super().__post_init__()

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> None:
        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(ll1ll11l1llll1l1Il1l1, 'multiprocessing.popen_spawn_posix')):
            ll11l11ll1l11lllIl1l1.l1llll11111lll11Il1l1(ll1ll11l1llll1l1Il1l1)

        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(ll1ll11l1llll1l1Il1l1, 'multiprocessing.popen_spawn_win32')):
            ll11l11ll1l11lllIl1l1.lll111ll1l11l111Il1l1(ll1ll11l1llll1l1Il1l1)

    def l1llll11111lll11Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> None:
        import multiprocessing.popen_spawn_posix
        multiprocessing.popen_spawn_posix.Popen._launch = l11l111l1l11l111Il1l1.l1ll1l1111l11ll1Il1l1.ll11l11111lll111Il1l1  # type: ignore

    def lll111ll1l11l111Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> None:
        import multiprocessing.popen_spawn_win32
        multiprocessing.popen_spawn_win32.Popen.__init__ = l11l111l1l11l111Il1l1.l1ll1l1111l11ll1Il1l1.__init__  # type: ignore
