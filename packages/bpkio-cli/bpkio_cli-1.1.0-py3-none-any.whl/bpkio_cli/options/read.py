import functools

import click


# Common parameters for READ and POLL
def read_options(fn):
    @click.option(
        "--raw",
        is_flag=True,
        type=bool,
        default=False,
        help="Get the raw content, unchanged",
    )
    @click.option(
        "--top", type=int, default=None, help="Only display the first N lines"
    )
    @click.option(
        "--tail", type=int, default=None, help="Only display the last N lines"
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
