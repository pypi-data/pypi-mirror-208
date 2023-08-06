from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass

from textual.binding import Binding


class HelpProvider:
    @abstractmethod
    def short_help_keys(self) -> list[HelpEntry]:
        pass


@dataclass(frozen=True)
class HelpEntry:
    name: str
    description: str
    is_primary: bool = True

    @staticmethod
    def from_binding(binding: Binding) -> HelpEntry:
        name = binding.key_display or binding.key
        return HelpEntry(name, binding.description)

    def __eq__(self, other):
        if isinstance(other, HelpEntry):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)
