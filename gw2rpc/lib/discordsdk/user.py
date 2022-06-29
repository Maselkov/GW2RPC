import ctypes
import typing as t

from . import sdk
from .enum import PremiumType, Result, UserFlag
from .event import bind_events
from .exception import get_exception
from .model import User


class UserManager:
    _internal: sdk.IDiscordUserManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordUserEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordUserEvents,
            self._on_current_user_update
        )

    def _on_current_user_update(self, event_data):
        self.on_current_user_update()

    def get_current_user(self) -> User:
        """
        Fetch information about the currently connected user account.
        """
        user = sdk.DiscordUser()
        result = Result(self._internal.get_current_user(self._internal, user))
        if result != Result.ok:
            raise get_exception(result)

        return User(internal=user)

    def get_user(self, user_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Get user information for a given id.

        Returns discordsdk.enum.Result (int) and User via callback.
        """
        def c_callback(callback_data, result, user):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                callback(result, User(copy=user.contents))
            else:
                callback(result, None)

        c_callback = self._internal.get_user.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.get_user(self._internal, user_id, ctypes.c_void_p(), c_callback)

    def get_current_user_premium_type(self) -> PremiumType:
        """
        Get the PremiumType for the currently connected user.
        """
        premium_type = ctypes.c_int32()
        result = Result(self._internal.get_current_user_premium_type(self._internal, premium_type))
        if result != Result.ok:
            raise get_exception(result)

        return PremiumType(premium_type.value)

    def current_user_has_flag(self, flag: UserFlag) -> bool:
        """
        See whether or not the current user has a certain UserFlag on their account.
        """
        has_flag = ctypes.c_bool()
        result = Result(self._internal.current_user_has_flag(self._internal, flag, has_flag))
        if result != Result.ok:
            raise get_exception(result)

        return has_flag.value

    def on_current_user_update(self) -> None:
        """
        Fires when the User struct of the currently connected user changes.
        """
