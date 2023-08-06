import functools

import click


# Common parameters for READ and POLL
def url_options(fn):
    @click.option(
        "-s",
        "--sub",
        type=int,
        default=None,
        help="For HLS, read a sub-playlist (by index - as given by the `read ID --table` option with the main playlist)",
    )
    @click.option(
        "-u",
        "--url",
        type=str,
        default=None,
        help="Full URL of URL sub-path (for asset catalogs) to fetch",
    )
    @click.option(
        "-f",
        "--fqdn",
        type=str,
        default=None,
        help="FQDN to use instead of the resource's own. Typically to go through a CDN",
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
