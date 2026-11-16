"""The logging unit of the defaults with the logger of the addon."""

__all__ = ("RedisLoggingUnit",)

import typing as t

from ingots.defaults.logging import LoggingUnit

if t.TYPE_CHECKING:
    from ..project import RedisProject


class RedisLoggingUnit(LoggingUnit):
    """
    The logging unit, with the logger of the addon, ``ingot_redis``, at
    ``REDIS_LOGGING_LEVEL``.
    """

    project: "RedisProject"

    @t.override
    def build_loggers(self) -> dict[str, dict[str, t.Any]]:
        level = self.project.settings.configs.REDIS_LOGGING_LEVEL
        addon = {"level": level, "handlers": ["default"], "propagate": False}
        return {**super().build_loggers(), "ingot_redis": addon}
