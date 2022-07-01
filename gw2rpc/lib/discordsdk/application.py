import ctypes
import typing as t

from . import sdk
from .enum import Result
from .model import OAuth2Token


class ApplicationManager:
    _internal: sdk.IDiscordApplicationManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordApplicationEvents = None

    def __init__(self):
        self._garbage = []

    def get_current_locale(self) -> str:
        """
        Get the locale the current user has Discord set to.
        """
        locale = sdk.DiscordLocale()
        self._internal.get_current_locale(self._internal, locale)
        return locale.value.decode("utf8")

    def get_current_branch(self) -> str:
        """
        Get the name of pushed branch on which the game is running.
        """
        branch = sdk.DiscordBranch()
        self._internal.get_current_branch(self._internal, branch)
        return branch.value.decode("utf8")

    def get_oauth2_token(
        self,
        callback: t.Callable[[Result, t.Optional[OAuth2Token]], None]
    ) -> None:
        """
        Retrieve an oauth2 bearer token for the current user.

        Returns discordsdk.enum.Result (int) and OAuth2Token (str) via callback.
        """
        def c_callback(callback_data, result, oauth2_token):
            self._garbage.remove(c_callback)
            if result == Result.ok:
                callback(result, OAuth2Token(copy=oauth2_token.contents))
            else:
                callback(result, None)

        c_callback = self._internal.get_oauth2_token.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.get_oauth2_token(self._internal, ctypes.c_void_p(), c_callback)

    def validate_or_exit(self, callback: t.Callable[[Result], None]) -> None:
        """
        Checks if the current user has the entitlement to run this game.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            callback(result)

        c_callback = self._internal.validate_or_exit.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.validate_or_exit(self._internal, ctypes.c_void_p(), c_callback)

    def get_ticket(self, callback: t.Callable[[Result, t.Optional[str]], None]) -> None:
        """
        Get the signed app ticket for the current user.

        Returns discordsdk.Enum.Result (int) and str via callback.
        """
        def c_callback(callback_data, result, data):
            self._garbage.remove(c_callback)
            if result == Result.ok:
                callback(result, data.contents.value.decode("utf8"))
            else:
                callback(result, None)

        c_callback = self._internal.get_ticket.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.get_ticket(self._internal, ctypes.c_void_p(), c_callback)
