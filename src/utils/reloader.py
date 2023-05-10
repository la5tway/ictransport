import logging
import multiprocessing
import os
import signal
import sys
import threading
from multiprocessing.context import SpawnProcess
from pathlib import Path
from types import FrameType
from typing import Callable, Iterator


class FileReloader:
    HANDLED_SIGNALS = (
        signal.SIGINT,
        signal.SIGTERM,
    )

    def __init__(
        self,
        target: Callable[[], None] | None = None,
        name: str | None = None,
        reload_delay: float = 0.25,
        reload_dirs: list[str] | str | None = None,
        reload_includes: list[str] | str | None = None,
        reload_excludes: list[str] | str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        if not name:
            name = self.__class__.__name__
        self.name = name
        self.target = target
        self.reload_delay = reload_delay
        self.should_exit = threading.Event()
        self.pid = os.getpid()
        if not logger:
            self.logger = logging.getLogger(name)
        else:
            self.logger = logger.getChild(name)
        self.reload_dirs_raw = reload_dirs
        self.reload_includes_raw = reload_includes
        self.reload_excludes_raw = reload_excludes

        self.should_restart: bool = False

        self.mtimes: dict[Path, float] = {}
        self.reload_dirs: list[Path]
        self.reload_includes: list[str]
        self.reload_excludes: list[str]

    def __iter__(self) -> Iterator[list[Path] | None]:
        return self

    def __next__(self) -> list[Path] | None:
        return self._should_restart()

    def start(self) -> None:
        self._startup()
        self._observe()
        self._shutdown()

    def stop(
        self,
        sig: int | None = None,
        frame: FrameType | None = None,
    ) -> None:
        self.should_exit.set()

    def restart(self) -> None:
        self.should_restart = True

    def _init_signal_handlers(self):
        for sig in self.HANDLED_SIGNALS:
            signal.signal(sig, self._signal_handler)

    def _startup(self) -> None:
        if self.target is None:
            raise RuntimeError("target is required")
        self.logger.info(f"Started reloader process [{self.pid}] using {self.name}")
        self._init_signal_handlers()
        self._init_reload_dirs()
        self.process = get_subprocess(
            target=self.target,
        )
        self.process.start()

    def _observe(self) -> None:
        for changes in self:
            if changes:
                self.logger.warning(
                    f"{self.name} detected changes in "
                    f"{', '.join(map(self._display_path, changes))}. Reloading...",
                )
                self._restart()
            elif self.should_restart:
                self.logger.warning(
                    f"{self.name} detected restart trigger. Reloading..."
                )
                self._restart()

    def _restart(self):
        if self.target is None:
            raise RuntimeError("target is required")
        self.should_restart = False
        self.mtimes = {}
        self.process.terminate()
        self.process.join()

        self.process = get_subprocess(target=self.target)
        self.process.start()

    def _signal_handler(
        self,
        sig: int,
        frame: FrameType | None,
    ) -> None:
        self.stop(sig=sig, frame=frame)

    def _shutdown(self) -> None:
        self.process.terminate()
        self.process.join()

        self.logger.info(f"Stopping reloader process [{self.pid}]")

    def _should_restart(self) -> list[Path] | None:
        self._pause()

        for file in self._iter_py_files():
            try:
                mtime = file.stat().st_mtime
            except OSError:  # pragma: nocover
                continue

            old_time = self.mtimes.get(file)
            if old_time is None:
                self.mtimes[file] = mtime
                continue
            elif mtime > old_time:
                return [file]
        return None

    def _pause(self) -> None:
        if self.should_exit.wait(self.reload_delay):
            raise StopIteration()

    def _iter_py_files(self) -> Iterator[Path]:
        for reload_dir in self.reload_dirs:
            for path in list(reload_dir.rglob("*.py")):
                yield path.resolve()

    def _init_reload_dirs(self):
        reload_dirs = self._normalize_dirs(self.reload_dirs_raw)

        self.reload_includes, self.reload_dirs = self._resolve_reload_patterns(
            self._normalize_dirs(self.reload_includes_raw),
            reload_dirs,
        )

        self.reload_excludes, self.reload_dirs_excludes = self._resolve_reload_patterns(
            self._normalize_dirs(self.reload_excludes_raw), []
        )

        reload_dirs_tmp = self.reload_dirs.copy()

        for directory in self.reload_dirs_excludes:
            for reload_directory in reload_dirs_tmp:
                if (
                    directory == reload_directory
                    or directory in reload_directory.parents
                ):
                    try:
                        self.reload_dirs.remove(reload_directory)
                    except ValueError:
                        pass

        for pattern in self.reload_excludes:
            if pattern in self.reload_includes:
                self.reload_includes.remove(pattern)

        if not self.reload_dirs:
            if reload_dirs:
                self.logger.warning(
                    f"Provided reload directories {reload_dirs} did not contain valid "
                    + "directories, watching current working directory."
                )
            self.reload_dirs = [Path(os.getcwd())]

        self.logger.info(
            "Will watch for changes in these directories: "
            f"{sorted(list(map(str, self.reload_dirs)))}",
        )

    def _normalize_dirs(
        self,
        dirs: list[str] | str | None,
    ) -> list[str]:
        if dirs is None:
            return []
        if isinstance(dirs, str):
            return [dirs]
        return list(set(dirs))

    def _resolve_reload_patterns(
        self,
        patterns_list: list[str],
        directories_list: list[str],
    ) -> tuple[list[str], list[Path]]:
        directories: list[Path] = list(set(map(Path, directories_list.copy())))
        patterns: list[str] = patterns_list.copy()

        current_working_directory = Path.cwd()
        for pattern in patterns_list:
            # Special case for the .* pattern, otherwise this would only match
            # hidden directories which is probably undesired
            if pattern == ".*":
                continue
            patterns.append(pattern)
            if self._is_dir(Path(pattern)):
                directories.append(Path(pattern))
            else:
                for match in current_working_directory.glob(pattern):
                    if self._is_dir(match):
                        directories.append(match)

        directories = list(set(directories))
        directories = list(map(Path, directories))
        directories = list(map(lambda x: x.resolve(), directories))
        directories = list(
            set(
                [
                    reload_path
                    for reload_path in directories
                    if self._is_dir(reload_path)
                ]
            )
        )

        children = []
        for j in range(len(directories)):
            for k in range(j + 1, len(directories)):
                if directories[j] in directories[k].parents:
                    children.append(directories[k])  # pragma: py-darwin
                elif directories[k] in directories[j].parents:
                    children.append(directories[j])

        directories = list(set(directories).difference(set(children)))

        return list(set(patterns)), directories

    def _is_dir(self, path: Path) -> bool:
        try:
            if not path.is_absolute():
                path = path.resolve()
            return path.is_dir()
        except OSError:
            return False

    def _display_path(self, path: Path) -> str:
        try:
            return f"'{path.relative_to(Path.cwd())}'"
        except ValueError:
            return f"'{path}'"


multiprocessing.allow_connection_pickling()
spawn = multiprocessing.get_context("spawn")


def get_subprocess(
    target: Callable[..., None],
) -> SpawnProcess:
    """
    Called in the parent process, to instantiate a new child process instance.
    The child is not yet started at this point.
    * config - The Uvicorn configuration instance.
    * target - A callable that accepts a list of sockets. In practice this will
            be the `Server.run()` method.
    * sockets - A list of sockets to pass to the server. Sockets are bound once
                by the parent process, and then passed to the child processes.
    """
    # We pass across the stdin fileno, and reopen it in the child process.
    # This is required for some debugging environments.
    try:
        stdin_fileno = sys.stdin.fileno()
    except OSError:
        stdin_fileno = None

    kwargs = {
        "target": target,
        "stdin_fileno": stdin_fileno,
    }

    return spawn.Process(
        target=subprocess_started,
        kwargs=kwargs,
    )


def subprocess_started(
    target: Callable[..., None],
    stdin_fileno: int | None,
) -> None:
    """
    Called when the child process starts.
    * config - The Uvicorn configuration instance.
    * target - A callable that accepts a list of sockets. In practice this will
            be the `Server.run()` method.
    * sockets - A list of sockets to pass to the server. Sockets are bound once
                by the parent process, and then passed to the child processes.
    * stdin_fileno - The file number of sys.stdin, so that it can be reattached
                    to the child process.
    """
    # Re-open stdin.
    if stdin_fileno is not None:
        sys.stdin = os.fdopen(stdin_fileno)

    # Now we can call into `Server.run(sockets=sockets)`
    target()
