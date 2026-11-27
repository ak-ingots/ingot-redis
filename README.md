# ingot-redis

[![PyPI](https://img.shields.io/pypi/v/ingot-redis.svg)](https://pypi.org/project/ingot-redis/)
[![Python](https://img.shields.io/pypi/pyversions/ingot-redis.svg)](https://pypi.org/project/ingot-redis/)
[![ci](https://github.com/ak-ingots/ingot-redis/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-redis/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-redis/blob/main/LICENSE)

<!-- Links must be absolute: this README also renders on PyPI. -->

Integration of redis-py, the official client of Redis, into Ingots
applications, on its asynchronous API. An addon of
[Ingots](https://github.com/ak-ingots/ingots).

**Status:** pre-alpha: the clients of Redis servers, as
components.

## For Consumers

### Install

```sh
uv add ingot-redis
```

### Integrate

An application of Ingots has its own configs, settings, logging and project;
each takes the class of the addon among its bases:

```python
# app/project.py
import typing as t

from ingot_redis import RedisProject
from ingot_redis.logging import RedisLoggingUnit
from ingot_redis.settings import RedisSettingsUnit
from ingot_redis.settings.configs import RedisConfigs
from ingots.puer import Slot


class AppConfigs(RedisConfigs):
    pass


class AppSettingsUnit(RedisSettingsUnit):
    configs = Slot(AppConfigs)


class AppLoggingUnit(RedisLoggingUnit):
    project: "AppProject"


class AppProject(RedisProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
```

With other addons, their classes join the same bases:
`class AppConfigs(HttpConfigs, RedisConfigs)`, and so on, as the
[addon guide](https://github.com/ak-ingots/ingots/blob/main/docs/defaults/addon.md)
of Ingots shows. An application with this addon alone may inherit
`RedisProject` and nothing more.

The application runs through its own `__main__.py`:

```python
# app/__main__.py
import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.defaults.cli import CommandRunner

from .project import AppProject

configure_startup_logging()
sys.exit(CommandRunner(AppProject).run())
```

```sh
uv run python -m app settings list    # the configs, REDIS_* among them
uv run python -m app components list  # the clients, redis.clients.default among them
```

### Use the clients

`project.redis.clients.default` is a component holding redis-py's
asynchronous client, `redis.asyncio.Redis`, on `REDIS_DEFAULT_*`. Awaited,
it creates the client and pings the server, so that a server out of reach
fails the start and not the first command; the project closes it at the
shutdown. It gives redis-py as it is, `client`:

```python
redis = await self.project.redis.clients.default
await redis.client.set("greeting", b"hello", ex=60)
greeting = await redis.client.get("greeting")
```

Another server or database to reach is another client next to the default
one: a subclass of `BaseRedisClient` implementing its hooks on configs of
its own, `REDIS_<NAME>_*`, in a slot of a subclass of `RedisClientsUnit`,
set in a subclass of `RedisUnit` as `clients`; the project takes it as
`redis`. The options of redis-py the configs do not cover, such as
`decode_responses` or `ssl_ca_certs`, come from the hook `_get_options()`.
The extra of redis-py is that of the addon too:
`uv add "ingot-redis[hiredis]"`.

### Configs

Set as environment variables with the prefix of the project
(`APP_REDIS_DEFAULT_HOST`), in a `--configs-file` or with `--config`.

| Name | Default | Meaning |
|---|---|---|
| `REDIS_LOGGING_LEVEL` | `INFO` | the level of the logger of the addon, `ingot_redis` |
| `REDIS_DEFAULT_HOST` | `localhost` | the host of the server |
| `REDIS_DEFAULT_PORT` | `6379` | the port of the server |
| `REDIS_DEFAULT_DB` | `0` | the number of the database |
| `REDIS_DEFAULT_USER` | | the user of the ACL; empty, the user `default` |
| `REDIS_DEFAULT_PASSWORD` | | the password, a secret; empty, no authentication |
| `REDIS_DEFAULT_IS_TLS` | `False` | whether to connect by TLS, the certificate verified |
| `REDIS_DEFAULT_TIMEOUT` | `5.0` | the seconds to wait to connect, and for a reply |
| `REDIS_DEFAULT_IS_PING_ON_START` | `True` | whether to ping the server on start |

## Development

Requires [uv](https://docs.astral.sh/uv/), `make` and Docker, for the
Redis of the tests; uv fetches the interpreters it needs.

```sh
make                 # the target list
make check           # everything CI runs: lint, test, coverage, wheel-test, integration, cl-check
make format          # black
make all             # build the sdist and the wheel into dist/
```

- Every change users should know about adds a news fragment to `changelog.d/`
  (see [its README](https://github.com/ak-ingots/ingot-redis/blob/main/changelog.d/README.md)).
- A release is a pull request setting the version (`uv version X.Y.Z`) and
  collating the changelog (`make cl-build VERSION=X.Y.Z`), then the tag
  `vX.Y.Z` on `main`: the `release` workflow publishes the tested build to
  TestPyPI, tests it as installed from there, then
  publishes it to PyPI. Run by hand, it rehearses on TestPyPI only.
