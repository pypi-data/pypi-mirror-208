from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

__all__ = ["Seq", "SeqIter"]


@dataclass
class Seq:
    id: int
    name: str
    data: str


class SeqIter(metaclass=ABCMeta):
    @abstractmethod
    def __next__(self) -> Seq:
        ...
