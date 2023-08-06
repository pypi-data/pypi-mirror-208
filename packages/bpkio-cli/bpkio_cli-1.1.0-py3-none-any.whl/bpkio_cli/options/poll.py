import functools

import click


# Common parameters for READ and POLL
def poll_options(fn):
    @click.option(
        "--max",
        type=int,
        is_flag=False,
        default=-2,
        help="Number of times to poll before stopping. Don't specify or set to 0 for infinite polling",
    )
    @click.option(
        "-i",
        "--interval",
        type=int,
        default=4,
        help="Polling frequency to re-read the source's content",
    )
    @click.option(
        "-d",
        "--diff",
        is_flag=True,
        type=bool,
        default=False,
        help="Highlight the difference with last polled data (requires `--poll`)",
    )
    @click.option(
        "--clear/--no-clear",
        is_flag=True,
        default=True,
        help="Clear the screen first when polling",
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
