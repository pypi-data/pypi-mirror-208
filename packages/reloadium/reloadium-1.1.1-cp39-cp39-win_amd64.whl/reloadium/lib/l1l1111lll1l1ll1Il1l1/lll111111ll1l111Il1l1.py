import asyncio
from contextlib import contextmanager
import os
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type

from reloadium.lib.environ import env
from reloadium.corium.ll1llll11111llllIl1l1 import l1lll11ll1ll111lIl1l1
from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1llll111lll1ll1Il1l1 import ll11lll1111111llIl1l1, l1l1llll11l1l1llIl1l1
from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1l111llllllll1lIl1l1 import l11111l11111l111Il1l1
from reloadium.corium.llll1l11ll111lllIl1l1 import l1ll1111l111l11lIl1l1, l1l111ll11111l1lIl1l1, l11lllll1l1ll111Il1l1, l1111lll11l1l11lIl1l1, lllll111lllllll1Il1l1
from reloadium.corium.l11lll11l1l11lllIl1l1 import ll1l1l1111ll1l1lIl1l1, l1l1l11l1111l1l1Il1l1
from reloadium.corium.l1ll1l1111l1ll1lIl1l1 import ll1lll11l11lll1lIl1l1
from reloadium.corium.lll111l11l11lll1Il1l1 import ll111llll1l1llllIl1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field

    from django.db import transaction
    from django.db.transaction import Atomic
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass(**lllll111lllllll1Il1l1)
class l1111ll1ll1111l1Il1l1(l1111lll11l1l11lIl1l1):
    llll1l1ll11l1lllIl1l1 = 'Field'

    @classmethod
    def ll11lllll1l1l1llIl1l1(ll1l1l1lll11l11lIl1l1, l11ll1l1ll1lll1lIl1l1: ll1lll11l11lll1lIl1l1.ll11l1llll1llll1Il1l1, l1ll11ll1llll11lIl1l1: Any, l1ll1111111lll1lIl1l1: l1l111ll11111l1lIl1l1) -> bool:
        from django.db.models.fields import Field

        if ((hasattr(l1ll11ll1llll11lIl1l1, 'field') and isinstance(l1ll11ll1llll11lIl1l1.field, Field))):
            return True

        return False

    def lll1ll1l1l1l1lllIl1l1(ll11l11ll1l11lllIl1l1, l111l1111l1111llIl1l1: l11lllll1l1ll111Il1l1) -> bool:
        return True

    @classmethod
    def llll1ll1111ll1l1Il1l1(ll1l1l1lll11l11lIl1l1) -> int:
        return 200


@dataclass(repr=False)
class ll1lll1111lll1llIl1l1(ll11lll1111111llIl1l1):
    llll11l11l11ll1lIl1l1: "Atomic" = field(init=False)

    ll11lll11111ll11Il1l1: bool = field(init=False, default=False)

    def l11111ll1l111l1lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().l11111ll1l111l1lIl1l1()
        from django.db import transaction

        ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1 = transaction.atomic()
        ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1.__enter__()

    def l1ll111ll1lll1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().l1ll111ll1lll1l1Il1l1()
        if (ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1):
            return 

        ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1 = True
        from django.db import transaction

        transaction.set_rollback(True)
        ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1.__exit__(None, None, None)

    def ll11ll1111l111l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().ll11ll1111l111l1Il1l1()

        if (ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1):
            return 

        ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1 = True
        ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1.__exit__(None, None, None)

    def __repr__(ll11l11ll1l11lllIl1l1) -> str:
        return 'DbMemento'


@dataclass(repr=False)
class ll1l11llll111l1lIl1l1(l1l1llll11l1l1llIl1l1):
    llll11l11l11ll1lIl1l1: "Atomic" = field(init=False)

    ll11lll11111ll11Il1l1: bool = field(init=False, default=False)

    async def l11111ll1l111l1lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        await super().l11111ll1l111l1lIl1l1()
        from django.db import transaction
        from asgiref.sync import sync_to_async

        ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1 = transaction.atomic()
        await sync_to_async(ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1.__enter__)()

    async def l1ll111ll1lll1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        from asgiref.sync import sync_to_async

        await super().l1ll111ll1lll1l1Il1l1()
        if (ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1):
            return 

        ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1 = True
        from django.db import transaction

        def l1l11ll1l1ll11l1Il1l1() -> None:
            transaction.set_rollback(True)
            ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1.__exit__(None, None, None)
        await sync_to_async(l1l11ll1l1ll11l1Il1l1)()

    async def ll11ll1111l111l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        from asgiref.sync import sync_to_async

        await super().ll11ll1111l111l1Il1l1()

        if (ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1):
            return 

        ll11l11ll1l11lllIl1l1.ll11lll11111ll11Il1l1 = True
        await sync_to_async(ll11l11ll1l11lllIl1l1.llll11l11l11ll1lIl1l1.__exit__)(None, None, None)

    def __repr__(ll11l11ll1l11lllIl1l1) -> str:
        return 'AsyncDbMemento'


@dataclass
class ll1lll11llll1ll1Il1l1(l11111l11111l111Il1l1):
    l1l111l1ll1llll1Il1l1 = 'Django'

    l1l11ll11l1lll1lIl1l1: Optional[int] = field(init=False)
    lll1llll1lll1ll1Il1l1: Optional[Callable[..., Any]] = field(init=False, default=None)

    def __post_init__(ll11l11ll1l11lllIl1l1) -> None:
        super().__post_init__()
        ll11l11ll1l11lllIl1l1.l1l11ll11l1lll1lIl1l1 = None

    def l11ll111l11lllllIl1l1(ll11l11ll1l11lllIl1l1) -> List[Type[l11lllll1l1ll111Il1l1]]:
        return [l1111ll1ll1111l1Il1l1]

    def l11l1111ll11l1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().l11l1111ll11l1l1Il1l1()
        if ('runserver' in sys.argv):
            sys.argv.append('--noreload')

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, ll1ll11l1llll1l1Il1l1: types.ModuleType) -> None:
        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(ll1ll11l1llll1l1Il1l1, 'django.core.management.commands.runserver')):
            ll11l11ll1l11lllIl1l1.ll11ll1ll1l1lll1Il1l1()
            ll11l11ll1l11lllIl1l1.l11lll1ll111l111Il1l1()

    def l111l1lll1l1l111Il1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str, ll11l11ll1l11ll1Il1l1: bool) -> Optional["ll1l1l1111ll1l1lIl1l1"]:
        if ( not os.environ.get('DJANGO_SETTINGS_MODULE')):
            return None

        if (ll11l11ll1l11ll1Il1l1):
            return None
        else:
            l1ll1lll11llllllIl1l1 = ll1lll1111lll1llIl1l1(ll11ll11l1llll1lIl1l1=ll11ll11l1llll1lIl1l1, l1llll111lll1ll1Il1l1=ll11l11ll1l11lllIl1l1)
            l1ll1lll11llllllIl1l1.l11111ll1l111l1lIl1l1()

        return l1ll1lll11llllllIl1l1

    async def l1lll1ll1l11ll11Il1l1(ll11l11ll1l11lllIl1l1, ll11ll11l1llll1lIl1l1: str) -> Optional["l1l1l11l1111l1l1Il1l1"]:
        if ( not os.environ.get('DJANGO_SETTINGS_MODULE')):
            return None

        l1ll1lll11llllllIl1l1 = ll1l11llll111l1lIl1l1(ll11ll11l1llll1lIl1l1=ll11ll11l1llll1lIl1l1, l1llll111lll1ll1Il1l1=ll11l11ll1l11lllIl1l1)
        await l1ll1lll11llllllIl1l1.l11111ll1l111l1lIl1l1()
        return l1ll1lll11llllllIl1l1

    def ll11ll1ll1l1lll1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        import django.core.management.commands.runserver

        l11l11l1l11ll1llIl1l1 = django.core.management.commands.runserver.Command.handle

        def l11l1ll1l11l1l1lIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **lll1l11ll1l111l1Il1l1: Any) -> Any:
            with l1lll11ll1ll111lIl1l1():
                l1lll11l1ll1llllIl1l1 = lll1l11ll1l111l1Il1l1.get('addrport')
                if ( not l1lll11l1ll1llllIl1l1):
                    l1lll11l1ll1llllIl1l1 = django.core.management.commands.runserver.Command.default_port

                l1lll11l1ll1llllIl1l1 = l1lll11l1ll1llllIl1l1.split(':')[ - 1]
                l1lll11l1ll1llllIl1l1 = int(l1lll11l1ll1llllIl1l1)
                ll11l11ll1l11lllIl1l1.l1l11ll11l1lll1lIl1l1 = l1lll11l1ll1llllIl1l1

            return l11l11l1l11ll1llIl1l1(*ll1l1ll11lll1lllIl1l1, **lll1l11ll1l111l1Il1l1)

        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(django.core.management.commands.runserver.Command, 'handle', l11l1ll1l11l1l1lIl1l1)

    def l11lll1ll111l111Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        import django.core.management.commands.runserver

        l11l11l1l11ll1llIl1l1 = django.core.management.commands.runserver.Command.get_handler

        def l11l1ll1l11l1l1lIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **lll1l11ll1l111l1Il1l1: Any) -> Any:
            with l1lll11ll1ll111lIl1l1():
                assert ll11l11ll1l11lllIl1l1.l1l11ll11l1lll1lIl1l1
                ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1 = ll11l11ll1l11lllIl1l1.ll1l11ll11l11l11Il1l1(ll11l11ll1l11lllIl1l1.l1l11ll11l1lll1lIl1l1)
                if (env.page_reload_on_start):
                    ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.llll1ll1l111lll1Il1l1(2.0)

            return l11l11l1l11ll1llIl1l1(*ll1l1ll11lll1lllIl1l1, **lll1l11ll1l111l1Il1l1)

        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(django.core.management.commands.runserver.Command, 'get_handler', l11l1ll1l11l1l1lIl1l1)

    def lll1ll1l11l1lll1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().lll1ll1l11l1lll1Il1l1()

        import django.core.handlers.base

        l11l11l1l11ll1llIl1l1 = django.core.handlers.base.BaseHandler.get_response

        def l11l1ll1l11l1l1lIl1l1(ll11ll1ll1l111l1Il1l1: Any, l1l1l1ll11l1llllIl1l1: Any) -> Any:
            l1l1ll1l11111lllIl1l1 = l11l11l1l11ll1llIl1l1(ll11ll1ll1l111l1Il1l1, l1l1l1ll11l1llllIl1l1)

            if ( not ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1):
                return l1l1ll1l11111lllIl1l1

            l1ll11l1l1l11l11Il1l1 = l1l1ll1l11111lllIl1l1.get('content-type')

            if (( not l1ll11l1l1l11l11Il1l1 or 'text/html' not in l1ll11l1l1l11l11Il1l1)):
                return l1l1ll1l11111lllIl1l1

            l1l1ll1ll11l111lIl1l1 = l1l1ll1l11111lllIl1l1.content

            if (isinstance(l1l1ll1ll11l111lIl1l1, bytes)):
                l1l1ll1ll11l111lIl1l1 = l1l1ll1ll11l111lIl1l1.decode('utf-8')

            llll1111l1ll1lllIl1l1 = ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.lll11llll111l1llIl1l1(l1l1ll1ll11l111lIl1l1)

            l1l1ll1l11111lllIl1l1.content = llll1111l1ll1lllIl1l1.encode('utf-8')
            l1l1ll1l11111lllIl1l1['content-length'] = str(len(l1l1ll1l11111lllIl1l1.content)).encode('ascii')
            return l1l1ll1l11111lllIl1l1

        django.core.handlers.base.BaseHandler.get_response = l11l1ll1l11l1l1lIl1l1  # type: ignore

    def lll11llll1ll111lIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path) -> None:
        super().lll11llll1ll111lIl1l1(lll1l1ll1lll11llIl1l1)

        from django.apps.registry import Apps

        ll11l11ll1l11lllIl1l1.lll1llll1lll1ll1Il1l1 = Apps.register_model

        def ll1ll1ll11111l1lIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> Any:
            pass

        Apps.register_model = ll1ll1ll11111l1lIl1l1

    def l11l1ll1l1ll11llIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path, l111l11ll111llllIl1l1: List[l1ll1111l111l11lIl1l1]) -> None:
        super().l11l1ll1l1ll11llIl1l1(lll1l1ll1lll11llIl1l1, l111l11ll111llllIl1l1)

        if ( not ll11l11ll1l11lllIl1l1.lll1llll1lll1ll1Il1l1):
            return 

        from django.apps.registry import Apps

        Apps.register_model = ll11l11ll1l11lllIl1l1.lll1llll1lll1ll1Il1l1
