import sys

# ANSI escape codes — stdlib only, zero dependencies
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RESET = "\033[0m"

_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _COLOR else text


def red(text: str) -> str:
    return _c(_RED, text)


def green(text: str) -> str:
    return _c(_GREEN, text)


def yellow(text: str) -> str:
    return _c(_YELLOW, text)


def bold(text: str) -> str:
    return _c(_BOLD, text)


def dim(text: str) -> str:
    return _c(_DIM, text)


def ok(msg: str) -> None:
    print(f"  {green('✓')} {msg}")


def warn(msg: str) -> None:
    print(f"  {yellow('⚠')} {msg}")


def fail(msg: str) -> None:
    print(f"  {red('✗')} {msg}")


def info(msg: str) -> None:
    print(f"    {dim(msg)}")


def error(msg: str) -> None:
    print(f"    {red(msg)}")


def warning(msg: str) -> None:
    print(f"    {yellow(msg)}")
