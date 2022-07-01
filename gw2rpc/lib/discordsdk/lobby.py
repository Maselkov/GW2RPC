import ctypes
import typing as t

from . import sdk
from .enum import (
    LobbySearchCast, LobbySearchComparison, LobbySearchDistance, LobbyType,
    Result)
from .event import bind_events
from .exception import get_exception
from .model import Lobby, User


class LobbyTransaction:
    _internal: sdk.IDiscordLobbyTransaction

    def __init__(self, internal: sdk.IDiscordLobbyTransaction):
        self._internal = internal

    def set_type(self, type: LobbyType) -> None:
        """
        Marks a lobby as private or public.
        """
        result = Result(self._internal.set_type(self._internal, type))
        if result != Result.ok:
            raise get_exception(result)

    def set_owner(self, user_id: int) -> None:
        """
        Sets a new owner for the lobby.
        """
        result = Result(self._internal.set_owner(self._internal, user_id))
        if result != Result.ok:
            raise get_exception(result)

    def set_capacity(self, capacity: int) -> None:
        """
        Sets a new capacity for the lobby.
        """
        result = Result(self._internal.set_capacity(self._internal, capacity))
        if result != Result.ok:
            raise get_exception(result)

    def set_metadata(self, key: str, value: str) -> None:
        """
        Sets metadata value under a given key name for the lobby.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        metadata_value = sdk.DiscordMetadataValue()
        metadata_value.value = value.encode("utf8")

        result = Result(self._internal.set_metadata(self._internal, metadata_key, metadata_value))
        if result != Result.ok:
            raise get_exception(result)

    def delete_metadata(self, key: str) -> None:
        """
        Deletes the lobby metadata for a key.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        result = Result(self._internal.delete_metadata(self._internal, metadata_key))
        if result != Result.ok:
            raise get_exception(result)

    def set_locked(self, locked: bool) -> None:
        """
        Sets the lobby to locked or unlocked.
        """
        result = Result(self._internal.set_locked(self._internal, locked))
        if result != Result.ok:
            raise get_exception(result)


class LobbyMemberTransaction:
    _internal: sdk.IDiscordLobbyMemberTransaction

    def __init__(self, internal: sdk.IDiscordLobbyMemberTransaction):
        self._internal = internal

    def set_metadata(self, key: str, value: str) -> None:
        """
        Sets metadata value under a given key name for the current user.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        metadata_value = sdk.DiscordMetadataValue()
        metadata_value.value = value.encode("utf8")

        result = Result(self._internal.set_metadata(self._internal, metadata_key, metadata_value))
        if result != Result.ok:
            raise get_exception(result)

    def delete_metadata(self, key: str) -> None:
        """
        Sets metadata value under a given key name for the current user.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        result = Result(self._internal.delete_metadata(self._internal, metadata_key))
        if result != Result.ok:
            raise get_exception(result)


class LobbySearchQuery:
    _internal: sdk.IDiscordLobbySearchQuery

    def __init__(self, internal: sdk.IDiscordLobbySearchQuery):
        self._internal = internal

    def filter(
        self,
        key: str,
        comp: LobbySearchComparison,
        cast: LobbySearchCast,
        value: str
    ) -> None:
        """
        Filters lobbies based on metadata comparison.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        metadata_value = sdk.DiscordMetadataValue()
        metadata_value.value = value.encode("utf8")

        result = Result(self._internal.filter(
            self._internal,
            metadata_key,
            comp,
            cast,
            metadata_value
        ))
        if result != Result.ok:
            raise get_exception(result)

    def sort(self, key: str, cast: LobbySearchCast, value: str) -> None:
        """
        Sorts the filtered lobbies based on "near-ness" to a given value.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        metadata_value = sdk.DiscordMetadataValue()
        metadata_value.value = value.encode("utf8")

        result = Result(self._internal.sort(self._internal, metadata_key, cast, metadata_value))
        if result != Result.ok:
            raise get_exception(result)

    def limit(self, limit: int) -> None:
        """
        Limits the number of lobbies returned in a search.
        """
        result = Result(self._internal.limit(self._internal, limit))
        if result != Result.ok:
            raise get_exception(result)

    def distance(self, distance: LobbySearchDistance) -> None:
        """
        Filters lobby results to within certain regions relative to the user's location.
        """
        result = Result(self._internal.distance(self._internal, distance))
        if result != Result.ok:
            raise get_exception(result)


class LobbyManager:
    _internal: sdk.IDiscordLobbyManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordLobbyEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordLobbyEvents,
            self._on_lobby_update,
            self._on_lobby_delete,
            self._on_member_connect,
            self._on_member_update,
            self._on_member_disconnect,
            self._on_lobby_message,
            self._on_speaking,
            self._on_network_message
        )

    def _on_lobby_update(self, event_data, lobby_id):
        self.on_lobby_update(lobby_id)

    def _on_lobby_delete(self, event_data, lobby_id, reason):
        self.on_lobby_delete(lobby_id, reason)

    def _on_member_connect(self, event_data, lobby_id, user_id):
        self.on_member_connect(lobby_id, user_id)

    def _on_member_update(self, event_data, lobby_id, user_id):
        self.on_member_update(lobby_id, user_id)

    def _on_member_disconnect(self, event_data, lobby_id, user_id):
        self.on_member_disconnect(lobby_id, user_id)

    def _on_lobby_message(self, event_data, lobby_id, user_id, data, data_length):
        message = bytes(data[:data_length]).decode("utf8")
        self.on_lobby_message(lobby_id, user_id, message)

    def _on_speaking(self, event_data, lobby_id, user_id, speaking):
        self.on_speaking(lobby_id, user_id, speaking)

    def _on_network_message(self, event_data, lobby_id, user_id, channel_id, data, data_length):
        data = bytes(data[:data_length])
        self.on_network_message(lobby_id, user_id, channel_id, data)

    def get_lobby_create_transaction(self) -> LobbyTransaction:
        """
        Gets a Lobby transaction used for creating a new lobby
        """
        transaction = ctypes.POINTER(sdk.IDiscordLobbyTransaction)()
        result = Result(self._internal.get_lobby_create_transaction(self._internal, transaction))
        if result != Result.ok:
            raise get_exception(result)

        return LobbyTransaction(internal=transaction.contents)

    def get_lobby_update_transaction(self, lobby_id: int) -> LobbyTransaction:
        """
        Gets a lobby transaction used for updating an existing lobby.
        """
        transaction = ctypes.POINTER(sdk.IDiscordLobbyTransaction)()
        result = Result(self._internal.get_lobby_update_transaction(
            self._internal,
            lobby_id,
            transaction
        ))
        if result != Result.ok:
            raise get_exception(result)

        return LobbyTransaction(internal=transaction.contents)

    def get_member_update_transaction(self, lobby_id: int, user_id: int) -> LobbyMemberTransaction:
        """
        Gets a new member transaction for a lobby member in a given lobby.
        """
        transaction = ctypes.POINTER(sdk.IDiscordLobbyMemberTransaction)()
        result = Result(self._internal.get_member_update_transaction(
            self._internal, lobby_id, user_id, transaction))
        if result != Result.ok:
            raise get_exception(result)

        return LobbyMemberTransaction(internal=transaction.contents)

    def create_lobby(
        self,
        transaction: LobbyTransaction,
        callback: t.Callable[[Result, t.Optional[Lobby]], None]
    ) -> None:
        """
        Creates a lobby.

        Returns discordsdk.enum.Result (int) and Lobby via callback.
        """
        def c_callback(callback_data, result, lobby):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                callback(result, Lobby(copy=lobby.contents))
            else:
                callback(result, None)

        c_callback = self._internal.create_lobby.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.create_lobby(
            self._internal,
            transaction._internal,
            ctypes.c_void_p(),
            c_callback
        )

    def update_lobby(
        self,
        lobby_id: int,
        transaction: LobbyTransaction,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Updates a lobby with data from the given transaction.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.update_lobby.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.update_lobby(
            self._internal,
            lobby_id,
            transaction._internal,
            ctypes.c_void_p(),
            c_callback
        )

    def delete_lobby(self, lobby_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Deletes a given lobby.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.delete_lobby.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.delete_lobby(self._internal, lobby_id, ctypes.c_void_p(), c_callback)

    def connect_lobby(
        self,
        lobby_id: int,
        lobby_secret: str,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Connects the current user to a given lobby.
        """
        def c_callback(callback_data, result, lobby):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                callback(result, Lobby(copy=lobby.contents))
            else:
                callback(result, None)

        c_callback = self._internal.connect_lobby.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        _lobby_secret = sdk.DiscordLobbySecret()
        _lobby_secret.value = lobby_secret.encode("utf8")

        self._internal.connect_lobby(
            self._internal,
            lobby_id,
            _lobby_secret,
            ctypes.c_void_p(),
            c_callback
        )

    def connect_lobby_with_activity_secret(
        self,
        activity_secret: str,
        callback: t.Callable[[Result, t.Optional[Lobby]], None]
    ) -> None:
        """
        Connects the current user to a lobby; requires the special activity secret from the lobby
        which is a concatenated lobby_id and secret.
        """
        def c_callback(callback_data, result, lobby):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                callback(result, Lobby(copy=lobby.contents))
            else:
                callback(result, None)

        c_callback = self._internal.connect_lobby_with_activity_secret.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        _activity_secret = sdk.DiscordLobbySecret()
        _activity_secret.value = activity_secret.encode("utf8")

        self._internal.connect_lobby_with_activity_secret(
            self._internal,
            _activity_secret,
            ctypes.c_void_p(),
            c_callback
        )

    def get_lobby_activity_secret(self, lobby_id: int) -> str:
        """
        Gets the special activity secret for a given lobby.
        """
        lobby_secret = sdk.DiscordLobbySecret()

        result = self._internal.get_lobby_activity_secret(self._internal, lobby_id, lobby_secret)
        if result != Result.ok:
            raise get_exception(result)

        return lobby_secret.value.decode("utf8")

    def disconnect_lobby(self, lobby_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Disconnects the current user from a lobby.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.disconnect_lobby.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.disconnect_lobby(self._internal, lobby_id, ctypes.c_void_p(), c_callback)

    def get_lobby(self, lobby_id: int) -> Lobby:
        """
        Gets the lobby object for a given lobby id.
        """
        lobby = sdk.DiscordLobby()

        result = Result(self._internal.get_lobby(self._internal, lobby_id, lobby))
        if result != Result.ok:
            raise get_exception(result)

        return Lobby(internal=lobby)

    def lobby_metadata_count(self, lobby_id: int) -> int:
        """
        Returns the number of metadata key/value pairs on a given lobby.
        """
        count = ctypes.c_int32()

        result = Result(self._internal.lobby_metadata_count(self._internal, lobby_id, count))
        if result != Result.ok:
            raise get_exception(result)

        return count.value

    def get_lobby_metadata_key(self, lobby_id: int, index: int) -> str:
        """
        Returns the key for the lobby metadata at the given index.
        """
        metadata_key = sdk.DiscordMetadataKey()

        result = Result(self._internal.get_lobby_metadata_key(
            self._internal,
            lobby_id,
            index,
            metadata_key
        ))
        if result != Result.ok:
            raise get_exception(result)

        return metadata_key.value.decode("utf8")

    def get_lobby_metadata_value(self, lobby_id: int, key: str) -> str:
        """
        Returns lobby metadata value for a given key and id.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        metadata_value = sdk.DiscordMetadataValue()

        result = Result(self._internal.get_lobby_metadata_value(
            self._internal,
            lobby_id,
            metadata_key,
            metadata_value
        ))
        if result != Result.ok:
            raise get_exception(result)

        return metadata_value.value.decode("utf8")

    def member_count(self, lobby_id: int) -> int:
        """
        Get the number of members in a lobby.
        """
        count = ctypes.c_int32()

        result = Result(self._internal.member_count(self._internal, lobby_id, count))
        if result != Result.ok:
            raise get_exception(result)

        return count.value

    def get_member_user_id(self, lobby_id: int, index: int) -> int:
        """
        Gets the user id of the lobby member at the given index.
        """
        user_id = sdk.DiscordUserId()

        result = Result(self._internal.get_member_user_id(self._internal, lobby_id, index, user_id))
        if result != Result.ok:
            raise get_exception(result)

        return user_id.value

    def get_member_user(self, lobby_id: int, user_id: int) -> User:
        """
        Gets the user object for a given user id.
        """
        user = sdk.DiscordUser()

        result = Result(self._internal.get_member_user(self._internal, lobby_id, user_id, user))
        if result != Result.ok:
            raise get_exception(result)

        return User(internal=user)

    def member_metadata_count(self, lobby_id: int, user_id: int) -> int:
        """
        Gets the number of metadata key/value pairs for the given lobby member.
        """
        count = ctypes.c_int32()

        result = Result(self._internal.member_metadata_count(
            self._internal,
            lobby_id,
            user_id,
            count
        ))
        if result != Result.ok:
            raise get_exception(result)

        return count.value

    def get_member_metadata_key(self, lobby_id: int, user_id: int, index: int) -> str:
        """
        Gets the key for the lobby metadata at the given index on a lobby member.
        """
        metadata_key = sdk.DiscordMetadataKey()

        result = Result(self._internal.get_member_metadata_key(
            self._internal,
            lobby_id,
            user_id,
            index,
            metadata_key
        ))
        if result != Result.ok:
            raise get_exception(result)

        return metadata_key.value.decode("utf8")

    def get_member_metadata_value(self, lobby_id: int, user_id: int, key: str) -> str:
        """
        Returns user metadata for a given key.
        """
        metadata_key = sdk.DiscordMetadataKey()
        metadata_key.value = key.encode("utf8")

        metadata_value = sdk.DiscordMetadataValue()

        result = Result(self._internal.get_member_metadata_value(
            self._internal,
            lobby_id,
            user_id,
            metadata_key,
            metadata_value
        ))
        if result != Result.ok:
            raise get_exception(result)

        return metadata_value.value.decode("utf8")

    def update_member(
        self,
        lobby_id: int,
        user_id: int,
        transaction: LobbyMemberTransaction,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Updates lobby member info for a given member of the lobby.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.update_member.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.update_member(
            self._internal,
            lobby_id,
            user_id,
            transaction._internal,
            ctypes.c_void_p(),
            c_callback
        )

    def send_lobby_message(
        self,
        lobby_id: int,
        data: str,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Sends a message to the lobby on behalf of the current user.

        Returns discordsdk.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.send_lobby_message.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        data = data.encode("utf8")
        data = (ctypes.c_uint8 * len(data))(*data)
        self._internal.send_lobby_message(
            self._internal, lobby_id, data, len(data), ctypes.c_void_p(), c_callback)

    def get_search_query(self) -> LobbySearchQuery:
        """
        Creates a search object to search available lobbies.
        """
        search_query = (ctypes.POINTER(sdk.IDiscordLobbySearchQuery))()
        result = Result(self._internal.get_search_query(self._internal, ctypes.byref(search_query)))
        if result != Result.ok:
            raise get_exception(result)

        return LobbySearchQuery(internal=search_query.contents)

    def search(self, search: LobbySearchQuery, callback: t.Callable[[Result], None]) -> None:
        """
        Searches available lobbies based on the search criteria chosen in the LobbySearchQuery
        member functions.

        Lobbies that meet the criteria are then globally filtered, and can be accessed via
        iteration with lobby_count() and get_lobby_id(). The callback fires when the list of lobbies
        is stable and ready for iteration.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.search.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.search(self._internal, search._internal, ctypes.c_void_p(), c_callback)

    def lobby_count(self) -> int:
        """
        Get the number of lobbies that match the search.
        """
        count = ctypes.c_int32()
        self._internal.lobby_count(self._internal, count)
        return count.value

    def get_lobby_id(self, index: int) -> int:
        """
        Returns the id for the lobby at the given index.
        """

        lobby_id = sdk.DiscordLobbyId()

        result = Result(self._internal.get_lobby_id(self._internal, index, lobby_id))
        if result != Result.ok:
            raise get_exception(result)

        return lobby_id.value

    def connect_voice(self, lobby_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Connects to the voice channel of the current lobby.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.connect_voice.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.connect_voice(self._internal, lobby_id, ctypes.c_void_p(), c_callback)

    def disconnect_voice(self, lobby_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Disconnects from the voice channel of a given lobby.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.disconnect_voice.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.disconnect_voice(self._internal, lobby_id, ctypes.c_void_p(), c_callback)

    def on_lobby_update(self, lobby_id: int) -> None:
        """
        Fires when a lobby is updated.
        """

    def on_lobby_delete(self, lobby_id: int, reason: str) -> None:
        """
        Fired when a lobby is deleted.
        """

    def on_member_connect(self, lobby_id: int, user_id: int) -> None:
        """
        Fires when a new member joins the lobby.
        """

    def on_member_update(self, lobby_id: int, user_id: int) -> None:
        """
        Fires when data for a lobby member is updated.
        """

    def on_member_disconnect(self, lobby_id: int, user_id: int) -> None:
        """
        Fires when a member leaves the lobby.
        """

    def on_lobby_message(self, lobby_id: int, user_id: int, message: str) -> None:
        """
        Fires when a message is sent to the lobby.
        """

    def on_speaking(self, lobby_id: int, user_id: int, speaking: bool) -> None:
        """
        Fires when a user connected to voice starts or stops speaking.
        """

    def connect_network(self, lobby_id: int) -> None:
        """
        Connects to the networking layer for the given lobby ID.
        """
        result = Result(self._internal.connect_network(self._internal, lobby_id))
        if result != Result.ok:
            raise get_exception(result)

    def disconnect_network(self, lobby_id: int) -> None:
        """
        Disconnects from the networking layer for the given lobby ID.
        """
        result = Result(self._internal.disconnect_network(self._internal, lobby_id))
        if result != Result.ok:
            raise get_exception(result)

    def flush_network(self) -> None:
        """
        Flushes the network. Call this when you're done sending messages.
        """
        result = Result(self._internal.flush_network(self._internal))
        if result != Result.ok:
            raise get_exception(result)

    def open_network_channel(self, lobby_id: int, channel_id: int, reliable: bool) -> None:
        """
        Opens a network channel to all users in a lobby on the given channel number. No need to
        iterate over everyone!
        """
        result = Result(self._internal.open_network_channel(
            self._internal,
            lobby_id,
            channel_id,
            reliable
        ))
        if result != Result.ok:
            raise get_exception(result)

    def send_network_message(
        self,
        lobby_id: int,
        user_id: int,
        channel_id: int,
        data: bytes
    ) -> None:
        """
        Sends a network message to the given user ID that is a member of the given lobby ID over
        the given channel ID.
        """
        data = (ctypes.c_uint8 * len(data))(*data)
        result = Result(self._internal.send_network_message(
            self._internal,
            lobby_id,
            user_id,
            channel_id,
            data,
            len(data)
        ))
        if result != Result.ok:
            raise get_exception(result)

    def on_network_message(self, lobby_id: int, user_id: int, channel_id: int, data: bytes) -> None:
        """
        Fires when the user receives a message from the lobby's networking layer.
        """
