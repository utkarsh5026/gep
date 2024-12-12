# test_watcher.py

from src.watcher import start_watching, FileWatcher, EventType, FileEvent
import queue
import time
import pytest

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)


# Now we can import from src

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    print(f"Created temporary directory at: {tmp_path}")
    return str(tmp_path)


@pytest.fixture
def watcher(temp_dir: str):
    """Create a FileWatcher instance for testing."""
    w = FileWatcher(temp_dir)
    yield w
    w.close()


def test_file_creation(watcher: FileWatcher, temp_dir: str):
    """Test that file creation events are detected."""
    test_file = Path(temp_dir) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test content")

    time.sleep(0.2)

    event = watcher.event_queue.get(timeout=1)

    assert event.type == EventType.FILE_MODIFIED
    assert event.path == str(test_file)
    assert not event.is_dir


def test_file_modification(watcher, temp_dir):
    """Test that file modification events are detected."""
    # Create and modify a test file
    test_file = Path(temp_dir) / "test.txt"

    with open(test_file, "w") as f:
        f.write("initial content")

    time.sleep(0.2)
    watcher.event_queue.get(timeout=1)
    with open(test_file, "w") as f:
        f.write("modified content")

    time.sleep(0.2)
    event = watcher.event_queue.get(timeout=1)

    assert event.type == EventType.FILE_MODIFIED
    assert event.path == str(test_file)


def test_file_deletion(watcher, temp_dir):
    """Test that file deletion events are detected."""
    test_file = Path(temp_dir) / "test.txt"

    with open(test_file, "w") as f:
        f.write("test content")

    time.sleep(0.2)
    watcher.event_queue.get(timeout=1)
    os.remove(test_file)

    time.sleep(0.2)
    event = watcher.event_queue.get(timeout=1)

    assert event.type == EventType.FILE_DELETED
    assert event.path == str(test_file)


def test_ignore_paths(temp_dir):
    """Test that ignored paths are not watched."""
    ignore_dir = Path(temp_dir) / "ignore"
    ignore_dir.mkdir()

    watcher = FileWatcher(temp_dir, ignore_paths=[str(ignore_dir)])

    test_file = ignore_dir / "test.txt"
    with open(test_file, "w") as f:
        f.write("test content")

    time.sleep(0.2)

    with pytest.raises(queue.Empty):
        watcher.event_queue.get(timeout=0.1)

    watcher.close()


def test_event_coalescing(watcher, temp_dir):
    """Test that rapid successive events are coalesced."""
    test_file = Path(temp_dir) / "test.txt"

    for i in range(5):
        with open(test_file, "w") as f:
            f.write(f"content {i}")
        time.sleep(0.01)

    time.sleep(0.2)

    events = []
    try:
        while True:
            events.append(watcher.event_queue.get(timeout=0.1))
    except queue.Empty:
        pass
