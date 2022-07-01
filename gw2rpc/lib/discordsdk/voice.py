import ctypes
import typing as t

from . import sdk
from .enum import Result
from .event import bind_events
from .exception import get_exception
from .model import InputMode


class VoiceManager:
    _internal: sdk.IDiscordVoiceManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordVoiceEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordVoiceEvents,
            self._on_settings_update
        )

    def _on_settings_update(self, event_data):
        self.on_settings_update()

    def get_input_mode(self) -> InputMode:
        """
        Get the current voice input mode for the user
        """
        input_mode = sdk.DiscordInputMode()
        result = Result(self._internal.get_input_mode(self._internal, input_mode))
        if result != Result.ok:
            raise get_exception(result)

        return InputMode(internal=input_mode)

    def set_input_mode(self, inputMode: InputMode, callback: t.Callable[[Result], None]) -> None:
        """
        Sets a new voice input mode for the uesr.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.set_input_mode.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.set_input_mode(
            self._internal,
            inputMode._internal,
            ctypes.c_void_p(),
            c_callback
        )

    def is_self_mute(self) -> bool:
        """
        Whether the connected user is currently muted.
        """
        mute = ctypes.c_bool()
        result = Result(self._internal.is_self_mute(self._internal, mute))
        if result != Result.ok:
            raise get_exception(result)

        return mute.value

    def set_self_mute(self, mute: bool) -> None:
        """
        Mutes or unmutes the currently connected user.
        """
        result = Result(self._internal.set_self_mute(self._internal, mute))
        if result != Result.ok:
            raise get_exception(result)

    def is_self_deaf(self) -> bool:
        """
        Whether the connected user is currently deafened.
        """
        deaf = ctypes.c_bool()
        result = Result(self._internal.is_self_deaf(self._internal, deaf))
        if result != Result.ok:
            raise get_exception(result)

        return deaf.value

    def set_self_deaf(self, deaf: bool) -> None:
        """
        Deafens or undefeans the currently connected user.
        """
        result = Result(self._internal.set_self_deaf(self._internal, deaf))
        if result != Result.ok:
            raise get_exception(result)

    def is_local_mute(self, user_id: int) -> bool:
        """
        Whether the given user is currently muted by the connected user.
        """
        mute = ctypes.c_bool()
        result = Result(self._internal.is_local_mute(self._internal, user_id, mute))
        if result != Result.ok:
            raise get_exception(result)

        return mute.value

    def set_local_mute(self, user_id: int, mute: bool) -> None:
        """
        Mutes or unmutes the given user for the currently connected user.
        """
        result = Result(self._internal.set_local_mute(self._internal, user_id, mute))
        if result != Result.ok:
            raise get_exception(result)

    def get_local_volume(self, user_id: int) -> int:
        """
        Gets the local volume for a given user.
        """
        volume = ctypes.c_uint8()
        result = Result(self._internal.get_local_volume(self._internal, user_id, volume))
        if result != Result.ok:
            raise get_exception(result)

        return volume.value

    def set_local_volume(self, user_id: int, volume: int) -> None:
        """
        Sets the local volume for a given user.
        """
        result = Result(self._internal.set_local_volume(self._internal, user_id, volume))
        if result != Result.ok:
            raise get_exception(result)

    def on_settings_update(self) -> None:
        # This event is not documented anywhere (yet?)
        pass
