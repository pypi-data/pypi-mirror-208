import atexit
import json
import logging
import logging.handlers
from dataclasses import asdict
from queue import Queue
from typing import Callable, Collection, Iterator, List, Optional, cast

import backoff
import requests

from gantry.api_client import APIClient
from gantry.exceptions import GantryRequestException
from gantry.logger.consumer import BatchConsumer
from gantry.logger.types import (
    IngestFromDataConnectorRequest,
    IngestFromDataConnectorResponse,
)
from gantry.serializers import EventEncoder

logger = logging.getLogger(__name__)


BATCH_UPLOAD_MAX_TRIES = 3
BACKOFF_INTERVAL_FOR_ERROR_CODE_SECS = 5
BACKOFF_INTERVAL_FOR_TIMEOUT_SECS = 1


def non_retry_error(e: Exception) -> bool:
    gre = cast(GantryRequestException, e)
    return gre.status_code != 502


def backoff_retry_handler(backoff_ctx: backoff._typing.Details):
    logger.warning("Experiencing timeouts. Please check your connection.")


def backoff_giveup_handler(backoff_ctx: backoff._typing.Details):
    logger.error(
        f"""Failed to log events due to timeout. Have tried {backoff_ctx['tries']}
         times for {backoff_ctx['elapsed']} seconds. Please check your connection."""
    )


def _batch_iterator_factory(
    collection: Collection, batch_size: int
) -> Callable[[], Iterator[List]]:
    if batch_size <= 0:
        raise ValueError(f"Batch size needs to be a positive int, not {batch_size}")

    def _iterator():
        size = len(collection)
        for ndx in range(0, size, batch_size):
            yield collection[ndx : min(ndx + batch_size, size)]  # noqa: E203

    return _iterator


class BaseLogStore:
    def log(self, application: str, event: dict) -> None:
        """
        Logs a prediction or feedback event.

        Args:
            application: Name of the application
            event: Data to logs as event body
        """
        self.log_batch(application, [event])

    def log_batch(self, application: str, events: List[dict]) -> None:
        pass

    def ping(self):
        pass

    def ready(self):
        pass


class APILogStore(BaseLogStore):
    BATCH_SIZE = 20
    BATCH_UPLOAD_TIMEOUT = 20  # seconds before retrying on upload

    def __init__(
        self,
        location: str,
        api_key: Optional[str] = None,
        send_in_background: bool = True,
        bypass_firehose: bool = False,
        consumer_factory=BatchConsumer,
    ):
        """
        Send logged events directly to the Gantry API.
        This is the recommended log store when using the local Gantry stack.

        Args:
            location (str): Gantry API host URI
            api_key (str, Optional): Gantry API Key, retrieved from the dashboard.
            send_in_background (bool, true by default): Whether to send events
                in a background thread.
            bypass_firehose (bool, false by default): Bypass firehose streaming
                and send directly to DB.
            consumer_factory: Used only for testing. Never use parameter in production.
        """
        self._api_client = APIClient(location, api_key=api_key)

        self._bypass_firehose = bypass_firehose

        self.num_consumer_threads: int = 1
        self.send_in_background = send_in_background
        self.queue: Queue = Queue()

        self.consumers = []
        self._consumer_factory = consumer_factory

        if self.send_in_background:
            # On program exit, allow the consumer thread to exit cleanly.
            # This prevents exceptions and a messy shutdown when the
            # interpreter is destroyed before the daemon thread finishes
            # execution.
            atexit.register(self._join)
            for _ in range(self.num_consumer_threads):
                consumer = self._consumer_factory(self.queue, self.consumer_func)
                self.consumers.append(consumer)
                consumer.start()

    def ping(self) -> bool:
        """
        Pings the API to check if it is up and running. Returns True if alive, else False.
        """
        try:
            # Cannot use /healthz/* endpoints as those will be answered by nginx
            # need to use /.
            # See https://linear.app/gantry/issue/ENG-2978/revisit-ping-in-sdk
            self._api_client.request("GET", "/api/ping", raise_for_status=True)
            return True
        except Exception as e:
            logger.error(f"Error during ping: {e}")
            return False

    def ready(self) -> bool:
        """
        Checks whether the API is ready to receive traffic with
        the provided API Key.
        """
        try:
            self._api_client.request("GET", "/api/v1/auth-ping", raise_for_status=True)
            return True
        except Exception as e:
            logger.error(f"Error during api key check: {e}")
            return False

    def consumer_func(self, batch):
        # Catch all errors and do not raise in order
        # for thread consumer to continue running.
        try:
            return self.send_batch_as_raw_events(batch, as_raw=True)
        except Exception as e:
            logger.error("Internal error sending batches: %s", e)

    @backoff.on_exception(
        backoff.constant,
        (requests.Timeout, requests.ConnectionError),
        interval=BACKOFF_INTERVAL_FOR_TIMEOUT_SECS,
        max_tries=BATCH_UPLOAD_MAX_TRIES,
        on_backoff=backoff_retry_handler,
        on_giveup=backoff_giveup_handler,
        jitter=None,
    )
    @backoff.on_exception(
        backoff.constant,
        GantryRequestException,
        max_tries=BATCH_UPLOAD_MAX_TRIES,
        interval=BACKOFF_INTERVAL_FOR_ERROR_CODE_SECS,
        on_backoff=backoff_retry_handler,
        on_giveup=backoff_giveup_handler,
        giveup=non_retry_error,
        jitter=None,
    )
    def send_batch_as_raw_events(self, batch: List, as_raw: bool = False) -> None:
        if as_raw:
            data = b",".join(batch)
            data = bytes('{"events": [', "utf8") + data + bytes("]}", "utf8")
        else:
            data = json.dumps({"events": batch}, cls=EventEncoder).encode("utf8")

        params = {}
        if self._bypass_firehose:
            params["bypass-firehose"] = "true"

        response = self._api_client.request(
            "POST",
            "/api/v1/ingest/raw",
            data=data,
            params=params,
            headers={"Content-Type": "application/json"},
            timeout=APILogStore.BATCH_UPLOAD_TIMEOUT,
            raise_for_status=True,
        )

        if response.get("response") != "ok":
            logger.error("Failed to log events. Response = %s", response)

    def log_batch(self, application: str, events: List[dict]) -> None:
        if not self.send_in_background:
            logger.info("Sending batch synchronously")
            batch_iterator_builder = _batch_iterator_factory(events, APILogStore.BATCH_SIZE)
            for batch in batch_iterator_builder():
                self.send_batch_as_raw_events(batch)
        else:
            for e in events:
                self.queue.put(e)

    def log_from_data_connector_async(
        self, request: IngestFromDataConnectorRequest
    ) -> IngestFromDataConnectorResponse:
        response = self._api_client.request(
            "POST",
            "/api/v1/ingest/data-connectors",
            json=asdict(request),
            headers={"Content-Type": "application/json"},
            raise_for_status=True,
        )

        return IngestFromDataConnectorResponse(**response["data"])

    def _join(self):
        """
        Ends the consumer thread once the queue is empty.
        Blocks execution until finished
        """
        for consumer in self.consumers:
            consumer.pause()
            try:
                consumer.join()
            except RuntimeError:
                # consumer thread has not started
                pass
