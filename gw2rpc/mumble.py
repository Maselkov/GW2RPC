import ctypes
import json
import mmap
import time


class MumbleLinkException(Exception):
    pass


# yapf:disable QA OFF
class Link(ctypes.Structure):
    _fields_ = [
        ("uiVersion",       ctypes.c_uint32),
        ("uiTick",          ctypes.c_ulong),
        ("fAvatarPosition", ctypes.c_float * 3),
        ("fAvatarFront",    ctypes.c_float * 3),
        ("fAvatarTop",      ctypes.c_float * 3),
        ("name",            ctypes.c_wchar * 256),
        ("fCameraPosition", ctypes.c_float * 3),
        ("fCameraFront",    ctypes.c_float * 3),
        ("fCameraTop",      ctypes.c_float * 3),
        ("identity",        ctypes.c_wchar * 256),
        ("context_len",     ctypes.c_uint32),
        ("context",         ctypes.c_uint32 * 64),
        ("description",     ctypes.c_wchar * 2048)
    ]
# yapf:enable QA ON


class MumbleData:
    def __init__(self):
        self.memfile = None
        self.last_map_id = None
        self.last_timestamp = None
        self.last_character_name = None

    def create_map(self):
        self.memfile = mmap.mmap(-1, ctypes.sizeof(Link), "MumbleLink")

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
        data = self.memfile.read(ctypes.sizeof(Link))
        result = self.Unpack(Link, data)
        if not result.identity:
            return None
        data = json.loads(result.identity)
        character = data["name"]
        map_id = data["map_id"]
        if self.last_character_name != character or self.last_map_id != map_id:
            self.last_timestamp = int(time.time())
        self.last_map_id = map_id
        self.last_character_name = character
        return data

    def get_position(self):
        self.memfile.seek(0)
        data = self.memfile.read(ctypes.sizeof(Link))
        result = self.Unpack(Link, data)
        return Position(result.fAvatarPosition)


class Position:
    def __init__(self, position_data):
        def m_to_in(m):
            return m * 39.3700787

        self.x = m_to_in(position_data[0])
        self.y = m_to_in(position_data[2])
        self.z = m_to_in(position_data[1])
