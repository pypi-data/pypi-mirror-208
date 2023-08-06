from __future__ import annotations

from rich.console import Console, ConsoleOptions, ConsoleRenderable, RenderResult
from rich.markdown import Markdown
from rich.style import Style
from rich.text import Text
from textual.widget import Widget

from feathers.renderables import DividerWithLabel

from ._models import ChatEntry, ChatRenderer


class MinimalChatRenderer(ChatRenderer):
    def __init__(self, widget: Widget, *, max_width: int | None = None) -> None:
        super().__init__(widget)
        self._max_width = max_width
        self._blank_line = Text(style=self._widget.rich_style)

    def render(self, entry: ChatEntry, console: Console, options: ConsoleOptions) -> RenderResult:
        divider_style = self._widget.get_component_rich_style("chat--divider")
        content_width = self._max_width or self._widget.content_size.width
        divider = Text("─" * content_width, style=divider_style)

        yield self._blank_line
        yield Text.assemble(
            (f"{entry.participant.name}: ", Style(color=entry.participant.color)),
            (entry.message, Style(color="white")),
            end="\n",
        )
        yield self._blank_line
        yield divider


class MarkdownChatRenderer(ChatRenderer):
    def __init__(
        self, widget: Widget, prompt_renderable: ConsoleRenderable | None = None, *, max_width: int | None = None
    ) -> None:
        super().__init__(widget)
        self._max_width = max_width
        self._prompt_renderable = prompt_renderable
        self._blank_line = Text(style=self._widget.rich_style)

    def render(self, entry: ChatEntry, console: Console, options: ConsoleOptions) -> RenderResult:
        divider_style = self._widget.get_component_rich_style("chat--divider")
        prompt_style = Style(color=entry.participant.color)
        prompt_renderable = self._prompt_renderable or DividerWithLabel(
            entry.participant.name,
            label_style=prompt_style,
            line_style=divider_style,
            width=self._max_width,
            end="\n\n",
        )

        yield prompt_renderable
        yield Markdown(entry.message, code_theme="github-dark")
        yield self._blank_line
