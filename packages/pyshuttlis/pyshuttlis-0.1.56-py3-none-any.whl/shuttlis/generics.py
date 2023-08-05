from dataclasses import dataclass
from functools import total_ordering
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
@total_ordering
class Window(Generic[T]):
    start: T
    end: T

    def __post_init__(self):
        assert self.start <= self.end

    def __lt__(self, other):
        return (
            self.end < other.end
            if self.start == other.start
            else self.start < other.start
        )
