import contextlib
import io
import os
import socket
import typing as t
import unittest
from unittest import mock

from ingot_redis import RedisProject
from ingot_redis.redis.clients import DefaultRedisClient, base
from ingots.defaults.cli import CommandRunner
from redis.asyncio import Redis
from redis.exceptions import ConnectionError


def find_closed_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port: int = sock.getsockname()[1]
    return port


class ClientTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        self.enterContext(
            mock.patch.dict(
                os.environ,
                {
                    "INGOT_REDIS_DEFAULT_HOST": "127.0.0.1",
                    "INGOT_REDIS_DEFAULT_PORT": str(find_closed_port()),
                    "INGOT_REDIS_DEFAULT_TIMEOUT": "0.1",
                    "INGOT_IS_PRINT_CONFIGS": "off",
                },
                clear=True,
            )
        )
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))
        self.created = self.enterContext(mock.patch.object(base, "Redis", wraps=Redis))

    async def start(self) -> tuple[RedisProject, DefaultRedisClient]:
        project = RedisProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return project, await project.redis.clients.default

    async def test_an_unreachable_server_fails_the_start(self) -> None:
        with (
            mock.patch.object(Redis, "aclose", autospec=True) as close,
            self.assertRaises(ConnectionError),
        ):
            await self.start()
        close.assert_awaited_once()

    async def test_the_ping_on_start_connects(self) -> None:
        # a server of its own is in tests.test_server; the ping alone here
        ping = mock.AsyncMock(return_value=True)
        with (
            mock.patch.object(Redis, "ping", ping),
            self.assertLogs("ingot_redis", "INFO") as logs,
        ):
            _, redis = await self.start()
        ping.assert_awaited_once_with()
        self.assertIn(f"{redis!r}: connected", logs.output[0])

    async def test_without_the_ping_the_client_connects_later(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_IS_PING_ON_START"] = "off"
        with self.assertLogs("ingot_redis", "INFO") as logs:
            _, redis = await self.start()
        self.assertIn("to connect at the first command", logs.output[0])
        self.assertIsInstance(redis.client, Redis)

    async def test_the_configs_reach_the_client(self) -> None:
        os.environ.update(
            {
                "INGOT_REDIS_DEFAULT_IS_PING_ON_START": "off",
                "INGOT_REDIS_DEFAULT_DB": "3",
                "INGOT_REDIS_DEFAULT_USER": "app",
                "INGOT_REDIS_DEFAULT_PASSWORD": "p@ss:w/rd",
                "INGOT_REDIS_DEFAULT_IS_TLS": "on",
            }
        )
        with self.assertLogs("ingot_redis", "INFO") as logs:
            _, redis = await self.start()
        self.created.assert_called_once_with(
            host="127.0.0.1",
            port=int(os.environ["INGOT_REDIS_DEFAULT_PORT"]),
            db=3,
            username="app",
            password="p@ss:w/rd",
            ssl=True,
            socket_timeout=0.1,
            socket_connect_timeout=0.1,
        )
        self.assertIn(
            f"{redis!r}: to connect at the first command as app", logs.output[0]
        )
        self.assertNotIn("p@ss", "".join(logs.output))

    async def test_without_a_password_there_is_no_authentication(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_IS_PING_ON_START"] = "off"
        await self.start()
        kwargs = self.created.call_args.kwargs
        self.assertIsNone(kwargs["username"])
        self.assertIsNone(kwargs["password"])
        self.assertFalse(kwargs["ssl"])

    async def test_a_password_alone_is_that_of_the_user_default(self) -> None:
        os.environ.update(
            {
                "INGOT_REDIS_DEFAULT_IS_PING_ON_START": "off",
                "INGOT_REDIS_DEFAULT_PASSWORD": "secret",
            }
        )
        await self.start()
        kwargs = self.created.call_args.kwargs
        self.assertIsNone(kwargs["username"])
        self.assertEqual(kwargs["password"], "secret")

    async def test_the_options_hook_adds_options_of_redis_py(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_IS_PING_ON_START"] = "off"
        with mock.patch.object(
            DefaultRedisClient, "_get_options", return_value={"client_name": "app"}
        ):
            await self.start()
        self.assertEqual(self.created.call_args.kwargs["client_name"], "app")

    async def test_the_shutdown_closes_the_client(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_IS_PING_ON_START"] = "off"
        project, redis = await self.start()
        with (
            mock.patch.object(
                redis.client, "aclose", wraps=redis.client.aclose
            ) as close,
            self.assertLogs("ingot_redis", "INFO") as logs,
        ):
            await project._do_shut_down()
        close.assert_awaited_once_with()
        self.assertIn(f"{redis!r}: closed", logs.output[-1])

    async def test_the_client_tells_its_server(self) -> None:
        os.environ["INGOT_REDIS_DEFAULT_IS_PING_ON_START"] = "off"
        _, redis = await self.start()
        port = os.environ["INGOT_REDIS_DEFAULT_PORT"]
        self.assertEqual(repr(redis), f"<DefaultRedisClient 127.0.0.1:{port}/0>")


class ComponentTestCase(unittest.TestCase):
    def run_project(self, *argv: str) -> str:
        with (
            mock.patch.dict(os.environ, clear=True),
            mock.patch("logging.config.dictConfig"),
            contextlib.redirect_stdout(io.StringIO()) as out,
        ):
            code = CommandRunner(
                RedisProject, ["--config", "IS_PRINT_CONFIGS=off", *argv]
            ).run()
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_the_client_is_a_component_of_the_project(self) -> None:
        self.assertIn(
            "redis.clients.default: DefaultRedisClient, shutdown order 8\n",
            self.run_project("components", "list"),
        )

    def test_the_password_is_a_secret(self) -> None:
        out = self.run_project(
            "--config", "REDIS_DEFAULT_PASSWORD=p@ss", "settings", "list"
        )
        self.assertIn("REDIS_DEFAULT_PASSWORD = ***\n", out)
        self.assertNotIn("p@ss", out)
