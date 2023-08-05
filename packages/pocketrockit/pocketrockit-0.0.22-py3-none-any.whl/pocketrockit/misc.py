#!/usr/bin/env python3

"""Stuff that doesn't go anywhere else
"""

import asyncio
import logging
import os
import sys
import termios
import threading
from collections.abc import AsyncIterator, Callable, Coroutine, Iterator, MutableMapping
from contextlib import contextmanager
from functools import wraps
from typing import NoReturn, TextIO


def logger() -> logging.Logger:
    """Logger for this module"""
    return logging.getLogger("pr.misc")


class Singleton(type):
    """Yes, a Singleton"""

    _instances: MutableMapping[type, object] = {}

    def __call__(cls: "Singleton", *args: object, **kwargs: object) -> object:
        """Creates an instance if not available yet, returns it"""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def watchdog(
    afunc: Callable[..., Coroutine[object, object, object]]
) -> Callable[..., Coroutine[object, object, object]]:
    """Watch for async functions to throw an unhandled exception"""

    @wraps(afunc)
    async def run(*args: object, **kwargs: object) -> object:
        """Run wrapped function and handle exceptions"""
        try:
            return await afunc(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger().info("KeyboardInterrupt in `%s`", afunc.__name__)
        except Exception:  # pylint: disable=broad-except
            logger().exception("Exception in `%s`:", afunc.__name__)
            asyncio.get_event_loop().stop()
        return None

    return run


def colored(text: str, color: str) -> str:
    """Returns @color formatted @text"""
    return (
        text
        if color is None or not sys.stdout.isatty() or "COLORTERM" not in os.environ
        else {
            "none": "%s",
            "green": "\033[0;32m%s\033[0m",
            "green_bold": "\033[1;32m%s\033[0m",
            "red": "\033[0;31m%s\033[0m",
            "red_bold": "\033[1;31m%s\033[0m",
            "black": "\033[0;30m%s\033[0m",
            "black_bold": "\033[1;30m%s\033[0m",
            "blue": "\033[0;34m%s\033[0m",
            "blue_bold": "\033[1;34m%s\033[0m",
            "yellow": "\033[0;33m%s\033[0m",
            "yellow_bold": "\033[1;33m%s\033[0m",
        }.get(color, "%s")
        % text
    )


def error(message: str) -> None:
    """Prints colorful text"""
    print(colored(message, "red"))


@contextmanager
def raw_mode(file: TextIO) -> Iterator[None]:
    """Context manager switches off stream buffering and resets it aftwerwards"""
    old_attrs = termios.tcgetattr(file.fileno())
    new_attrs = old_attrs[:]
    new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
    try:
        termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
        yield
    finally:
        termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)


async def keyboard_reader(
    loop: asyncio.BaseEventLoop, _terminator: threading.Event
) -> AsyncIterator[str]:
    """Async keyboard reader"""
    try:
        with raw_mode(sys.stdin):
            reader = asyncio.StreamReader()
            await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), sys.stdin)
            while not reader.at_eof():
                # handle terminator         while not terminator.is_set():
                if (char := bytes.decode(await reader.read(2)).replace("\r", "\n")) == chr(4):
                    # chr(4) means EOT (sent by CTRL+D on UNIX terminals)
                    logger().info("CTRL+D")
                    break
                yield char
    except termios.error as exc:
        raise RuntimeError(f"Could not use raw mode on STDIN: {exc}") from exc
    finally:
        logging.debug("keyboard reader terminated")


def setup_logging(level: str | int = logging.DEBUG) -> None:
    '''
    def thread_id_filter(record):
        """Inject thread_id to log records"""
        record.thread_id = threading.get_native_id()
        return record

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(thread_id)s | %(message)s")
    )
    handler.addFilter(thread_id_filter)
    logger().addHandler(handler)
    logging.getLogger().setLevel(level)
    '''
    use_col = "TERM" in os.environ
    col_terminator = "\033[0m" if use_col else ""
    logging.basicConfig(
        format=f"%(levelname)s %(asctime)s.%(msecs)03d %(name)-12s│ %(message)s{col_terminator}",
        datefmt="%H:%M:%S",
        level=getattr(logging, level) if isinstance(level, str) else level,
    )
    for name, color in (
        ("DEBUG", "\033[32m"),
        ("INFO", "\033[36m"),
        ("WARNING", "\033[33m"),
        ("ERROR", "\033[31m"),
        ("CRITICAL", "\033[37m"),
    ):
        logging.addLevelName(
            getattr(logging, name),
            f"{color if use_col else ''}({name[0] * 2})",
        )


def throw(exc: Exception) -> NoReturn:
    """Make raising an exception functional"""
    raise exc
