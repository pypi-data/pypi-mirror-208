"""Client implementation, use it to send model to latency measurement server."""
import logging
import time
from typing import Dict
from typing import Optional

import requests
from requests.exceptions import RequestException

from enot_latency_server.server import _DEFAULT_ENDPOINT
from enot_latency_server.server import _DEFAULT_HOST
from enot_latency_server.server import _DEFAULT_PORT

__all__ = ['measure_latency_remote']

logger = logging.getLogger(__name__)

_TRIAL_TIMEOUTS = [1, 1, 1, 5, 5, 5, 60, 60, 60]


def measure_latency_remote(
    model: bytes,
    host: str = _DEFAULT_HOST,
    port: int = _DEFAULT_PORT,
    endpoint: str = _DEFAULT_ENDPOINT,
    timeout: Optional[float] = None,
) -> Dict[str, float]:
    """
    Send model to remote measurement server and return latency in ms.

    Parameters
    ----------
    model : bytes
        Model for latency measurement.
    host : str
        Address of measurement service.
    port : int
        Port of measurement service.
    endpoint : str
        Endpoint of measurement service, default value is 'measurement_latency'.
    timeout : Optional[float]
        A number indicating how many seconds to wait for a client to make a connection or send a response.
        The default value of None means that the request will wait indefinitely.

    Returns
    -------
    Dict[str, float]
        Latency in milliseconds and anything else (optional).

    """
    for trial_timeout in _TRIAL_TIMEOUTS:
        try:
            response = requests.post(
                url=f'http://{host}:{port}/{endpoint}',
                data=model,
                headers={'Content-Type': 'application/octet-stream'},
                timeout=timeout,
            )
            if response.status_code == 200:
                return response.json()

            logger.warning(f'Expected status code is 200, got {response.status_code}')
        except RequestException as exc:
            logger.warning(f'An exception occured during latency measurement: {exc}')

        logger.warning(f'Next try will be in {trial_timeout}s')
        time.sleep(trial_timeout)

    raise RuntimeError('All attempts failed, latency cannot be measured, please check server log')
