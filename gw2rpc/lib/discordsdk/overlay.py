import ctypes
import typing as t

from . import sdk
from .enum import ActivityActionType, Result
from .event import bind_events


class OverlayManager:
    _internal: sdk.IDiscordOverlayManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordOverlayEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordOverlayEvents,
            self._on_toggle
        )

    def _on_toggle(self, event_data, locked):
        self.on_toggle(locked)

    def is_enabled(self) -> bool:
        """
        Check whether the user has the overlay enabled or disabled.
        """
        enabled = ctypes.c_bool()
        self._internal.is_enabled(self._internal, enabled)
        return enabled.value

    def is_locked(self) -> bool:
        """
        Check if the overlay is currently locked or unlocked
        """
        locked = ctypes.c_bool()
        self._internal.is_locked(self._internal, locked)
        return locked.value

    def set_locked(self, locked: bool, callback: t.Callable[[Result], None]) -> None:
        """
        Locks or unlocks input in the overlay.
        """
        def c_callback(event_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.set_locked.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.set_locked(self._internal, locked, ctypes.c_void_p(), c_callback)

    def open_activity_invite(
        self,
        type: ActivityActionType,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Opens the overlay modal for sending game invitations to users, channels, and servers.
        """
        def c_callback(event_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.open_activity_invite.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.open_activity_invite(self._internal, type, ctypes.c_void_p(), c_callback)

    def open_guild_invite(self, code: str, callback: t.Callable[[Result], None]) -> None:
        """
        Opens the overlay modal for joining a Discord guild, given its invite code.
        """
        def c_callback(event_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.open_guild_invite.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        code = ctypes.c_char_p(code.encode("utf8"))
        self._internal.open_guild_invite(self._internal, code, ctypes.c_void_p(), c_callback)

    def open_voice_settings(self, callback: t.Callable[[Result], None]) -> None:
        """
        Opens the overlay widget for voice settings for the currently connected application.
        """
        def c_callback(event_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.open_voice_settings.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.open_voice_settings(self._internal, ctypes.c_void_p(), c_callback)

    def on_toggle(self, locked: bool) -> None:
        """
        Fires when the overlay is locked or unlocked (a.k.a. opened or closed)
        """
