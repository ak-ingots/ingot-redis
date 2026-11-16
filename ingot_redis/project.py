"""The project of the addon: what an application inherits from."""

__all__ = ("RedisProject",)

from ingots.defaults import Project
from ingots.puer import Slot

from .logging import RedisLoggingUnit
from .redis import RedisUnit
from .settings import RedisSettingsUnit


class RedisProject(Project):
    """
    The project of the defaults with the addon's :class:`RedisSettingsUnit`,
    :class:`RedisLoggingUnit` and Redis, :class:`RedisUnit`. An application
    inherits from it and sets its own ``env_configs_prefix``; the addon run on
    its own (``python -m ingot_redis``) keeps the prefix of the defaults,
    ``INGOT``.
    """

    settings = Slot(RedisSettingsUnit)
    logging = Slot(RedisLoggingUnit)
    redis = Slot(RedisUnit)
