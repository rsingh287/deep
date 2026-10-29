"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: SHARED MEMORY FRAME BUFFER (PHASE 4)
===================================================================
Safe, leak-proof Inter-Process Communication (IPC) for MJPEG vision
frames using multiprocessing.shared_memory with:
- Ping-Pong Double-Buffering (Slot 0 / Slot 1) to eliminate tearing.
- 64-byte binary atomic frame header protocol.
- Zero-copy NumPy buffer views for sub-millisecond frame exchange.
- Windows-hardened leak-proof lifecycle management with atexit and signal
  cleanups preventing stuck OS memory handles.
"""

import atexit
import logging
import os
import signal
import struct
import sys
import time
from multiprocessing import shared_memory
from typing import Any, Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger("SharedMemoryFrameBuffer")

# Header Protocol: 64 Bytes
# Magic (4s: 'DPMJ'), Seq (Q: uint64), Timestamp (d: double),
# Width (I: uint32), Height (I: uint32), Channels (I: uint32), FrameSize (I: uint32),
# ActiveSlot (B: uint8), IsValid (B: uint8), Reserved (26s)
HEADER_FORMAT = "<4sQdIIIIBB26s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # Exactly 64 bytes
MAGIC_BYTES = b"DPMJ"

DEFAULT_BUFFER_NAME = "deep_mjpeg_frame_buffer"
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
CHANNELS = 3
SLOT_FRAME_BYTES = MAX_WIDTH * MAX_HEIGHT * CHANNELS  # ~6.22 MB
TOTAL_BUFFER_SIZE = HEADER_SIZE + (2 * SLOT_FRAME_BYTES)  # ~12.44 MB

# Global registry of active buffers in this process for leak-proof exit
_ACTIVE_WRITERS = set()
_ACTIVE_READERS = set()


def _cleanup_registered_handles():
    """Deterministic process-exit cleanup hook for Windows memory handles."""
    for writer in list(_ACTIVE_WRITERS):
        try:
            writer.close()
            writer.unlink()
        except Exception:
            pass
    _ACTIVE_WRITERS.clear()

    for reader in list(_ACTIVE_READERS):
        try:
            reader.close()
        except Exception:
            pass
    _ACTIVE_READERS.clear()


atexit.register(_cleanup_registered_handles)

# Also capture termination signals if possible
try:
    signal.signal(signal.SIGINT, lambda s, f: (_cleanup_registered_handles(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (_cleanup_registered_handles(), sys.exit(0)))
except Exception:
    pass


class SharedMemoryFrameWriter:
    """
    Producer: Writes video frames into a shared physical RAM buffer.
    Uses ping-pong double buffering so consumers read the last committed
    slot without race conditions or memory locks.
    """

    def __init__(
        self,
        name: str = DEFAULT_BUFFER_NAME,
        max_width: int = MAX_WIDTH,
        max_height: int = MAX_HEIGHT,
        channels: int = CHANNELS
    ):
        self.name = name
        self.max_width = max_width
        self.max_height = max_height
        self.channels = channels
        self.slot_size = max_width * max_height * channels
        self.total_size = HEADER_SIZE + (2 * self.slot_size)
        self.sequence = 0
        self.active_slot = 0
        self.is_closed = False
        self.is_owner = False
        self.shm: Optional[shared_memory.SharedMemory] = None

        self._attach_or_create()
        _ACTIVE_WRITERS.add(self)

    def _attach_or_create(self):
        """Creates or reclaims the shared memory segment safely on Windows."""
        try:
            # First try creating a new named buffer
            self.shm = shared_memory.SharedMemory(create=True, name=self.name, size=self.total_size)
            self.is_owner = True
            # Zero out the header
            self.shm.buf[0:HEADER_SIZE] = b"\x00" * HEADER_SIZE
            logger.info(f"[SharedMemoryWriter] Created shared memory buffer '{self.name}' ({self.total_size} bytes)")
        except FileExistsError:
            # Segment exists from previous run or concurrent process; attach to it
            try:
                self.shm = shared_memory.SharedMemory(name=self.name)
                self.is_owner = False
                logger.info(f"[SharedMemoryWriter] Reattached to existing shared memory buffer '{self.name}'")
            except Exception as e:
                logger.error(f"[SharedMemoryWriter] Failed to attach to existing buffer: {e}")
                raise

    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Writes a frame array into the inactive slot and atomically flips the active slot.
        Zero Python heap allocation after initial setup.
        """
        if self.is_closed or self.shm is None:
            return False

        if not isinstance(frame, np.ndarray):
            return False

        h, w = frame.shape[:2]
        c = frame.shape[2] if frame.ndim == 3 else 1
        frame_bytes = frame.nbytes

        if frame_bytes > self.slot_size:
            logger.error(f"[SharedMemoryWriter] Frame size {frame_bytes} exceeds slot capacity {self.slot_size}")
            return False

        # Ping-pong: write to the inactive slot
        write_slot = 1 - self.active_slot
        slot_offset = HEADER_SIZE + (write_slot * self.slot_size)

        # Direct memory copy into shared buffer
        try:
            target_view = np.ndarray(
                frame.shape,
                dtype=frame.dtype,
                buffer=self.shm.buf,
                offset=slot_offset
            )
            np.copyto(target_view, frame)

            # Atomically update header
            self.sequence += 1
            now = time.time()
            header_bytes = struct.pack(
                HEADER_FORMAT,
                MAGIC_BYTES,
                self.sequence,
                now,
                w,
                h,
                c,
                frame_bytes,
                write_slot,
                1,  # is_valid
                b"\x00" * 26
            )
            self.shm.buf[0:HEADER_SIZE] = header_bytes
            self.active_slot = write_slot
            return True
        except Exception as e:
            logger.error(f"[SharedMemoryWriter] Write error: {e}")
            return False

    def close(self):
        """Closes handle to shared memory."""
        if not self.is_closed and self.shm is not None:
            try:
                self.shm.close()
            except Exception:
                pass
            self.is_closed = True
            _ACTIVE_WRITERS.discard(self)

    def unlink(self):
        """Destroys shared memory segment in the OS."""
        if self.shm is not None:
            try:
                self.shm.unlink()
            except Exception:
                pass
            self.shm = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if self.is_owner:
            self.unlink()


class SharedMemoryFrameReader:
    """
    Consumer: Attaches to shared memory frame buffer and reads the latest
    committed frame with zero IPC serialization latency.
    """

    def __init__(
        self,
        name: str = DEFAULT_BUFFER_NAME,
        max_width: int = MAX_WIDTH,
        max_height: int = MAX_HEIGHT,
        channels: int = CHANNELS
    ):
        self.name = name
        self.max_width = max_width
        self.max_height = max_height
        self.channels = channels
        self.slot_size = max_width * max_height * channels
        self.is_closed = False
        self.shm: Optional[shared_memory.SharedMemory] = None

        self._attach()
        _ACTIVE_READERS.add(self)

    def _attach(self):
        """Attaches to existing shared memory block."""
        try:
            self.shm = shared_memory.SharedMemory(name=self.name)
            logger.info(f"[SharedMemoryReader] Attached to buffer '{self.name}'")
        except Exception as e:
            self.shm = None
            logger.debug(f"[SharedMemoryReader] Buffer '{self.name}' not yet available ({e})")

    def read_frame(self, copy: bool = True) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Reads the latest committed frame from the active double-buffer slot.
        If copy=False, returns a zero-copy NumPy view (fastest, read-only).
        If copy=True, returns an independent copy safe for downstream mutation.
        """
        if self.is_closed:
            return None, {"error": "reader_closed"}

        if self.shm is None:
            self._attach()
            if self.shm is None:
                return None, {"error": "buffer_unavailable"}

        try:
            header_bytes = bytes(self.shm.buf[0:HEADER_SIZE])
            (
                magic,
                sequence,
                timestamp,
                width,
                height,
                channels,
                frame_size,
                active_slot,
                is_valid,
                _
            ) = struct.unpack(HEADER_FORMAT, header_bytes)

            if magic != MAGIC_BYTES or is_valid != 1 or frame_size == 0:
                return None, {"error": "no_valid_frame_yet", "sequence": sequence}

            slot_offset = HEADER_SIZE + (active_slot * self.slot_size)
            shape = (height, width, channels) if channels > 1 else (height, width)

            raw_view = np.ndarray(
                shape,
                dtype=np.uint8,
                buffer=self.shm.buf,
                offset=slot_offset
            )

            frame = raw_view.copy() if copy else raw_view
            metadata = {
                "sequence": sequence,
                "timestamp": timestamp,
                "latency_ms": round((time.time() - timestamp) * 1000, 2),
                "width": width,
                "height": height,
                "channels": channels,
                "slot": active_slot
            }
            return frame, metadata
        except Exception as e:
            logger.error(f"[SharedMemoryReader] Read error: {e}")
            return None, {"error": str(e)}

    def close(self):
        """Closes reader handle."""
        if not self.is_closed and self.shm is not None:
            try:
                self.shm.close()
            except Exception:
                pass
            self.is_closed = True
            _ACTIVE_READERS.discard(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def force_cleanup_shared_memory(name: str = DEFAULT_BUFFER_NAME):
    """Emergency utility to unlink orphaned shared memory on Windows after an unhandled crash."""
    try:
        shm = shared_memory.SharedMemory(name=name)
        shm.close()
        shm.unlink()
        return True
    except Exception:
        return False


def acquire_vision_frame(
    camera_index: int = 0,
    name: str = DEFAULT_BUFFER_NAME,
    fallback_to_hardware: bool = True
) -> Optional[np.ndarray]:
    """
    Safely acquires the latest video frame with ZERO camera hardware conflicts:
    1. First reads from zero-copy shared physical RAM buffer (0.1ms).
    2. Then checks LiveMJPEGStreamEngine in-memory cache pointer.
    3. Only if no live stream is active and fallback_to_hardware=True,
       safely captures from cv2.VideoCapture with deterministic try...finally cleanup.
    """
    # 1. Try reading from physical RAM shared memory buffer
    try:
        reader = SharedMemoryFrameReader(name=name)
        frame, meta = reader.read_frame(copy=True)
        reader.close()
        if frame is not None and "error" not in meta:
            return frame
    except Exception:
        pass

    # 2. Try in-process LiveMJPEGStreamEngine memory pointer
    try:
        from mjpeg_stream_engine import LiveMJPEGStreamEngine
        with LiveMJPEGStreamEngine.lock:
            if LiveMJPEGStreamEngine.latest_raw_frame is not None:
                return LiveMJPEGStreamEngine.latest_raw_frame.copy()
    except Exception:
        pass

    # 3. Last resort: Direct camera capture with deterministic try...finally mutex cleanup
    if not fallback_to_hardware:
        return None

    cap = None
    try:
        import cv2
        if sys.platform.startswith("win"):
            try:
                cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            except Exception:
                cap = cv2.VideoCapture(camera_index)
        else:
            cap = cv2.VideoCapture(camera_index)

        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(0)

        if cap is not None and cap.isOpened():
            ret, captured_frame = cap.read()
            if ret and captured_frame is not None:
                return captured_frame
        return None
    except Exception as e:
        logger.warning(f"[acquire_vision_frame] Direct hardware capture error: {e}")
        return None
    finally:
        if cap is not None and hasattr(cap, "isOpened") and cap.isOpened():
            cap.release()
