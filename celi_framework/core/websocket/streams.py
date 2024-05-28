import asyncio
import inspect
import logging
from typing import AsyncIterator, Callable, Optional, TypeVar, Union, Awaitable

import asyncstdlib
from starlette.websockets import WebSocketState, WebSocket

logger = logging.getLogger(__name__)

T = TypeVar("T")
Output = TypeVar("Output", covariant=True)
AwaitableOrObj = Union[T, Awaitable[T]]


class _MarkerObjectType:
    """This is a marker object used to indicate a special case during stream iteration."""

    pass


EndOfStreamMarker = _MarkerObjectType()
"""Special marker object that indicates the end of a stream.
"""


async def resolve_awaitable_or_obj(obj: AwaitableOrObj[T]) -> T:
    """Returns the result of an object or a future"""
    if inspect.isawaitable(obj):
        return await obj
    return obj


async def cancel_with_confirmation(task: asyncio.Task) -> None:
    """Cancels a task and waits for confirmation that it has stopped."""
    task.cancel()
    try:
        a = await task
        # logger.debug(f"Return {a}")
    except asyncio.CancelledError:
        # logger.debug("C")
        pass
    except StopAsyncIteration:
        # logger.debug("S")
        pass
    # logger.debug(f"Cancelled task {format_task(task)}")


async def map_step(
    async_iter: AsyncIterator[T],
    func: Callable[[T], Output],
    ignore_none: Optional[bool] = False,
) -> AsyncIterator[Output]:
    """
    Data flow step that transforms items using a mapping function.

    This function applies either a synchronous or asynchronous mapping function to each item in the
    input async iterator. If `ignore_none` is set to True, any items that are transformed to `None`
    are not yielded. This feature allows the function to perform both transformation and filtering in a single step.

    Parameters
    ----------
    async_iter : AsyncIterator[T]
        The asynchronous iterator whose items are to be transformed.
    func : Callable[[T], Output]
        A mapping function to apply to each item. This can be either a synchronous or asynchronous function.
    ignore_none : Optional[bool], default False
        If True, items that are transformed to None by `func` are not yielded.

    Returns
    -------
    AsyncIterator[Output]
        An asynchronous iterator yielding transformed items, optionally skipping None values.
    """
    is_async = inspect.iscoroutinefunction(func)
    async with asyncstdlib.scoped_iter(async_iter) as owned_aiter:
        async for item in owned_aiter:
            v = func(item)
            if is_async:
                v = await v
            if (not ignore_none) or (v is not None):
                yield v


async def fastapi_websocket_text_sink(
    async_iter: AsyncIterator[Union[str, dict]], websocket: WebSocket
) -> None:
    """
    Data flow sink to send data to a FastAPI WebSocket connection.

    This function takes an asynchronous iterator, which can yield either strings, Pydantic objects, or
    dictionaries, and sends each item to a specified WebSocket. If the item is a dictionary,
    it is sent as a JSON message. Otherwise, it is sent as a text message.

    Parameters
    ----------
    async_iter : AsyncIterator[Union[str, dict]]
        An asynchronous iterator that yields either strings or dictionaries.
    websocket : WebSocket
        The FastAPI WebSocket connection to which the data will be sent.

    Notes
    -----
    - This function is useful for streaming data from an asynchronous source to a WebSocket
      client. It supports both text and JSON formats, making it versatile for various types
      of data communication in a FastAPI application.
    - This sink will call `accept` on the websocket if it has not already been called.

    See Also
    --------
    WebSocket.send_json : Method of FastAPI's WebSocket to send JSON data.
    WebSocket.send_text : Method of FastAPI's WebSocket to send text data.

    """
    async with asyncstdlib.scoped_iter(async_iter) as owned_aiter:
        if websocket.client_state == WebSocketState.CONNECTING:
            await websocket.accept()
        async for message in owned_aiter:
            if isinstance(message, dict):
                await websocket.send_json(message)
            elif hasattr(message, "model_dump"):
                json = message.model_dump()
                logger.info(f"Sending {json}")
                await websocket.send_json(json)
            else:
                await websocket.send_text(message)


class QueueAsyncIterator:
    """
    An asynchronous iterator that operates on its own queue.

    This class implements an async iterator which allows asynchronous iteration over
    queued items. It uses an asyncio.Queue for storing items and provides a `put` method
    to add items to this queue. The iterator retrieves items from the queue in the order
    they were added.
    """

    def __init__(self):
        self.queue = asyncio.Queue()
        self.iter = queue_source(self.queue)

    async def put(self, item):
        """Adds an item to the queue managed by this iterator.

        Parameters
        ----------
        item : any type
            The item to be added to the queue.
        """
        return await self.queue.put(item)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.iter.__anext__()


def queue_source(
    queue: AwaitableOrObj[asyncio.Queue[T]] = None,
    cancel_event: asyncio.Event = None,
) -> Union[AsyncIterator[T], QueueAsyncIterator]:
    """
    Data flow source that yields items from an asyncio.Queue.

    This function returns an asynchronous iterator that consumes items from an asyncio.Queue.  The iteration continues
    until an `EndOfStreamMarker` is encountered in the queue, signaling the end of iteration.

    Parameters
    ----------
    queue : AwaitableOrObj[asyncio.Queue[T]], optional
        An instance of asyncio.Queue from which the items will be consumed. This can be an instance of the queue
        or an Awaitable that returns the queue, which can be useful if the queue isn't yet created.  This parameter is
        optional.  If not provided, the AsyncIterator will be a :func:`~voice_stream.QueueAsyncIterator` which allows
        items to be added to the queue via the `put` method.
    cancel_event : asyncio.Event
        An optional cancellation event that externally indicates that this sink should stop listening on the queue.
        This is useful if the queue will be reused for another operation.  Otherwise this event will sit around waiting
        for a new message.

    Returns
    -------
    AsyncIterator[T]
        An asynchronous iterator over the items in the queue.


    Notes
    -----
    - The function expects that the queue will be closed by putting `EndOfStreamMarker` into it.
    - If an Awaitable[Queue] is passed, this function will return immediately and the queue will be awaited when the iterator is started.
    - cancel_event is only allowed if a queue is passed in.  (It doesn't make sense otherwise.  If the queue is internally managed, it can't be reused).
    """
    if queue:
        if cancel_event:

            class WaitingIter:
                def __init__(self, queue, event):
                    self.queue = queue
                    self.event = event

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    if self.event.is_set():
                        raise StopAsyncIteration
                    resolved_queue = await resolve_awaitable_or_obj(self.queue)
                    item_task = asyncio.create_task(resolved_queue.get())
                    stop_task = asyncio.create_task(self.event.wait())
                    done, pending = await asyncio.wait(
                        {item_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in pending:
                        await cancel_with_confirmation(task)
                    if item_task in done:
                        item = await item_task
                        if item == EndOfStreamMarker:
                            raise StopAsyncIteration
                        return item
                    else:
                        assert stop_task in done
                        raise StopAsyncIteration

            return WaitingIter(queue, cancel_event)

        else:

            async def gen():
                resolved_queue = await resolve_awaitable_or_obj(queue)
                while True:
                    try:
                        item = await resolved_queue.get()
                        if item == EndOfStreamMarker:
                            break
                    except asyncio.CancelledError:
                        # logger.debug("Queue iterator cancelled.")
                        raise
                    # logger.debug(f"Got {str(item)[:50]} from queue")
                    yield item
                # logger.debug("Queue exhausted.")

            return gen()
    else:
        return QueueAsyncIterator()
