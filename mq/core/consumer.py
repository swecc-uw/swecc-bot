import asyncio
import logging
import functools
from typing import Callable, Dict, List, Optional, Any, Coroutine

import pika
import pika.exceptions
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType

LOGGER = logging.getLogger(__name__)


class AsyncRabbitConsumer:
    def __init__(
        self,
        amqp_url: str,
        exchange: str,
        exchange_type: ExchangeType,
        declare_exchange: bool,
        queue: str,
        routing_key: str,
        callback: Callable[[bytes, Any], Coroutine],
        prefetch_count: int = 1,
    ):
        # queue config
        self._url = amqp_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._queue = queue
        self._routing_key = routing_key
        self.message_callback = callback
        self._prefetch_count = prefetch_count
        self._declare_exchange = declare_exchange

        # connection state
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

    async def connect(self, loop=None):
        LOGGER.info(
            f"Connecting to {self._url} for exchange {self._exchange}, queue {self._queue}"
        )

        try:
            if self._connection and not (self._connection.is_closed or self._connection.is_closing):
                LOGGER.info(f"Using existing connection for {self._queue}")
                return self._connection

            future_connection = AsyncioConnection(
                parameters=pika.URLParameters(self._url),
                on_open_callback=self.on_connection_open,
                on_open_error_callback=self.on_connection_open_error,
                on_close_callback=self.on_connection_closed,
                custom_ioloop=loop,
            )

            self._connection = future_connection
            return self._connection
        except Exception as e:
            LOGGER.error(f"Failed to create connection for {self._queue}: {str(e)}")
            self._connection = None
            raise

    def on_connection_open(self, connection):
        LOGGER.info(f"Connection opened for {self._queue}")
        self.open_channel()

    def on_connection_open_error(self, connection, err):
        LOGGER.error(f"Connection open failed for {self._queue}: {err}")

    def on_connection_closed(self, connection, reason):
        self._channel = None
        if self._closing:
            LOGGER.info(f'Connection closed for {self._queue}')
        else:
            LOGGER.warning(f'Connection closed unexpectedly for {self._queue}: {reason}')
            # health monitor handles reconnection

    def open_channel(self):
        LOGGER.info(f"Creating a new channel for {self._queue}")
        if self._connection:
            self._connection.channel(on_open_callback=self.on_channel_open)
        else:
            LOGGER.warning(f"Connection is not open for {self._queue}")

    def on_channel_open(self, channel):
        LOGGER.info(f"Channel opened for {self._queue}")
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self.setup_exchange(self._exchange)

    def on_channel_closed(self, channel, reason):
        LOGGER.warning(f"Channel was closed for {self._queue}: {reason}")

    def setup_exchange(self, exchange_name):
        """declare exchange"""
        if self._declare_exchange:
            LOGGER.info(f"Declaring exchange: {exchange_name}")
            cb = functools.partial(self.on_exchange_declareok, exchange_name=exchange_name)
            if self._channel:
                self._channel.exchange_declare(
                    exchange=exchange_name, exchange_type=self._exchange_type, callback=cb
                )
            else:
                LOGGER.warning(f"Channel is not open for exchange declaration: {exchange_name}")
        else:
            LOGGER.info(f"Skipping exchange declaration for {exchange_name}")
            self.setup_queue(self._queue)

    def on_exchange_declareok(self, _unused_frame, exchange_name):
        """exchange is declared"""
        LOGGER.info(f"Exchange declared: {exchange_name}")
        self.setup_queue(self._queue)

    def setup_queue(self, queue_name):
        """declare the queue"""
        LOGGER.info(f"Declaring queue {queue_name}")
        cb = functools.partial(self.on_queue_declareok, queue_name=queue_name)
        if self._channel:
            self._channel.queue_declare(queue=queue_name, callback=cb)
        else:
            LOGGER.warning(f"Channel is not open for queue declaration: {queue_name}")

    def on_queue_declareok(self, _unused_frame, queue_name):
        """queue is declared"""
        LOGGER.info(
            f"Binding {self._exchange} to {queue_name} with {self._routing_key}"
        )
        cb = functools.partial(self.on_bindok, queue_name=queue_name)
        if self._channel:
            self._channel.queue_bind(
                queue_name, self._exchange, routing_key=self._routing_key, callback=cb
            )
        else:
            LOGGER.warning(f"Channel is not open for queue binding: {queue_name}")

    def on_bindok(self, _unused_frame, queue_name):
        """queue bound to exchange"""
        LOGGER.info(f"Queue bound: {queue_name}")
        self.set_qos()

    def set_qos(self):
        """set prefetch count"""
        if self._channel:
            self._channel.basic_qos(
                prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok
            )
        else:
            LOGGER.warning(f"Channel is not open for setting QoS: {self._queue}")

    def on_basic_qos_ok(self, _unused_frame):
        """called when QoS set"""
        LOGGER.info(f"QOS set to: {self._prefetch_count} for {self._queue}")
        self.start_consuming()

    def start_consuming(self):
        LOGGER.info(f"Starting to consume messages for {self._queue}")
        if self._channel:
            self._consumer_tag = self._channel.basic_consume(self._queue, self.on_message)
        else:
            LOGGER.warning(f"Channel is not open for consuming messages: {self._queue}")

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        LOGGER.info(f"Received message # {basic_deliver.delivery_tag} on {self._queue}")

        if self.message_callback:
            # process in event loop
            asyncio.create_task(self.message_callback(body, properties))

        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        LOGGER.info(f"Acknowledging message {delivery_tag} on {self._queue}")
        if self._channel:
            self._channel.basic_ack(delivery_tag)
        else:
            LOGGER.warning(f"Channel is not open for acknowledging message: {self._queue}")

    def stop_consuming(self):
        if self._channel:
            LOGGER.info(f"Stopping consumption for {self._queue}")
            self._channel.basic_cancel(self._consumer_tag, self.on_cancelok)

    def on_cancelok(self, _unused_frame):
        """consumption is cancelled"""
        LOGGER.info(f"Consumption cancelled for {self._queue}")
        self.close_channel()

    def close_channel(self):
        LOGGER.info(f"Closing the channel for {self._queue}")
        if self._channel:
            self._channel.close()
        else:
            LOGGER.warning(f"Channel is already closed for {self._queue}")

    def close_connection(self):
        self._closing = True
        LOGGER.info(f"Closing connection for {self._queue}")
        try:
            if self._connection and not (self._connection.is_closed):
                self._connection.close()
            else:
                LOGGER.info(f"Connection already closed for {self._queue}")
        except pika.exceptions.ConnectionWrongStateError as e:
            LOGGER.warning(f"Connection already in closed state for {self._queue}: {str(e)}")
        except Exception as e:
            LOGGER.error(f"Error closing connection for {self._queue}: {str(e)}")

    async def shutdown(self):
        LOGGER.info(f"Shutting down consumer for {self._queue}")
        try:
            if self._channel:
                self.stop_consuming()

            if self._connection and not (
                self._connection.is_closing or self._connection.is_closed
            ):
                self.close_connection()
        except pika.exceptions.ConnectionWrongStateError as e:
            LOGGER.warning(f"Connection already closed for {self._queue}: {str(e)}")
        except Exception as e:
            LOGGER.error(f"Error during shutdown for {self._queue}: {str(e)}")
        finally:
            self._channel = None
            self._connection = None
            self._consumer_tag = None