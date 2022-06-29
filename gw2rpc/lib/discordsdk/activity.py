import ctypes
import typing as t

from . import sdk
from .enum import ActivityActionType, ActivityJoinRequestReply, Result
from .event import bind_events
from .model import Activity, User


class ActivityManager:
    _internal: sdk.IDiscordActivityManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordActivityEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordActivityEvents,
            self._on_activity_join,
            self._on_activity_spectate,
            self._on_activity_join_request,
            self._on_activity_invite
        )

    def _on_activity_join(self, event_data, secret):
        self.on_activity_join(secret.decode("utf8"))

    def _on_activity_spectate(self, event_data, secret):
        self.on_activity_spectate(secret.decode("utf8"))

    def _on_activity_join_request(self, event_data, user):
        self.on_activity_join_request(User(copy=user.contents))

    def _on_activity_invite(self, event_data, type, user, activity):
        self.on_activity_invite(type, User(copy=user.contents), Activity(copy=activity.contents))

    def register_command(self, command: str) -> Result:
        """
        Registers a command by which Discord can launch your game.
        """
        result = Result(self._internal.register_command(self._internal, command.encode("utf8")))
        return result

    def register_steam(self, steam_id: int) -> Result:
        """
        Registers your game's Steam app id for the protocol `steam://run-game-id/<id>`.
        """
        result = Result(self._internal.register_steam(self._internal, steam_id))
        return result

    def update_activity(self, activity: Activity, callback: t.Callable[[Result], None]) -> None:
        """
        Set a user's presence in Discord to a new activity.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.update_activity.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.update_activity(
            self._internal,
            activity._internal,
            ctypes.c_void_p(),
            c_callback
        )

    def clear_activity(self, callback: t.Callable[[Result], None]) -> None:
        """
        Clears a user's presence in Discord to make it show nothing.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.clear_activity.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.clear_activity(self._internal, ctypes.c_void_p(), c_callback)
        

    def send_request_reply(
        self,
        user_id: int,
        reply: ActivityJoinRequestReply,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Sends a reply to an Ask to Join request.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.send_request_reply.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.send_request_reply(
            self._internal,
            user_id,
            reply,
            ctypes.c_void_p(),
            c_callback
        )

    def send_invite(
        self,
        user_id: int,
        type: ActivityActionType,
        content: str,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Sends a game invite to a given user.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.send_invite.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.send_invite(
            self._internal,
            user_id,
            type,
            content.encode("utf8"),
            ctypes.c_void_p(),
            c_callback
        )

    def accept_invite(self, user_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Accepts a game invitation from a given userId.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.accept_invite.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.accept_invite(self._internal, user_id, ctypes.c_void_p(), c_callback)

    def on_activity_join(self, join_secret: str) -> None:
        """
        Fires when a user accepts a game chat invite or receives confirmation from Asking to Join.
        """

    def on_activity_spectate(self, spectate_secret: str) -> None:
        """
        Fires when a user accepts a spectate chat invite or clicks the Spectate button on a user's
        profile.
        """

    def on_activity_join_request(self, user: User) -> None:
        """
        Fires when a user asks to join the current user's game.
        """

    def on_activity_invite(self, type: ActivityActionType, user: User, activity: Activity) -> None:
        """
        Fires when the user receives a join or spectate invite.
        """
