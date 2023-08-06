import re
from contextlib import contextmanager
import os
import sys
import types
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union

from reloadium.corium.exceptions import reloader_code
from reloadium.lib.extensions.extension import Extension, ExtensionMemento
from reloadium.corium.state import Memento
from reloadium.corium.utils import misc

if TYPE_CHECKING:
    from dataclasses import dataclass, field

    from sqlalchemy.engine.base import Engine, Transaction
    from sqlalchemy.orm.session import Session
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass(repr=False)
class DbMemento(ExtensionMemento):
    extension: "Sqlalchemy"
    transactions: List["Transaction"] = field(init=False, default_factory=list)

    def create(self) -> None:
        from sqlalchemy.orm.session import _sessions

        super().create()

        sessions = list(_sessions.values())

        for s in sessions:
            if not s.is_active:
                continue

            t = s.begin_nested()
            self.transactions.append(t)

    def __repr__(self) -> str:
        return "DbMemento"

    def restore(self) -> None:
        super().restore()

        while self.transactions:
            t = self.transactions.pop()
            if t.is_active:
                try:
                    t.rollback()
                except:
                    pass

    def cleanup(self) -> None:
        super().cleanup()

        while self.transactions:
            t = self.transactions.pop()
            if t.is_active:
                try:
                    t.commit()
                except:
                    pass


@dataclass
class Sqlalchemy(Extension):
    NAME = "Sqlalchemy"

    engines: List["Engine"] = field(init=False, default_factory=list)
    sessions: Set["Session"] = field(init=False, default_factory=set)
    version: Tuple[int, ...] = field(init=False)

    def on_import(self, module: types.ModuleType) -> None:
        if self.is_import(module, "sqlalchemy"):
            self._watch_version(module)

        if self.is_import(module, "sqlalchemy.engine.base"):
            self._watch_engine_creating(module)

    def _watch_version(self, module: Any) -> None:
        content = Path(module.__file__).read_text(encoding="utf-8")
        __version__ = re.findall(r'__version__\s*?=\s*?"(.*?)"', content)[0]

        versions = [int(v) for v in __version__.split(".")]
        self.version = tuple(versions)

    def create_function_memento(self, name: str, is_async: bool) -> Optional["Memento"]:
        ret = DbMemento(name=name, extension=self)
        ret.create()
        return ret

    def _watch_engine_creating(self, module: Any) -> None:
        ctx = locals().copy()

        ctx.update({
            "original": module.Engine.__init__,
            "reloader_code": reloader_code,
            "engines": self.engines
        })

        old_code = dedent("""
            def patched(
                    self2: Any,
                    pool: Any,
                    dialect: Any,
                    url: Any,
                    logging_name: Any = None,
                    echo: Any = None,
                    proxy: Any = None,
                    execution_options: Any = None,
                    hide_parameters: Any = None,
            ) -> Any:
                original(self2,
                         pool,
                         dialect,
                         url,
                         logging_name,
                         echo,
                         proxy,
                         execution_options,
                         hide_parameters
                         )
                with reloader_code():
                    engines.append(self2)""")

        new_code = dedent("""
            def patched(
                    self2: Any,
                    pool: Any,
                    dialect: Any,
                    url: Any,
                    logging_name: Any = None,
                    echo: Any = None,
                    query_cache_size: Any = 500,
                    execution_options: Any = None,
                    hide_parameters: Any = False,
            ) -> Any:
                original(self2,
                         pool,
                         dialect,
                         url,
                         logging_name,
                         echo,
                         query_cache_size,
                         execution_options,
                         hide_parameters)
                with reloader_code():
                    engines.append(self2)
        """)

        if self.version <= (1, 3, 24):
            exec(old_code, {**globals(), **ctx}, ctx)
        else:
            exec(new_code, {**globals(), **ctx}, ctx)

        misc.patch(module.Engine, "__init__", ctx["patched"])
