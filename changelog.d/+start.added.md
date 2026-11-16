Started ingot-redis, an addon of Ingots for redis-py, for `ingots` 0.34.
`RedisProject` takes the addon's `RedisSettingsUnit`, whose `RedisConfigs`
add `REDIS_LOGGING_LEVEL` and `REDIS_DEFAULT_*`, `RedisLoggingUnit`, which
adds the logger `ingot_redis`, and `RedisUnit`, whose `clients.default` is
a component holding redis-py's asynchronous `Redis` on `REDIS_DEFAULT_HOST`,
`_PORT`, `_DB`, `_USER`, `_PASSWORD`, `_IS_TLS`, `_TIMEOUT` and
`_IS_PING_ON_START`: it pings the server on start, so that a server out of
reach fails the start, and closes the client at the shutdown. The extra
`hiredis` is redis-py's. `python -m ingot_redis` runs it on its own.
