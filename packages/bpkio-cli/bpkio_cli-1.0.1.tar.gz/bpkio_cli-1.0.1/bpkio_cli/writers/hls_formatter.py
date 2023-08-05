import re

from bpkio_api.helpers.handlers import HLSHandler
from colorama import Fore, Style, init

from bpkio_cli.writers.colorizer import Colorizer as CL
from bpkio_cli.writers.formatter import OutputFormatter

init()


class HLSFormatter(OutputFormatter):
    def __init__(self, handler: HLSHandler) -> None:
        super().__init__()
        self.handler = handler
        self.top: int = 0
        self.tail: int = 0

    @property
    def _content(self):
        content = self.handler.content.decode()
        if self.top or self.tail:
            top = self.top
            tail = self.tail
            
            lines = content.splitlines()
            lines_to_return = []

            if top + tail > len(lines):
                return content

            if top > 0:
                lines_to_return.extend(lines[:top])

            if (rest := len(lines) - top - tail) > 0:
                lines_to_return.append(f"# ... {rest} other lines ...")

            if tail > 0:
                lines_to_return.extend(lines[-tail:])

            return "\n".join(lines_to_return)

        return content

    def format(self, mode="standard", top: int = 0, tail: int = 0):
        if top and top > 0:
            self.top = top
        if tail and tail > 0:
            self.tail = tail

        match mode:
            case "raw":
                return self._content
            case "standard":
                return self.highlight()

    def highlight(self):
        """Highlights specific HLS elements of interest"""

        nodes_to_highlight = {
            "#EXT-X-DATERANGE": CL.high2,
            "#EXT-OATCLS-SCTE35": CL.high2,
            "#EXT-X-PROGRAM-DATE-TIME": CL.high2,
            "#EXT-X-ENDLIST": CL.high2,
            "#EXT-X-DISCONTINUITY-SEQUENCE": CL.high2,
        }

        separator_sequences = [
            "#EXT-X-DISCONTINUITY",
            "#EXT-X-CUE-IN",
            "#EXT-X-CUE-OUT",
            "#EXT-X-CUE",
        ]

        new_lines = []

        for line in self._content.splitlines():
            pattern = re.compile(r"^(#[A-Z0-9\-]*?)(\:|$)(.*)$")
            match = pattern.match(line)

            if match:
                node = match.group(1)

                # Special treatment for separators. Add a separator line
                if node in separator_sequences:
                    ansi_escape = re.compile(
                        r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]"
                    )
                    for index, line in reversed(list(enumerate(new_lines))):
                        line = ansi_escape.sub("", line)
                        if line.startswith("#"):
                            continue
                        else:
                            new_lines.insert(
                                index + 1, CL.make_separator(new_lines[index])
                            )
                            break

                if node in nodes_to_highlight:
                    new_node = nodes_to_highlight[node](node)
                elif node in separator_sequences:
                    new_node = CL.high3(node)
                else:
                    new_node = CL.node(node)

                new_lines.append(
                    "{}{}{}".format(
                        new_node,
                        match.group(2),
                        self.highlight_attributes(match.group(3)),
                    )
                )

            elif line.startswith("#"):
                new_lines.append(CL.markup(line))

            else:
                if "/bpkio-" in line:
                    new_lines.append(CL.url2(line))
                else:
                    new_lines.append(CL.url(line))
                # new_lines.append(line)

        return "\n".join(new_lines)

    @staticmethod
    def highlight_attributes(text):
        pattern = re.compile(r'([\w-]+)=((?:[^,"]+|"[^"]*")+),?')
        matches = pattern.findall(text)
        key_value_pairs = [match for match in matches]

        if matches:
            new_attrs = []
            for k, v in key_value_pairs:
                new_key = CL.attr(k)
                has_quotes = v.startswith('"')
                if has_quotes:
                    v = v[1:-1]
                new_value = CL.url(v) if k == "URI" else CL.value(v)
                if has_quotes:
                    new_value = f'"{new_value}"'
                new_attrs.append(f"{new_key}={new_value}")

            return ",".join(new_attrs)
        else:
            return CL.value(text)
