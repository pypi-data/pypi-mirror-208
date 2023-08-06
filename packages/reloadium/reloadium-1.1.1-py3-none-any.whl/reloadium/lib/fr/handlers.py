from pathlib import Path
import sys
import threading
from types import CodeType, FrameType, ModuleType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, cast

from reloadium.corium import const, exceptions, public, testing, utils
from reloadium.corium.builtins import Builtins, re_builtins
from reloadium.corium.exceptions import UserError, reloader_code, user_code
from reloadium.corium.globals import g
from reloadium.corium.loggium import loggium
from reloadium.corium.sanitizer import san
from reloadium.corium.state import Memento, AsyncMemento

if TYPE_CHECKING:
    from dataclasses import dataclass, field
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True

__all__ = ["FrameReloadHandler", "MethodFrameReloadHandler", "ModuleFrameReloadHandler"]


logger = loggium.factory(__name__)


class FrameReloadHandler:
    @classmethod
    def get_stop_frame(self) -> Optional[FrameType]:
        frame: FrameType = sys._getframe(2)
        ret = next(utils.frame.iterate_frames(frame))
        return ret


class MethodFrameReloadHandler(FrameReloadHandler):
    @classmethod
    def handle(cls, args: List[Any], kwargs: Dict[str, Any], mementos: List[Memento]) -> Any:  # type: ignore
        with reloader_code():
            assert g.core.fr
            frame = g.core.fr.stack.get_current_frame()
            frame.make_stale()

            fun = g.core.code_reg.get_code_fun_link(frame.code, frame.mod.get_dict())
            assert fun
            stop_frame = cls.get_stop_frame()

            for m in mementos:
                m.restore()

            for m in mementos:
                m.cleanup()

        # fmt: off
        ret = fun(*args, **kwargs);frame.thread.additional_info.pydev_step_stop = stop_frame  # type: ignore
        # fmt: on
        return ret

    @classmethod
    async def handle_async(cls, args: List[Any], kwargs: Dict[str, Any], mementos: List[AsyncMemento]) -> Any:  # type: ignore
        with reloader_code():
            assert g.core.fr
            frame = g.core.fr.stack.get_current_frame()
            frame.make_stale()

            fun = g.core.code_reg.get_code_fun_link(frame.code, frame.mod.get_dict())
            assert fun
            stop_frame = cls.get_stop_frame()

            for m in mementos:
                await m.restore()

            for m in mementos:
                await m.cleanup()

        # fmt: off
        ret = await fun(*args, **kwargs);frame.thread.additional_info.pydev_step_stop = stop_frame  # type: ignore
        # fmt: on
        return ret


class ModuleFrameReloadHandler(FrameReloadHandler):
    @classmethod
    def handle(cls) -> Optional[ModuleType]:  # type: ignore
        with reloader_code():
            assert g.core.fr
            frame = g.core.fr.stack.get_current_frame()

            file = Path(frame.py_obj.f_globals["__spec__"].origin).absolute()
            fullname = frame.py_obj.f_globals["__name__"]
            frame.make_stale()
            src = g.core.src_manager.get_src(file)

            if not src:
                logger.error(
                    "Could not retrieve src.", data={"file": san.path(file), "fullname": san.fullname(fullname)}
                )
            assert src

        try:
            src.preprocess()
            src.process(save=False)
            src.compile(save=False)
        except UserError as e:
            frame.handle_exception(e)
            return None

        import importlib.util

        spec = frame.py_obj.f_locals["__spec__"]
        module = importlib.util.module_from_spec(spec)

        src.exec(module)
        return module


re_builtins.set(Builtins.METHOD_FRAME_RELOAD_HANDLER, MethodFrameReloadHandler.handle)
re_builtins.set(Builtins.METHOD_FRAME_RELOAD_HANDLER_ASYNC, MethodFrameReloadHandler.handle_async)
re_builtins.set(Builtins.MODULE_FRAME_RELOAD_HANDLER, ModuleFrameReloadHandler.handle)
