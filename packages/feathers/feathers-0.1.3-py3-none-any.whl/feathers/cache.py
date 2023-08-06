from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

from rich.console import Console, ConsoleOptions, RenderableType
from rich.measure import Measurement
from rich.segment import Segment
from rich.text import Text
from textual.geometry import Size
from textual.strip import Strip


class CacheListener:
    def on_cache_update(self):
        pass


@dataclass
class RenderableWithOptions:
    renderableType: RenderableType
    width: int | None = None
    expand: bool | None = False
    strink: bool | None = True
    wrap: bool = False


class RenderablesCache:
    """Represents a collection of renderables for a Textual Widget.

    A renderables can result in Strips which are cached. The renderables can
    be added and removed and Strips are cached for better performance.

    """

    def __init__(
        self, console: Console, options: ConsoleOptions | None = None, listener: CacheListener | None = None
    ) -> None:
        self._console = console
        self._options = options if options is not None else console.options
        self._listener = listener

        self._all_renderables: OrderedDict[int, RenderableWithOptions] = OrderedDict()
        self._renderables_added: list[int] = []
        self._renderables_removed: list[int] = []
        self._cache: list[tuple[int, Strip]] = []
        self._virtual_size: Size = Size(0, 0)

        self._content_width: int | None = None

    @property
    def virtual_size(self) -> Size:
        return self._virtual_size

    @property
    def content_width(self) -> int | None:
        return self._content_width

    @content_width.setter
    def content_width(self, value: int) -> None:
        if value != self._content_width:
            self._content_width = value
            self.refresh()

    def strip_at(self, index: int) -> Strip | None:
        if index >= len(self._cache):
            return None
        return self._cache[index][1]

    def add(self, renderable: RenderableWithOptions):
        renderable_id = id(renderable)
        self._all_renderables[renderable_id] = renderable
        self._renderables_added.append(renderable_id)
        self._update_cache()

    def remove(self, renderable: RenderableWithOptions):
        renderable_id = id(renderable)
        self._renderables_removed.append(renderable_id)
        self._all_renderables.pop(renderable_id)
        self._update_cache()

    def refresh(self) -> None:
        self._cache.clear()
        self._renderables_added.clear()
        self._renderables_removed.clear()
        for id in self._all_renderables.keys():
            self._renderables_added.append(id)
        self._virtual_size = Size(0, 0)
        self._update_cache()

    def clear(self) -> None:
        self._all_renderables.clear()
        self.refresh()

    def _update_cache(self) -> None:
        if not self._content_width:
            return None
        is_updated = False

        for id in self._renderables_added:
            self._add_to_cache(id, self._all_renderables[id])
            is_updated = True
        self._renderables_added.clear()

        for id in self._renderables_removed:
            is_updated = True
            self._remove_from_cache(id)
        self._renderables_removed.clear()

        if is_updated and self._listener is not None:
            self._listener.on_cache_update()

    def _add_to_cache(self, id: int, renderable: RenderableWithOptions) -> None:
        strips = self._extract_lines(renderable)
        if strips is None:
            return
        for strip in strips:
            self._cache.append((id, strip))

    def _remove_from_cache(self, id: int) -> None:
        # By iterating over the list in reverse order, we can safely remove items without changing
        # the indices of the remaining items in the list. This approach can be more memory-efficient
        # than making a copy of the list to iterate over, especially for large lists, since we only need
        # to keep track of the current index and don't need to create a copy of the list.
        for i in range(len(self._cache) - 1, -1, -1):
            if id in self._cache[i]:
                self._cache.pop(i)
        self._refresh_virtual_size()

    def _extract_lines(
        self,
        renderable: RenderableWithOptions,
    ) -> list[Strip] | None:
        renderableType, width, expand, shrink, wrap = (
            renderable.renderableType,
            renderable.width,
            renderable.expand,
            renderable.strink,
            renderable.wrap,
        )
        render_options = self._console.options

        if isinstance(renderable, Text) and not wrap:
            render_options = render_options.update(overflow="ignore", no_wrap=True)

        render_width = Measurement.get(self._console, render_options, renderableType).maximum
        optimal_width = self._content_width if width is None else width

        if optimal_width:
            if expand and render_width < optimal_width:
                render_width = optimal_width
            if shrink and render_width > optimal_width:
                render_width = optimal_width

        segments = self._console.render(renderableType, render_options.update_width(render_width))
        lines = list(Segment.split_lines(segments))
        if not lines:
            return None

        strips = Strip.from_lines(lines)
        for strip in strips:
            strip.adjust_cell_length(render_width)

        max_width = max(strip.cell_length for strip in strips)
        new_width = max(self._virtual_size.width, max_width)
        new_height = self._virtual_size.height + len(strips)
        self._virtual_size = Size(new_width, new_height)
        return strips

    def _refresh_virtual_size(self):
        max_width = max(strip[1].cell_length for strip in self._cache)
        self._virtual_size = Size(max_width, len(self._cache))

    def __len__(self) -> int:
        return len(self._cache)
