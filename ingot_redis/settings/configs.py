"""The configs of the addon, named ``REDIS_*``."""

__all__ = ("RedisConfigs",)

import logging

from ingots.defaults.settings.configs import (
    BoolConfig,
    Configs,
    FloatConfig,
    IntConfig,
    LogLevelConfig,
    SecureStrConfig,
    StrConfig,
)


class RedisConfigs(Configs):
    """
    The configs of the defaults with those of redis-py. ``REDIS_DEFAULT_*``
    are the configs of the default client: another client takes configs of
    its own, ``REDIS_<NAME>_*``.
    """

    REDIS_LOGGING_LEVEL = LogLevelConfig(logging.INFO)

    # the default client
    REDIS_DEFAULT_HOST = StrConfig("localhost")
    REDIS_DEFAULT_PORT = IntConfig(6379)
    REDIS_DEFAULT_DB = IntConfig(0)
    REDIS_DEFAULT_USER = StrConfig("")  # empty: the user default of Redis
    REDIS_DEFAULT_PASSWORD = SecureStrConfig("")  # empty: no authentication
    REDIS_DEFAULT_IS_TLS = BoolConfig(False)
    REDIS_DEFAULT_TIMEOUT = FloatConfig(5.0)  # seconds, to connect and to reply
    REDIS_DEFAULT_IS_PING_ON_START = BoolConfig(True)
