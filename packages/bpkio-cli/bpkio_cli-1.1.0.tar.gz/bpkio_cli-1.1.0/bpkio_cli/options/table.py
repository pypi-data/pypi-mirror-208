import functools

import click


# Common parameters for READ and POLL
def table_options(fn):
    @click.option(
        "-t",
        "--table",
        is_flag=True,
        type=bool,
        default=False,
        help="For supported formats, extract key information about the content "
        "and show it as a table",
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
