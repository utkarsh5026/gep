import logging
import asyncio
import pathlib
import time
from enum import Enum, auto
from typing import Optional, AsyncGenerator, Callable
from dataclasses import dataclass

from watchdog import observers, events

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


DEFAULT_EVENT_BUFFER_SIZE = 1000


class EventType(Enum):
    """
    Event types for the watcher.
    """
    FILE_CREATED = auto()
    FILE_MODIFIED = auto()
    FILE_DELETED = auto()
    FILE_MOVED = auto()

    def __str__(self):
        return self.name.replace('_', ' ').lower().title()


@dataclass
class FileEvent:
    """
    Represents a file system event with detailed metadata.

    Attributes:
        event_type: Type of the file system event
        path: Path to the affected file
        mod_time: Timestamp of the event
        is_dir: Whether the event concerns a directory
        size: Size of the file (if applicable)
        old_path: Previous path (for move events)
    """
    event_type: EventType
    path: str
    mod_time: float
    is_dir: bool
    size: Optional[int] = None
    old_path: Optional[str] = None


class AsyncEventHandler(events.FileSystemEventHandler):
    """
    An asynchronous event handler for file system events.
    """

    def __init__(self, callback: Callable[[events.FileSystemEvent], None], loop: asyncio.AbstractEventLoop):
        self.callback = callback
        self.loop = loop
        super().__init__()

    def on_any_event(self, event: events.FileSystemEvent) -> None:
        """
        Handle any file system event.
        Note: This runs in a different thread, so we need to use call_soon_threadsafe
        """
        self.loop.call_soon_threadsafe(self._create_task, event)

    def _create_task(self, event: events.FileSystemEvent) -> None:
        """Create a task in the main event loop"""
        task = self.loop.create_task(self.callback(event))
        if hasattr(self.callback, '__self__'):
            watcher = self.callback.__self__
            if isinstance(watcher, AsyncFileWatcher):
                watcher.pending_tasks.add(task)
                task.add_done_callback(watcher.pending_tasks.discard)


class EventBuffer:
    """
    Manages event buffering and deduplication.

    This class helps prevent event flooding by coalescing similar events
    that occur within a short time window.
    """

    def __init__(self, coalesce_window: float = 0.1) -> None:
        self.events: dict[str, FileEvent] = {}
        self.coalesce_window = coalesce_window
        self._lock = asyncio.Lock()
        self.last_flush_time = time.time()

    async def add_event(self, event: FileEvent) -> None:
        """
        Add an event to the buffer, potentially coalescing with existing events.

        Parameters:
            event (FileEvent): The event to add to the buffer.
        """
        async with self._lock:
            key = event.path
            curr_time = time.time()

            if key in self.events:
                existing_event = self.events[key]
                if curr_time - existing_event.mod_time < self.coalesce_window:
                    return

            self.events[key] = event

    async def get_pending_events(self) -> list[FileEvent]:
        """
        Retrieve and clear pending events if the coalesce window has elapsed.
        """
        async with self._lock:
            curr_time = time.time()
            if curr_time - self.last_flush_time < self.coalesce_window:
                return []

            events = list(self.events.values())
            self.events.clear()
            self.last_flush_time = curr_time
            return events


class AsyncFileWatcher:
    """
    Asynchronous event handler for file system events.

    This handler converts watchdog's synchronous events into async events
    that can be processed without blocking.
    """

    def __init__(self, root_path: str, ignored_patterns: Optional[list[str]] = None, coalesce_window: float = 0.1) -> None:
        self.root_path = pathlib.Path(root_path).resolve()
        self.ignored_patterns = set(ignored_patterns or [])

        self.event_queue = asyncio.Queue(maxsize=DEFAULT_EVENT_BUFFER_SIZE)
        self.event_buffer = EventBuffer(coalesce_window)
        self.observer = observers.Observer()
        self.is_running = False
        self.pending_tasks: set[asyncio.Task] = set()

    def __should_ignore(self, file_path: str) -> bool:
        """
        Check if the path should be ignored.

        Parameters:
            file_path (str): The path to the file.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        path = pathlib.Path(file_path).resolve()
        for pattern in self.ignored_patterns:
            if '*' in pattern or '?' in pattern:
                if path.match(pattern):
                    return True
            else:
                if str(path).endswith(pattern):
                    return True
        return False

    async def __handle_event(self, event: events.FileSystemEvent) -> None:
        """
        Handle a file system event. and add it to the event buffer.
        """
        logger.debug(f"Received raw event: {event}")
        try:
            if self.__should_ignore(event.src_path):
                print(f"Ignored {event.src_path}")
                return

            event_type = self.__get_event_type(event)
            logger.debug(f"Mapped event type: {event_type}")
            size = None
            if event_type != EventType.FILE_DELETED and not event.is_directory:
                try:
                    size = pathlib.Path(event.src_path).stat().st_size
                except (OSError):
                    pass
            if event_type is not None:
                file_event = FileEvent(
                    event_type=event_type,
                    path=event.src_path,
                    mod_time=time.time(),
                    is_dir=event.is_directory,
                    size=size,
                    old_path=str(event.dest_path) if event.dest_path else None
                )
                await self.event_buffer.add_event(file_event)

        except Exception as e:
            logger.error(f"Error handling event: {e}")
            logger.debug(f"Event details: {event.__dict__}")

    async def watch(self) -> None:
        """
        Watch for file changes and add them to the event buffer.
        """

        if self.is_running:
            raise RuntimeError("File watcher is already running")

        logger.info(f"Watching {pathlib.Path(
            self.root_path).resolve()} for changes...")
        self.is_running = True

        try:

            event_handler = AsyncEventHandler(
                self.__handle_event, asyncio.get_running_loop())
            self.observer.schedule(
                event_handler=event_handler,
                path=str(self.root_path),
                recursive=True
            )

            self.observer.start()
            asyncio.create_task(self.__process_buffer())

            logger.info("Watcher running successfully")

        except Exception as e:
            self.is_running = False
            logger.error(f"Error starting file watcher: {e}")
            raise

    async def get_event(self) -> AsyncGenerator[FileEvent, None]:
        """
        Get events from the event buffer.
        """
        while self.is_running:

            try:
                event = await self.event_queue.get()
                yield event
                self.event_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def stop(self) -> None:
        """Stop the file watcher and clean up resources."""

        if not self.is_running:
            return

        logger.info("Stopping file watcher...")
        self.is_running = False

        try:
            # First stop getting new events
            self.observer.stop()
            self.observer.join()

            for task in self.pending_tasks:
                task.cancel()

            if self.pending_tasks:
                await asyncio.gather(*self.pending_tasks, return_exceptions=True)
            await self.event_queue.join()

            logger.info("File watcher stopped.")
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")
            raise
        finally:
            self.pending_tasks.clear()

    async def __process_buffer(self) -> None:
        """
        Continuously process the event buffer and send events to the queue.
        """
        while self.is_running:

            try:
                events = await self.event_buffer.get_pending_events()
                for event in events:
                    try:
                        await self.event_queue.put(event)
                    except asyncio.QueueFull:
                        logger.warning("Event queue is full, skipping event.")

            except Exception as e:
                logger.error(f"Error processing events: {e}")

            await asyncio.sleep(0.01)  # Sleep to avoid busy-waiting

    def __get_event_type(self, event: events.FileSystemEvent) -> EventType | None:
        """Get the event type from the event."""
        event_type_map = {
            events.FileCreatedEvent: EventType.FILE_CREATED,
            events.FileModifiedEvent: EventType.FILE_MODIFIED,
            events.FileDeletedEvent: EventType.FILE_DELETED,
            events.FileMovedEvent: EventType.FILE_MOVED
        }
        return event_type_map.get(type(event))


async def start_watching(wather: AsyncFileWatcher, on_event: Callable[[FileEvent], None]) -> None:
    """Start watching for file changes and call the callback on each event."""
    try:
        await wather.watch()
        async for event in wather.get_event():
            on_event(event)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Error starting file watcher: {e}")
    finally:
        await wather.stop()


def pretty_describe_event(event: FileEvent) -> str:
    return f"{event.event_type} {event.path} {event.mod_time}"
