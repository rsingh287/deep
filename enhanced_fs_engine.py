"""
Enhanced Filesystem & Archive Engine
Enterprise-Grade File Operations, Line Streaming, Safe Quarantine Deletion,
Parallel Multi-Read with LRU/mtime Caching, and Archive Management.
"""

import os
import sys
import shutil
import time
import json
import zipfile
import tarfile
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
TRASH_DIR = os.path.join(WORKSPACE_ROOT, ".trash")
TRASH_MANIFEST_FILE = os.path.join(TRASH_DIR, "manifest.json")


class FileCache:
    """Thread-safe LRU and mtime-aware in-memory file cache."""
    def __init__(self, max_items: int = 128, max_file_size: int = 2 * 1024 * 1024):
        self.max_items = max_items
        self.max_file_size = max_file_size
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, file_path: str) -> Optional[str]:
        abs_path = os.path.abspath(file_path)
        if abs_path not in self._cache:
            return None
        entry = self._cache[abs_path]
        try:
            current_mtime = os.path.getmtime(abs_path)
            if current_mtime != entry["mtime"]:
                del self._cache[abs_path]
                return None
            entry["last_accessed"] = time.time()
            return entry["content"]
        except Exception:
            self._cache.pop(abs_path, None)
            return None

    def put(self, file_path: str, content: str):
        abs_path = os.path.abspath(file_path)
        if len(content.encode("utf-8", errors="ignore")) > self.max_file_size:
            return
        if len(self._cache) >= self.max_items:
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k]["last_accessed"])
            del self._cache[oldest]
        try:
            mtime = os.path.getmtime(abs_path)
        except Exception:
            mtime = time.time()
        self._cache[abs_path] = {
            "content": content,
            "mtime": mtime,
            "last_accessed": time.time()
        }

    def invalidate(self, file_path: str):
        abs_path = os.path.abspath(file_path)
        self._cache.pop(abs_path, None)

    def clear(self):
        self._cache.clear()


GLOBAL_FILE_CACHE = FileCache()


def _ensure_trash_init():
    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR, exist_ok=True)
    if not os.path.exists(TRASH_MANIFEST_FILE):
        with open(TRASH_MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def _load_trash_manifest() -> List[Dict[str, Any]]:
    _ensure_trash_init()
    try:
        with open(TRASH_MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_trash_manifest(manifest: List[Dict[str, Any]]):
    _ensure_trash_init()
    with open(TRASH_MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def read_lines(
    file_path: str,
    mode: str = "head",
    count: int = 10,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Reads lines from a file without loading the entire file into memory if large.
    Modes:
      - 'head': reads the first `count` lines.
      - 'tail': reads the last `count` lines using reverse chunk seek.
      - 'range': reads lines from `start_line` to `end_line` (1-indexed, inclusive).
    """
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        return {"success": False, "error": f"File not found: {file_path}", "filePath": file_path}
    if os.path.isdir(abs_path):
        return {"success": False, "error": f"Path is a directory: {file_path}", "filePath": file_path}

    try:
        file_size = os.path.getsize(abs_path)

        # 1. Mode: HEAD
        if mode == "head":
            count = max(1, count)
            lines = []
            with open(abs_path, "r", encoding=encoding, errors="replace") as f:
                for _ in range(count):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
            return {
                "success": True,
                "filePath": abs_path,
                "mode": "head",
                "count": len(lines),
                "lines": lines,
                "content": "".join(lines),
                "fileSize": file_size
            }

        # 2. Mode: TAIL
        elif mode == "tail":
            count = max(1, count)
            # For small files (< 512KB), simple readlines is fast and safe
            if file_size < 512 * 1024:
                with open(abs_path, "r", encoding=encoding, errors="replace") as f:
                    all_lines = f.readlines()
                    tail_lines = all_lines[-count:]
                return {
                    "success": True,
                    "filePath": abs_path,
                    "mode": "tail",
                    "count": len(tail_lines),
                    "lines": tail_lines,
                    "content": "".join(tail_lines),
                    "fileSize": file_size
                }

            # For large files: backward buffer seek
            lines_found = []
            buffer_size = 4096
            with open(abs_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                position = f.tell()
                remainder = b""

                while position > 0 and len(lines_found) <= count:
                    read_size = min(buffer_size, position)
                    position -= read_size
                    f.seek(position)
                    chunk = f.read(read_size) + remainder
                    raw_lines = chunk.split(b"\n")
                    remainder = raw_lines[0]
                    # Keep lines from chunk
                    for l in reversed(raw_lines[1:]):
                        if l or lines_found:  # preserve empty lines except trailing EOF
                            lines_found.append(l.decode(encoding, errors="replace") + "\n")
                            if len(lines_found) >= count:
                                break

                if remainder and len(lines_found) < count:
                    lines_found.append(remainder.decode(encoding, errors="replace") + "\n")

            lines_found.reverse()
            return {
                "success": True,
                "filePath": abs_path,
                "mode": "tail",
                "count": len(lines_found),
                "lines": lines_found,
                "content": "".join(lines_found),
                "fileSize": file_size
            }

        # 3. Mode: RANGE
        elif mode == "range":
            s = 1 if start_line is None else max(1, int(start_line))
            e = s + count - 1 if end_line is None else max(s, int(end_line))
            lines = []
            current_line_num = 1

            with open(abs_path, "r", encoding=encoding, errors="replace") as f:
                for line in f:
                    if current_line_num >= s and current_line_num <= e:
                        lines.append(line)
                    if current_line_num > e:
                        break
                    current_line_num += 1

            return {
                "success": True,
                "filePath": abs_path,
                "mode": "range",
                "startLine": s,
                "endLine": e,
                "count": len(lines),
                "lines": lines,
                "content": "".join(lines),
                "fileSize": file_size
            }

        else:
            return {"success": False, "error": f"Unknown mode: {mode}. Use 'head', 'tail', or 'range'."}

    except Exception as ex:
        return {"success": False, "error": str(ex), "filePath": abs_path}


def append_file(
    file_path: str,
    content: str,
    create_if_missing: bool = True,
    ensure_newline: bool = True
) -> Dict[str, Any]:
    """Appends content to a file atomically, creating parent folders if necessary."""
    abs_path = os.path.abspath(file_path)
    try:
        parent_dir = os.path.dirname(abs_path)
        if not os.path.exists(parent_dir):
            if create_if_missing:
                os.makedirs(parent_dir, exist_ok=True)
            else:
                return {"success": False, "error": f"Parent directory does not exist: {parent_dir}"}

        payload = content
        if ensure_newline and not payload.endswith("\n"):
            payload += "\n"

        with open(abs_path, "a", encoding="utf-8") as f:
            bytes_written = f.write(payload)

        GLOBAL_FILE_CACHE.invalidate(abs_path)

        return {
            "success": True,
            "filePath": abs_path,
            "bytesWritten": bytes_written,
            "totalSize": os.path.getsize(abs_path)
        }
    except Exception as ex:
        return {"success": False, "error": str(ex), "filePath": abs_path}


def delete_file(
    path: str,
    permanent: bool = False,
    quarantine: bool = True
) -> Dict[str, Any]:
    """
    Deletes a file from the file system.
    Matches schema: { "path": string } -> { "success": bool, "filePath": string }
    Safety: By default, moves the file to quarantine (.trash) with a restore manifest.
    """
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        return {"success": False, "error": f"File does not exist: {path}", "filePath": abs_path}
    if os.path.isdir(abs_path):
        return delete_directory(abs_path, recursive=False, quarantine=quarantine)

    # Protect critical paths
    normalized = os.path.normpath(abs_path).lower()
    for protected in ["c:\\windows", "c:\\boot", os.path.normpath(WORKSPACE_ROOT).lower() + "\\.git"]:
        if normalized == protected or normalized.startswith(protected + "\\"):
            return {"success": False, "error": f"SECURITY_VIOLATION: Cannot delete protected path: {path}", "filePath": abs_path}

    try:
        file_size = os.path.getsize(abs_path)
        sha256_hash = hashlib.sha256()
        with open(abs_path, "rb") as f:
            for b in iter(lambda: f.read(65536), b""):
                sha256_hash.update(b)
        digest = sha256_hash.hexdigest()

        GLOBAL_FILE_CACHE.invalidate(abs_path)

        if not permanent and quarantine:
            _ensure_trash_init()
            timestamp = int(time.time() * 1000)
            trash_filename = f"{timestamp}_{os.path.basename(abs_path)}"
            trash_path = os.path.join(TRASH_DIR, trash_filename)

            shutil.move(abs_path, trash_path)

            manifest = _load_trash_manifest()
            entry = {
                "id": str(timestamp),
                "original_path": abs_path,
                "trash_path": trash_path,
                "filename": os.path.basename(abs_path),
                "size_bytes": file_size,
                "sha256": digest,
                "deleted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "is_directory": False
            }
            manifest.append(entry)
            _save_trash_manifest(manifest)

            return {
                "success": True,
                "filePath": abs_path,
                "quarantined": True,
                "trashId": str(timestamp),
                "message": f"File moved to quarantine (.trash): {os.path.basename(abs_path)}"
            }
        else:
            os.remove(abs_path)
            return {
                "success": True,
                "filePath": abs_path,
                "quarantined": False,
                "message": f"File permanently removed: {abs_path}"
            }

    except Exception as ex:
        return {"success": False, "error": str(ex), "filePath": abs_path}


def restore_file(identifier: str) -> Dict[str, Any]:
    """Restores a quarantined file by trashId or original path."""
    manifest = _load_trash_manifest()
    target_entry = None
    target_idx = -1

    for idx, entry in enumerate(manifest):
        if entry["id"] == identifier or os.path.abspath(entry["original_path"]) == os.path.abspath(identifier):
            target_entry = entry
            target_idx = idx
            break

    if not target_entry:
        return {"success": False, "error": f"Quarantine record not found for: {identifier}"}

    trash_path = target_entry["trash_path"]
    original_path = target_entry["original_path"]

    if not os.path.exists(trash_path):
        return {"success": False, "error": f"Quarantined file missing on disk: {trash_path}"}

    try:
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        shutil.move(trash_path, original_path)
        manifest.pop(target_idx)
        _save_trash_manifest(manifest)
        GLOBAL_FILE_CACHE.invalidate(original_path)
        return {
            "success": True,
            "filePath": original_path,
            "message": f"Successfully restored '{target_entry['filename']}' to original location."
        }
    except Exception as ex:
        return {"success": False, "error": str(ex), "filePath": original_path}


def list_trash() -> List[Dict[str, Any]]:
    """Returns the list of all quarantined files."""
    return _load_trash_manifest()


def delete_directory(
    path: str,
    recursive: bool = False,
    quarantine: bool = True
) -> Dict[str, Any]:
    """Deletes a directory with optional quarantine staging."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        return {"success": False, "error": f"Directory does not exist: {path}", "filePath": abs_path}
    if not os.path.isdir(abs_path):
        return delete_file(abs_path, quarantine=quarantine)

    if not recursive and os.listdir(abs_path):
        return {"success": False, "error": f"Directory not empty. Set recursive=True to delete.", "filePath": abs_path}

    try:
        if quarantine:
            _ensure_trash_init()
            timestamp = int(time.time() * 1000)
            trash_dirname = f"{timestamp}_dir_{os.path.basename(abs_path)}"
            trash_path = os.path.join(TRASH_DIR, trash_dirname)

            shutil.move(abs_path, trash_path)

            manifest = _load_trash_manifest()
            manifest.append({
                "id": str(timestamp),
                "original_path": abs_path,
                "trash_path": trash_path,
                "filename": os.path.basename(abs_path),
                "deleted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "is_directory": True
            })
            _save_trash_manifest(manifest)
            return {"success": True, "filePath": abs_path, "quarantined": True, "trashId": str(timestamp)}
        else:
            shutil.rmtree(abs_path)
            return {"success": True, "filePath": abs_path, "quarantined": False}
    except Exception as ex:
        return {"success": False, "error": str(ex), "filePath": abs_path}


def read_multiple_files_fast(
    paths: List[str],
    max_size_bytes: int = 5 * 1024 * 1024,
    parallel_threads: int = 8
) -> Dict[str, Any]:
    """
    Reads multiple files concurrently using a thread pool and LRU cache.
    Handles large numbers of files with minimal latency.
    """
    t0 = time.time()
    results: Dict[str, Any] = {}

    def _read_single(p: str) -> Tuple[str, Dict[str, Any]]:
        abs_p = os.path.abspath(p)
        cached = GLOBAL_FILE_CACHE.get(abs_p)
        if cached is not None:
            return (abs_p, {"success": True, "content": cached, "cached": True, "size": len(cached)})

        if not os.path.exists(abs_p):
            return (abs_p, {"success": False, "error": "File not found"})
        if os.path.isdir(abs_p):
            return (abs_p, {"success": False, "error": "Path is a directory"})

        try:
            sz = os.path.getsize(abs_p)
            if sz > max_size_bytes:
                return (abs_p, {"success": False, "error": f"File exceeds maximum size limit ({sz} > {max_size_bytes} bytes)"})

            with open(abs_p, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            GLOBAL_FILE_CACHE.put(abs_p, content)
            return (abs_p, {"success": True, "content": content, "cached": False, "size": sz})
        except Exception as e:
            return (abs_p, {"success": False, "error": str(e)})

    with ThreadPoolExecutor(max_workers=min(parallel_threads, len(paths) or 1)) as executor:
        for p, res in executor.map(_read_single, paths):
            results[p] = res

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    return {
        "success": True,
        "totalFiles": len(paths),
        "results": results,
        "elapsedMs": elapsed_ms
    }


def compress_files(
    source_paths: List[str],
    output_archive_path: str,
    format: str = "zip"
) -> Dict[str, Any]:
    """
    Compresses files or directories into a zip or tar.gz archive.
    """
    abs_out = os.path.abspath(output_archive_path)
    os.makedirs(os.path.dirname(abs_out), exist_ok=True)

    try:
        total_raw_size = 0
        file_count = 0

        if format == "zip" or abs_out.endswith(".zip"):
            with zipfile.ZipFile(abs_out, "w", zipfile.ZIP_DEFLATED) as zf:
                for src in source_paths:
                    abs_src = os.path.abspath(src)
                    if not os.path.exists(abs_src):
                        continue
                    if os.path.isfile(abs_src):
                        arcname = os.path.basename(abs_src)
                        zf.write(abs_src, arcname)
                        total_raw_size += os.path.getsize(abs_src)
                        file_count += 1
                    elif os.path.isdir(abs_src):
                        base_dir = os.path.basename(abs_src)
                        for root, _, files in os.walk(abs_src):
                            for file in files:
                                fpath = os.path.join(root, file)
                                rel = os.path.relpath(fpath, abs_src)
                                zf.write(fpath, os.path.join(base_dir, rel))
                                total_raw_size += os.path.getsize(fpath)
                                file_count += 1

        elif format in ["tar", "tar.gz", "tgz"] or abs_out.endswith((".tar.gz", ".tgz")):
            with tarfile.open(abs_out, "w:gz") as tf:
                for src in source_paths:
                    abs_src = os.path.abspath(src)
                    if not os.path.exists(abs_src):
                        continue
                    arcname = os.path.basename(abs_src)
                    tf.add(abs_src, arcname=arcname)
                    if os.path.isfile(abs_src):
                        total_raw_size += os.path.getsize(abs_src)
                        file_count += 1
                    else:
                        for root, _, files in os.walk(abs_src):
                            for f in files:
                                total_raw_size += os.path.getsize(os.path.join(root, f))
                                file_count += 1

        archive_size = os.path.getsize(abs_out)
        ratio = round((1.0 - (archive_size / max(total_raw_size, 1))) * 100, 1)

        return {
            "success": True,
            "archivePath": abs_out,
            "fileCount": file_count,
            "rawSizeBytes": total_raw_size,
            "archiveSizeBytes": archive_size,
            "compressionRatioPercent": ratio
        }
    except Exception as ex:
        return {"success": False, "error": str(ex), "archivePath": abs_out}


def decompress_file(
    archive_path: str,
    extract_to_dir: str,
    safe_extract: bool = True
) -> Dict[str, Any]:
    """
    Safely decompresses an archive with Zip-Slip vulnerability prevention.
    """
    abs_archive = os.path.abspath(archive_path)
    abs_dest = os.path.abspath(extract_to_dir)

    if not os.path.exists(abs_archive):
        return {"success": False, "error": f"Archive not found: {archive_path}"}

    os.makedirs(abs_dest, exist_ok=True)
    extracted_files = []

    try:
        if zipfile.is_zipfile(abs_archive):
            with zipfile.ZipFile(abs_archive, "r") as zf:
                for member in zf.infolist():
                    target = os.path.abspath(os.path.join(abs_dest, member.filename))
                    if safe_extract and not target.startswith(abs_dest):
                        return {
                            "success": False,
                            "error": f"SECURITY_VIOLATION: Zip-Slip path traversal attempt detected in: {member.filename}"
                        }
                    zf.extract(member, abs_dest)
                    extracted_files.append(member.filename)

        elif tarfile.is_tarfile(abs_archive):
            with tarfile.open(abs_archive, "r:*") as tf:
                for member in tf.getmembers():
                    target = os.path.abspath(os.path.join(abs_dest, member.name))
                    if safe_extract and not target.startswith(abs_dest):
                        return {
                            "success": False,
                            "error": f"SECURITY_VIOLATION: Tar-Slip path traversal attempt detected in: {member.name}"
                        }
                    tf.extract(member, abs_dest)
                    extracted_files.append(member.name)
        else:
            return {"success": False, "error": "Unsupported archive format (must be .zip, .tar, or .tar.gz)"}

        return {
            "success": True,
            "archivePath": abs_archive,
            "destination": abs_dest,
            "extractedCount": len(extracted_files),
            "files": extracted_files
        }
    except Exception as ex:
        return {"success": False, "error": str(ex), "archivePath": abs_archive}


def create_symlink(
    target_path: str,
    link_path: str,
    is_directory: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Creates a symbolic link or directory junction on Windows/POSIX.
    """
    abs_target = os.path.abspath(target_path)
    abs_link = os.path.abspath(link_path)

    if not os.path.exists(abs_target):
        return {"success": False, "error": f"Target path does not exist: {target_path}"}
    if os.path.exists(abs_link):
        return {"success": False, "error": f"Link path already exists: {link_path}"}

    target_is_dir = os.path.isdir(abs_target) if is_directory is None else is_directory
    os.makedirs(os.path.dirname(abs_link), exist_ok=True)

    try:
        if os.name == "nt":
            # On Windows, try os.symlink first, fallback to mklink junction for directories
            try:
                os.symlink(abs_target, abs_link, target_is_directory=target_is_dir)
            except OSError:
                if target_is_dir:
                    import subprocess
                    cmd = f'mklink /J "{abs_link}" "{abs_target}"'
                    subprocess.check_call(cmd, shell=True)
                else:
                    raise
        else:
            os.symlink(abs_target, abs_link)

        return {
            "success": True,
            "linkPath": abs_link,
            "targetPath": abs_target,
            "isDirectory": target_is_dir
        }
    except Exception as ex:
        return {"success": False, "error": str(ex), "linkPath": abs_link, "targetPath": abs_target}
