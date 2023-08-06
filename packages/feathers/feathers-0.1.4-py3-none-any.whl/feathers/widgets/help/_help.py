from __future__ import annotations

from typing import Literal

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ContentSwitcher

from feathers.utils import friendly_list

from ._base import BaseHelp
from ._long_help import LongHelp
from ._models import HelpEntry
from ._short_help import ShortHelp

HelpMode = Literal["short", "long"]
"""The names of the valid help mode.

These are the modes that can be used with a [`Help`][feathers.widgets.Help].
"""

_VALID_HELP_MODES = {"short", "long"}


class InvalidHelpMode(Exception):
    """Exception raised if an invalid button variant is used."""


class Help(Widget):
    """A single and multi line mode help widget to display key bindings"""

    DEFAULT_CSS = """
    Help {
        dock: bottom;
        width: 100w;
        min-height: 1;
        height: auto;
    }

    Help > ContentSwitcher {
        height: auto;
    }
    """

    mode: reactive[HelpMode] = reactive[HelpMode]("short")
    """The current display mode, either short or long."""

    class Toggled(Message, bubble=True):
        """Posted when the help mode changes."""

        def __init__(self, help: Help, mode: HelpMode) -> None:
            """Initialise the message.

            Args:
                help: The help widget sending the message.
                mode: The current mode of the help button.
            """
            super().__init__()
            self._help = help
            """A reference to the help widget that was changed."""
            self.mode = mode
            """The value of the help mode after the change."""

    def __init__(
        self,
        toggle_key: HelpEntry = HelpEntry("?", "toggle help", is_primary=True),
        short_help_separator: str = " • ",
        short_help_placeholder: str = "No available key mappings",
        long_help_separator: str = "  ",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._short_help: BaseHelp = ShortHelp("short-help", toggle_key, short_help_separator, short_help_placeholder)
        self._long_help: BaseHelp = LongHelp("long-help", long_help_separator)

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="short-help"):
            yield self._short_help
            yield self._long_help

    def toggle_help(self) -> Help:
        """Toggle the help view between short and long.

        Returns:
            The `Help` instance.
        """
        self._switch_view()
        return self

    def action_toggle_help(self) -> None:
        """Toggle the mode of the help when called as an action.

        This would normally be used for a keyboard binding.
        """
        self.toggle_help()

    def validate_mode(self, mode: str) -> str:
        """Validate the mode."""
        if mode not in _VALID_HELP_MODES:
            raise InvalidHelpMode(f"Valid help modes are {friendly_list(_VALID_HELP_MODES)}")
        return mode

    def watch_mode(self) -> None:
        """React to the mode being changed."""

        self.post_message(self.Toggled(self, self.mode))

    def _switch_view(self) -> None:
        switcher = self.query_one(ContentSwitcher)
        if switcher.current == "short-help" and self._short_help._can_switch():
            switcher.current = "long-help"
            self.mode = "long"
        else:
            switcher.current = "short-help"
            self.mode = "short"
