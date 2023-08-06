from abc import ABC
from contextlib import contextmanager
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Generator, List, Optional, Tuple, Type

from reloadium.corium.loggium import LoggiumLogger, loggium
from reloadium.corium.objects import Action, Object
from reloadium.corium.state import Memento, AsyncMemento

if TYPE_CHECKING:
    from dataclasses import dataclass, field

    from reloadium.lib.extensions.manager import ExtensionManager
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class Extension:
    manager: "ExtensionManager"

    NAME: ClassVar[str] = NotImplemented
    activated: bool = field(init=False, default=False)

    _logger: LoggiumLogger = field(init=False)

    def __post_init__(self) -> None:
        self._logger = loggium.factory(self.NAME)
        self._logger.info(f"Creating extension")
        self.manager.core.obj_cls_manager.add_obj_classes(self._get_objects())

    def _get_objects(self) -> List[Type[Object]]:
        ret = []
        objects = self.get_objects()
        for o in objects:
            o.namespace = self.NAME

        ret.extend(objects)
        return ret

    def activate(self) -> None:
        self.activated = True

    def on_import(self, module: types.ModuleType) -> None:
        pass

    @classmethod
    def should_create(cls, module: types.ModuleType) -> bool:
        if not hasattr(module, "__name__"):
            return False

        ret = module.__name__.split(".")[0].lower() == cls.NAME.lower()
        return ret

    @contextmanager
    def on_execute(self) -> Generator[None, None, None]:
        yield

    def on_start(self) -> None:
        pass

    def on_error(self, exc: Exception) -> None:
        pass

    def create_function_memento(self, name: str, is_async: bool) -> Optional[Memento]:
        return None

    async def create_function_memento_async(self, name: str) -> Optional[AsyncMemento]:
        return None

    def create_module_memento(self, name: str) -> Optional[Memento]:
        return None

    async def create_module_memento_async(self, name: str) -> Optional[AsyncMemento]:
        return None

    def on_other_modify(self, path: Path) -> None:
        pass

    def before_reload(self, path: Path) -> None:
        pass

    def after_reload(self, path: Path, actions: List[Action]) -> None:
        pass

    def __eq__(self, other: Any) -> bool:
        return id(other) == id(self)

    def get_objects(self) -> List[Type[Object]]:
        return []

    def is_import(self, module: types.ModuleType, name: str) -> bool:
        ret = hasattr(module, "__name__") and module.__name__ == name
        return ret


@dataclass(repr=False)
class ExtensionMemento(Memento):
    extension: Extension

    def __repr__(self) -> str:
        return "ExtensionMemento"


@dataclass(repr=False)
class AsyncExtensionMemento(AsyncMemento):
    extension: Extension

    def __repr__(self) -> str:
        return "AsyncExtensionMemento"
