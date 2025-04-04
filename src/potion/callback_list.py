from collections import UserList
from inspect import ismethod
from typing import Callable
from weakref import ref, WeakMethod


class CallbackList(UserList):
    """ A specialized list for managing callbacks. """
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    def __str__(self) -> str:
        return f"CallbackList({self._name})"

    def __repr__(self) -> str:
        return str(self)

    def append(self, callback: Callable) -> None:
        if ismethod(callback):
            cb_ref = WeakMethod(callback)
        else:
            cb_ref = ref(callback)

        if cb_ref not in self.data:
            super().append(cb_ref)

    def remove(self, callback: Callable) -> None:
        if ismethod(callback):
            cb_ref = WeakMethod(callback)
        else:
            cb_ref = ref(callback)

        if cb_ref in self.data:
            super().remove(cb_ref)

    def execute_callbacks(self) -> None:
        """ Execute all callbacks in the list. """
        to_remove = []

        for cb_ref in self.data:
            cb = cb_ref()
            if cb:
                cb()
            else:
                to_remove.append(cb_ref)

        for cb_ref in to_remove:
            self.data.remove(cb_ref)
