"""
The client against a real Redis: run by ``make integration``, which starts
the server of ``docker-compose.yml`` and sets ``INGOT_REDIS_TEST_PORT``;
skipped without it.
"""

import os
import typing as t
import unittest
from unittest import mock

from ingot_redis import RedisProject
from ingot_redis.redis.clients import DefaultRedisClient
from redis.exceptions import AuthenticationError

PORT = os.environ.get("INGOT_REDIS_TEST_PORT")


@unittest.skipUnless(PORT, "no Redis: run make integration")
class ServerTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        self.enterContext(
            mock.patch.dict(
                os.environ,
                {
                    "INGOT_REDIS_DEFAULT_HOST": "127.0.0.1",
                    "INGOT_REDIS_DEFAULT_PORT": str(PORT),
                    "INGOT_REDIS_DEFAULT_USER": "ingot",
                    "INGOT_REDIS_DEFAULT_PASSWORD": "p@ss:w/rd",
                    "INGOT_REDIS_DEFAULT_TIMEOUT": "5",
                    "INGOT_IS_PRINT_CONFIGS": "off",
                },
                clear=True,
            )
        )
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))

    async def start(self) -> DefaultRedisClient:
        project = RedisProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return await project.redis.clients.default

    async def test_the_server_tells_its_version(self) -> None:
        redis = await self.start()
        info = await redis.client.info("server")
        self.assertRegex(info["redis_version"], r"^\d+\.\d+\.\d+")

    async def test_a_key_is_written_read_and_expires(self) -> None:
        redis = await self.start()
        self.addAsyncCleanup(redis.client.delete, "ingot_redis_test")
        await redis.client.set("ingot_redis_test", b"ingot", ex=60)
        self.assertEqual(await redis.client.get("ingot_redis_test"), b"ingot")
        self.assertGreater(await redis.client.ttl("ingot_redis_test"), 0)

    async def test_a_wrong_password_fails_the_start(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_PASSWORD"] = "wrong"
        with self.assertRaises(AuthenticationError):
            await self.start()

    async def test_the_user_default_is_off(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_USER"] = ""
        with self.assertRaises(AuthenticationError):
            await self.start()
