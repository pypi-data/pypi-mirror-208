from contextlib import contextmanager
from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type

from reloadium.lib.environ import env
from reloadium.corium.ll1llll11111llllIl1l1 import l1lll11ll1ll111lIl1l1
from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1l111llllllll1lIl1l1 import l11111l11111l111Il1l1
from reloadium.corium.llll1l11ll111lllIl1l1 import l1l111ll11111l1lIl1l1, l11lllll1l1ll111Il1l1, l1111lll11l1l11lIl1l1, lllll111lllllll1Il1l1
from reloadium.corium.l1ll1l1111l1ll1lIl1l1 import ll1lll11l11lll1lIl1l1
from reloadium.corium.lll111l11l11lll1Il1l1 import ll111llll1l1llllIl1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass
else:
    from reloadium.vendored.dataclasses import dataclass


__RELOADIUM__ = True


@dataclass(**lllll111lllllll1Il1l1)
class lll1lll11l111111Il1l1(l1111lll11l1l11lIl1l1):
    llll1l1ll11l1lllIl1l1 = 'FlaskApp'

    @classmethod
    def ll11lllll1l1l1llIl1l1(ll1l1l1lll11l11lIl1l1, l11ll1l1ll1lll1lIl1l1: ll1lll11l11lll1lIl1l1.ll11l1llll1llll1Il1l1, l1ll11ll1llll11lIl1l1: Any, l1ll1111111lll1lIl1l1: l1l111ll11111l1lIl1l1) -> bool:
        import flask

        if (isinstance(l1ll11ll1llll11lIl1l1, flask.Flask)):
            return True

        return False

    def l1l1111ll1ll1ll1Il1l1(ll11l11ll1l11lllIl1l1) -> bool:
        return True

    @classmethod
    def llll1ll1111ll1l1Il1l1(ll1l1l1lll11l11lIl1l1) -> int:
        return (super().llll1ll1111ll1l1Il1l1() + 10)


@dataclass(**lllll111lllllll1Il1l1)
class l11lllll111lll1lIl1l1(l1111lll11l1l11lIl1l1):
    llll1l1ll11l1lllIl1l1 = 'Request'

    @classmethod
    def ll11lllll1l1l1llIl1l1(ll1l1l1lll11l11lIl1l1, l11ll1l1ll1lll1lIl1l1: ll1lll11l11lll1lIl1l1.ll11l1llll1llll1Il1l1, l1ll11ll1llll11lIl1l1: Any, l1ll1111111lll1lIl1l1: l1l111ll11111l1lIl1l1) -> bool:
        if (repr(l1ll11ll1llll11lIl1l1) == '<LocalProxy unbound>'):
            return True

        return False

    def l1l1111ll1ll1ll1Il1l1(ll11l11ll1l11lllIl1l1) -> bool:
        return True

    @classmethod
    def llll1ll1111ll1l1Il1l1(ll1l1l1lll11l11lIl1l1) -> int:

        return int(10000000000.0)


@dataclass
class l1ll11l1l11lll11Il1l1(l11111l11111l111Il1l1):
    l1l111l1ll1llll1Il1l1 = 'Flask'

    @contextmanager
    def llll1ll111lll1llIl1l1(ll11l11ll1l11lllIl1l1) -> Generator[None, None, None]:




        from flask import Flask as FlaskLib 

        def ll111l11l1111111Il1l1(*ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> Any:
            def l11l1l1l1l1lll1lIl1l1(ll1llll111l1l11lIl1l1: Any) -> Any:
                return ll1llll111l1l11lIl1l1

            return l11l1l1l1l1lll1lIl1l1

        l1111llllll1l11lIl1l1 = FlaskLib.route
        FlaskLib.route = ll111l11l1111111Il1l1  # type: ignore

        try:
            yield 
        finally:
            FlaskLib.route = l1111llllll1l11lIl1l1  # type: ignore

    def l11ll111l11lllllIl1l1(ll11l11ll1l11lllIl1l1) -> List[Type[l11lllll1l1ll111Il1l1]]:
        return [lll1lll11l111111Il1l1, l11lllll111lll1lIl1l1]

    def l1111l111lll1ll1Il1l1(ll11l11ll1l11lllIl1l1, l1111l111lll1l11Il1l1: types.ModuleType) -> None:
        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(l1111l111lll1l11Il1l1, 'flask.app')):
            ll11l11ll1l11lllIl1l1.llll11lll1l11lllIl1l1()
            ll11l11ll1l11lllIl1l1.l111111l1l11l111Il1l1()
            ll11l11ll1l11lllIl1l1.ll111ll111lll1l1Il1l1()

        if (ll11l11ll1l11lllIl1l1.l1ll1ll11l11ll1lIl1l1(l1111l111lll1l11Il1l1, 'flask.cli')):
            ll11l11ll1l11lllIl1l1.l111l1l1lll11ll1Il1l1()

    def llll11lll1l11lllIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        try:
            import werkzeug.serving
            import flask.cli
        except ImportError:
            return 

        l11l11l1l11ll1llIl1l1 = werkzeug.serving.run_simple

        def l11l1ll1l11l1l1lIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> Any:
            with l1lll11ll1ll111lIl1l1():
                l1lll11l1ll1llllIl1l1 = l11l1111l1111ll1Il1l1.get('port')
                if ( not l1lll11l1ll1llllIl1l1):
                    l1lll11l1ll1llllIl1l1 = ll1l1ll11lll1lllIl1l1[1]

                ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1 = ll11l11ll1l11lllIl1l1.ll1l11ll11l11l11Il1l1(l1lll11l1ll1llllIl1l1)
                if (env.page_reload_on_start):
                    ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.llll1ll1l111lll1Il1l1(1.0)
            l11l11l1l11ll1llIl1l1(*ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1)

        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(werkzeug.serving, 'run_simple', l11l1ll1l11l1l1lIl1l1)
        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(flask.cli, 'run_simple', l11l1ll1l11l1l1lIl1l1)

    def ll111ll111lll1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        try:
            import flask
        except ImportError:
            return 

        l11l11l1l11ll1llIl1l1 = flask.app.Flask.__init__

        def l11l1ll1l11l1l1lIl1l1(l1l11l11l1l1111lIl1l1: Any, *ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> Any:
            l11l11l1l11ll1llIl1l1(l1l11l11l1l1111lIl1l1, *ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1)
            with l1lll11ll1ll111lIl1l1():
                l1l11l11l1l1111lIl1l1.config['TEMPLATES_AUTO_RELOAD'] = True

        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(flask.app.Flask, '__init__', l11l1ll1l11l1l1lIl1l1)

    def l111111l1l11l111Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        try:
            import waitress  # type: ignore
        except ImportError:
            return 

        l11l11l1l11ll1llIl1l1 = waitress.serve


        def l11l1ll1l11l1l1lIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> Any:
            with l1lll11ll1ll111lIl1l1():
                l1lll11l1ll1llllIl1l1 = l11l1111l1111ll1Il1l1.get('port')
                if ( not l1lll11l1ll1llllIl1l1):
                    l1lll11l1ll1llllIl1l1 = int(ll1l1ll11lll1lllIl1l1[1])

                l1lll11l1ll1llllIl1l1 = int(l1lll11l1ll1llllIl1l1)

                ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1 = ll11l11ll1l11lllIl1l1.ll1l11ll11l11l11Il1l1(l1lll11l1ll1llllIl1l1)
                if (env.page_reload_on_start):
                    ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.llll1ll1l111lll1Il1l1(1.0)

            l11l11l1l11ll1llIl1l1(*ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1)

        ll111llll1l1llllIl1l1.l11l1ll1111lll1lIl1l1(waitress, 'serve', l11l1ll1l11l1l1lIl1l1)

    def l111l1l1lll11ll1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        try:
            from flask import cli
        except ImportError:
            return 

        ll1111111ll11l11Il1l1 = Path(cli.__file__).read_text(encoding='utf-8')
        ll1111111ll11l11Il1l1 = ll1111111ll11l11Il1l1.replace('.tb_next', '.tb_next.tb_next')

        exec(ll1111111ll11l11Il1l1, cli.__dict__)

    def lll1ll1l11l1lll1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        super().lll1ll1l11l1lll1Il1l1()
        import flask.app

        l11l11l1l11ll1llIl1l1 = flask.app.Flask.dispatch_request

        def l11l1ll1l11l1l1lIl1l1(*ll1l1ll11lll1lllIl1l1: Any, **l11l1111l1111ll1Il1l1: Any) -> Any:
            l1l1ll1l11111lllIl1l1 = l11l11l1l11ll1llIl1l1(*ll1l1ll11lll1lllIl1l1, **l11l1111l1111ll1Il1l1)

            if ( not ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1):
                return l1l1ll1l11111lllIl1l1

            if (isinstance(l1l1ll1l11111lllIl1l1, str)):
                l1ll1lll11llllllIl1l1 = ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.lll11llll111l1llIl1l1(l1l1ll1l11111lllIl1l1)
                return l1ll1lll11llllllIl1l1
            elif ((isinstance(l1l1ll1l11111lllIl1l1, flask.app.Response) and 'text/html' in l1l1ll1l11111lllIl1l1.content_type)):
                l1l1ll1l11111lllIl1l1.data = ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.lll11llll111l1llIl1l1(l1l1ll1l11111lllIl1l1.data.decode('utf-8')).encode('utf-8')
                return l1l1ll1l11111lllIl1l1
            else:
                return l1l1ll1l11111lllIl1l1

        flask.app.Flask.dispatch_request = l11l1ll1l11l1l1lIl1l1  # type: ignore
