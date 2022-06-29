import ctypes
import typing as t

from . import sdk
from .achievement import AchievementManager
from .activity import ActivityManager
from .application import ApplicationManager
from .enum import CreateFlags, LogLevel, Result
from .exception import get_exception
from .image import ImageManager
from .lobby import LobbyManager
from .network import NetworkManager
from .overlay import OverlayManager
from .relationship import RelationshipManager
from .storage import StorageManager
from .store import StoreManager
from .user import UserManager
from .voice import VoiceManager


class Discord:
    _garbage: t.List[t.Any]

    core: sdk.IDiscordCore = None

    def __init__(self, client_id: int, flags: CreateFlags):
        self._garbage = []

        self._activity_manager = ActivityManager()
        self._relationship_manager = RelationshipManager()
        self._image_manager = ImageManager()
        self._user_manager = UserManager()
        self._lobby_manager = LobbyManager()
        self._network_manager = NetworkManager()
        self._overlay_manager = OverlayManager()
        self._application_manager = ApplicationManager()
        self._storage_manager = StorageManager()
        self._store_manager = StoreManager()
        self._voice_manager = VoiceManager()
        self._achievement_manager = AchievementManager()

        version = sdk.DiscordVersion(2)

        params = sdk.DiscordCreateParams()
        params.client_id = client_id
        params.flags = flags

        sdk.DiscordCreateParamsSetDefault(params)
        params.activity_events = self._activity_manager._events
        params.relationship_events = self._relationship_manager._events
        params.image_events = self._image_manager._events
        params.user_events = self._user_manager._events
        params.lobby_events = self._lobby_manager._events
        params.network_events = self._network_manager._events
        params.overlay_events = self._overlay_manager._events
        params.application_events = self._application_manager._events
        params.storage_events = self._storage_manager._events
        params.store_events = self._store_manager._events
        params.voice_events = self._voice_manager._events
        params.achievement_events = self._achievement_manager._events

        pointer = ctypes.POINTER(sdk.IDiscordCore)()

        result = Result(sdk.DiscordCreate(version, ctypes.pointer(params), ctypes.pointer(pointer)))
        if result != Result.ok:
            raise get_exception(result)

        self.core = pointer.contents


    def __del__(self):
        if self.core:
            self.core.destroy(self.core)
            self.core = None

    def dispose(self):
        self.core.dispose(self.core)


    def set_log_hook(self, min_level: LogLevel, hook: t.Callable[[LogLevel, str], None]) -> None:
        """
        Registers a logging callback function with the minimum level of message to receive.
        """
        def c_hook(hook_data, level, message):
            level = LogLevel(level)
            hook(level, message.decode("utf8"))

        c_hook = self.core.set_log_hook.argtypes[-1](c_hook)
        self._garbage.append(c_hook)

        self.core.set_log_hook(self.core, min_level.value, ctypes.c_void_p(), c_hook)

    def run_callbacks(self) -> None:
        """
        Runs all pending SDK callbacks.
        """
        result = Result(self.core.run_callbacks(self.core))
        if result != Result.ok:
            raise get_exception(result)

    def get_activity_manager(self) -> ActivityManager:
        """
        Fetches an instance of the manager for interfacing with activies in the SDK.
        """
        if not self._activity_manager._internal:
            self._activity_manager._internal = self.core.get_activity_manager(self.core).contents

        return self._activity_manager

    def get_relationship_manager(self) -> RelationshipManager:
        """
        Fetches an instance of the manager for interfacing with relationships in the SDK.
        """
        if not self._relationship_manager._internal:
            self._relationship_manager._internal = self.core.get_relationship_manager(self.core).contents  # noqa: E501

        return self._relationship_manager

    def get_image_manager(self) -> ImageManager:
        """
        Fetches an instance of the manager for interfacing with images in the SDK.
        """
        if not self._image_manager._internal:
            self._image_manager._internal = self.core.get_image_manager(self.core).contents

        return self._image_manager

    def get_user_manager(self) -> UserManager:
        """
        Fetches an instance of the manager for interfacing with users in the SDK.
        """
        if not self._user_manager._internal:
            self._user_manager._internal = self.core.get_user_manager(self.core).contents

        return self._user_manager

    def get_lobby_manager(self) -> LobbyManager:
        """
        Fetches an instance of the manager for interfacing with lobbies in the SDK.
        """
        if not self._lobby_manager._internal:
            self._lobby_manager._internal = self.core.get_lobby_manager(self.core).contents

        return self._lobby_manager

    def get_network_manager(self) -> NetworkManager:
        """
        Fetches an instance of the manager for interfacing with networking in the SDK.
        """
        if not self._network_manager._internal:
            self._network_manager._internal = self.core.get_network_manager(self.core).contents

        return self._network_manager

    def get_overlay_manager(self) -> OverlayManager:
        """
        Fetches an instance of the manager for interfacing with the overlay in the SDK.
        """
        if not self._overlay_manager._internal:
            self._overlay_manager._internal = self.core.get_overlay_manager(self.core).contents

        return self._overlay_manager

    def get_application_manager(self) -> ApplicationManager:
        """
        Fetches an instance of the manager for interfacing with applications in the SDK.
        """
        if not self._application_manager._internal:
            self._application_manager._internal = self.core.get_application_manager(self.core).contents  # noqa: E501

        return self._application_manager

    def get_storage_manager(self) -> StorageManager:
        """
        Fetches an instance of the manager for interfacing with storage in the SDK.
        """
        if not self._storage_manager._internal:
            self._storage_manager._internal = self.core.get_storage_manager(self.core).contents

        return self._storage_manager

    def get_store_manager(self) -> StoreManager:
        """
        Fetches an instance of the manager for interfacing with SKUs and Entitlements in the SDK.
        """
        if not self._store_manager._internal:
            self._store_manager._internal = self.core.get_store_manager(self.core).contents

        return self._store_manager

    def get_voice_manager(self) -> VoiceManager:
        """
        Fetches an instance of the manager for interfacing with voice chat in the SDK.
        """
        if not self._voice_manager._internal:
            self._voice_manager._internal = self.core.get_voice_manager(self.core).contents

        return self._voice_manager

    def get_achievement_manager(self) -> AchievementManager:
        """
        Fetches an instance of the manager for interfacing with achievements in the SDK.
        """
        if not self._achievement_manager._internal:
            self._achievement_manager._internal = self.core.get_achievement_manager(self.core).contents  # noqa: E501

        return self._achievement_manager
