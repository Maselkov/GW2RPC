import ctypes
import typing as t

from . import sdk
from .enum import Result
from .event import bind_events
from .exception import get_exception
from .model import UserAchievement


class AchievementManager:
    _internal: sdk.IDiscordAchievementManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordAchievementEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordAchievementEvents,
            self._on_user_achievement_update
        )

    def _on_user_achievement_update(self, event_data, user_achievement):
        self.on_user_achievement_update(UserAchievement(copy=user_achievement.contents))

    def set_user_achievement(
        self,
        achievement_id: int,
        percent_complete: int,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Updates the current user's status for a given achievement.

        Returns discordsdk.enum.Result via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.set_user_achievement.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.set_user_achievement(
            self._internal,
            achievement_id,
            percent_complete,
            ctypes.c_void_p(),
            c_callback
        )

    def fetch_user_achievements(self, callback: t.Callable[[Result], None]) -> None:
        """
        Loads a stable list of the current user's achievements to iterate over.

        Returns discordsdk.enum.Result via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.fetch_user_achievements.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.fetch_user_achievements(self._internal, ctypes.c_void_p(), c_callback)

    def count_user_achievements(self) -> int:
        """
        Counts the list of a user's achievements for iteration.
        """
        count = ctypes.c_int32()
        self._internal.count_user_achievements(self._internal, count)
        return count.value

    def get_user_achievement_at(self, index: int) -> UserAchievement:
        """
        Gets the user's achievement at a given index of their list of achievements.
        """
        achievement = sdk.DiscordUserAchievement()
        result = Result(self._internal.get_user_achievement_at(
            self._internal,
            index,
            achievement
        ))
        if result != Result.ok:
            raise get_exception(result)

        return UserAchievement(internal=achievement)

    def get_user_achievement(self, achievement_id: int) -> None:
        """
        Gets the user achievement for the given achievement id.
        """
        achievement = sdk.DiscordUserAchievement()
        result = Result(self._internal.get_user_achievement(
            self._internal,
            achievement_id,
            achievement
        ))
        if result != Result.ok:
            raise get_exception(result)

        return UserAchievement(internal=achievement)

    def on_user_achievement_update(self, achievement: UserAchievement) -> None:
        """
        Fires when an achievement is updated for the currently connected user
        """
