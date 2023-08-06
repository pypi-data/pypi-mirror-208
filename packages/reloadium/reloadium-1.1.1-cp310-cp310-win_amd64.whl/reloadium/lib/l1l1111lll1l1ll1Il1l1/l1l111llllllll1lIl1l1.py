import logging
from pathlib import Path
from threading import Thread
import time
from typing import TYPE_CHECKING, List, Optional

from reloadium.corium import lll111l11l11lll1Il1l1
from reloadium.lib.l1l1111lll1l1ll1Il1l1.l1llll111lll1ll1Il1l1 import l1l1lll1l1ll1ll1Il1l1
from reloadium.corium.llllll1l11ll1l11Il1l1 import ll1llllll1lllll1Il1l1
from reloadium.corium.l11lllllll11llllIl1l1 import l1ll1ll1111ll111Il1l1
from reloadium.corium.llll1l11ll111lllIl1l1 import l1ll1111l111l11lIl1l1
from reloadium.corium.l1l11lll11l111llIl1l1 import l1l11lll11l111llIl1l1

if (TYPE_CHECKING):
    from dataclasses import dataclass, field

    from reloadium.vendored.websocket_server import WebsocketServer
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True

__all__ = ['l11ll1llllll1111Il1l1']



llllll1111111l11Il1l1 = '\n<!--{info}-->\n<script type="text/javascript">\n   // <![CDATA[  <-- For SVG support\n     function refreshCSS() {\n        var sheets = [].slice.call(document.getElementsByTagName("link"));\n        var head = document.getElementsByTagName("head")[0];\n        for (var i = 0; i < sheets.length; ++i) {\n           var elem = sheets[i];\n           var parent = elem.parentElement || head;\n           parent.removeChild(elem);\n           var rel = elem.rel;\n           if (elem.href && typeof rel != "string" || rel.length === 0 || rel.toLowerCase() === "stylesheet") {\n              var url = elem.href.replace(/(&|\\?)_cacheOverride=\\d+/, \'\');\n              elem.href = url + (url.indexOf(\'?\') >= 0 ? \'&\' : \'?\') + \'_cacheOverride=\' + (new Date().valueOf());\n           }\n           parent.appendChild(elem);\n        }\n     }\n     let protocol = window.location.protocol === \'http:\' ? \'ws://\' : \'wss://\';\n     let address = protocol + "{address}:{port}";\n     let socket = undefined;\n     let lost_connection = false;\n\n     function connect() {\n        socket = new WebSocket(address);\n         socket.onmessage = function (msg) {\n            if (msg.data === \'reload\') window.location.href = window.location.href;\n            else if (msg.data === \'refreshcss\') refreshCSS();\n         };\n     }\n\n     function checkConnection() {\n        if ( socket.readyState === socket.CLOSED ) {\n            lost_connection = true;\n            connect();\n        }\n     }\n\n     connect();\n     setInterval(checkConnection, 500)\n\n   // ]]>\n</script>\n'














































@dataclass
class l11ll1llllll1111Il1l1:
    l1ll1ll1111lll1lIl1l1: str
    l1lll11l1ll1llllIl1l1: int
    ll1l1ll1111l1111Il1l1: l1ll1ll1111ll111Il1l1

    ll1ll1ll1lll1lllIl1l1: Optional["WebsocketServer"] = field(init=False, default=None)
    lll111111l1l1l11Il1l1: str = field(init=False, default='')

    llllll111111lll1Il1l1 = 'Reloadium page reloader'

    def l1l111111lll111lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        from reloadium.vendored.websocket_server import WebsocketServer

        ll11l11ll1l11lllIl1l1.ll1l1ll1111l1111Il1l1.llllll111111lll1Il1l1(''.join(['Starting reload websocket server on port ', '{:{}}'.format(ll11l11ll1l11lllIl1l1.l1lll11l1ll1llllIl1l1, '')]))

        ll11l11ll1l11lllIl1l1.ll1ll1ll1lll1lllIl1l1 = WebsocketServer(host=ll11l11ll1l11lllIl1l1.l1ll1ll1111lll1lIl1l1, port=ll11l11ll1l11lllIl1l1.l1lll11l1ll1llllIl1l1, loglevel=logging.CRITICAL)
        ll11l11ll1l11lllIl1l1.ll1ll1ll1lll1lllIl1l1.run_forever(threaded=True)

        ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1 = llllll1111111l11Il1l1

        ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1 = ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1.replace('{info}', str(ll11l11ll1l11lllIl1l1.llllll111111lll1Il1l1))
        ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1 = ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1.replace('{port}', str(ll11l11ll1l11lllIl1l1.l1lll11l1ll1llllIl1l1))
        ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1 = ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1.replace('{address}', ll11l11ll1l11lllIl1l1.l1ll1ll1111lll1lIl1l1)

    def lll11llll111l1llIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1l1l1ll1Il1l1: str) -> str:
        lllll1l11ll11111Il1l1 = lll1l1ll1l1l1ll1Il1l1.find('<head>')
        if (lllll1l11ll11111Il1l1 ==  - 1):
            lllll1l11ll11111Il1l1 = 0
        l1ll1lll11llllllIl1l1 = ((lll1l1ll1l1l1ll1Il1l1[:lllll1l11ll11111Il1l1] + ll11l11ll1l11lllIl1l1.lll111111l1l1l11Il1l1) + lll1l1ll1l1l1ll1Il1l1[lllll1l11ll11111Il1l1:])
        return l1ll1lll11llllllIl1l1

    def lll1l11llll1ll1lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        try:
            ll11l11ll1l11lllIl1l1.l1l111111lll111lIl1l1()
        except Exception as l111ll1l11l111l1Il1l1:
            ll11l11ll1l11lllIl1l1.ll1l1ll1111l1111Il1l1.l111111l1111ll11Il1l1('Could not start server')

    def llll1l11l1llll1lIl1l1(ll11l11ll1l11lllIl1l1) -> None:
        if ( not ll11l11ll1l11lllIl1l1.ll1ll1ll1lll1lllIl1l1):
            return 

        ll11l11ll1l11lllIl1l1.ll1l1ll1111l1111Il1l1.llllll111111lll1Il1l1('Reloading page')
        ll11l11ll1l11lllIl1l1.ll1ll1ll1lll1lllIl1l1.send_message_to_all('reload')
        l1l11lll11l111llIl1l1.l11lll11lllll111Il1l1()

    def llll1ll1l111lll1Il1l1(ll11l11ll1l11lllIl1l1, l11l11l1l11lllllIl1l1: float) -> None:
        def l11ll111lll11111Il1l1() -> None:
            time.sleep(l11l11l1l11lllllIl1l1)
            ll11l11ll1l11lllIl1l1.llll1l11l1llll1lIl1l1()

        Thread(target=l11ll111lll11111Il1l1, daemon=True, name=lll111l11l11lll1Il1l1.l1ll1llll11l1l11Il1l1.ll1l111llll11ll1Il1l1('page-reloader')).start()


@dataclass
class l11111l11111l111Il1l1(l1l1lll1l1ll1ll1Il1l1):
    llllll1111111l11Il1l1: Optional[l11ll1llllll1111Il1l1] = field(init=False, default=None)

    lll1lll1ll11llllIl1l1 = '127.0.0.1'
    ll11l11l11llllllIl1l1 = 4512

    def l11l1111ll11l1l1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        ll1llllll1lllll1Il1l1.l1ll1111ll1l111lIl1l1.l1l11l11ll1llll1Il1l1.l1lll11l1l1111llIl1l1('html')

    def l11l1ll1l1ll11llIl1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path, l111l11ll111llllIl1l1: List[l1ll1111l111l11lIl1l1]) -> None:
        if ( not ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1):
            return 

        from reloadium.corium.l1ll1ll11lll1lllIl1l1.lll1lll111l1ll11Il1l1 import lll11111l1ll11l1Il1l1

        if ( not any((isinstance(l111l111ll1l1l1lIl1l1, lll11111l1ll11l1Il1l1) for l111l111ll1l1l1lIl1l1 in l111l11ll111llllIl1l1))):
            if (ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1):
                ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.llll1l11l1llll1lIl1l1()

    def ll11ll11111ll1l1Il1l1(ll11l11ll1l11lllIl1l1, lll1l1ll1lll11llIl1l1: Path) -> None:
        if ( not ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1):
            return 
        ll11l11ll1l11lllIl1l1.llllll1111111l11Il1l1.llll1l11l1llll1lIl1l1()

    def ll1l11ll11l11l11Il1l1(ll11l11ll1l11lllIl1l1, l1lll11l1ll1llllIl1l1: int) -> l11ll1llllll1111Il1l1:
        while True:
            l11ll1ll11l1l111Il1l1 = (l1lll11l1ll1llllIl1l1 + ll11l11ll1l11lllIl1l1.ll11l11l11llllllIl1l1)
            try:
                l1ll1lll11llllllIl1l1 = l11ll1llllll1111Il1l1(l1ll1ll1111lll1lIl1l1=ll11l11ll1l11lllIl1l1.lll1lll1ll11llllIl1l1, l1lll11l1ll1llllIl1l1=l11ll1ll11l1l111Il1l1, ll1l1ll1111l1111Il1l1=ll11l11ll1l11lllIl1l1.lllll1l1llllll11Il1l1)
                l1ll1lll11llllllIl1l1.lll1l11llll1ll1lIl1l1()
                ll11l11ll1l11lllIl1l1.lll1ll1l11l1lll1Il1l1()
                break
            except OSError:
                ll11l11ll1l11lllIl1l1.lllll1l1llllll11Il1l1.llllll111111lll1Il1l1(''.join(["Couldn't create page reloader on ", '{:{}}'.format(l11ll1ll11l1l111Il1l1, ''), ' port']))
                ll11l11ll1l11lllIl1l1.ll11l11l11llllllIl1l1 += 1

        return l1ll1lll11llllllIl1l1

    def lll1ll1l11l1lll1Il1l1(ll11l11ll1l11lllIl1l1) -> None:
        ll11l11ll1l11lllIl1l1.lllll1l1llllll11Il1l1.llllll111111lll1Il1l1('Injecting page reloader')
