from abc import ABC, abstractmethod
from typing import IO, Generic, TypeVar

from stacks.cards.card import Card
from stacks.stack import Stack

T = TypeVar("T", bound=Card)


class StackReader(ABC, Generic[T]):
    @abstractmethod
    def read(self, file: IO) -> Stack[T]:
        pass


class StackWriter(ABC, Generic[T]):
    @abstractmethod
    def write(self, stack: Stack[T], file: IO):
        pass
