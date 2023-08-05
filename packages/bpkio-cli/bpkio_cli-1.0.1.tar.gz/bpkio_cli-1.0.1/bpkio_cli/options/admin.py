import functools

import click


def extra_tenant_option(fn):
    @click.option(
        "--tenant",
        type=int,
        required=False,
        help="[ADMIN] ID of the tenant",
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
