from __future__ import annotations

import math
from dataclasses import dataclass

from rich.text import Text

from ._base import BaseHelp
from ._models import HelpEntry
from ._utils import arrange_items_in_columns


@dataclass
class Measurement:
    width: int
    entries: list[HelpEntry]
    separator: str

    col_padding: int = 1
    min_h: int = 3
    max_w: int = 32
    max_key_w: int = 10
    max_separator_w: int = 6

    def __post_init__(self) -> None:
        self._col_count: int | None = None
        self._col_w: int | None = None
        self._entry_key_w: int | None = None
        self._entry_sep_w: int | None = None
        self._entry_desc_w: int | None = None

    def _key_width(self) -> int:
        if self._entry_key_w is None:
            max_provided_key_width = max(len(entry.name) for entry in self.entries)
            self._entry_key_w = min(max_provided_key_width, self.max_key_w)
        return self._entry_key_w

    def _separator_width(self) -> int:
        if self._entry_sep_w is None:
            self._entry_sep_w = min(len(self.separator), self.max_separator_w)
        return self._entry_sep_w

    def _desc_width(self) -> int:
        if self._entry_desc_w is None:
            max_provided_desc_width = max(len(entry.description) for entry in self.entries)
            leftover_width = self.max_w - (self._key_width() + self._separator_width() + (2 * self.col_padding))
            self._entry_desc_w = min(max_provided_desc_width, leftover_width)
        return self._entry_desc_w

    @property
    def entry_widths(self) -> tuple[int, int, int]:
        return (self._key_width(), self._separator_width(), self._desc_width())

    @property
    def col_width(self) -> int:
        if self._col_w is None:
            entry_w = self._key_width() + self._separator_width() + self._desc_width() + (2 * self.col_padding)
            self._col_w = min(entry_w, self.max_w)
        return self._col_w

    @property
    def col_count(self) -> int:
        if self._col_count is None:
            self._col_count = max(1, math.floor(self.width / self.col_width))
        return self._col_count

    @property
    def height(self) -> int:
        expected_h = math.ceil(len(self.entries) / self.col_count)
        return max(expected_h, self.min_h)

    @staticmethod
    def default() -> Measurement:
        return Measurement(0, [], " ")


class LongHelp(BaseHelp):
    """A multi-line help widget to display key bindings"""

    COMPONENT_CLASSES = {
        "longhelp--separator",
        "longhelp--key",
        "longhelp--description",
    }

    DEFAULT_CSS = """
    LongHelp {
        width: 100w;
        height: auto;
        padding: 1;
    }
    LongHelp .longhelp--separator {
        color: #3C3C3C;
    }
    LongHelp .longhelp--key {
        color: #626262;
    }
    LongHelp .longhelp--description {
        color: #4A4A4A;
    }
    """

    def __init__(self, id: str, separator: str = "  ", debug: bool = False) -> None:
        super().__init__(id=id)
        self._separator = separator
        self._debug = debug

        self._measurement: Measurement = Measurement.default()
        self._pad_char = "#" if debug else " "
        self._pad_box = "|"

    def __entry_text(self, entry: HelpEntry) -> Text:
        key_style = self.get_component_rich_style("longhelp--key")
        description_style = self.get_component_rich_style("longhelp--description")
        separator_style = self.get_component_rich_style("longhelp--separator")

        (key_w, _, desc_w) = self._measurement.entry_widths

        line_text = Text(
            style=self.rich_style,
            no_wrap=True,
            overflow="ellipsis",
            end="",
        )

        line_text.pad(self._measurement.col_padding, self._pad_char)

        key_text = Text(entry.name.lower(), key_style, justify="right", overflow="ellipsis", no_wrap=True, end="")
        key_text.truncate(key_w, overflow="ellipsis")
        key_text.pad_left(key_w - len(entry.name))
        if self._debug:
            key_text.pad(1, self._pad_box)
        line_text.append(key_text)

        separator_text = Text(self._separator, separator_style, justify="center", overflow="crop", no_wrap=True, end="")
        line_text.append(separator_text)

        desc_text = Text(
            entry.description.lower(), description_style, justify="left", overflow="ellipsis", no_wrap=True, end=""
        )
        desc_text.truncate(desc_w, overflow="ellipsis")
        desc_text.pad_right(desc_w - len(entry.description))
        if self._debug:
            desc_text.pad(1, self._pad_box)
        line_text.append(desc_text)

        return line_text

    def _create_help(self) -> Text:
        # avoid division by zero
        if self.content_size.width == 0:
            return Text("")

        entries = self._get_entries_from_bindings()
        self._measurement = Measurement(self.content_size.width, entries, self._separator)
        entry_texts = [self.__entry_text(e) for e in entries]

        line_text = Text(
            style=self.rich_style,
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )

        line_separator = Text(
            "\n",
            style=self.rich_style,
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )

        table = arrange_items_in_columns(entry_texts, self._measurement.height, self._measurement.col_count)
        line_items = [line_text.join(rows) for rows in table]
        return line_separator.join(line_items)

    def get_content_height(self, *_) -> int:
        content = self._create_help()
        line_count = content.plain.count("\n") + 1
        return line_count
