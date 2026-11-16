"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("RedisSettingsUnit",)

from ingots.defaults.settings import SettingsUnit
from ingots.puer import Slot

from .configs import RedisConfigs


class RedisSettingsUnit(SettingsUnit):
    """The settings unit, with the addon's :class:`RedisConfigs`."""

    configs = Slot(RedisConfigs)
