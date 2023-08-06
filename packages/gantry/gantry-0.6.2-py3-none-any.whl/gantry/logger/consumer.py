import json
import logging
import time
from queue import Empty, Queue
from threading import Thread
from typing import List, Optional

from gantry.serializers import EventEncoder

logger = logging.getLogger(__name__)


BATCH_SIZE_RECORD_LIMIT = 500  # 500 records / request.
BATCH_SIZE_LIMIT_BYTES = 5243000  # 5MiB / request
SINGLE_EVENT_LIMIT_BYTES = 1049000  # 1MiB / record
TIMEOUT_SECS = 1  # Max block time for fetching from queue
FLUSH_AFTER_SECS = 1  # Max time to hold data in cache


class _BatchIterBuilder:
    def __init__(
        self,
        queue: Queue,
        batch_size_record_limit: int = BATCH_SIZE_RECORD_LIMIT,
        single_event_limit_bytes: int = SINGLE_EVENT_LIMIT_BYTES,
        batch_size_limit_bytes: int = BATCH_SIZE_LIMIT_BYTES,
        timeout_secs: int = TIMEOUT_SECS,
        flush_after_secs: int = FLUSH_AFTER_SECS,
    ):
        self.queue = queue

        # Serves as cache. Needs to be flushed.
        self.current_json_dumped_batch: List[str] = []
        self.current_json_dumped_batch_size_bytes: int = 0

        self.batch_size_record_limit = batch_size_record_limit
        self.single_event_limit_bytes = single_event_limit_bytes
        self.batch_size_limit_bytes = batch_size_limit_bytes
        self.timeout_secs = timeout_secs
        self.flush_after_secs = flush_after_secs

        self._last_flushed: Optional[float] = None

    def empty(self) -> bool:
        return self.queue.empty() and len(self.current_json_dumped_batch) == 0

    def __iter__(self):
        return self

    def _store_event(self, dumped_json_event):
        self.current_json_dumped_batch.append(dumped_json_event)
        self.current_json_dumped_batch_size_bytes += len(dumped_json_event)

    def _flush(self):
        ret = self.current_json_dumped_batch
        self.current_json_dumped_batch = []
        self.current_json_dumped_batch_size_bytes = 0
        return ret

    def _reset(self, first_event):
        self.current_json_dumped_batch = [first_event]
        self.current_json_dumped_batch_size_bytes = len(first_event)

    def _flush_and_reset(self, dumped_json_event: str):
        # Mark this event as done to enable workers to join
        self.queue.task_done()
        ret = self._flush()
        self._reset(dumped_json_event)
        self._last_flushed = time.time()
        return ret

    def __next__(self):
        """
        If next(it) returns an empty batch, doesn't mean there are no more
        events, as they could be stored in the cache.
        """
        try:
            event = self.queue.get(block=True, timeout=self.timeout_secs)
            dumped_json_event = json.dumps(event, cls=EventEncoder).encode("utf8")

            if len(dumped_json_event) > self.single_event_limit_bytes:
                logger.error(
                    "Dropping record as it is larger than the maximum size allowed (%s bytes)",
                    self.single_event_limit_bytes,
                )
                # Mark this event as done to enable workers to join
                self.queue.task_done()
                return []

            if len(self.current_json_dumped_batch) >= self.batch_size_record_limit:
                logger.debug("Reached batch event size limit. Flushing.")
                return self._flush_and_reset(dumped_json_event)

            if (
                len(dumped_json_event) + self.current_json_dumped_batch_size_bytes
                > self.batch_size_limit_bytes
            ):
                logger.debug("Reached batch limit in bytes. Flushing.")
                return self._flush_and_reset(dumped_json_event)

            if (
                self._last_flushed is None
                or time.time() - self._last_flushed > self.flush_after_secs
            ):
                logger.debug("Reached cache holding limit. Flushing.")
                return self._flush_and_reset(dumped_json_event)

            self._store_event(dumped_json_event)
            # Mark this event as done to enable workers to join
            self.queue.task_done()
            return []

        except Empty:
            logger.debug("No items to consume from queue. Flushing.")
            return self._flush()


class BatchConsumer(Thread):
    def __init__(self, queue, func, batch_iter=_BatchIterBuilder):
        # Daemon threads don't block program exit
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.func = func

        # It's important to set running in the constructor: if we are asked to
        # pause immediately after construction, we might set running to True in
        # run() *after* we set it to False in pause... and keep running
        # forever.
        self.running = True

        # Should only be provided for testing purposes
        self._batch_iter = batch_iter

    def pause(self):
        self.running = False

    def consume(self, batch_iter):
        batch = next(batch_iter)
        if batch:
            self.func(batch)

    def run(self):
        batch_iter = iter(self._batch_iter(self.queue))
        while self.running or not batch_iter.empty():
            self.consume(batch_iter)
