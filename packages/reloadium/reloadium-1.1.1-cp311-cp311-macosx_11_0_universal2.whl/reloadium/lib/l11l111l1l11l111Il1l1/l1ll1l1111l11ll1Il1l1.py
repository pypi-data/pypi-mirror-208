import sys

__RELOADIUM__ = True


def ll11l11111lll111Il1l1(l1l11l11l1l1111lIl1l1, l1ll1l1lll1ll11lIl1l1):
    from pathlib import Path
    from multiprocessing import util, spawn
    from multiprocessing.context import reduction, set_spawning_popen
    import io
    import os

    def ll1l1l1111l111l1Il1l1(*lllll1ll1ll11l1lIl1l1):

        for ll11lll11l1lll1lIl1l1 in lllll1ll1ll11l1lIl1l1:
            os.close(ll11lll11l1lll1lIl1l1)

    if (sys.version_info > (3, 8, )):
        from multiprocessing import resource_tracker as tracker 
    else:
        from multiprocessing import semaphore_tracker as tracker 

    lll1lllllll11l1lIl1l1 = tracker.getfd()
    l1l11l11l1l1111lIl1l1._fds.append(lll1lllllll11l1lIl1l1)
    lll11ll1111ll11lIl1l1 = spawn.get_preparation_data(l1ll1l1lll1ll11lIl1l1._name)
    l1111l1l1lll1l11Il1l1 = io.BytesIO()
    set_spawning_popen(l1l11l11l1l1111lIl1l1)

    try:
        reduction.dump(lll11ll1111ll11lIl1l1, l1111l1l1lll1l11Il1l1)
        reduction.dump(l1ll1l1lll1ll11lIl1l1, l1111l1l1lll1l11Il1l1)
    finally:
        set_spawning_popen(None)

    ll1ll11l11l11111Il1l1lll1l1lll1llll11Il1l1l11ll111l1l111l1Il1l1l1ll111l1l111lllIl1l1 = None
    try:
        (ll1ll11l11l11111Il1l1, lll1l1lll1llll11Il1l1, ) = os.pipe()
        (l11ll111l1l111l1Il1l1, l1ll111l1l111lllIl1l1, ) = os.pipe()
        ll11lll111l1l1llIl1l1 = spawn.get_command_line(tracker_fd=lll1lllllll11l1lIl1l1, pipe_handle=l11ll111l1l111l1Il1l1)


        l11ll1l1lll1ll1lIl1l1 = str(Path(lll11ll1111ll11lIl1l1['sys_argv'][0]).absolute())
        ll11lll111l1l1llIl1l1 = [ll11lll111l1l1llIl1l1[0], '-B', '-m', 'reloadium_launcher', 'spawn_process', str(lll1lllllll11l1lIl1l1), 
str(l11ll111l1l111l1Il1l1), l11ll1l1lll1ll1lIl1l1]
        l1l11l11l1l1111lIl1l1._fds.extend([l11ll111l1l111l1Il1l1, lll1l1lll1llll11Il1l1])
        l1l11l11l1l1111lIl1l1.pid = util.spawnv_passfds(spawn.get_executable(), 
ll11lll111l1l1llIl1l1, l1l11l11l1l1111lIl1l1._fds)
        l1l11l11l1l1111lIl1l1.sentinel = ll1ll11l11l11111Il1l1
        with open(l1ll111l1l111lllIl1l1, 'wb', closefd=False) as ll1llll111l1l11lIl1l1:
            ll1llll111l1l11lIl1l1.write(l1111l1l1lll1l11Il1l1.getbuffer())
    finally:
        ll1ll1l1l1111l1lIl1l1 = []
        for ll11lll11l1lll1lIl1l1 in (ll1ll11l11l11111Il1l1, l1ll111l1l111lllIl1l1, ):
            if (ll11lll11l1lll1lIl1l1 is not None):
                ll1ll1l1l1111l1lIl1l1.append(ll11lll11l1lll1lIl1l1)
        l1l11l11l1l1111lIl1l1.finalizer = util.Finalize(l1l11l11l1l1111lIl1l1, ll1l1l1111l111l1Il1l1, ll1ll1l1l1111l1lIl1l1)

        for ll11lll11l1lll1lIl1l1 in (l11ll111l1l111l1Il1l1, lll1l1lll1llll11Il1l1, ):
            if (ll11lll11l1lll1lIl1l1 is not None):
                os.close(ll11lll11l1lll1lIl1l1)


def __init__(l1l11l11l1l1111lIl1l1, l1ll1l1lll1ll11lIl1l1):
    from multiprocessing import util, spawn
    from multiprocessing.context import reduction, set_spawning_popen
    from multiprocessing.popen_spawn_win32 import TERMINATE, WINEXE, WINSERVICE, WINENV, _path_eq
    from pathlib import Path
    import os
    import msvcrt
    import sys
    import _winapi

    if (sys.version_info > (3, 8, )):
        from multiprocessing import resource_tracker as tracker 
        from multiprocessing.popen_spawn_win32 import _close_handles
    else:
        from multiprocessing import semaphore_tracker as tracker 
        _close_handles = _winapi.CloseHandle

    lll11ll1111ll11lIl1l1 = spawn.get_preparation_data(l1ll1l1lll1ll11lIl1l1._name)







    (lll1l1l1l11l1lllIl1l1, ll11l1l111l1ll1lIl1l1, ) = _winapi.CreatePipe(None, 0)
    l1111111lllll111Il1l1 = msvcrt.open_osfhandle(ll11l1l111l1ll1lIl1l1, 0)
    ll1l1l1l1111111lIl1l1 = spawn.get_executable()
    l11ll1l1lll1ll1lIl1l1 = str(Path(lll11ll1111ll11lIl1l1['sys_argv'][0]).absolute())
    ll11lll111l1l1llIl1l1 = ' '.join([ll1l1l1l1111111lIl1l1, '-B', '-m', 'reloadium_launcher', 'spawn_process', str(os.getpid()), 
str(lll1l1l1l11l1lllIl1l1), l11ll1l1lll1ll1lIl1l1])



    if ((WINENV and _path_eq(ll1l1l1l1111111lIl1l1, sys.executable))):
        ll1l1l1l1111111lIl1l1 = sys._base_executable
        l1l11ll1l11l1l11Il1l1 = os.environ.copy()
        l1l11ll1l11l1l11Il1l1['__PYVENV_LAUNCHER__'] = sys.executable
    else:
        l1l11ll1l11l1l11Il1l1 = None

    with open(l1111111lllll111Il1l1, 'wb', closefd=True) as l111llll1l111ll1Il1l1:

        try:
            (l11llll11l11l111Il1l1, ll1111ll1ll11lllIl1l1, l1l1ll1l1l1lll1lIl1l1, l1lll11ll1l1llllIl1l1, ) = _winapi.CreateProcess(ll1l1l1l1111111lIl1l1, ll11lll111l1l1llIl1l1, None, None, False, 0, l1l11ll1l11l1l11Il1l1, None, None)


            _winapi.CloseHandle(ll1111ll1ll11lllIl1l1)
        except :
            _winapi.CloseHandle(lll1l1l1l11l1lllIl1l1)
            raise 


        l1l11l11l1l1111lIl1l1.pid = l1l1ll1l1l1lll1lIl1l1
        l1l11l11l1l1111lIl1l1.returncode = None
        l1l11l11l1l1111lIl1l1._handle = l11llll11l11l111Il1l1
        l1l11l11l1l1111lIl1l1.sentinel = int(l11llll11l11l111Il1l1)
        if (sys.version_info > (3, 8, )):
            l1l11l11l1l1111lIl1l1.finalizer = util.Finalize(l1l11l11l1l1111lIl1l1, _close_handles, (l1l11l11l1l1111lIl1l1.sentinel, int(lll1l1l1l11l1lllIl1l1), 
))
        else:
            l1l11l11l1l1111lIl1l1.finalizer = util.Finalize(l1l11l11l1l1111lIl1l1, _close_handles, (l1l11l11l1l1111lIl1l1.sentinel, ))



        set_spawning_popen(l1l11l11l1l1111lIl1l1)
        try:
            reduction.dump(lll11ll1111ll11lIl1l1, l111llll1l111ll1Il1l1)
            reduction.dump(l1ll1l1lll1ll11lIl1l1, l111llll1l111ll1Il1l1)
        finally:
            set_spawning_popen(None)
