"""The base of the Redis clients: a component holding a client of redis-py."""

__all__ = ("BaseRedisClient",)

import logging
import typing as t

from ingots.puer import Component
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class BaseRedisClient(Component):
    """
    A client of a Redis server: the connection pool of redis-py's
    asynchronous :class:`~redis.asyncio.Redis`, given as it is. Await it
    before use, as any component of the project::

        redis = await self.project.redis.clients.default
        await redis.client.set("key", b"value", ex=60)

    Configured, it creates the client and, unless told otherwise, pings the
    server, so that a server out of reach fails the start and not the first
    command; shut down, it closes the client and its pool.

    A client takes its settings from the hooks, which a subclass implements:
    :meth:`_get_host`, :meth:`_get_port`, :meth:`_get_db`, :meth:`_get_user`,
    :meth:`_get_password`, :meth:`_is_tls`, :meth:`_get_timeout` and
    :meth:`_is_ping_on_start`; :meth:`_get_options` adds options of
    redis-py.
    """

    SHUTDOWN_ORDER = 8

    _client: Redis

    @t.final
    @property
    def client(self) -> Redis:
        """The client of redis-py, once configured."""
        return self._client

    @t.override
    def __repr__(self) -> str:
        return (
            f"<{type(self).__qualname__} "
            f"{self._get_host()}:{self._get_port()}/{self._get_db()}>"
        )

    @t.override
    async def _configure(self) -> None:
        user = self._get_user()
        timeout = self._get_timeout()
        client = Redis(
            host=self._get_host(),
            port=self._get_port(),
            db=self._get_db(),
            username=user or None,
            password=self._get_password() or None,
            ssl=self._is_tls(),
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
            **self._get_options(),
        )
        as_user = f" as {user}" if user else ""
        if self._is_ping_on_start():
            try:
                await client.ping()
            except Exception:
                await client.aclose()
                raise
            logger.info("%r: connected%s", self, as_user)
        else:
            logger.info("%r: to connect at the first command%s", self, as_user)
        self._client = client

    @t.override
    async def _shut_down(self) -> None:
        await self._client.aclose()
        logger.info("%r: closed", self)

    def _get_host(self) -> str:
        """The host of the server."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_host")

    def _get_port(self) -> int:
        """The port of the server."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_port")

    def _get_db(self) -> int:
        """The number of the database of the server."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_db")

    def _get_user(self) -> str:
        """The user of the ACL to authenticate as; empty, the user ``default``."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_user")

    def _get_password(self) -> str:
        """The password; empty for no authentication."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_password")

    def _is_tls(self) -> bool:
        """Whether the connection is of TLS, the certificate verified."""
        raise NotImplementedError(f"{type(self).__qualname__}._is_tls")

    def _get_timeout(self) -> float:
        """The seconds to wait to connect, and for a reply."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_timeout")

    def _is_ping_on_start(self) -> bool:
        """Whether to ping the server when configured."""
        raise NotImplementedError(f"{type(self).__qualname__}._is_ping_on_start")

    def _get_options(self) -> dict[str, t.Any]:
        """
        Other options of :class:`~redis.asyncio.Redis`, such as
        ``decode_responses`` or ``ssl_ca_certs``: none by default.
        """
        return {}
