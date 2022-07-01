import ctypes
import os.path
import sys
import typing as t

import sys as _sys

if "sphinx" in _sys.modules:
    setattr(_sys, "is_dsdk_doc_run", True)
_is_dsdk_doc_run = hasattr(_sys, "is_dsdk_doc_run") and _sys.is_dsdk_doc_run

if not _is_dsdk_doc_run:
    try:
        if sys.platform == "darwin":
            dll = ctypes.CDLL(os.path.abspath("lib/discord_game_sdk.dylib"))
        elif sys.platform == "linux":
            dll = ctypes.CDLL(os.path.abspath("lib/discord_game_sdk.so"))
        else:
            ctypes.windll.kernel32.SetDllDirectoryW(None)
            #dll = ctypes.CDLL(os.path.abspath("lib/discord_game_sdk"))
            dll = ctypes.CDLL('discord_game_sdk.dll')
    except FileNotFoundError:
        raise FileNotFoundError("Could not locate Discord's SDK DLLs. Check that they are in the /lib directory relative to the folder that the program is executed from.")  # noqa: E501

    DiscordCreate = dll.DiscordCreate

DiscordClientId = ctypes.c_int64
DiscordVersion = ctypes.c_int32
DiscordSnowflake = ctypes.c_int64
DiscordTimestamp = ctypes.c_int64
DiscordUserId = DiscordSnowflake
DiscordLocale = ctypes.c_char * 128
DiscordBranch = ctypes.c_char * 4096
DiscordLobbyId = DiscordSnowflake
DiscordLobbySecret = ctypes.c_char * 128
DiscordMetadataKey = ctypes.c_char * 256
DiscordMetadataValue = ctypes.c_char * 4096
DiscordNetworkPeerId = ctypes.c_uint64
DiscordNetworkChannelId = ctypes.c_uint8
DiscordPath = ctypes.c_char * 4096
DiscordDateTime = ctypes.c_char * 64


class DiscordUser(ctypes.Structure):
    _fields_ = [
        ("id", DiscordUserId),
        ("username", ctypes.c_char * 256),
        ("discriminator", ctypes.c_char * 8),
        ("avatar", ctypes.c_char * 128),
        ("bot", ctypes.c_bool),
    ]


class DiscordOAuth2Token(ctypes.Structure):
    _fields_ = [
        ("access_token", ctypes.c_char * 128),
        ("scopes", ctypes.c_char * 1024),
        ("expires", DiscordTimestamp),
    ]


class DiscordImageHandle(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int32),
        ("id", ctypes.c_int64),
        ("size", ctypes.c_uint32),
    ]


class DiscordImageDimensions(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
    ]


class DiscordActivityTimestamps(ctypes.Structure):
    _fields_ = [
        ("start", DiscordTimestamp),
        ("end", DiscordTimestamp),
    ]


class DiscordActivityAssets(ctypes.Structure):
    _fields_ = [
        ("large_image", ctypes.c_char * 128),
        ("large_text", ctypes.c_char * 128),
        ("small_image", ctypes.c_char * 128),
        ("small_text", ctypes.c_char * 128),
    ]


class DiscordPartySize(ctypes.Structure):
    _fields_ = [
        ("current_size", ctypes.c_int32),
        ("max_size", ctypes.c_int32),
    ]


class DiscordActivityParty(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 128),
        ("size", DiscordPartySize),
    ]


class DiscordActivitySecrets(ctypes.Structure):
    _fields_ = [
        ("match", ctypes.c_char * 128),
        ("join", ctypes.c_char * 128),
        ("spectate", ctypes.c_char * 128),
    ]


class DiscordActivity(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int32),
        ("application_id", ctypes.c_uint64),
        ("name", ctypes.c_char * 128),
        ("state", ctypes.c_char * 128),
        ("details", ctypes.c_char * 128),
        ("timestamps", DiscordActivityTimestamps),
        ("assets", DiscordActivityAssets),
        ("party", DiscordActivityParty),
        ("secrets", DiscordActivitySecrets),
        ("instance", ctypes.c_bool),
    ]


class DiscordPresence(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int32),
        ("activity", DiscordActivity),
    ]


class DiscordRelationship(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int32),
        ("user", DiscordUser),
        ("presence", DiscordPresence),
    ]


class DiscordLobby(ctypes.Structure):
    _fields_ = [
        ("id", DiscordLobbyId),
        ("type", ctypes.c_int32),
        ("owner_id", DiscordUserId),
        ("secret", DiscordLobbySecret),
        ("capacity", ctypes.c_uint32),
        ("locked", ctypes.c_bool),
    ]


# SDK VERSION 2.5.7+ STUFF
"""
class DiscordImeUnderline(ctypes.Structure):
    _fields_ = [
        ("from", ctypes.c_int32),
        ("to", ctypes.c_int32),
        ("color", ctypes.c_int32),
        ("background_color", ctypes.c_uint32),
        ("thick", ctypes.c_bool),
    ]

class DiscordRect(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_int32),
        ("top", ctypes.c_int32),
        ("right", ctypes.c_int32),
        ("bottom", ctypes.c_int32),
    ]
"""


class DiscordFileStat(ctypes.Structure):
    _fields_ = [
        ("filename", ctypes.c_char * 260),
        ("size", ctypes.c_uint64),
        ("last_modified", ctypes.c_uint64),
    ]


class DiscordEntitlement(ctypes.Structure):
    _fields_ = [
        ("id", DiscordSnowflake),
        ("type", ctypes.c_int32),
        ("sku_id", DiscordSnowflake),
    ]


class DiscordSkuPrice(ctypes.Structure):
    _fields_ = [
        ("amount", ctypes.c_uint32),
        ("currency", ctypes.c_char * 16),
    ]


class DiscordSku(ctypes.Structure):
    _fields_ = [
        ("id", DiscordSnowflake),
        ("type", ctypes.c_int32),
        ("name", ctypes.c_char * 256),
        ("price", DiscordSkuPrice),
    ]


class DiscordInputMode(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int32),
        ("shortcut", ctypes.c_char * 256),
    ]


class DiscordUserAchievement(ctypes.Structure):
    _fields_ = [
        ("user_id", DiscordSnowflake),
        ("achievement_id", DiscordSnowflake),
        ("percent_complete", ctypes.c_uint8),
        ("unlocked_at", DiscordDateTime),
    ]


class IDiscordLobbyTransaction(ctypes.Structure):
    pass


IDiscordLobbyTransaction._fields_ = [
    ("set_type", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyTransaction),
        ctypes.c_int32
    )),
    ("set_owner", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyTransaction),
        DiscordUserId
    )),
    ("set_capacity", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyTransaction),
        ctypes.c_uint32
    )),
    ("set_metadata", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyTransaction),
        DiscordMetadataKey,
        DiscordMetadataValue
    )),
    ("delete_metadata", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyTransaction),
        DiscordMetadataKey
    )),
    ("set_locked", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyTransaction),
        ctypes.c_bool
    )),
]


class IDiscordLobbyMemberTransaction(ctypes.Structure):
    pass


IDiscordLobbyMemberTransaction._fields_ = [
    ("set_metadata", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyMemberTransaction),
        DiscordMetadataKey, DiscordMetadataValue
    )),
    ("delete_metadata", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyMemberTransaction),
        DiscordMetadataKey
    )),
]


class IDiscordLobbySearchQuery(ctypes.Structure):
    pass


IDiscordLobbySearchQuery._fields_ = [
    ("filter", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbySearchQuery),
        DiscordMetadataKey,
        ctypes.c_int32,
        ctypes.c_int32,
        DiscordMetadataValue
    )),
    ("sort", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbySearchQuery),
        DiscordMetadataKey,
        ctypes.c_int32,
        DiscordMetadataValue
    )),
    ("limit", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbySearchQuery),
        ctypes.c_uint32
    )),
    ("distance", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbySearchQuery),
        ctypes.c_int32
    )),
]

IDiscordApplicationEvents = ctypes.c_void_p


class IDiscordApplicationManager(ctypes.Structure):
    pass


IDiscordApplicationManager._fields_ = [
    ("validate_or_exit", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordApplicationManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("get_current_locale", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordApplicationManager),
        ctypes.POINTER(DiscordLocale)
    )),
    ("get_current_branch", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordApplicationManager),
        ctypes.POINTER(DiscordBranch)
    )),
    ("get_oauth2_token", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordApplicationManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(DiscordOAuth2Token)
        )
    )),
    ("get_ticket", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordApplicationManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.c_char_p
        )
    )),
]


class IDiscordUserEvents(ctypes.Structure):
    _fields_ = [
        ("on_current_user_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p
        )),
    ]


class IDiscordUserManager(ctypes.Structure):
    pass


IDiscordUserManager._fields_ = [
    ("get_current_user", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordUserManager),
        ctypes.POINTER(DiscordUser)
    )),
    ("get_user", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordUserManager),
        DiscordUserId,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(DiscordUser)
        )
    )),
    ("get_current_user_premium_type", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordUserManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("current_user_has_flag", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordUserManager),
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_bool)
    )),
]

IDiscordImageEvents = ctypes.c_void_p


class IDiscordImageManager(ctypes.Structure):
    pass


IDiscordImageManager._fields_ = [
    ("fetch", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordImageManager),
        DiscordImageHandle,
        ctypes.c_bool,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            DiscordImageHandle
        )
    )),
    ("get_dimensions", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordImageManager),
        DiscordImageHandle,
        ctypes.POINTER(DiscordImageDimensions)
    )),
    ("get_data", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordImageManager),
        DiscordImageHandle,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )),
]


class IDiscordActivityEvents(ctypes.Structure):
    _fields_ = [
        ("on_activity_join", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_char_p
        )),
        ("on_activity_spectate", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_char_p
        )),
        ("on_activity_join_request", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.POINTER(DiscordUser)
        )),
        ("on_activity_invite", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(DiscordUser),
            ctypes.POINTER(DiscordActivity)
        )),
    ]

    on_activity_join: t.Callable[..., None]
    on_activity_spectate: t.Callable[..., None]
    on_activity_join_request: t.Callable[..., None]
    on_activity_invite: t.Callable[..., None]


class IDiscordActivityManager(ctypes.Structure):
    register_command: t.Callable[..., ctypes.c_int32]
    register_steam: t.Callable[..., ctypes.c_int32]
    update_activity: t.Callable[..., None]
    clear_activity: t.Callable[..., None]
    send_request_reply: t.Callable[..., None]
    send_invite: t.Callable[..., None]
    accept_invite: t.Callable[..., None]


IDiscordActivityManager._fields_ = [
    ("register_command", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordActivityManager),
        ctypes.c_char_p
    )),
    ("register_steam", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordActivityManager),
        ctypes.c_int32
    )),
    ("update_activity", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordActivityManager),
        ctypes.POINTER(DiscordActivity),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_uint32
        )
    )),
    ("clear_activity", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordActivityManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("send_request_reply", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordActivityManager),
        DiscordUserId,
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("send_invite", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordActivityManager),
        DiscordUserId,
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("accept_invite", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordActivityManager),
        DiscordUserId,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
]


class IDiscordRelationshipEvents(ctypes.Structure):
    _fields_ = [
        ("on_refresh", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p
        )),
        ("on_relationship_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.POINTER(DiscordRelationship)
        )),
    ]


class IDiscordRelationshipManager(ctypes.Structure):
    pass


IDiscordRelationshipManager._fields_ = [
    ("filter", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordRelationshipManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            ctypes.c_bool,
            ctypes.c_void_p,
            ctypes.POINTER(DiscordRelationship)
        )
    )),
    ("count", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordRelationshipManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("get", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordRelationshipManager),
        DiscordUserId,
        ctypes.POINTER(DiscordRelationship)
    )),
    ("get_at", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordRelationshipManager),
        ctypes.c_uint32,
        ctypes.POINTER(DiscordRelationship)
    )),
]


class IDiscordLobbyEvents(ctypes.Structure):
    _fields_ = [
        ("on_lobby_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64
        )),
        ("on_lobby_delete", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_uint32
        )),
        ("on_member_connect", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_int64
        )),
        ("on_member_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_int64
        )),
        ("on_member_disconnect", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_int64
        )),
        ("on_lobby_message", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32
        )),
        ("on_speaking", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.c_bool
        )),
        ("on_network_message", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32
        )),
    ]


class IDiscordLobbyManager(ctypes.Structure):
    pass


IDiscordLobbyManager._fields_ = [
    ("get_lobby_create_transaction", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.POINTER(ctypes.POINTER(IDiscordLobbyTransaction))
    )),
    ("get_lobby_update_transaction", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(ctypes.POINTER(IDiscordLobbyTransaction))
    )),
    ("get_member_update_transaction", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        ctypes.POINTER(ctypes.POINTER(IDiscordLobbyMemberTransaction))
    )),
    ("create_lobby", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.POINTER(IDiscordLobbyTransaction),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(DiscordLobby)
        )
    )),
    ("update_lobby", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(IDiscordLobbyTransaction),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("delete_lobby", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("connect_lobby", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordLobbySecret,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(DiscordLobby)
        )
    )),
    ("connect_lobby_with_activity_secret", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbySecret,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(DiscordLobby)
        )
    )),
    ("disconnect_lobby", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("get_lobby", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(DiscordLobby)
    )),
    ("get_lobby_activity_secret", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(DiscordLobbySecret)
    )),
    ("get_lobby_metadata_value", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordMetadataKey,
        ctypes.POINTER(DiscordMetadataValue)
    )),
    ("get_lobby_metadata_key", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_int32,
        ctypes.POINTER(DiscordMetadataKey)
    )),
    ("lobby_metadata_count", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("member_count", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("get_member_user_id", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_int32,
        ctypes.POINTER(DiscordUserId)
    )),
    ("get_member_user", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        ctypes.POINTER(DiscordUser)
    )),
    ("get_member_metadata_value", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        DiscordMetadataKey,
        ctypes.POINTER(DiscordMetadataValue)
    )),
    ("get_member_metadata_key", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        ctypes.c_int32,
        ctypes.POINTER(DiscordMetadataKey)
    )),
    ("member_metadata_count", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("update_member", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        ctypes.POINTER(IDiscordLobbyMemberTransaction),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("send_lobby_message", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("get_search_query", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.POINTER(ctypes.POINTER(IDiscordLobbySearchQuery))
    )),
    ("search", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.POINTER(IDiscordLobbySearchQuery),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("lobby_count", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("get_lobby_id", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.c_int32,
        ctypes.POINTER(DiscordLobbyId)
    )),
    ("connect_voice", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("disconnect_voice", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("connect_network", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId
    )),
    ("disconnect_network", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId
    )),
    ("flush_network", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager)
    )),
    ("open_network_channel", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        ctypes.c_uint8,
        ctypes.c_bool
    )),
    ("send_network_message", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordLobbyManager),
        DiscordLobbyId,
        DiscordUserId,
        ctypes.c_uint8,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )),
]


class IDiscordNetworkEvents(ctypes.Structure):
    _fields_ = [
        ("on_message", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            DiscordNetworkPeerId,
            DiscordNetworkChannelId,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32
        )),
        ("on_route_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_char_p
        )),
    ]


class IDiscordNetworkManager(ctypes.Structure):
    pass


IDiscordNetworkManager._fields_ = [
    ("get_peer_id", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordNetworkManager),
        ctypes.POINTER(DiscordNetworkPeerId)
    )),
    ("flush", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager)
    )),
    ("open_peer", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager),
        DiscordNetworkPeerId,
        ctypes.c_char_p
    )),
    ("update_peer", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager),
        DiscordNetworkPeerId,
        ctypes.c_char_p
    )),
    ("close_peer", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager),
        DiscordNetworkPeerId
    )),
    ("open_channel", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager),
        DiscordNetworkPeerId,
        DiscordNetworkChannelId,
        ctypes.c_bool
    )),
    ("close_channel", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager),
        DiscordNetworkPeerId,
        DiscordNetworkChannelId
    )),
    ("send_message", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordNetworkManager),
        DiscordNetworkPeerId,
        DiscordNetworkChannelId,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )),
]


class IDiscordOverlayEvents(ctypes.Structure):
    _fields_ = [
        ("on_toggle", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_bool
        )),
    ]


class IDiscordOverlayManager(ctypes.Structure):
    pass


IDiscordOverlayManager._fields_ = [
    ("is_enabled", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("is_locked", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("set_locked", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.c_bool,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("open_activity_invite", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("open_guild_invite", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("open_voice_settings", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
]

IDiscordStorageEvents = ctypes.c_void_p


class IDiscordStorageManager(ctypes.Structure):
    pass


IDiscordStorageManager._fields_ = [
    ("read", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32)
    )),
    ("read_async", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32)
    )),
    ("read_async_partial", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32
        )
    )),
    ("write", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )),
    ("write_async", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("delete_", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p
    )),
    ("exists", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("count", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("stat", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_char_p,
        ctypes.POINTER(DiscordFileStat)
    )),
    ("stat_at", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.c_int32,
        ctypes.POINTER(DiscordFileStat)
    )),
    ("get_path", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.POINTER(DiscordPath)
    )),
]


class IDiscordStoreEvents(ctypes.Structure):
    _fields_ = [
        ("on_entitlement_create", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.POINTER(DiscordEntitlement)
        )),
        ("on_entitlement_delete", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.POINTER(DiscordEntitlement)
        )),
    ]


class IDiscordStoreManager(ctypes.Structure):
    pass


IDiscordStoreManager._fields_ = [
    ("fetch_skus", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStoreManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("count_skus", ctypes.CFUNCTYPE(
        None, ctypes.POINTER(IDiscordStoreManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("get_sku", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStoreManager),
        DiscordSnowflake,
        ctypes.POINTER(DiscordSku)
    )),
    ("get_sku_at", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStoreManager),
        ctypes.c_int32,
        ctypes.POINTER(DiscordSku)
    )),
    ("fetch_entitlements", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStoreManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("count_entitlements", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStoreManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("get_entitlement", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStoreManager),
        DiscordSnowflake,
        ctypes.POINTER(DiscordEntitlement)
    )),
    ("get_entitlement_at", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStoreManager),
        ctypes.c_int32,
        ctypes.POINTER(DiscordEntitlement)
    )),
    ("has_sku_entitlement", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordStoreManager),
        DiscordSnowflake,
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("start_purchase", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordStoreManager),
        DiscordSnowflake,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
]


class IDiscordVoiceEvents(ctypes.Structure):
    _fields_ = [
        ("on_settings_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p
        )),
    ]


class IDiscordVoiceManager(ctypes.Structure):
    pass


IDiscordVoiceManager._fields_ = [
    ("get_input_mode", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        ctypes.POINTER(DiscordInputMode)
    )),
    ("set_input_mode", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordVoiceManager),
        DiscordInputMode,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("is_self_mute", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("set_self_mute", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        ctypes.c_bool
    )),
    ("is_self_deaf", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("set_self_deaf", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        ctypes.c_bool
    )),
    ("is_local_mute", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        DiscordSnowflake,
        ctypes.POINTER(ctypes.c_bool)
    )),
    ("set_local_mute", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        DiscordSnowflake,
        ctypes.c_bool
    )),
    ("get_local_volume", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        DiscordSnowflake,
        ctypes.POINTER(ctypes.c_uint8)
    )),
    ("set_local_volume", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordVoiceManager),
        DiscordSnowflake,
        ctypes.c_uint8
    )),
]


class IDiscordAchievementEvents(ctypes.Structure):
    _fields_ = [
        ("on_user_achievement_update", ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.POINTER(DiscordUserAchievement)
        )),
    ]

    on_user_achievement_update: t.Callable[[DiscordUserAchievement], None]


class IDiscordAchievementManager(ctypes.Structure):
    set_user_achievement: t.Callable[..., None]
    fetch_user_achievements: t.Callable[..., None]
    count_user_achievements: t.Callable[..., None]
    get_user_achievement: t.Callable[..., ctypes.c_int32]
    get_user_achievement_at: t.Callable[..., ctypes.c_int32]


IDiscordAchievementManager._fields_ = [
    ("set_user_achievement", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordAchievementManager),
        DiscordSnowflake,
        ctypes.c_uint8,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("fetch_user_achievements", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordAchievementManager),
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32
        )
    )),
    ("count_user_achievements", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordAchievementManager),
        ctypes.POINTER(ctypes.c_int32)
    )),
    ("get_user_achievement", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordAchievementManager),
        DiscordSnowflake,
        ctypes.POINTER(DiscordUserAchievement)
    )),
    ("get_user_achievement_at", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordAchievementManager),
        ctypes.c_int32,
        ctypes.POINTER(DiscordUserAchievement)
    )),
]

IDiscordCoreEvents = ctypes.c_void_p


class IDiscordCore(ctypes.Structure):
    pass


IDiscordCore._fields_ = [
    ("destroy", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordCore)
    )),
    ("run_callbacks", ctypes.CFUNCTYPE(
        ctypes.c_int32,
        ctypes.POINTER(IDiscordCore)
    )),
    ("set_log_hook", ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(IDiscordCore),
        ctypes.c_int32,
        ctypes.c_void_p,
        ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.c_char_p
        )
    )),
    ("get_application_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordApplicationManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_user_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordUserManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_image_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordImageManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_activity_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordActivityManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_relationship_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordRelationshipManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_lobby_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordLobbyManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_network_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordNetworkManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_overlay_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordOverlayManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_storage_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordStorageManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_store_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordStoreManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_voice_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordVoiceManager),
        ctypes.POINTER(IDiscordCore)
    )),
    ("get_achievement_manager", ctypes.CFUNCTYPE(
        ctypes.POINTER(IDiscordAchievementManager),
        ctypes.POINTER(IDiscordCore)
    )),
]


class DiscordCreateParams(ctypes.Structure):
    _fields_ = [
        ("client_id", DiscordClientId),
        ("flags", ctypes.c_uint64),
        ("events", ctypes.POINTER(IDiscordCoreEvents)),
        ("event_data", ctypes.c_void_p),
        ("application_events", ctypes.POINTER(IDiscordApplicationEvents)),
        ("application_version", DiscordVersion),
        ("user_events", ctypes.POINTER(IDiscordUserEvents)),
        ("user_version", DiscordVersion),
        ("image_events", ctypes.POINTER(IDiscordImageEvents)),
        ("image_version", DiscordVersion),
        ("activity_events", ctypes.POINTER(IDiscordActivityEvents)),
        ("activity_version", DiscordVersion),
        ("relationship_events", ctypes.POINTER(IDiscordRelationshipEvents)),
        ("relationship_version", DiscordVersion),
        ("lobby_events", ctypes.POINTER(IDiscordLobbyEvents)),
        ("lobby_version", DiscordVersion),
        ("network_events", ctypes.POINTER(IDiscordNetworkEvents)),
        ("network_version", DiscordVersion),
        ("overlay_events", ctypes.POINTER(IDiscordOverlayEvents)),
        ("overlay_version", DiscordVersion),
        ("storage_events", ctypes.POINTER(IDiscordStorageEvents)),
        ("storage_version", DiscordVersion),
        ("store_events", ctypes.POINTER(IDiscordStoreEvents)),
        ("store_version", DiscordVersion),
        ("voice_events", ctypes.POINTER(IDiscordVoiceEvents)),
        ("voice_version", DiscordVersion),
        ("achievement_events", ctypes.POINTER(IDiscordAchievementEvents)),
        ("achievement_version", DiscordVersion)
    ]


def DiscordCreateParamsSetDefault(params):
    params.application_version = 1
    params.user_version = 1
    params.image_version = 1
    params.activity_version = 1
    params.relationship_version = 1
    params.lobby_version = 1
    params.network_version = 1
    params.overlay_version = 1
    params.storage_version = 1
    params.store_version = 1
    params.voice_version = 1
    params.achievement_version = 1
