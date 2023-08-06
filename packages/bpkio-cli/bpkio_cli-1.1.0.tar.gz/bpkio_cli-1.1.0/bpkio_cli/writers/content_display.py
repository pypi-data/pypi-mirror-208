import os
import time
from datetime import datetime
from typing import Optional

import bpkio_api.helpers.handlers as handlers
import click

from bpkio_cli.core.exceptions import BroadpeakIoCliError
from bpkio_cli.writers.diff import generate_diff
from bpkio_cli.writers.hls_formatter import HLSFormatter
from bpkio_cli.writers.tables import display_table
from bpkio_cli.writers.xml_formatter import XMLFormatter


# ---- Shared Functions ----
def display_content(
    handler: handlers.ContentHandler,
    max: int,
    interval: int,
    table: bool = False,
    raw: bool = False,
    diff: bool = False,
    top: bool = False,
    tail: bool = False,
    clear: bool = False,
    header: bool = True,
):
    """Fetches the content of the URL associated with ID"""
    previous_content = None

    # TODO - move all this to a separate module

    counter = max
    inc_counter = 0

    try:
        while True:
            displayed = False
            stamp = datetime.utcnow()

            if clear:
                _clear_screen()

            if header:
                head = _make_header(
                    stamp=stamp,
                    url=handler.url,
                    original_url=handler.original_url,
                    counter=inc_counter,
                )
                click.secho(head, err=True, fg="white", underline=True)

            if table and handler:
                tb1 = handler.extract_info()
                if tb1:
                    display_table(tb1)

                if hasattr(handler, "extract_timeline"):
                    tb2 = handler.extract_timeline()
                    if tb2:
                        display_table(tb2)

                tb3 = handler.extract_features()
                if tb3 and len(tb3) == 0:
                    click.secho(
                        "Empty table returned. This is likely because the URL returned an empty response. \n"
                        "Use the `read` command for more",
                        fg="red",
                    )
                elif tb3 is not None:
                    display_table(tb3)

                else:
                    raise BroadpeakIoCliError(
                        "No summary functionality implemented for this type of resource"
                    )
                displayed = True

            if not displayed:
                content = "No content to display"
                match handler:
                    case handlers.XMLHandler():
                        formatter = XMLFormatter(handler=handler)
                        content = formatter.format("raw" if raw else "standard")

                    case handlers.HLSHandler():
                        formatter = HLSFormatter(handler=handler)
                        content = formatter.format(
                            "raw" if raw else "standard", top=top, tail=tail
                        )

                if previous_content and diff:
                    click.echo(generate_diff(previous_content, content))
                else:
                    click.echo(content)

                previous_content = content

            if counter == 1:
                break

            time.sleep(int(interval))
            handler.reload()
            counter = counter - 1
            inc_counter = inc_counter + 1

    except KeyboardInterrupt:
        print("Stopped!")


def _clear_screen():
    cls = lambda: os.system("cls" if os.name == "nt" else "clear")
    cls()


def _make_header(stamp: datetime, url: str, original_url: str, counter: Optional[int]):
    lines = []
    if url:
        lines.append(click.style(url, fg="white", underline=True))
    if original_url and original_url != url:
        original_url = click.style(original_url, fg="white", underline=True)
        lines.append(f"  ↪ redirected from {original_url}")

    lines.append(
        click.style(
            "[request{} @ {}]".format(
                " " + str(counter + 1) if counter else "", stamp.isoformat()
            ),
            bg="white",
            fg="black",
        )
    )

    header = "\n".join(lines)
    return header
