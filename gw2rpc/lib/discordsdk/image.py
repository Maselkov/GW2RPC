import ctypes
import typing as t

from . import sdk
from .enum import Result
from .exception import get_exception
from .model import ImageDimensions, ImageHandle


class ImageManager:
    _internal: sdk.IDiscordImageManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordImageEvents = None

    def __init__(self):
        self._garbage = []

    def fetch(
        self,
        handle: ImageHandle,
        refresh: bool,
        callback: t.Callable[[Result, t.Optional[ImageHandle]], None]
    ) -> None:
        """
        Prepares an image to later retrieve data about it.

        Returns discordsdk.enum.Result (int) and ImageHandle via callback.
        """
        def c_callback(callback_data, result, handle):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                callback(result, ImageHandle(internal=handle))
            else:
                callback(result, None)

        c_callback = self._internal.fetch.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        self._internal.fetch(
            self._internal,
            handle._internal,
            refresh,
            ctypes.c_void_p(),
            c_callback
        )

    def get_dimensions(self, handle: ImageHandle) -> ImageDimensions:
        """
        Gets the dimension for the given user's avatar's source image
        """
        dimensions = sdk.DiscordImageDimensions()
        result = Result(self._internal.get_dimensions(self._internal, handle._internal, dimensions))
        if result != Result.ok:
            raise get_exception(result)

        return ImageDimensions(internal=dimensions)

    def get_data(self, handle: ImageHandle) -> bytes:
        """
        Gets the image data for a given user's avatar.
        """
        dimensions = self.get_dimensions(handle)
        buffer = (ctypes.c_uint8 * (dimensions.width * dimensions.height * 4))()

        result = Result(self._internal.get_data(
            self._internal, handle._internal, buffer, len(buffer)))
        if result != Result.ok:
            raise get_exception(result)

        return bytes(buffer)
