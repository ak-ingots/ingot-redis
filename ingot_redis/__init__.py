"""
ingot-redis: Integration of redis-py, the official client of Redis, into
Ingots applications, on its asynchronous API. An application inherits from
:class:`RedisProject`, or joins the units of the addon, ``settings``,
``logging`` and ``redis``, with those of its other addons.
"""

__all__ = ("RedisProject",)

from .project import RedisProject
