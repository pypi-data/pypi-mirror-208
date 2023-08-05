import functools

import click


def json_options(fn):
    @click.option(
            "-j",
            "--json",
            is_flag=True,
            default=False,
            help="Return the results as a JSON representation",
        )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
