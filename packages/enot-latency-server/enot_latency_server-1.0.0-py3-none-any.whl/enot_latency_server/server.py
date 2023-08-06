"""Extendable latency measurement server."""
from abc import ABC
from abc import abstractmethod
from typing import Dict

from aiohttp import web

_DEFAULT_HOST: str = '0.0.0.0'
_DEFAULT_PORT: int = 5450
_DEFAULT_ENDPOINT: str = 'measure_latency'

__all__ = ['LatencyServer']


class LatencyServer(ABC):
    """
    Server for remote latency measurement.

    Extend this class by inheriting from it and implement the ``measure_latency`` method.
    This method should take model and return its latency in **milliseconds**.

    """

    __CLIENT_MAX_SIZE: int = 1000 * 1024 * 1024

    def __init__(self, host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT, endpoint: str = _DEFAULT_ENDPOINT):
        """
        Server ctor.

        Parameters
        ----------
        host : str
            Host name or IP address. Default value is '0.0.0.0'.
        port : int
            Port. Default value is 5450.
        endpoint : str
            Endpoint. Default value is 'measure_latency'.

        """
        super().__init__()

        self._host: str = host
        self._port: int = port
        self._endpoint: str = endpoint

        self._app = web.Application(client_max_size=self.__CLIENT_MAX_SIZE)

    def run(self) -> None:
        """Start latency measurement server."""

        async def _measure_latency_handler(request: web.Request) -> web.Response:
            model: bytes = await request.read()
            latency: Dict[str, float] = self.measure_latency(model)
            return web.json_response(data=latency, status=200)

        route = web.post(path=f'/{self._endpoint}', handler=_measure_latency_handler)
        self._app.add_routes([route])
        web.run_app(app=self._app, host=self._host, port=self._port)

    @staticmethod
    @abstractmethod
    def measure_latency(model: bytes) -> Dict[str, float]:
        """
        Latency measuring implementation for concrete device/framework/task/etc.

        Must return time in **MILLISECONDS** in the form: {'latency': latency}.
        You can also put in anything else like memory consumption: {'latency': latency, 'memory': memory}.
        When something bad happens you should raise ``web.HTTPBadRequest`` for correct reponse for client.

        Parameters
        ----------
        model : bytes
            Packaged model: pickled python object, ONNX, etc.

        Returns
        -------
        Dict[str, float]
            Latency in milliseconds and anything else (optional).

        """
