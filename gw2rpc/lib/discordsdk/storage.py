import ctypes
import typing as t

from . import sdk
from .enum import Result
from .exception import get_exception
from .model import FileStat


class StorageManager:
    _internal: sdk.IDiscordStorageManager = None
    _garbage: t.List[t.Any]
    _events: sdk.IDiscordStorageEvents = None

    def __init__(self):
        self._garbage = []

    def get_path(self) -> str:
        """
        Returns the filepath to which Discord saves files if you were to use the SDK's storage
        manager.
        """
        path = sdk.DiscordPath()

        result = Result(self._internal.get_path(self._internal, path))
        if result != Result.ok:
            raise get_exception(result)

        return path.value.decode("utf8")

    def read(self, name: str) -> bytes:
        """
        Reads data synchronously from the game's allocated save file.
        """
        # we need the file stat for this one, as length-fixed buffers does not exist in python
        file_stat = self.stat(name)
        file_size = file_stat.Size

        name = ctypes.c_char_p(name.encode("utf8"))
        buffer = (ctypes.c_uint8 * file_size)()
        read = ctypes.c_uint32()

        result = Result(self._internal.read(self._internal, name, buffer, len(buffer), read))
        if result != Result.ok:
            raise get_exception(result)

        if read.value != file_size:
            print("discord/storage.py: warning: attempting to read " +
                  str(file_size) + " bytes, but read " + str(read.value))

        return bytes(buffer[:read.value])

    def read_async(
        self,
        name: str,
        callback: t.Callable[[Result, t.Optional[bytes]], None]
    ) -> None:
        """
        Reads data asynchronously from the game's allocated save file.

        Returns discordsdk.enum.Result (int) and data (bytes) via callback.
        """
        def c_callback(callback_data, result, data, data_length):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                data = bytes(data[:data_length])
                callback(result, data)
            else:
                callback(result, None)

        c_callback = self._internal.read_async.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        name = ctypes.c_char_p(name.encode("utf8"))
        self._internal.read_async(self._internal, name, ctypes.c_void_p(), c_callback)

    def read_async_partial(
        self,
        name: str,
        offset: int,
        length: int,
        callback: t.Callable[[Result], None]
    ) -> None:
        """
        Reads data asynchronously from the game's allocated save file, starting at a given offset
        and up to a given length.
        """
        def c_callback(callback_data, result, data, data_length):
            self._garbage.remove(c_callback)
            result = Result(result)
            if result == Result.ok:
                data = bytes(data[:data_length])
                callback(result, data)
            else:
                callback(result, None)

        c_callback = self._internal.read_async.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        name = ctypes.c_char_p(name.encode("utf8"))
        self._internal.read_async_partial(
            self._internal,
            name,
            offset,
            length,
            ctypes.c_void_p(),
            c_callback
        )

    def write(self, name: str, data: bytes) -> None:
        """
        Writes data synchronously to disk, under the given key name.
        """
        name = ctypes.c_char_p(name.encode("utf8"))
        data = (ctypes.c_uint8 * len(data))(*data)

        result = Result(self._internal.write(self._internal, name, data, len(data)))
        if result != Result.ok:
            raise get_exception(result)

    def write_async(self, name: str, data: bytes, callback: t.Callable[[Result], None]) -> None:
        """
        Writes data asynchronously to disk under the given keyname.
        """
        def c_callback(callback_data, result):
            self._garbage.remove(c_callback)
            result = Result(result)
            callback(result)

        c_callback = self._internal.write_async.argtypes[-1](c_callback)
        self._garbage.append(c_callback)  # prevent it from being garbage collected

        name = ctypes.c_char_p(name.encode("utf8"))
        data = (ctypes.c_uint8 * len(data))(*data)

        self._internal.write_async(
            self._internal,
            name,
            data,
            len(data),
            ctypes.c_void_p(),
            c_callback
        )

    def delete(self, name: str) -> None:
        """
        Deletes written data for the given key name.
        """
        name = ctypes.c_char_p(name.encode("utf8"))

        result = Result(self._internal.delete_(self._internal, name))
        if result != Result.ok:
            raise get_exception(result)

    def exists(self, name: str) -> bool:
        """
        Checks if data exists for a given key name.
        """
        exists = ctypes.c_bool()
        name = ctypes.c_char_p(name.encode("utf8"))

        result = Result(self._internal.exists(self._internal, name, exists))
        if result != Result.ok:
            raise get_exception(result)

        return exists.value

    def stat(self, name: str) -> FileStat:
        """
        Returns file info for the given key name.
        """
        stat = sdk.DiscordFileStat()

        name = ctypes.c_char_p(name.encode("utf8"))
        result = Result(self._internal.stat(self._internal, name, stat))
        if result != Result.ok:
            raise get_exception(result)

        return FileStat(internal=stat)

    def count(self) -> int:
        """
        Returns the count of files, for iteration.
        """
        count = ctypes.c_int32()
        self._internal.count(self._internal, count)
        return count.value

    def stat_at(self, index: int) -> FileStat:
        """
        Returns file info for the given index when iterating over files.
        """
        stat = sdk.DiscordFileStat()

        result = Result(self._internal.stat_at(self._internal, index, stat))
        if result != Result.ok:
            raise get_exception(result)

        return FileStat(internal=stat)
