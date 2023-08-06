# from abc import abstractmethod
# from typing import TypeVar
#
# from .result import Result
# from .types import Ctx, Loc, RecoveryState
#
# S = TypeVar("S", bound="Stream")
#
#
# class Stream:
#     @abstractmethod
#     def cost(self) -> int:
#         ...
#
#     @abstractmethod
#     def copy(self: S) -> S:
#         ...
#
#     @abstractmethod
#     def advance(self, pos: int) -> None:
#         ...
#
#     @abstractmethod
#     def get_loc(self) -> Loc:
#         ...
#
#
# class EofStream(Stream):
#     @abstractmethod
#     def eof(self: S, ctx: Ctx, rs: RecoveryState) -> Result[None, S]:
#         ...
#
#
# class MarkStream(Stream):
#     @abstractmethod
#     def set_mark(self, mark: int) -> None:
#         ...
#
#     @abstractmethod
#     def get_mark(self) -> int:
#         ...
#
