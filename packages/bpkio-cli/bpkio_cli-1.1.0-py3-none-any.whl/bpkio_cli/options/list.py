import functools

import click

from bpkio_cli.utils import OptionEatAll


def list_options(default_fields=None):
    def decorator(fn):
        """Decorator to add multiple common decorators
        Idea from https://stackoverflow.com/questions/40182157/shared-options-and-flags-between-commands
        """

        @click.option(
            "-s",
            "--sort",
            "sort_fields",
            cls=OptionEatAll,
            type=tuple,
            help="List of fields used to sort the list. Append ':desc' to sort in descending order",
        )
        @click.option(
            "--select",
            "select_fields",
            cls=OptionEatAll,
            type=tuple,
            default=default_fields,
            help="List of fields to return, separated by spaces",
        )
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper
    return decorator
