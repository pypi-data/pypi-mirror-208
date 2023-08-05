import logging
import fnmatch
import os
import subprocess
import sys
import threading
import time
import typing as t
import traceback
from itertools import chain
from pathlib import PurePath
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import EVENT_TYPE_OPENED
from watchdog.events import FileModifiedEvent

__all__ = ["run_with_reloader", "file_run_with_reloader"]


__author__ = "Heppa Soft"
__copyright__ = "Copyright (C) 2023 Heppa Soft"
__license__ = "MIT License"
__version__ = "1.0.4"

_ignore_always = tuple({sys.base_prefix, sys.base_exec_prefix})


_ignore_common_dirs = {
    "__pycache__",
    ".git",
    ".hg",
    ".tox",
    ".nox",
    ".pytest_cache",
    ".mypy_cache",
}

_logger: t.Optional[logging.Logger] = None

def _has_level_handler(logger: logging.Logger) -> bool:
    """Check if there is a handler in the logging chain that will handle
    the given logger's effective level.
    """
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True

        if not current.propagate:
            break

        current = current.parent

    return False


class _ColorStreamHandler(logging.StreamHandler):
    """On Windows, wrap stream with Colorama for ANSI style support."""

    def __init__(self) -> None:
        try:
            import colorama
        except ImportError:
            stream = None
        else:
            stream = colorama.AnsiToWin32(sys.stderr)

        super().__init__(stream)


def _log(type: str, message: str, *args: t.Any, **kwargs: t.Any) -> None:
    """Log a message to the 'reloader' logger.

    The logger is created the first time it is needed. If there is no
    level set, it is set to :data:`logging.INFO`. If there is no handler
    for the logger's effective level, a :class:`logging.StreamHandler`
    is added.
    """
    global _logger

    if _logger is None:
        _logger = logging.getLogger("reloader")

        if _logger.level == logging.NOTSET:
            _logger.setLevel(logging.INFO)

        if not _has_level_handler(_logger):
            _logger.addHandler(_ColorStreamHandler())

    getattr(_logger, type)(message.rstrip(), *args, **kwargs)


def _iter_module_paths() -> t.Iterator[str]:
    """Find the filesystem paths associated with imported modules."""
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)

        if name is None or name in _ignore_always:
            continue

        while not os.path.isfile(name):
            old = name
            name = os.path.dirname(name)

            if name == old:
                break
        else:
            yield name


def _remove_by_pattern(paths: t.Set[str], exclude_patterns: t.Set[str]) -> None:
    for pattern in exclude_patterns:
        paths.difference_update(fnmatch.filter(paths, pattern))


def _find_watchdog_paths(
    extra_patterns: t.Set[str], exclude_patterns: t.Set[str]
) -> t.Iterable[str]:
    """Find paths for the stat reloader to watch. Looks at the same
    sources as the stat reloader, but watches everything under
    directories instead of individual files.
    """
    dirs = set()

    for name in chain(list(sys.path), extra_patterns):
        name = os.path.abspath(name)

        if os.path.isfile(name):
            name = os.path.dirname(name)

        dirs.add(name)

    for name in _iter_module_paths():
        dirs.add(os.path.dirname(name))

    _remove_by_pattern(dirs, exclude_patterns)
    return _find_common_roots(dirs)


def _find_common_roots(paths: t.Iterable[str]) -> t.Iterable[str]:
    root: t.Dict[str, dict] = {}

    for chunks in sorted((PurePath(x).parts for x in paths), key=len, reverse=True):
        node = root

        for chunk in chunks:
            node = node.setdefault(chunk, {})

        node.clear()

    rv = set()

    def _walk(node: t.Mapping[str, dict], path: t.Tuple[str, ...]) -> None:
        for prefix, child in node.items():
            _walk(child, path + (prefix,))

        if not node:
            rv.add(os.path.join(*path))

    _walk(root, ())
    return rv


def _get_args_for_reloading() -> t.List[str]:
    """Determine how the script was executed, and return the args needed
    to execute it again in a new process.
    """
    if sys.version_info >= (3, 10):
        return [sys.executable, *sys.orig_argv[1:]]

    rv = [sys.executable]
    py_script = sys.argv[0]
    args = sys.argv[1:]
    __main__ = sys.modules["__main__"]
    if getattr(__main__, "__package__", None) is None or (
        os.name == "nt"
        and __main__.__package__ == ""
        and not os.path.exists(py_script)
        and os.path.exists(f"{py_script}.exe")
    ):
        py_script = os.path.abspath(py_script)

        if os.name == "nt":
            if not os.path.exists(py_script) and os.path.exists(f"{py_script}.exe"):
                py_script += ".exe"

            if (
                os.path.splitext(sys.executable)[1] == ".exe"
                and os.path.splitext(py_script)[1] == ".exe"
            ):
                rv.pop(0)

        rv.append(py_script)
    else:
        if os.path.isfile(py_script):
            py_module = t.cast(str, __main__.__package__)
            name = os.path.splitext(os.path.basename(py_script))[0]

            if name != "__main__":
                py_module += f".{name}"
        else:
            py_module = py_script

        rv.extend(("-m", py_module.lstrip(".")))

    rv.extend(args)
    return rv


class ReloaderLoop:
    name = ""

    def __init__(
        self,
        extra_patterns: t.Optional[t.Iterable[str]] = None,
        exclude_patterns: t.Optional[t.Iterable[str]] = None,
        interval: t.Union[int, float] = 1,
        verbose: bool = True,
    ) -> None:
        self.extra_patterns: t.Set[str] = {os.path.abspath(x) for x in extra_patterns or ()}
        self.exclude_patterns: t.Set[str] = set(exclude_patterns or ())
        self.interval = interval
        self.verbose = verbose
        
        trigger_reload = self.trigger_reload

        class EventHandler(PatternMatchingEventHandler):
            def on_any_event(self, event: FileModifiedEvent):
                if event.event_type == EVENT_TYPE_OPENED:
                    return

                trigger_reload(event.src_path)

        reloader_name = Observer.__name__.lower()

        if reloader_name.endswith("observer"):
            reloader_name = reloader_name[:-8]

        self.name = f"watchdog ({reloader_name})"
        self.observer = Observer()
        self.event_handler = EventHandler(
            patterns=["*.py", "*.pyc", "*.zip", *self.extra_patterns],
            ignore_patterns=[
                *[f"*/{d}/*" for d in _ignore_common_dirs],
                *self.exclude_patterns,
            ],
        )
        self.should_reload = False

    def __enter__(self) -> "ReloaderLoop":
        """Do any setup, then run one step of the watch to populate the
        initial filesystem state.
        """
        self.watches: t.Dict[str, t.Any] = {}
        self.observer.start()
        self.run_step()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up any resources associated with the reloader."""
        self.observer.stop()
        self.observer.join()

    def run(self) -> None:
        """Continually run the watch step, sleeping for the configured
        interval after each step.
        """
        while not self.should_reload:
            self.run_step()
            time.sleep(self.interval)

        sys.exit(3)

    def run_step(self) -> None:
        """Run one step for watching the filesystem. Called once to set
        up initial state, then repeatedly to update it.
        """
        to_delete = set(self.watches)

        for path in _find_watchdog_paths(self.extra_patterns, self.exclude_patterns):
            if path not in self.watches:
                try:
                    self.watches[path] = self.observer.schedule(
                        self.event_handler, path, recursive=True
                    )
                except OSError:
                    self.watches[path] = None

            to_delete.discard(path)

        for path in to_delete:
            watch = self.watches.pop(path, None)

            if watch is not None:
                self.observer.unschedule(watch)

    def restart_with_reloader(self) -> int:
        """Spawn a new Python interpreter with the same arguments as the
        current one, but running the reloader thread.
        """
        while True:
            print("")
            _log("info", f" * Change detected. Restarting with {self.name}")
            print("")
            args = _get_args_for_reloading()
            new_environ = os.environ.copy()
            new_environ["HR_RUN_MAIN"] = "true"
            exit_code = subprocess.call(args, env=new_environ, close_fds=False)

            if exit_code != 3:
                return exit_code

    def trigger_reload(self, filename: str) -> None:
        self.should_reload = True
        self.log_reload(filename)

    def log_reload(self, filename: str) -> None:
        filename = os.path.abspath(filename)
        if self.verbose:
            _log("info", f" * Detected change in {filename!r}, reloading")


def ensure_echo_on() -> None:
    """Ensure that echo mode is enabled. Some tools such as PDB disable
    it which causes usability issues after a reload."""
    if sys.stdin is None or not sys.stdin.isatty():
        return

    try:
        import termios
    except ImportError:
        return

    attributes = termios.tcgetattr(sys.stdin)

    if not attributes[3] & termios.ECHO:
        attributes[3] |= termios.ECHO
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attributes)


def run_with_reloader(
    main_func: t.Callable[[], None],
    args: t.Union[list, None] = None,
    extra_patterns: t.Optional[t.Iterable[str]] = None,
    ignore_patterns: t.Optional[t.Iterable[str]] = None,
    interval: t.Union[int, float] = 1,
    verbose: bool = True,
    add_current_folder_to_patterns: bool = True,
    ignore_venv_and_python_lib: bool = True
) -> None:
    """Run the given function in an independent Python interpreter."""
    if add_current_folder_to_patterns:
        if extra_patterns == None:
            extra_patterns = []
            
        extra_patterns.append(f"{os.getcwd()}")
    
    if ignore_venv_and_python_lib :
        if ignore_patterns == None:
            ignore_patterns = []
        
        if (venv := os.getenv("VIRTUAL_ENV", None)):
            ignore_patterns.append(f"{venv}")
            ignore_patterns.append(f"{venv}{os.sep}*")
        
        ignore_patterns.append(f"{sys._stdlib_dir}")
        ignore_patterns.append(f"{sys._stdlib_dir}{os.sep}*")
    
    import signal

    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    reloader = ReloaderLoop(
        extra_patterns=extra_patterns, exclude_patterns=ignore_patterns, interval=interval, verbose=verbose
    )

    try:
        if os.environ.get("HR_RUN_MAIN") == "true":
            ensure_echo_on()
            t = threading.Thread(target=main_func, args=(args or ()))
            t.daemon = True

            with reloader:
                t.start()
                reloader.run()
        else:
            sys.exit(reloader.restart_with_reloader())
    except KeyboardInterrupt:
        pass


def file_run_with_reloader(
    file_path: str,
    args: t.Union[list, None] = None,
    extra_patterns: t.Optional[t.Iterable[str]] = None,
    ignore_patterns: t.Optional[t.Iterable[str]] = None,
    interval: t.Union[int, float] = 1,
    verbose: bool = True,
    add_current_folder_to_patterns: bool = True,
    ignore_venv_and_python_lib: bool = True
):
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        _log("error", f"File not found. File name: {file_path}")
        sys.exit()
    
    if not file_path.endswith(".py"):
        _log("error", "Entered file is not a Python file.")
        sys.exit()
        
    if not isinstance(args, list) and args is not None:
        args = [args]
    
    file_dir_name = os.path.dirname(file_path)
    sys.path.append(file_dir_name)
    
    file_path = os.path.basename(file_path).split(".")[0]
    tb = None
    tb_m = None
    
    try:
        module = __import__(file_path)
    except ModuleNotFoundError as e:
        if str(e) == f"ModuleNotFoundError: No module named '{file_path}'":
            _log("error", f"File not found. File name: {file_path}.py")
            sys.exit()
        else:
            tb = "".join(traceback.format_tb(e.__traceback__))
            tb_m = e.msg
    
    if tb != None:
        print(f"{tb}\n{tb_m}")
        sys.exit()
    
    try:
        module.main
    except AttributeError:
        _log("error", "'main' function not found")
        sys.exit()
    
    run_with_reloader(module.main, args, extra_patterns, ignore_patterns, interval, verbose, add_current_folder_to_patterns, ignore_venv_and_python_lib)