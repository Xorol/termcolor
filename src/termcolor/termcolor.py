# Copyright (c) 2008-2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

"""ANSI color formatting for output in terminal."""

from __future__ import annotations

import enum
import os
import sys
import warnings
from typing import Any, Iterable, Optional


def __getattr__(name: str) -> list[str]:
    if name == "__ALL__":
        warnings.warn(
            "__ALL__ is deprecated and will be removed in termcolor 3. "
            "Use __all__ instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ["colored", "cprint"]
    msg = f"module '{__name__}' has no attribute '{name}'"
    raise AttributeError(msg)


class Flag(enum.Flag):
  BOLD = 1
  DARK = 2
  UNDERLINE = 4
  BLINK = 8
  REVERSE = 16
  CONCEALED = 32

flag_codes = {
  Flag.BOLD: "1",
  Flag.DARK: "2",
  Flag.UNDERLINE: "4",
  Flag.BLINK: "5",
  Flag.REVERSE: "7",
  Flag.CONCEALED: "8"
}

def flag_to_code(flag: enum.Flag) -> str:
  flags = [""] * 6
  flags[:] = [flag_codes[x] if x in flag 
              else "" 
              for x in Flag]
  flags = filter(lambda x: x != "", flags)
  return ";".join(flags)

class BG(enum.IntEnum):
  BLACK = 40
  RED = 41
  GREEN = 42
  YELLOW = 43
  MAGENTA = 45
  CYAN = 46
  LIGHT_GRAY = 47
  DARK_GRAY = 100
  LIGHT_RED = 101
  LIGHT_GREEN = 102
  LIGHT_YELLOW = 103
  LIGHT_BLUE = 104
  LIGHT_MAGENTA = 105
  LIGHT_CYAN = 106
  WHITE = 107

class FG(enum.IntEnum):
  BLACK = 30
  RED = 31
  GREEN = 32
  YELLOW = 33
  MAGENTA = 35
  CYAN = 36
  LIGHT_GRAY = 37
  DARK_GRAY = 90
  LIGHT_RED = 91
  LIGHT_GREEN = 92
  LIGHT_YELLOW = 93
  LIGHT_BLUE = 94
  LIGHT_MAGENTA = 95
  LIGHT_CYAN = 96
  WHITE = 97

RESET = "\033[0m"


def _can_do_colour(
    *, no_color: bool | None = None, force_color: bool | None = None
) -> bool:
    """Check env vars and for tty/dumb terminal"""
    # First check overrides:
    # "User-level configuration files and per-instance command-line arguments should
    # override $NO_COLOR. A user should be able to export $NO_COLOR in their shell
    # configuration file as a default, but configure a specific program in its
    # configuration file to specifically enable color."
    # https://no-color.org
    if no_color is not None and no_color:
        return False
    if force_color is not None and force_color:
        return True

    # Then check env vars:
    if "ANSI_COLORS_DISABLED" in os.environ:
        return False
    if "NO_COLOR" in os.environ:
        return False
    if "FORCE_COLOR" in os.environ:
        return True
    return (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and os.environ.get("TERM") != "dumb"
    )


def colored(
    text: str,
    color: Optional[FG] = None,
    background_color: Optional[BG] = None,
    flag: Optional[Flag] = None,
    *,
    no_color: Optional[bool] = None,
    force_color: Optional[bool] = None,
) -> str:
    if not _can_do_colour(no_color=no_color, force_color=force_color):
        return text, "terminal does not support ANSI"

    fmt_str = "\033[%dm%s"
    if color is not None:
        text = fmt_str % (color, text)

    if background_color is not None:
        text = fmt_str % (background_color, text)

    if flag is not None:
        text = "\033[%sm%s" % (flag_to_code(flag), text)

    return text + RESET


def cprint(
    text: str,
    color: Optional[FG] = None,
    background_color: Optional[BG] = None,
    flag: Optional[Flag] = None,
    *,
    no_color: Optional[bool] = None,
    force_color: Optional[bool] = None,
    **kwargs: Any,
) -> None:
    """Print colorized text.

    It accepts arguments of print function.
    """

    print(
        (
            colored(
                text,
                color,
                background_color,
                flag,
                no_color=no_color,
                force_color=force_color,
            )
        ),
        **kwargs,
    )
