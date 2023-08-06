from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, List

from reloadium.lib.extensions.extension import Extension
from reloadium.corium.objects import Action
from reloadium.corium.utils import misc

if TYPE_CHECKING:
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class PyGame(Extension):
    NAME = "PyGame"

    reloading: bool = field(init=False, default=False)

    def on_import(self, py_module: types.ModuleType) -> None:
        if self.is_import(py_module, "pygame.base"):
            self._patch_update()

    def _patch_update(self) -> None:
        import pygame.display

        update_orig = pygame.display.update

        def update(*args: Any, **kwargs: Any) -> None:
            if self.reloading:
                misc.sleep(0.1)
                return None
            else:
                return update_orig(*args, **kwargs)

        pygame.display.update = update

    def before_reload(self, path: Path) -> None:
        self.reloading = True

    def after_reload(self, path: Path, actions: List[Action]) -> None:
        self.reloading = False

    def on_error(self, exc: Exception) -> None:
        self.reloading = False
