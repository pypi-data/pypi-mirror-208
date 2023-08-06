from contextlib import contextmanager
from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type

from reloadium.lib.environ import env
from reloadium.corium.exceptions import reloader_code
from reloadium.lib.extensions.server_extension import ServerExtension
from reloadium.corium.objects import Container, Object, Variable, obj_dc
from reloadium.corium.static_anal import symbols
from reloadium.corium.utils import misc

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from reloadium.vendored.dataclasses import dataclass


__RELOADIUM__ = True


@dataclass(**obj_dc)
class FlaskApp(Variable):
    TYPE_NAME = "FlaskApp"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        import flask

        if isinstance(py_obj, flask.Flask):
            return True

        return False

    def is_ignored(self) -> bool:
        return True

    @classmethod
    def get_rank(cls) -> int:
        return super().get_rank() + 10


@dataclass(**obj_dc)
class Request(Variable):
    TYPE_NAME = "Request"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        if repr(py_obj) == "<LocalProxy unbound>":
            return True

        return False

    def is_ignored(self) -> bool:
        return True

    @classmethod
    def get_rank(cls) -> int:
        # has to be very hight priority since doing anything on flask.request raises an exception
        return int(1e10)


@dataclass
class Flask(ServerExtension):
    NAME = "Flask"

    @contextmanager
    def on_execute(self) -> Generator[None, None, None]:
        """
        Disable url registering when rewriting source.
        Changing view settings is not supported yet.
        """
        from flask import Flask as FlaskLib

        def empty_decorator(*args: Any, **kwargs: Any) -> Any:
            def decorator(f: Any) -> Any:
                return f

            return decorator

        tmp_route = FlaskLib.route
        FlaskLib.route = empty_decorator  # type: ignore

        try:
            yield
        finally:
            FlaskLib.route = tmp_route  # type: ignore

    def get_objects(self) -> List[Type[Object]]:
        return [FlaskApp, Request]

    def on_import(self, py_module: types.ModuleType) -> None:
        if self.is_import(py_module, "flask.app"):
            self._patch_werkzeug()
            self._patch_waitress()
            self._patch_app_creation()

        if self.is_import(py_module, "flask.cli"):
            self._fix_locate_app()

    def _patch_werkzeug(self) -> None:
        try:
            import werkzeug.serving
            import flask.cli
        except ImportError:
            return

        original = werkzeug.serving.run_simple

        def patched(*args: Any, **kwargs: Any) -> Any:
            with reloader_code():
                port = kwargs.get("port")
                if not port:
                    port = args[1]

                self.page_reloader = self._page_reloader_factory(port)
                if env.page_reload_on_start:
                    self.page_reloader.reload_with_delay(1.0)
            original(*args, **kwargs)

        misc.patch(werkzeug.serving, "run_simple", patched)
        misc.patch(flask.cli, "run_simple", patched)

    def _patch_app_creation(self) -> None:
        try:
            import flask
        except ImportError:
            return

        original = flask.app.Flask.__init__

        def patched(self2: Any, *args: Any, **kwargs: Any) -> Any:
            original(self2, *args, **kwargs)
            with reloader_code():
                self2.config["TEMPLATES_AUTO_RELOAD"] = True

        misc.patch(flask.app.Flask, "__init__", patched)

    def _patch_waitress(self) -> None:
        try:
            import waitress  # type: ignore
        except ImportError:
            return

        original = waitress.serve
        # Retrieve port

        def patched(*args: Any, **kwargs: Any) -> Any:
            with reloader_code():
                port = kwargs.get("port")
                if not port:
                    port = int(args[1])

                port = int(port)

                self.page_reloader = self._page_reloader_factory(port)
                if env.page_reload_on_start:
                    self.page_reloader.reload_with_delay(1.0)

            original(*args, **kwargs)

        misc.patch(waitress, "serve", patched)

    def _fix_locate_app(self) -> None:
        try:
            from flask import cli
        except ImportError:
            return

        src_code = Path(cli.__file__).read_text(encoding="utf-8")
        src_code = src_code.replace(".tb_next", ".tb_next.tb_next")

        exec(src_code, cli.__dict__)

    def _inject_reloader(self) -> None:
        super()._inject_reloader()
        import flask.app

        original = flask.app.Flask.dispatch_request

        def patched(*args: Any, **kwargs: Any) -> Any:
            response = original(*args, **kwargs)

            if not self.page_reloader:
                return response

            if isinstance(response, str):
                ret = self.page_reloader.inject_script(response)
                return ret
            elif isinstance(response, flask.app.Response) and "text/html" in response.content_type:
                response.data = self.page_reloader.inject_script(response.data.decode("utf-8")).encode("utf-8")
                return response
            else:
                return response

        flask.app.Flask.dispatch_request = patched  # type: ignore
