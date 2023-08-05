from abc import ABC, abstractmethod
from overrides import overrides
from typing import Union, TypeVar

T1 = TypeVar("T1")
T2 = TypeVar("T2")

class Resource(ABC):
    @abstractmethod
    def enable(self, item: Union[T1, T2]) -> Union[T1, T2]:
        """Enables the resource"""
    
    def disable(self, item: Union[T1, T2]) -> Union[T1, T2]:
        """Disables the resource"""

class DummyResource(Resource):
    def __init__(self, index: int):
        self.index = index
    
    @overrides
    def enable(self, item: Union[T1, T2]) -> Union[T1, T2]:
        print(f"Enabling resource {self} to item {item}")
        return item

    @overrides
    def disable(self, item: Union[T1, T2]) -> Union[T1, T2]:
        print(f"Disabling resource {self} to item {item}")
        return item

    def __str__(self):
        return f"Dummy Resource (id: {self.index})"

    def __repr__(self):
        return str(self)
