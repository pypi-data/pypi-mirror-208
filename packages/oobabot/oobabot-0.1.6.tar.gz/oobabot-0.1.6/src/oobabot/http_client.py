import abc
import asyncio
import socket

import aiohttp


class OobaHttpClientError(Exception):
    pass


class SerializedHttpClient(abc.ABC):
    """
    Purpose: Limits the number of connections to a single host
    to one, so that we don't overwhelm the server.
    """

    HTTP_CLIENT_TIMEOUT_SECONDS: aiohttp.ClientTimeout = aiohttp.ClientTimeout(
        total=None,
        connect=None,
        sock_connect=5.0,
        sock_read=None,
    )

    @abc.abstractmethod
    async def _setup(self):
        # it's ok to raise an exception here, it will be caught
        ...

    async def setup(self):
        """
        Attempt to connect to the server.

        Returns:
            nothing, if the connection test was successful

        Raises:
            OobaHttpClientError, if the connection fails
        """
        try:
            await self._setup()
        except (
            aiohttp.ClientConnectionError,
            aiohttp.ClientError,
            ConnectionRefusedError,
            socket.gaierror,
            asyncio.exceptions.TimeoutError,
        ) as e:
            raise OobaHttpClientError(
                f"Could not connect to {self.service_name} server: [{self.base_url}]"
            ) from e

    def __init__(self, sevice_name: str, base_url: str):
        self.service_name = sevice_name
        self.base_url = base_url
        self._session = None

    def get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            raise OobaHttpClientError("Session not initialized")
        return self._session

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit_per_host=1)
        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            connector=connector,
            timeout=self.HTTP_CLIENT_TIMEOUT_SECONDS,
        )
        return self

    async def __aexit__(self, *_err):
        if self._session:
            await self._session.close()
        self._session = None

    def test_connection(self) -> None:
        async def try_setup():
            async with self:
                await self.setup()

        try:
            asyncio.run(try_setup())
        except AssertionError as e:
            # asyncio will throw an AssertionError if we try to run
            # with a base_url that has a path.  This is a user-supplied
            # value, so catching this is grody but necessary.
            raise OobaHttpClientError(
                f"Could not connect to {self.service_name} server: [{self.base_url}]"
            ) from e
