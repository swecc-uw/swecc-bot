import asyncio
import os
import urllib
import logging
from pika.adapters.asyncio_connection import AsyncioConnection
import pika


logger = logging.getLogger(__name__)


class ConnectionManager:
    instance = None

    def __init__(self, loop=None):

        if ConnectionManager.instance.initialized:
            return

        self._connection = None
        self._closing = False
        self._ready = asyncio.Event(loop=loop)
        self._connected = False
        self._loop = None
        self._url = self._build_amqp_url()
        self.initialized = True
        self._loop = loop

    async def connect(self):
        logger.info(f"Connecting to {self._url}.")

        try:
            if self._connection and not (
                self._connection.is_closed or self._connection.is_closing
            ):
                logger.info(f"Using existing connection.")
                return self._connection

            self._ready.clear()

            future_connection = AsyncioConnection(
                parameters=pika.URLParameters(self._url),
                on_open_callback=self.on_connection_open,
                on_open_error_callback=self.on_connection_open_error,
                on_close_callback=self.on_connection_closed,
                custom_ioloop=self._loop,
            )

            await self._ready.wait()

            self._connection = future_connection
            return self._connection
        except Exception as e:
            logger.error(f"Failed to create connection: {str(e)}")
            self._connection = None
            raise

    def on_connection_open(self, connection):
        logger.info(f"Connection opened for {self._url}")
        self._ready.set()
        self._connected = True

    def on_connection_open_error(self, connection, err):
        logger.error(f"Failed to open connection: {err}")
        self._ready.set()
        self._connected = False

    def _build_amqp_url(self) -> str:
        user = os.getenv("BOT_RABBIT_USER", "guest")
        password = os.getenv("BOT_RABBIT_PASS", "guest")
        host = os.getenv("RABBIT_HOST", "rabbitmq-host")
        port = os.getenv("RABBIT_PORT", "5672")
        vhost = os.getenv("RABBIT_VHOST", "/")
        vhost = urllib.parse.quote(vhost, safe="")
        return f"amqp://{user}:{password}@{host}:{port}/{vhost}"

    def on_connection_closed(self, connection, reason):
        self._connected = False
        if self._closing:
            logger.info(f"Connection to RabbitMQ closed.")
        else:
            logger.warning(f"Connection closed unexpectedly: {reason}")

    async def close(self):
        self._closing = True
        logger.info(f"Closing connection...")
        if self._connection and not (
            self._connection.is_closing or self._connection.is_closed
        ):
            self._connection.close()
        self._connected = False

    def is_connected(self):
        return self._connected

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(ConnectionManager, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance
