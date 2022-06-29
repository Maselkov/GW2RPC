import ctypes
import typing as t

from . import sdk
from .enum import Result
from .event import bind_events
from .exception import get_exception
from .model import Entitlement, Sku


class StoreManager:
    _internal: sdk.IDiscordStoreManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordStoreEvents

    def __init__(self):
        self._garbage = []
        self._events = bind_events(
            sdk.IDiscordStoreEvents,
            self._on_entitlement_create,
            self._on_entitlement_delete
        )

    def _on_entitlement_create(self, event_data, entitlement):
        self.on_entitlement_create(Entitlement(copy=entitlement))

    def _on_entitlement_delete(self, event_data, entitlement):
        self.on_entitlement_delete(Entitlement(copy=entitlement))

    def fetch_skus(self, callback: t.Callable[[Result], None]) -> None:
        """
        Fetches the list of SKUs for the connected application, readying them for iteration.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.fetch_skus.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.fetch_skus(self._internal, ctypes.c_void_p(), c_callback)

    def count_skus(self) -> int:
        """
        Get the number of SKUs readied by FetchSkus().
        """
        count = ctypes.c_int32()
        self._internal.count_skus(self._internal, count)
        return count.value

    def get_sku(self, sku_id: int) -> Sku:
        """
        Gets a SKU by its ID.
        """
        sku = sdk.DiscordSku()

        result = Result(self._internal.get_sku(sku_id, sku))
        if result != Result.ok:
            raise get_exception(result)

        return Sku(internal=sku)

    def get_sku_at(self, index: int) -> Sku:
        """
        Gets a SKU by index when iterating over SKUs.
        """
        sku = sdk.DiscordSku()

        result = Result(self._internal.get_sku_at(index, sku))
        if result != Result.ok:
            raise get_exception(result)

        return Sku(internal=sku)

    def fetch_entitlements(self, callback: t.Callable[[Result], None]) -> None:
        """
        Fetches a list of entitlements to which the user is entitled.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.fetch_entitlements.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.fetch_entitlements(self._internal, ctypes.c_void_p(), c_callback)

    def count_entitlements(self) -> int:
        """
        Get the number of entitlements readied by FetchEntitlements().
        """
        count = ctypes.c_int32()
        self._internal.count_entitlements(self._internal, count)
        return count.value

    def get_entitlement(self, entitlement_id: int) -> Entitlement:
        """
        Gets an entitlement by its id.
        """
        entitlement = sdk.DiscordEntitlement()

        result = Result(self._internal.get_entitlement(entitlement_id, entitlement))
        if result != Result.ok:
            raise get_exception(result)

        return Entitlement(internal=Sku)

    def get_entitlement_at(self, index: int) -> Entitlement:
        """
        Gets an entitlement by index when iterating over a user's entitlements.
        """
        entitlement = sdk.DiscordEntitlement()

        result = Result(self._internal.get_entitlement_at(index, entitlement))
        if result != Result.ok:
            raise get_exception(result)

        return Entitlement(internal=Sku)

    def has_sku_entitlement(self, sku_id: int) -> bool:
        """
        Returns whether or not the user is entitled to the given SKU ID.
        """
        has_entitlement = ctypes.c_bool()

        result = Result(self._internal.has_sku_entitlement(sku_id, has_entitlement))
        if result != Result.ok:
            raise get_exception(result)

        return has_entitlement.value

    def start_purchase(self, sku_id: int, callback: t.Callable[[Result], None]) -> None:
        """
        Opens the overlay to begin the in-app purchase dialogue for the given SKU ID.

        Returns discordsdk.enum.Result (int) via callback.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.start_purchase.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.start_purchase(self._internal, sku_id, ctypes.c_void_p(), c_callback)

    def on_entitlement_create(self, entitlement: Entitlement) -> None:
        """
        Fires when the connected user receives a new entitlement, either through purchase or
        through a developer grant.
        """

    def on_entitlement_delete(self, entitlement: Entitlement) -> None:
        """
        Fires when the connected user loses an entitlement, either by expiration, revocation, or
        consumption in the case of consumable entitlements.
        """
