import json
import sys
import traceback
from datetime import datetime
from types import coroutine
from threading import Thread
from asyncio import (
    get_event_loop,
    set_event_loop,
    run_coroutine_threadsafe,
    AbstractEventLoop
)

from aiohttp import ClientSession, ClientWebSocketResponse


class WebsocketClient:
    """
    Websocket API base class

    * overridden unpack_data method to unpack data
    * overridden on_connected method to handle callback on connected
    * overridden on_disconnected method to to handle callback on disconnected
    * overridden on_packet method to handle packet received
    * overridden on_error method to handle error
    """

    def __init__(self):
        """Constructor"""
        self._active: bool = False
        self._host: str = ""

        self._session: ClientSession = ClientSession()
        self._ws: ClientWebSocketResponse = None
        self._loop: AbstractEventLoop = None

        self._proxy: str = ""
        self._ping_interval: int = 60  # seconds
        self._header: dict = {}

        self._last_sent_text: str = ""
        self._last_received_text: str = ""

    def init(
        self,
        host: str,
        proxy_host: str = "",
        proxy_port: int = 0,
        ping_interval: int = 60,
        header: dict = None
    ):
        """
        init websocket client
        """
        self._host = host
        self._ping_interval = ping_interval

        if header:
            self._header = header

        if proxy_host and proxy_port:
            self._proxy = f"http://{proxy_host}:{proxy_port}"

    def start(self):
        """
        start websocket
        end with calling on_connected()
        """
        self._active = True

        if not self._loop:
            self._loop = get_event_loop()
        start_event_loop(self._loop)

        run_coroutine_threadsafe(self._run(), self._loop)

    def stop(self):
        """
        stop websocket session
        """
        self._active = False

        if self._ws:
            coro = self._ws.close()
            run_coroutine_threadsafe(coro, self._loop)

        if self._loop and self._loop.is_running():
            self._loop.stop()

    def join(self):
        """
        wait for thread finish
        """
        pass

    def send_packet(self, packet: dict):
        """
        send json to server
        if non-json data needed, overridden this method
        """
        if self._ws:
            text: str = json.dumps(packet)
            self._record_last_sent_text(text)

            coro: coroutine = self._ws.send_str(text)
            run_coroutine_threadsafe(coro, self._loop)

    def unpack_data(self, data: str):
        """
        unpack json data
        if non-json data needed, overridden this method
        """
        return json.loads(data)

    def on_connected(self):
        """on connected callback"""
        pass

    def on_disconnected(self):
        """on disconnected callback"""
        pass

    def on_packet(self, packet: dict):
        """on packet callback"""
        pass

    def on_error(self, exception_type: type, exception_value: Exception, tb):
        """on error callback"""
        sys.stderr.write(
            self.exception_detail(exception_type, exception_value, tb)
        )
        return sys.excepthook(exception_type, exception_value, tb)

    def exception_detail(
        self, exception_type: type, exception_value: Exception, tb
    ):
        """parse exception"""
        text = "[{}]: Unhandled WebSocket Error:{}\n".format(
            datetime.now().isoformat(), exception_type
        )
        text += "LastSentText:\n{}\n".format(self._last_sent_text)
        text += "LastReceivedText:\n{}\n".format(self._last_received_text)
        text += "Exception trace: \n"
        text += "".join(
            traceback.format_exception(exception_type, exception_value, tb)
        )
        return text

    async def _run(self):
        """
        use coroutine
        """
        while self._active:
            try:
                self._ws = await self._session.ws_connect(
                    self._host,
                    proxy=self._proxy,
                    verify_ssl=False,
                    headers=self._header
                )

                self.on_connected()

                async for msg in self._ws:
                    text: str = msg.data
                    self._record_last_received_text(text)

                    data: dict = self.unpack_data(text)
                    self.on_packet(data)

                self._ws = None

                self.on_disconnected()
            except Exception:
                et, ev, tb = sys.exc_info()
                self.on_error(et, ev, tb)

    def _record_last_sent_text(self, text: str):
        """record last send text"""
        self._last_sent_text = text[:1000]

    def _record_last_received_text(self, text: str):
        """record last received text"""
        self._last_received_text = text[:1000]


def start_event_loop(loop: AbstractEventLoop) -> AbstractEventLoop:
    if not loop.is_running():
        thread = Thread(target=run_event_loop, args=(loop,))
        thread.daemon = True
        thread.start()


def run_event_loop(loop: AbstractEventLoop) -> None:
    set_event_loop(loop)
    loop.run_forever()
