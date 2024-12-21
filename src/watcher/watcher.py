import time
from typing import Callable, Optional, Generator
from enum import Enum, auto
import queue
from threading import Timer


from watchdog import events, observers

# Constants that define the watcher's behavior
DEFAULT_EVENT_BUFFER_SIZE = 100
DEFAULT_FLUSH_INTERVAL = 0.1  # 100ms in seconds


class EventType(Enum):
    """
    Event types for the watcher.
    """
    FILE_CREATED = auto()
    FILE_MODIFIED = auto()
    FILE_DELETED = auto()
    FILE_MOVED = auto()

    def __str__(self):
        return self.name.replace('_', ' ').title()


class FileEvent:
    """Represents a file system event with additional metadata."""

    def __init__(self, event_type: EventType, path: str, mod_time: float, is_dir: bool):
        self.type = event_type
        self.path = path
        self.mod_time = mod_time
        self.is_dir = is_dir


class EventHandler(events.FileSystemEventHandler):
    """Handles file system events and forwards them to the FileWatcher."""

    def __init__(self, callback: Callable[[events.FileSystemEvent], None]):
        self.callback = callback
        super().__init__()

    def on_any_event(self, event: events.FileSystemEvent):
        self.callback(event)


class FileWatcher:
    """
    Watches a directory tree for file system changes and reports them through an event queue.
    Implements debouncing to prevent event flooding and coalesces rapid sequences of events.
    """

    event_map = {
        'created': EventType.FILE_CREATED,
        'modified': EventType.FILE_MODIFIED,
        'deleted': EventType.FILE_DELETED,
    }

    def __init__(self, root_path: str, ignore_paths: Optional[list[str]] = None):
        self.root_path = root_path
        self.event_queue = queue.Queue(maxsize=DEFAULT_EVENT_BUFFER_SIZE)
        self.observer = observers.Observer()
        self.ignore_paths: set[str] = set()
        self.pending_events: dict[str, FileEvent] = {}
        self.flush_timer: Optional[Timer] = None

        if ignore_paths:
            self.ignore_paths = set(ignore_paths)

        # Start watching the directory tree
        event_handler = EventHandler(self._handle_event)
        self.observer.schedule(event_handler, root_path, recursive=True)
        self.observer.start()

    def _should_ignore(self, path: str) -> bool:
        """Check if the given path should be ignored."""
        return any(path.startswith(ignore) for ignore in self.ignore_paths)

    def _handle_event(self, event: events.FileSystemEvent):
        """
        Handle a file system event.
        """
        if self._should_ignore(event.src_path):
            return

        if event.event_type not in self.event_map:
            return  # Ignore other event types

        event_type = self.event_map[event.event_type]

        file_event = FileEvent(
            event_type=event_type,
            path=event.src_path,
            mod_time=time.time(),
            is_dir=event.is_directory,
        )

        print(file_event.type)

        self.pending_events[event.src_path] = file_event

        if self.flush_timer:
            self.flush_timer.cancel()

        self.flush_timer = Timer(DEFAULT_FLUSH_INTERVAL, self._flush_events)
        self.flush_timer.start()

    def _flush_events(self):
        """Flush all pending events to the event queue."""
        for event in self.pending_events.values():
            try:
                self.event_queue.put(event)
            except queue.Full:
                break
        self.pending_events.clear()
        self.flush_timer = None

    def events(self) -> Generator[FileEvent, None, None]:
        """Generator that yields file events as they occur."""
        while True:
            try:
                yield self.event_queue.get()
            except Exception as e:
                print(f"Error getting event: {e}")

    def close(self):
        """Stop the watcher and release resources."""
        if self.flush_timer:
            self.flush_timer.cancel()
        self.observer.stop()
        self.observer.join()


def start_watching(root_path: str, on_event: Callable[[FileEvent], None]) -> None:
    """
    Start watching a directory tree and call the provided callback for each file event.

    Args:
        root_path: The root directory to watch
        on_event: Callback function that takes a FileEvent parameter
    """
    watcher = FileWatcher(root_path)
    try:
        for event in watcher.events():
            try:
                on_event(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
                break
    finally:
        watcher.close()
