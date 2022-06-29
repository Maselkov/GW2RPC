import ctypes
import typing as t

from . import sdk
from .enum import Result
from .event import bind_events
from .exception import get_exception


class NetworkManager:
    _internal: sdk.IDiscordNetworkManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordNetworkEvents

    def __init__(self):
        self._events = bind_events(
            sdk.IDiscordNetworkEvents,
            self._on_message,
            self._on_route_update
        )

    def _on_message(self, event_data, peer_id, channel_id, data, data_length):
        data = bytes(data[:data_length])
        self.on_message(peer_id, channel_id, data)

    def _on_route_update(self, event_data, route_data):
        self.on_route_update(route_data.decode("utf8"))

    def get_peer_id(self) -> int:
        """
        Get the networking peer_id for the current user, allowing other users to send packets to
        them.
        """
        peerId = sdk.DiscordNetworkPeerId()
        self._internal.get_peer_id(self._internal, peerId)
        return peerId.value

    def flush(self) -> None:
        """
        Flushes the network.
        """
        result = Result(self._internal.flush(self._internal))
        if result != Result.ok:
            raise get_exception(result)

    def open_channel(self, peer_id: int, channel_id: int, reliable: bool) -> None:
        """
        Opens a channel to a user with their given peer_id on the given channel number.
        """
        result = Result(self._internal.open_channel(self._internal, peer_id, channel_id, reliable))
        if result != Result.ok:
            raise get_exception(result)

    def open_peer(self, peer_id: int, route: str) -> None:
        """
        Opens a network connection to another Discord user.
        """
        route_data = ctypes.create_string_buffer(route.encode("utf8"))
        result = Result(self._internal.open_peer(self._internal, peer_id, route_data))
        if result != Result.ok:
            raise get_exception(result)

    def update_peer(self, peer_id: int, route: str) -> None:
        """
        Updates the network connection to another Discord user.
        """
        route_data = ctypes.create_string_buffer(route.encode("utf8"))
        result = Result(self._internal.update_peer(self._internal, peer_id, route_data))
        if result != Result.ok:
            raise get_exception(result)

    def send_message(self, peer_id: int, channel_id: int, data: bytes) -> None:
        """
        Sends data to a given peer_id through the given channel.
        """
        data = (ctypes.c_uint8 * len(data))(*data)
        result = Result(self._internal.send_message(
            self._internal,
            peer_id,
            channel_id,
            data,
            len(data)
        ))
        if result != Result.ok:
            raise get_exception(result)

    def close_channel(self, peer_id: int, channel_id: int) -> None:
        """
        Close the connection to a given user by peer_id on the given channel.
        """
        result = Result(self._internal.close_channel(self._internal, peer_id, channel_id))
        if result != Result.ok:
            raise get_exception(result)

    def close_peer(self, peer_id: int) -> None:
        """
        Disconnects the network session to another Discord user.
        """
        result = Result(self._internal.close_peer(self._internal, peer_id))
        if result != Result.ok:
            raise get_exception(result)

    def on_message(self, peer_id: int, channel_id: int, data: bytes) -> None:
        """
        Fires when you receive data from another user.
        """

    def on_route_update(self, route: str) -> None:
        """
        Fires when your networking route has changed.
        """
