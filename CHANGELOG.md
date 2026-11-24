# ingot-redis Changelog

ingot-redis is rewritten from scratch starting with 0.2.0; 0.1.0, on PyPI
and TestPyPI since 2021, is the previous implementation.

<!-- towncrier release notes start -->

## [0.5.0] - 2026-11-24
### Changed
- Moved on to ingots 0.37.

## [0.4.0] - 2026-11-20
### Changed
- Moved on to ingots 0.36.

## [0.3.0] - 2026-11-17
### Changed
- Moved on to ingots 0.35.

## [0.2.0] - 2026-11-16
### Added
- Started ingot-redis, an addon of Ingots for redis-py, for `ingots` 0.34.
  `RedisProject` takes the addon's `RedisSettingsUnit`, whose `RedisConfigs`
  add `REDIS_LOGGING_LEVEL` and `REDIS_DEFAULT_*`, `RedisLoggingUnit`, which
  adds the logger `ingot_redis`, and `RedisUnit`, whose `clients.default` is
  a component holding redis-py's asynchronous `Redis` on `REDIS_DEFAULT_HOST`,
  `_PORT`, `_DB`, `_USER`, `_PASSWORD`, `_IS_TLS`, `_TIMEOUT` and
  `_IS_PING_ON_START`: it pings the server on start, so that a server out of
  reach fails the start, and closes the client at the shutdown. The extra
  `hiredis` is redis-py's. `python -m ingot_redis` runs it on its own.
