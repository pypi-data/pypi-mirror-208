from __future__ import annotations

from abc import abstractmethod

from rich.text import Text
from textual.widget import Widget, events
from textual.widgets import Static

from ._models import HelpEntry


class BaseHelp(Static):
    # called by textual
    def _on_resize(self, _: events.Resize) -> None:
        self.__reset(None)

    # called by textual
    def _on_mount(self, _: events.Mount) -> None:
        self.watch(self.screen, "focused", self.__reset)
        self.watch(self.screen, "stack_updates", self.__reset)
        self.__reset(None)

    # called by textual
    def _notify_style_update(self) -> None:
        self.__reset(None)

    @abstractmethod
    def _create_help(self) -> Text:
        pass

    def _can_switch(self) -> bool:
        return True

    def _get_entries_from_bindings(self) -> list[HelpEntry]:
        binding_entries = set([HelpEntry.from_binding(b) for (_, b) in self.app.namespace_bindings.values() if b.show])
        return sorted(list(binding_entries), key=lambda entry: entry.name)

    def __reset(self, _: Widget | None) -> None:
        self.update(self._create_help())
