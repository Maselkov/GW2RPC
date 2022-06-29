import ctypes
import typing as t

from . import sdk
from .enum import Result
from .event import bind_events
from .exception import get_exception
from .model import Relationship


class RelationshipManager:
    _internal: sdk.IDiscordRelationshipManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordRelationshipEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordRelationshipEvents,
            self._on_refresh,
            self._on_relationship_update
        )

    def _on_refresh(self, event_data):
        self.on_refresh()

    def _on_relationship_update(self, event_data, relationship):
        self.on_relationship_update(Relationship(copy=relationship.contents))

    def filter(self, filter: t.Callable[[Relationship], None]) -> None:
        """
        Filters a user's relationship list by a boolean condition.
        """
        def c_filter(filter_data, relationship):
            return bool(filter(Relationship(copy=relationship.contents)))

        c_filter = self._internal.filter.argtypes[-1](c_filter)

        self._internal.filter(self._internal, ctypes.c_void_p(), c_filter)

    def get(self, user_id: int) -> Relationship:
        """
        Get the relationship between the current user and a given user by id.
        """
        pointer = sdk.DiscordRelationship()
        result = Result(self._internal.get(self._internal, user_id, pointer))
        if result != Result.ok:
            raise get_exception(result)

        return Relationship(internal=pointer)

    def get_at(self, index: int) -> Relationship:
        """
        Get the relationship at a given index when iterating over a list of relationships.
        """
        pointer = sdk.DiscordRelationship()
        result = Result(self._internal.get_at(self._internal, index, pointer))
        if result != Result.ok:
            raise get_exception(result)

        return Relationship(internal=pointer)

    def count(self) -> int:
        """
        Get the number of relationships that match your filter.
        """
        count = ctypes.c_int32()
        result = Result(self._internal.count(self._internal, count))
        if result != Result.ok:
            raise get_exception(result)

        return count.value

    def on_refresh(self) -> None:
        """
        Fires at initialization when Discord has cached a snapshot of the current status of all
        your relationships.
        """

    def on_relationship_update(self, relationship: Relationship) -> None:
        """
        Fires when a relationship in the filtered list changes, like an updated presence or user
        attribute.
        """
