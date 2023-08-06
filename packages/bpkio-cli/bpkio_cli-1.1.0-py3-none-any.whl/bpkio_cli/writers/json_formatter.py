import json

from pygments import formatters, highlight, lexers

from bpkio_cli.utils.config_provider import ConfigProvider
from bpkio_cli.writers.formatter import OutputFormatter


class JSONFormatter(OutputFormatter):
    def __init__(self) -> None:
        super().__init__()

    def format(self, data: object | list, mode="standard") -> str:
        style = ConfigProvider().get("style", section="pygments")
        with_linenos = ConfigProvider().get(
            "linenos", section="pygments", cast_type=bool
        )

        return highlight(
            json.dumps(data, indent=3),
            lexers.JsonLexer(),
            formatters.Terminal256Formatter(style=style, linenos=with_linenos),
        )
