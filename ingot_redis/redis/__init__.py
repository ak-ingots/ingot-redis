"""The Redis unit: the clients of the project."""

__all__ = ("RedisUnit",)

from ingots.puer import Slot, Unit

from .clients import RedisClientsUnit


class RedisUnit(Unit):
    """
    Redis in the project: :attr:`clients`, the clients of its servers. An
    application with more clients declares ``clients = Slot(AppRedisClientsUnit)``
    in a subclass of this unit.
    """

    clients = Slot(RedisClientsUnit)
