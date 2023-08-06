import types
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union, cast

from reloadium.lib.extensions.extension import Extension
from reloadium.lib import extensions_raw

if TYPE_CHECKING:
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class Multiprocessing(Extension):
    NAME = "Multiprocessing"

    def __post_init__(self) -> None:
        super().__post_init__()

    def on_import(self, module: types.ModuleType) -> None:
        if self.is_import(module, "multiprocessing.popen_spawn_posix"):
            self._inject_spawn_process_posix(module)

        if self.is_import(module, "multiprocessing.popen_spawn_win32"):
            self._inject_spawn_process_win(module)

    def _inject_spawn_process_posix(self, module: types.ModuleType) -> None:
        import multiprocessing.popen_spawn_posix
        multiprocessing.popen_spawn_posix.Popen._launch = extensions_raw.multiprocessing._launch  # type: ignore

    def _inject_spawn_process_win(self, module: types.ModuleType) -> None:
        import multiprocessing.popen_spawn_win32
        multiprocessing.popen_spawn_win32.Popen.__init__ = extensions_raw.multiprocessing.__init__  # type: ignore
