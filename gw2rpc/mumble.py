import ctypes
import json
import mmap


class MumbleLinkException(Exception):
    pass


class DataUnchangedError(MumbleLinkException):
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
        self.memfile = mmap.mmap(-1, ctypes.sizeof(Link), "MumbleLink")
        self.last_character = None
        self.last_map_id = None

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
        if character == self.last_character and map_id == self.last_map_id:
            raise DataUnchangedError
        self.last_character = character
        self.last_map_id = map_id
        return data
