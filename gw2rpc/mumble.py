import ctypes
import json
import mmap
import time

from .settings import config

class MumbleLinkException(Exception):
    pass

class Context(ctypes.Structure):
    _fields_ = [
        ("serverAddress", ctypes.c_ubyte * 28),   # 28 bytes
        ("mapId", ctypes.c_uint32),               # 4 bytes
        ("mapType", ctypes.c_uint32),             # 4 bytes
        ("shardId", ctypes.c_uint32),             # 4 bytes
        ("instance", ctypes.c_uint32),            # 4 bytes
        ("buildId", ctypes.c_uint32),             # 4 bytes
        ("uiState", ctypes.c_uint32),             # 4 bytes
        ("compassWidth", ctypes.c_uint16),        # 2 bytes
        ("compassHeight", ctypes.c_uint16),       # 2 bytes
        ("compassRotation", ctypes.c_float),      # 4 bytes
        ("playerX", ctypes.c_float),              # 4 bytes
        ("playerY", ctypes.c_float),              # 4 bytes
        ("mapCenterX", ctypes.c_float),           # 4 bytes
        ("mapCenterY", ctypes.c_float),           # 4 bytes
        ("mapScale", ctypes.c_float),             # 4 bytes
        ("processId", ctypes.c_uint32),           # 4 bytes
        ("mountIndex", ctypes.c_uint8),           # 1 byte
    ]


# yapf:disable QA OFF
class Link(ctypes.Structure):
    _fields_ = [
        ("uiVersion", ctypes.c_uint32),           # 4 bytes
        ("uiTick", ctypes.c_ulong),               # 4 bytes
        ("fAvatarPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fAvatarFront", ctypes.c_float * 3),     # 3*4 bytes
        ("fAvatarTop", ctypes.c_float * 3),       # 3*4 bytes
        ("name", ctypes.c_wchar * 256),           # 512 bytes
        ("fCameraPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fCameraFront", ctypes.c_float * 3),     # 3*4 bytes
        ("fCameraTop", ctypes.c_float * 3),       # 3*4 bytes
        ("identity", ctypes.c_wchar * 256),       # 512 bytes
        ("context_len", ctypes.c_uint32),         # 4 bytes
        # ("context", ctypes.c_ubyte * 256),      # 256 bytes, see below
        # ("description", ctypes.c_wchar * 2048), # 4096 bytes, always empty
    ]
# yapf:enable QA ON


class MumbleData:
    def __init__(self, mumble_link="MumbleLink"):
        self.mumble_link = mumble_link
        self.memfile = None
        self.last_map_id = None
        self.last_timestamp = None
        self.last_character_name = None
        self.size_link = ctypes.sizeof(Link)
        self.size_context = ctypes.sizeof(Context)
        self.in_focus = False

    def create_map(self):
        size_discarded = 256 - self.size_context + 4096 # empty areas of context and description
        memfile_length = self.size_link + self.size_context + size_discarded
        self.memfile = mmap.mmap(-1, memfile_length, self.mumble_link)

    def close_map(self):
        if self.memfile:
            self.memfile.close()
            self.memfile = None
            self.last_map_id = None
            self.last_timestamp = None
            self.last_character_name = None

    @staticmethod
    def Unpack(ctype, buf):
        cstring = ctypes.create_string_buffer(buf)
        ctype_instance = ctypes.cast(
            ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
        return ctype_instance

    def get_mumble_data(self):
        self.memfile.seek(0)
        data = self.memfile.read(self.size_link)
        context = self.memfile.read(self.size_context)
        result = self.Unpack(Link, data)
        result_context = self.Unpack(Context, context)
        if not result.identity:
            return None
        data = json.loads(result.identity)
        data["mount_index"] = result_context.mountIndex
        uiState = str(bin(result_context.uiState))[2:].zfill(32)
        # Determines if the active instance is in focus
        self.in_focus = True if uiState[28] == "1" else False
        character = data["name"]
        map_id = data["map_id"]
        if self.last_character_name != character or self.last_map_id != map_id:
            self.last_timestamp = int(time.time())
        self.last_map_id = map_id
        self.last_character_name = character
        return data

    def get_position(self):
        self.memfile.seek(0)
        data = self.memfile.read(self.size_link)
        result = self.Unpack(Link, data)
        return Position(result.fAvatarPosition)


class Position:
    def __init__(self, position_data):
        def m_to_in(m):
            return m * 39.3700787

        self.x = m_to_in(position_data[0])
        self.y = m_to_in(position_data[2])
        self.z = position_data[1]
