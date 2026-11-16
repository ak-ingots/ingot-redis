"""The default Redis client of the project."""

__all__ = ("DefaultRedisClient",)

import typing as t

from .base import BaseRedisClient

if t.TYPE_CHECKING:
    from ingot_redis.project import RedisProject


class DefaultRedisClient(BaseRedisClient):
    """The client of the configs ``REDIS_DEFAULT_*``."""

    project: "RedisProject"

    @t.override
    def _get_host(self) -> str:
        return self.project.settings.configs.REDIS_DEFAULT_HOST

    @t.override
    def _get_port(self) -> int:
        return self.project.settings.configs.REDIS_DEFAULT_PORT

    @t.override
    def _get_db(self) -> int:
        return self.project.settings.configs.REDIS_DEFAULT_DB

    @t.override
    def _get_user(self) -> str:
        return self.project.settings.configs.REDIS_DEFAULT_USER

    @t.override
    def _get_password(self) -> str:
        return self.project.settings.configs.REDIS_DEFAULT_PASSWORD

    @t.override
    def _is_tls(self) -> bool:
        return self.project.settings.configs.REDIS_DEFAULT_IS_TLS

    @t.override
    def _get_timeout(self) -> float:
        return self.project.settings.configs.REDIS_DEFAULT_TIMEOUT

    @t.override
    def _is_ping_on_start(self) -> bool:
        return self.project.settings.configs.REDIS_DEFAULT_IS_PING_ON_START
