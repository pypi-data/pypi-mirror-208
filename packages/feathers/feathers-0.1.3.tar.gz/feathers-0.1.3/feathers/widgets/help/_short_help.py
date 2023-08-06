from __future__ import annotations

from typing import cast

from rich.text import Text

from ._base import BaseHelp
from ._models import HelpEntry, HelpProvider


class ShortHelp(BaseHelp):
    """A single line help widget to display key bindings"""

    COMPONENT_CLASSES = {
        "shorthelp--separator",
        "shorthelp--key",
        "shorthelp--description",
    }

    DEFAULT_CSS = """
    ShortHelp {
        padding: 0 1;
        width: 100w;
        height: 1;
    }
    ShortHelp .shorthelp--separator {
        color: #3C3C3C
    }
    ShortHelp .shorthelp--key {
        color: #626262
    }
    ShortHelp .shorthelp--description {
        color: #4A4A4A
    }
    """

    def __init__(
        self,
        id: str,
        toggle_key: HelpEntry,
        separator: str,
        placeholder_text: str = "No key mappings found. Trying changing focus",
    ) -> None:
        super().__init__(id=id)
        self.toggle_key = toggle_key
        self.separator = separator
        self.placeholder_text: str = placeholder_text

        self._can_switch_to_long_help: bool = False
        self._text_style = Text(
            style=self.rich_style,
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )

    def _can_switch(self) -> bool:
        return self._can_switch_to_long_help

    def _create_help(self) -> Text:
        text = self._text_style.copy()
        entries = self.__get_entries()

        if self.__has_long_help_entries(entries):
            self._can_switch_to_long_help = True
            entries.append(self.toggle_key)
        else:
            self._can_switch_to_long_help = False

        if len(entries) == 0:
            return self.__get_placeholder_text()

        separator_style = self.get_component_rich_style("shorthelp--separator")
        separator = text.append(self.separator, separator_style)

        entry_texts = [self.__entry_text(e) for e in entries]
        return separator.join(entry_texts)

    def __entry_text(self, entry: HelpEntry) -> Text:
        key_style = self.get_component_rich_style("shorthelp--key")
        description_style = self.get_component_rich_style("shorthelp--description")
        return Text.assemble((entry.name.lower(), key_style), (f" {entry.description.lower()}", description_style))

    def __get_placeholder_text(self) -> Text:
        description_style = self.get_component_rich_style("shorthelp--description")
        return Text(
            self.placeholder_text,
            style=description_style,
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )

    def __get_entries(self) -> list[HelpEntry]:
        focused_widget = self.app.focused

        if focused_widget is None:
            self.log.info("No focused widget found")
            return []

        if isinstance(focused_widget, HelpProvider):
            return focused_widget.short_help_keys()

        if not hasattr(focused_widget, "short_help_keys") or not callable(getattr(focused_widget, "short_help_keys")):
            self.log.info("No short_help_keys method found on the current widget")
            return []

        widget = cast(HelpProvider, focused_widget)  # make mypy happy
        keys = widget.short_help_keys()

        if not isinstance(keys, list):
            self.log.warning("short_help_keys should return a list")
            return []

        if not all(isinstance(key, HelpEntry) for key in keys):
            self.log.warning("Not all items returned by short_help_keys are of they HelpEntry")
            return []

        return list(dict.fromkeys(keys))  ## dedupe list

    def __has_long_help_entries(self, entries: list[HelpEntry]) -> bool:
        long_help_entries = self._get_entries_from_bindings()
        if self.toggle_key in long_help_entries:
            long_help_entries.remove(self.toggle_key)
        return bool(set(long_help_entries) - set(entries))
