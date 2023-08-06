import sys
from collections.abc import Callable
from functools import wraps

import pendulum
from pendulum.tz import local_timezone
from rich import print


def now():
    tz = local_timezone()
    return pendulum.now(tz)


def capture(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except OSError as exc:
            print(f"[red]{exc.strerror} on {exc.filename or exc.filename2}")
            sys.exit(exc.errno)
        except ValueError as exc:
            print(f"[red]{exc}")
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            print(f"[beld red] Unexpected error: {exc}")
            sys.exit(2)

    return wrapper
