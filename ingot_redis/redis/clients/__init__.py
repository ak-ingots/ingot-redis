"""The clients: the Redis clients of the project, each a component."""

__all__ = ("BaseRedisClient", "DefaultRedisClient", "RedisClientsUnit")

from ingots.puer import Slot, Unit

from .base import BaseRedisClient
from .default import DefaultRedisClient


class RedisClientsUnit(Unit):
    """
    The Redis clients of the project: :attr:`default` for a start. An
    application with more servers to reach adds clients in a subclass, each
    a subclass of :class:`BaseRedisClient` with configs of its own.
    """

    default = Slot(DefaultRedisClient)
