from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass

from rich.console import Console, ConsoleOptions, RenderResult
from textual.widget import Widget


@dataclass
class Participant:
    name: str
    icon: str = ""
    color: str | None = None


@dataclass
class ChatEntry:
    message: str
    participant: Participant
    timestamp: float | None = None


class ChatRenderer:
    """An object that supports the console protocol and can render a chat"""

    def __init__(self, widget: Widget) -> None:
        self._widget = widget

    @abstractmethod
    def render(self, entry: ChatEntry, console: Console, options: ConsoleOptions) -> RenderResult:
        pass


class ChatRenderable:
    """An object that supports the console protocol and can render a chat"""

    def __init__(self, renderer: ChatRenderer, entry: ChatEntry) -> None:
        self._renderer = renderer
        self._entry = entry

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        return self._renderer.render(self._entry, console, options)
