import ctypes
import json
import mmap
import psutil
import socket


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
        ("addressFamily",   ctypes.c_uint16), # contains sockaddr_in or sockaddr_in6
        ("serverPort",      ctypes.c_uint16),
        ("serverAddress",   ctypes.c_uint8 * 24),
        ("mapId",           ctypes.c_uint32),
        ("mapType",         ctypes.c_uint32),
        ("shardId",         ctypes.c_uint32),
        ("instance",        ctypes.c_uint32),
        ("buildId",         ctypes.c_uint32),
        ("context",         ctypes.c_uint8 * 208), # first 48 bytes are defined
        ("description",     ctypes.c_wchar * 2048)
    ]
# yapf:enable QA ON


class MumbleData:
    def __init__(self):
        self.memfile = mmap.mmap(-1, ctypes.sizeof(Link), "MumbleLink")
        self.last_character = None
        self.last_map_id = None
        self.last_server_ip = None

    @staticmethod
    def Unpack(ctype, buf):
        cstring = ctypes.create_string_buffer(buf)
        ctype_instance = ctypes.cast(
            ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
        return ctype_instance

    def get_mumble_data(self, process=None):
        self.memfile.seek(0)
        data = self.memfile.read(ctypes.sizeof(Link))
        result = self.Unpack(Link, data)
        if result.name != "Guild Wars 2":
            return None
        if not result.identity:
            return None
        if result.addressFamily == socket.AF_INET:
            self.last_server_ip = socket.inet_ntop(socket.AF_INET, bytearray(result.serverAddress[0:4]))
        elif result.addressFamily == socket.AF_INET6:
            self.last_server_ip = socket.inet_ntop(socket.AF_INET6, bytearray(result.serverAddress[4:20]))
        else:
            self.last_server_ip = None
        if process and self.last_server_ip:
            try:
                have_connection = False
                for conn in process.connections():
                    if conn.status == 'ESTABLISHED' and conn.raddr.ip == self.last_server_ip:
                        have_connection = True
                        break
                if not have_connection:
                    return None
            except:
                pass
        data = json.loads(result.identity)
        character = data["name"]
        map_id = data["map_id"]
        if character == self.last_character and map_id == self.last_map_id:
            raise DataUnchangedError
        self.last_character = character
        self.last_map_id = map_id
        return data
