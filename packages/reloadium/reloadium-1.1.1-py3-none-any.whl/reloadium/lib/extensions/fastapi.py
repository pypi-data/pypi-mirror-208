import sys
from contextlib import contextmanager
from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type

from reloadium.corium.utils import misc
from reloadium.lib.environ import env
from reloadium.corium.exceptions import reloader_code
from reloadium.lib.extensions.server_extension import ServerExtension
from reloadium.corium.objects import Container, Object, Variable, obj_dc

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from reloadium.vendored.dataclasses import dataclass


__RELOADIUM__ = True


@dataclass
class FastApi(ServerExtension):
    NAME = "FastApi"

    UVICORN = "uvicorn"

    @contextmanager
    def on_execute(self) -> Generator[None, None, None]:
        yield

    def get_objects(self) -> List[Type[Object]]:
        return []

    def on_import(self, py_module: types.ModuleType) -> None:
        if self.is_import(py_module, self.UVICORN):
            self._remove_builtin_reloader()

    @classmethod
    def should_create(cls, module: types.ModuleType) -> bool:
        ret = super().should_create(module)
        ret |= module.__name__ == cls.UVICORN
        return ret

    def _remove_builtin_reloader(self) -> None:
        reload_flag = "--reload"
        if reload_flag in sys.argv:
            sys.argv.remove("--reload")
