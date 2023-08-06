from __future__ import annotations

from typing import cast

from rich.console import RenderableType
from rich.highlighter import ReprHighlighter
from rich.pretty import Pretty
from rich.protocol import is_renderable
from rich.text import Text
from textual.geometry import Size
from textual.strip import Strip

from feathers.cache import CacheListener, RenderablesCache, RenderableWithOptions

from ._nav_view import NavigableView


class CachedView(NavigableView, CacheListener):
    # scrollbar-gutter here is a fix to calculate scrollbar_gutter which impact the scrollable_content_region
    # calculation in `on_resize`. This looks like a bug in base widget code. Without this, the horizontal scrollbar
    # shows up for few characters on first call to `on_resize`
    DEFAULT_CSS = """
    CachedView{
        scrollbar-gutter: stable;
    }
    """

    max_width: int | None = None
    wrap: bool = False
    highlight: bool = False
    markup: bool = False
    auto_scroll: bool = True

    def __init__(
        self,
        *,
        max_width: int | None = None,
        wrap: bool = False,
        highlight: bool = False,
        markup: bool = False,
        auto_scroll: bool = True,
        enable_cursor: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Create a TextLog widget.

        Args:
            wrap: Enable word wrapping (default is off).
            highlight: Automatically highlight content.
            markup: Apply Rich console markup.
            auto_scroll: Enable automatic scrolling to end.
            enable_cursor: Enable cursor which name this view navigable. This also make this view focusable.
            name: The name of the text log.
            id: The ID of the text log in the DOM.
            classes: The CSS classes of the text log.
            disabled: Whether the text log is disabled or not.
        """
        super().__init__(disable_cursor=not enable_cursor, name=name, id=id, classes=classes, disabled=disabled)
        self.max_width = max_width
        """Enforce max width of all the content"""
        self.wrap = wrap
        """Enable word wrapping."""
        self.highlight = highlight
        """Automatically highlight content."""
        self.markup = markup
        """Apply Rich console markup."""
        self.auto_scroll = auto_scroll
        """Automatically scroll to the end on write."""
        self.highlighter = ReprHighlighter()

        self._renderables_cache: RenderablesCache = RenderablesCache(self.app.console, listener=self)

    def notify_style_update(self) -> None:
        self._renderables_cache.refresh()

    def _extract_renderable(
        self, content: RenderableType | object, width: int | None, expand: bool | None, shrink: bool | None
    ) -> RenderableWithOptions:
        renderable: RenderableType
        if not is_renderable(content):
            renderable = Pretty(content)
        else:
            if isinstance(content, str):
                if self.markup:
                    renderable = Text.from_markup(content)
                else:
                    renderable = Text(content)
                if self.highlighter is not None:
                    renderable = self.highlighter(renderable)
            else:
                renderable = cast(RenderableType, content)

        return RenderableWithOptions(renderable, width, expand, shrink, self.wrap)

    def add(
        self,
        content: RenderableType | object,
        width: int | None = None,
        expand: bool = False,
        shrink: bool = True,
        scroll_end: bool | None = None,
    ) -> CachedView:
        """Write text or a rich renderable.

        Args:
            content: Rich renderable (or text).
            width: Width to render or `None` to use optimal width.
                Only used if either or both expand and shrink are True.
            expand: Enable expand to widget width, or `False` to use `width`.
            shrink: Enable shrinking of content to fit width.
            scroll_end: Enable automatic scroll to end, or `None` to use `self.auto_scroll`.

        Returns:
            The `TextLog` instance.
        """

        width = width or self.max_width
        renderable = self._extract_renderable(content, width, expand, shrink)
        self._renderables_cache.add(renderable)

        auto_scroll = self.auto_scroll if scroll_end is None else scroll_end
        if auto_scroll:
            self.scroll_end(animate=False)

        return self

    def on_resize(self):
        self._renderables_cache.content_width = self.scrollable_content_region.width

    def clear(self) -> CachedView:
        self._renderables_cache.clear()
        self.max_width = 0
        self.virtual_size = Size(0, 0)
        self.refresh()
        return self

    def on_cache_update(self):
        self.virtual_size = self._renderables_cache.virtual_size
        if self.auto_scroll:
            self.scroll_end(animate=False)

    def line_count(self) -> int:
        return len(self._renderables_cache)

    def line_width(self, y: int) -> int:
        _, scroll_y = self.scroll_offset
        line = self._renderables_cache.strip_at(scroll_y + y)
        if line is None:
            return 0
        return line.cell_length

    def render_line(self, y: int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        line = self._render_line(scroll_y + y, scroll_x, self.size.width)
        strip = line.apply_style(self.rich_style)
        strip = self.add_cursor(y, line)
        return strip

    def _render_line(self, y: int, scroll_x: int, width: int) -> Strip:
        strip = self._renderables_cache.strip_at(y)
        if strip is None:
            return Strip.blank(width, self.rich_style)

        line = strip.crop(scroll_x, scroll_x + width)

        return line
