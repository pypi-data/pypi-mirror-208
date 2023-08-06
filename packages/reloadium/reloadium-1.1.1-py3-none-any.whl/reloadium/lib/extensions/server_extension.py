import logging
from pathlib import Path
from threading import Thread
import time
from typing import TYPE_CHECKING, List, Optional

from reloadium.corium import utils
from reloadium.lib.extensions.extension import Extension
from reloadium.corium.globals import g
from reloadium.corium.loggium import LoggiumLogger
from reloadium.corium.objects import Action
from reloadium.corium.testing import testing

if TYPE_CHECKING:
    from dataclasses import dataclass, field

    from reloadium.vendored.websocket_server import WebsocketServer
else:
    from reloadium.vendored.dataclasses import dataclass, field


__RELOADIUM__ = True

__all__ = ["PageReloader"]



page_reloader = """
<!--{info}-->
<script type="text/javascript">
   // <![CDATA[  <-- For SVG support
     function refreshCSS() {
        var sheets = [].slice.call(document.getElementsByTagName("link"));
        var head = document.getElementsByTagName("head")[0];
        for (var i = 0; i < sheets.length; ++i) {
           var elem = sheets[i];
           var parent = elem.parentElement || head;
           parent.removeChild(elem);
           var rel = elem.rel;
           if (elem.href && typeof rel != "string" || rel.length === 0 || rel.toLowerCase() === "stylesheet") {
              var url = elem.href.replace(/(&|\\?)_cacheOverride=\\d+/, '');
              elem.href = url + (url.indexOf('?') >= 0 ? '&' : '?') + '_cacheOverride=' + (new Date().valueOf());
           }
           parent.appendChild(elem);
        }
     }
     let protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
     let address = protocol + "{address}:{port}";
     let socket = undefined;
     let lost_connection = false;

     function connect() {
        socket = new WebSocket(address);
         socket.onmessage = function (msg) {
            if (msg.data === 'reload') window.location.href = window.location.href;
            else if (msg.data === 'refreshcss') refreshCSS();
         };
     }

     function checkConnection() {
        if ( socket.readyState === socket.CLOSED ) {
            lost_connection = true;
            connect();
        }
     }

     connect();
     setInterval(checkConnection, 500)

   // ]]>
</script>
"""


@dataclass
class PageReloader:
    address: str
    port: int
    logger: LoggiumLogger

    _server: Optional["WebsocketServer"] = field(init=False, default=None)
    _page_reloader_rendered: str = field(init=False, default="")

    info = "Reloadium page reloader"

    def _start_server(self) -> None:
        from reloadium.vendored.websocket_server import WebsocketServer

        self.logger.info(f"Starting reload websocket server on port {self.port}")

        self._server = WebsocketServer(host=self.address, port=self.port, loglevel=logging.CRITICAL)
        self._server.run_forever(threaded=True)

        self._page_reloader_rendered = page_reloader

        self._page_reloader_rendered = self._page_reloader_rendered.replace("{info}", str(self.info))
        self._page_reloader_rendered = self._page_reloader_rendered.replace("{port}", str(self.port))
        self._page_reloader_rendered = self._page_reloader_rendered.replace("{address}", self.address)

    def inject_script(self, html: str) -> str:
        head_pos = html.find("<head>")
        if head_pos == -1:
            head_pos = 0
        ret = html[:head_pos] + self._page_reloader_rendered + html[head_pos:]
        return ret

    def start(self) -> None:
        try:
            self._start_server()
        except Exception as e:
            self.logger.warning("Could not start server")

    def reload(self) -> None:
        if not self._server:
            return

        self.logger.info("Reloading page")
        self._server.send_message_to_all("reload")
        testing.on_page_reload()

    def reload_with_delay(self, delay: float) -> None:
        def reload_page() -> None:
            time.sleep(delay)
            self.reload()

        Thread(target=reload_page, daemon=True, name=utils.thread.name_factory("page-reloader")).start()


@dataclass
class ServerExtension(Extension):
    page_reloader: Optional[PageReloader] = field(init=False, default=None)

    _page_reloader_address = "127.0.0.1"
    _port_offset = 4512

    def on_start(self) -> None:
        g.core.event_producer.add_watched_extension("html")

    def after_reload(self, path: Path, actions: List[Action]) -> None:
        if not self.page_reloader:
            return

        from reloadium.corium.fr.frame_reloader import UpdateFrame

        if not any(isinstance(a, UpdateFrame) for a in actions):
            if self.page_reloader:
                self.page_reloader.reload()

    def on_other_modify(self, path: Path) -> None:
        if not self.page_reloader:
            return
        self.page_reloader.reload()

    def _page_reloader_factory(self, port: int) -> PageReloader:
        while True:
            reloader_port = port + self._port_offset
            try:
                ret = PageReloader(address=self._page_reloader_address, port=reloader_port, logger=self._logger)
                ret.start()
                self._inject_reloader()
                break
            except OSError:
                self._logger.info(f"Couldn't create page reloader on {reloader_port} port")
                self._port_offset += 1

        return ret

    def _inject_reloader(self) -> None:
        self._logger.info("Injecting page reloader")
