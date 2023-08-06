"""
An interface for implementing file-system watching tasks.
"""

# built-in
from asyncio import Event, get_event_loop, sleep
from logging import getLogger
from os import getpid
from pathlib import Path

# third-party
from vcorelib.asyncio import run_handle_stop
from vcorelib.asyncio.cli import run_command, run_shell
from vcorelib.paths.info_cache import FileChanged, file_info_cache

# internal
from rcmpy.paths import default_cache_directory
from rcmpy.watch.params import WatchParams

LOG = getLogger(__name__)


def watch_cache() -> Path:
    """Obtain a file path to use as a cache."""
    return default_cache_directory().joinpath(f"watch_cache-{getpid()}.json")


async def command(*args: str, shell: bool = False) -> int:
    """Run a subprocess and return the return code."""

    runner = run_shell if shell else run_command
    proc = await runner(LOG, *args)
    assert proc.returncode is not None
    return proc.returncode


async def entry(stop_sig: Event, params: WatchParams) -> int:
    """The async entry-point for the watch command."""

    cache_file = watch_cache()

    count = 0

    def poll_cb(_: FileChanged) -> bool:
        """Method to run when any watched file changes."""

        nonlocal count
        count += 1
        return True

    with file_info_cache(
        cache_file, poll_cb, logger=LOG, check_contents=params.check_contents
    ) as files:
        while not stop_sig.is_set():
            files.poll_directory(params.directory, base=params.base)
            files.poll_existing(base=params.base)

            if count > 0:
                # Run the command, return True if it exits 0.
                await command(*params.cmd, shell=params.shell)
                count = 0

            if params.single_pass:
                stop_sig.set()

            # Would be neat to implement something to keep this going at
            # a regular period
            await sleep(params.poll_rate)

    # The cache file shouldn't persist across invocations.
    cache_file.unlink()
    return 0


def watch(params: WatchParams) -> int:
    """Watch a directory for changes."""

    eloop = get_event_loop()
    stop_sig = Event()
    return run_handle_stop(
        stop_sig,
        entry(stop_sig, params),
        eloop=eloop,
    )
