"""
Tools for working with Open Ephys raw data files.
"""
from __future__ import annotations
import contextlib
import datetime
import os
import pathlib
import shutil
import subprocess
import time
from typing import Optional, Union

import crc32c
import np_config
import np_logging
import rich.progress

logger = np_logging.get_logger(__name__)

PathLike = Union[str, bytes, os.PathLike, pathlib.Path]
def from_pathlike(pathlike):
    return pathlib.Path(os.fsdecode(pathlike))

if os.name == 'nt':
    # Remote to remote symlink creation is disabled by default
    try:
        proc = subprocess.run('fsutil behavior set SymlinkEvaluation R2R:1', check=True)
    except subprocess.CalledProcessError:
        logger.warning('Failed to enable remote-to-remote symlink creation: try running as admin')
        R2R_SYMLINKS_ENABLED = False
    else:
        R2R_SYMLINKS_ENABLED = True
else:
    R2R_SYMLINKS_ENABLED = True
    
def checksum(path: PathLike, show_progress_bar=True) -> str:
    path = from_pathlike(path)
    hasher = crc32c.crc32c
    def formatted(x):
        return f'{x:08X}'
    blocks_per_chunk = 4096
    multi_part_threshold_gb = 0.2
    if path.stat().st_size < multi_part_threshold_gb * 1024**3:
        return formatted(hasher(path.read_bytes()))
    hash = 0
    
    with open(path, 'rb') as f, get_progress():
        progress: rich.progress.Progress = globals()['progress']
        task = progress.add_task(f'Checksumming {path.name}', total=path.stat().st_size, visible=show_progress_bar)
        for chunk in iter(
            lambda: f.read(blocks_per_chunk), b''
        ):  
            progress.update(task, advance=blocks_per_chunk) # type: ignore
            hash = hasher(chunk, hash)
    progress.update(task, visible=False)
    return formatted(hash)

def get_progress() -> rich.progress.Progress | contextlib.nullcontext[None]:
    progress_context = contextlib.nullcontext()
    if 'progress' not in globals():
        progress_context = globals()['progress'] = rich.progress.Progress(
            rich.progress.TextColumn("{task.description}", justify="right"),
            rich.progress.BarColumn(),
            rich.progress.TimeRemainingColumn(),
            rich.progress.FileSizeColumn(),
            rich.progress.TotalFileSizeColumn(),
        )
    return progress_context

def get_copy_task(src) -> rich.progress.TaskID:
    get_progress()
    progress: rich.progress.Progress = globals()['progress']
    if not progress.tasks:
        task = progress.add_task(
            description='[cyan]Getting file sizes',
            start=False,
            )
        progress.update(
            task,
            description='[cyan]Copying files',
            total=size(src)
            )
        progress.start_task(task)
    return progress.tasks[0].id

def checksums_match(*paths: PathLike) -> bool:
    checksums = tuple(checksum(p) for p in paths)
    return all(c == checksums[0] for c in checksums)


def copy(src: PathLike, dest: PathLike, max_attempts: int = 2) -> None:
    """Copy `src` to `dest` with checksum validation.

    - copies recursively if `src` is a directory
    - if dest already exists, checksums are compared, copying is skipped if they match
    - attempts to copy up to 3 times if checksums don't match
    - replaces existing symlinks with actual files
    - creates parent dirs if needed
    """
    src, dest = from_pathlike(src), from_pathlike(dest)

    with get_progress():
        progress: rich.progress.Progress = globals()['progress']
        task = get_copy_task(src)
    
        if dest.exists() and dest.is_symlink():
            dest.unlink() # we'll replace symlink with src file
        
        if src.is_dir(): # copy files recursively
            for path in src.iterdir():
                copy(path, dest / path.name)
            return
        
        if not dest.suffix: # dest is a folder, but might not exist yet so can't use `is_dir`
            dest = dest / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if not dest.exists():
            shutil.copy2(src, dest)
            logger.debug(f'Copied {src} to {dest}')
            
        for _ in range(max_attempts):
            if checksums_match(src, dest):
                break
            shutil.copy2(src, dest)
        else:
            raise OSError(
                f'Failed to copy {src} to {dest} with checksum-validation after {max_attempts} attempts'
            )
        progress.update(task, advance=size(src))
        logger.debug(f'Copy of {src} at {dest} validated with checksum')


def move(src: PathLike, dest: PathLike, **rmtree_kwargs) -> None:
    """Copy `src` to `dest` with checksum validation, then delete `src`.
    """
    src, dest = from_pathlike(src), from_pathlike(dest)
    copy(src, dest)
    if src.is_dir():
        shutil.rmtree(src, **rmtree_kwargs)
    else:
        src.unlink()
    logger.debug(f'Deleted {src}')


def symlink(src: PathLike, dest: PathLike) -> None:
    """Create symlink at `dest` pointing to file at `src`.

    - creates symlinks recursively if `src` is a directory
    - creates parent dirs if needed (as folders, not symlinks)
    - skips if symlink already exists and points to `src`
    - replaces existing file or symlink pointing to a different location
    """
    src, dest = from_pathlike(src), from_pathlike(dest)
    if src.is_dir():
        for path in src.iterdir():
            symlink(src, dest / path.name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() and dest.resolve() == src.resolve():
        logger.debug(f'Symlink already exists to {src} from {dest}')
        return
    with contextlib.suppress(FileNotFoundError):
        dest.unlink()
    with contextlib.suppress(FileExistsError):
        dest.symlink_to(src)
    logger.debug(f'Created symlink to {src} from {dest}')

    
def size(path: PathLike) -> int:
    """Return the size of a file or directory in bytes"""
    path = from_pathlike(path)
    return dir_size(path) if path.is_dir() else path.stat().st_size

def size_gb(path: PathLike) -> float:
    """Return the size of a file or directory in GB"""
    return round(size(path) / 1024 ** 3, 1)

def dir_size(path: PathLike) -> int:
    """Return the size of a directory in bytes"""
    path = from_pathlike(path)
    if not path.is_dir():
        raise ValueError(f'{path} is not a directory')
    dir_size = 0
    dir_size += sum(
        f.stat().st_size
        for f in path.rglob('*')
        if f.is_file()
    )
    return dir_size

def dir_size_gb(path: PathLike) -> float:
    """Return the size of a directory in GB"""
    return round(dir_size(path) / 1024 ** 3, 1)

def free_gb(path: PathLike) -> float:
    "Return free space at `path`, to .1 GB. Raises FileNotFoundError if `path` not accessible."
    path = from_pathlike(path)
    path = np_config.unc_to_local(path)
    return round(shutil.disk_usage(path).free / 1024 ** 3, 1)

def get_files_created_between(
    path: PathLike,
    glob: str = "*",
    start: float | datetime.datetime = 0,
    end: Optional[float | datetime.datetime] = None,
    reverse: bool = False,
) -> tuple[pathlib.Path, ...]:
    """Recusively get search for files in subfolders of `path` created between `start` and `end`.
    
    Sequence is sorted by ascending creation time (oldest first). `reverse` reverses this order.
    """
    path = from_pathlike(path)
    if not path.is_dir():
        raise ValueError(f'{path} is not a directory, cannot glob for files')
    if not end:
        end = time.time()
    start = start.timestamp() if isinstance(start, datetime.datetime) else start
    end = end.timestamp() if isinstance(end, datetime.datetime) else end
    def ctime(x):
        return x.stat().st_ctime
    files = (file for file in path.rglob(glob) if int(start) <= ctime(file) <= end)
    return tuple(sorted(files, key=ctime, reverse=reverse))
