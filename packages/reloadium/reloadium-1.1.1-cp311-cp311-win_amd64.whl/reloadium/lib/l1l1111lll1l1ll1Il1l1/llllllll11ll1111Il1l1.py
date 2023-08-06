import re
from contextlib import contextmanager
import os
import sys
import types
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union

from reloadium.corium.ll1llll11111llllIl1l1 import l1lll11ll1ll111lIl1l1
from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1llll111lll1ll1Il1l1 import l1l1lll1l1ll1ll1Il1l1, ll11lll1111111llIl1l1
from reloadium.corium.l11lll11l1l11lllIl1l1 import ll1l1l1111ll1l1lIl1l1
from reloadium.corium.lll111l11l11lll1Il1l1 import ll111llll1l1llllIl1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field

    from sqlalchemy.engine.base import Engine, Transaction
    from sqlalchemy.orm.session import Session
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass(repr=False)
class ll1lll1111lll1llIl1l1(ll11lll1111111llIl1l1):
    l1llll111lll1ll1Il1l1: "lll111lllll111llIl1l1"
    l1111l11ll11111lIl1l1: List["Transaction"] = field(init=False, default_factory=list)

    def l11111ll1l111l1lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        from sqlalchemy.orm.session import _sessions

        super().l11111ll1l111l1lIl1l1()

        llll11ll1l1lllllIl1l1 = list(_sessions.values())

        for l111lllll1llllllIl1l1 in llll11ll1l1lllllIl1l1:
            if ( not l111lllll1llllllIl1l1.is_active):
                continue

            ll111ll1l1lll11lIl1l1 = l111lllll1llllllIl1l1.begin_nested()
            ll11l11ll1l11lllIl1l1.l1111l11ll11111lIl1l1.append(ll111ll1l1lll11lIl1l1)

    def __repr__(ll11l11ll1l11lllIl1l1) -> str:
        return 'DbMemento'

    def l1ll111ll1lll1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().l1ll111ll1lll1l1Il1l1()

        while ll11l11ll1l11lllIl1l1.l1111l11ll11111lIl1l1:
            ll111ll1l1lll11lIl1l1 = ll11l11ll1l11lllIl1l1.l1111l11ll11111lIl1l1.pop()
            if (ll111ll1l1lll11lIl1l1.is_active):
                try:
                    ll111ll1l1lll11lIl1l1.rollback()
                except :
                    pass

    def ll11ll1111l111l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().ll11ll1111l111l1Il1l1()

        while ll11l11ll1l11lllIl1l1.l1111l11ll11111lIl1l1:
            ll111ll1l1lll11lIl1l1 = ll11l11ll1l11lllIl1l1.l1111l11ll11111lIl1l1.pop()
            if (ll111ll1l1lll11lIl1l1.is_active):
                try:
                    ll111ll1l1lll11lIl1l1.commit()
                except :
                    pass


@dataclass
class lll111lllll111llIl1l1(l1l1lll1l1ll1ll1Il1l1):
    l1l111l1ll1llll1Il1l1 = 'Sqlalchemy'

    lll1lll11l1ll1l1Il1l1: List["Engine"] = field(init=False, default_factory=list)
    llll11ll1l1lllllIl1l1: Set["Session"] = field(init=False, default_factory=set)
    l111111llllll111Il1l1: Tuple[int, ...] = field(init=False)

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> None:
        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(ll1ll11l1llll1l1Il1l1, 'sqlalchemy')):
            ll11l11ll1l11lllIl1l1.llll1lll11ll11l1Il1l1(ll1ll11l1llll1l1Il1l1)

        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(ll1ll11l1llll1l1Il1l1, 'sqlalchemy.engine.base')):
            ll11l11ll1l11lllIl1l1.l11ll11lll11111lIl1l1(ll1ll11l1llll1l1Il1l1)

    def llll1lll11ll11l1Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: Any) -> None:
        l1l1ll1ll11l111lIl1l1 = Path(ll1ll11l1llll1l1Il1l1.__file__).read_text(encoding='utf-8')
        __version__ = re.findall('__version__\\s*?=\\s*?"(.*?)"', l1l1ll1ll11l111lIl1l1)[0]

        l1lll1l1l1l11l11Il1l1 = [int(lll11l111ll1l111Il1l1) for lll11l111ll1l111Il1l1 in __version__.split('.')]
        ll11l11ll1l11lllIl1l1.l111111llllll111Il1l1 = tuple(l1lll1l1l1l11l11Il1l1)

    def l111l1lll1l1l111Il1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str, ll11l11ll1l11ll1Il1l1: bool) -> Optional["ll1l1l1111ll1l1lIl1l1"]:
        l1ll1lll11llllllIl1l1 = ll1lll1111lll1llIl1l1(ll11ll11l1llll1lIl1l1=ll11ll11l1llll1lIl1l1, l1llll111lll1ll1Il1l1=ll11l11ll1l11lllIl1l1)
        l1ll1lll11llllllIl1l1.l11111ll1l111l1lIl1l1()
        return l1ll1lll11llllllIl1l1

    def l11ll11lll11111lIl1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: Any) -> None:
        l1l1lll111l1l1l1Il1l1 = locals().copy()

        l1l1lll111l1l1l1Il1l1.update({'original': ll1ll11l1llll1l1Il1l1.Engine.__init__, 'reloader_code': l1lll11ll1ll111lIl1l1, 'engines': ll11l11ll1l11lllIl1l1.lll1lll11l1ll1l1Il1l1})





        l111ll11l1111l1lIl1l1 = dedent('\n            def patched(\n                    self2: Any,\n                    pool: Any,\n                    dialect: Any,\n                    url: Any,\n                    logging_name: Any = None,\n                    echo: Any = None,\n                    proxy: Any = None,\n                    execution_options: Any = None,\n                    hide_parameters: Any = None,\n            ) -> Any:\n                original(self2,\n                         pool,\n                         dialect,\n                         url,\n                         logging_name,\n                         echo,\n                         proxy,\n                         execution_options,\n                         hide_parameters\n                         )\n                with reloader_code():\n                    engines.append(self2)')
























        l11lll1l11l1l11lIl1l1 = dedent('\n            def patched(\n                    self2: Any,\n                    pool: Any,\n                    dialect: Any,\n                    url: Any,\n                    logging_name: Any = None,\n                    echo: Any = None,\n                    query_cache_size: Any = 500,\n                    execution_options: Any = None,\n                    hide_parameters: Any = False,\n            ) -> Any:\n                original(self2,\n                         pool,\n                         dialect,\n                         url,\n                         logging_name,\n                         echo,\n                         query_cache_size,\n                         execution_options,\n                         hide_parameters)\n                with reloader_code():\n                    engines.append(self2)\n        ')
























        if (ll11l11ll1l11lllIl1l1.l111111llllll111Il1l1 <= (1, 3, 24, )):
            exec(l111ll11l1111l1lIl1l1, {**globals(), **l1l1lll111l1l1l1Il1l1}, l1l1lll111l1l1l1Il1l1)
        else:
            exec(l11lll1l11l1l11lIl1l1, {**globals(), **l1l1lll111l1l1l1Il1l1}, l1l1lll111l1l1l1Il1l1)

        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(ll1ll11l1llll1l1Il1l1.Engine, '__init__', l1l1lll111l1l1l1Il1l1['patched'])
