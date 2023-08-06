from __future__ import annotations

from enum import Enum
from typing import Literal

from feathers.utils import friendly_list
from feathers.widgets import CachedView

from ._models import ChatEntry, ChatRenderable, ChatRenderer
from ._renderers import MarkdownChatRenderer, MinimalChatRenderer

ChatStyle = Literal["minimal"]
"""The names of the supported chat styles.

These are the styles that can be used with a [`Chat`][feathers.widgets._chat].
"""

_VALID_CHAT_STYLES = {"minimal"}


class InvalidChatStyle(Exception):
    """Exception raised if an invalid chat style is used."""


class RendererType(Enum):
    MINIMAL = "minimal"
    MARKDOWN = "markdown"


class Chat(CachedView):
    COMPONENT_CLASSES = {
        "chat--divider",
    }

    DEFAULT_CSS = """
    Chat {
        content-align: center middle;
        padding-left: 2;
    }

    Chat .chat--divider {
        color: $surface-lighten-2;
    }
    """

    def __init__(
        self,
        renderer: ChatRenderer | RendererType = RendererType.MINIMAL,
        *,
        max_width: int = 100,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(wrap=True, max_width=max_width, name=name, id=id, classes=classes, disabled=disabled)
        self._entries: list[ChatEntry] = []
        if isinstance(renderer, RendererType):
            if renderer == RendererType.MINIMAL:
                renderer = MinimalChatRenderer(self, max_width=self.max_width)
            elif renderer == RendererType.MARKDOWN:
                renderer = MarkdownChatRenderer(self, max_width=self.max_width)
            else:
                raise InvalidChatStyle(f"Valid chat styles are {friendly_list(_VALID_CHAT_STYLES)}")
        self._renderer = renderer

    def validate_chat_style(self, chat_style: str) -> str:
        """Validate the chat style."""
        if chat_style not in _VALID_CHAT_STYLES:
            raise InvalidChatStyle(f"Valid chat styles are {friendly_list(_VALID_CHAT_STYLES)}")
        return chat_style

    def add_chat(self, entry: ChatEntry) -> None:
        self._entries.append(entry)
        renderable = ChatRenderable(self._renderer, entry)
        self.add_entry(renderable)

    def get_entries(self) -> list[ChatEntry]:
        return self._entries

    def clear_all_chats(self) -> None:
        self._entries.clear()
        self.clear()
