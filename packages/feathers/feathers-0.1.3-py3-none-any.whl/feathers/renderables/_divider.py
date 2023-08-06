from __future__ import annotations

from typing import Literal

from rich.align import AlignMethod
from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, ConsoleRenderable, RenderResult
from rich.style import Style
from rich.text import Text

LabelType = Literal["simple", "box"]
"""The names of the valid label types.

These are the types that can be used with a [`DividerWithLabel`][feathers.renderables.DividerWithLabel].
"""


class DividerWithLabel(ConsoleRenderable):
    def __init__(
        self,
        label: str,
        *,
        label_style: Style | None = None,
        label_padding: int = 2,
        label_type: LabelType = "simple",
        line_style: Style | None = None,
        width: int | None = None,
        align: AlignMethod = "left",
        end: str = "\n",
    ) -> None:
        """Create a DividerWithLabel renderable.

        Args:
            label: The text for label
            label_style: Style for the label
            label_padding: The left or right padding for label. Ignored if align in center. Defaults to 2
            label_type: The type of the label. Defaults to "simple"
            line_style: Style for the line
            width: The width of the divider. Defaults to console_options.max_width
            align: The alignment of the label. Defaults to "left"
        """

        self.label = label
        self.label_style = label_style
        self.label_padding = label_padding
        self._label_type = label_type
        self.line_style = line_style
        self.width = width
        self.align = align
        self.end = end

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self._label_type == "box":
            return self._render_box(console, options)
        else:
            return self._render_simple(console, options)

    def _render_simple(self, console: Console, options: ConsoleOptions) -> RenderResult:
        content_width = self.width or options.max_width
        spacing_around_prompt = 1
        prompt_width = cell_len(self.label) + (spacing_around_prompt * 2)
        label_style = self.label_style or console.style or Style()
        line_style = self.line_style or console.style or Style()

        left_divider_width = right_divider_width = 0
        if self.align == "left":
            left_divider_width = self.label_padding
            right_divider_width = content_width - prompt_width - left_divider_width
        elif self.align == "right":
            right_divider_width = self.label_padding
            left_divider_width = content_width - prompt_width - right_divider_width
        else:
            left_divider_width = right_divider_width = (content_width // 2) - (prompt_width // 2)

        yield Text("─" * left_divider_width, style=line_style, end="")
        yield Text(f'{" " * spacing_around_prompt}{self.label}{" " * spacing_around_prompt}', style=label_style, end="")
        yield Text("─" * right_divider_width, style=line_style, end=self.end)

    def _render_box(self, console: Console, options: ConsoleOptions) -> RenderResult:
        raise NotImplementedError("Not yet implemented")
