"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: SHARED RING BUFFER ADAPTER
===================================================================
Zero-copy physical RAM buffer adapter backed by shared_memory_frame_buffer
with ping-pong double-buffering and leak-proof lifecycle management.
"""

from shared_memory_frame_buffer import (
    SharedMemoryFrameWriter,
    SharedMemoryFrameReader,
    force_cleanup_shared_memory,
    DEFAULT_BUFFER_NAME,
    TOTAL_BUFFER_SIZE
)

_GLOBAL_WRITERS = {}


def init_shared_buffer(name=DEFAULT_BUFFER_NAME, size=TOTAL_BUFFER_SIZE):
    """Initializes or attaches to the high-performance shared frame buffer."""
    try:
        writer = SharedMemoryFrameWriter(name=name)
        _GLOBAL_WRITERS[name] = writer
        return {
            "status": "success",
            "name": name,
            "size": writer.total_size,
            "message": "Initialized leak-proof double-buffered shared RAM frame buffer."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def cleanup_shared_buffer(name=DEFAULT_BUFFER_NAME):
    """Safely closes and unlinks the shared frame buffer."""
    try:
        writer = _GLOBAL_WRITERS.pop(name, None)
        if writer:
            writer.close()
            writer.unlink()
        else:
            force_cleanup_shared_memory(name)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
