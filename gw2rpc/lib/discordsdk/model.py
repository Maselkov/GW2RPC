import ctypes
from enum import Enum

from . import sdk
from .enum import (EntitlementType, ImageType, InputModeType, LobbyType,
                   RelationshipType, SkuType, Status)


class Model:
    def __init__(self, **kwargs):
        self._internal = kwargs.get("internal", self._struct_())
        if "copy" in kwargs:
            ctypes.memmove(
                ctypes.byref(self._internal),
                ctypes.byref(kwargs["copy"]),
                ctypes.sizeof(self._struct_)
            )

        self._fields = {}

        for field, ftype in self._fields_:
            self._fields[field] = ftype
            if issubclass(ftype, Model):
                setattr(self, "_" + field, ftype(internal=getattr(self._internal, field)))

    def __getattribute__(self, key):
        if key.startswith("_"):
            return super().__getattribute__(key)
        else:
            ftype = self._fields[key]
            value = getattr(self._internal, key)
            if ftype == int:
                return int(value)
            elif ftype == str:
                return value.decode("utf8")
            elif ftype == bool:
                return bool(value)
            elif issubclass(ftype, Model):
                return getattr(self, "_" + key)
            elif issubclass(ftype, Enum):
                return ftype(int(value))
            else:
                raise TypeError(ftype)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            ftype = self._fields[key]
            if ftype == int:
                value = int(value)
                setattr(self._internal, key, value)
            elif ftype == str:
                value = value.encode("utf8")
                setattr(self._internal, key, value)
            elif ftype == bool:
                value = bool(value)
                setattr(self._internal, key, value)
            elif issubclass(ftype, Model):
                setattr(self, "_" + key, value)
                setattr(self._internal, key, value._internal)
            elif issubclass(ftype, Enum):
                setattr(self._internal, key, value.value)
            else:
                raise TypeError(ftype)

    def __dir__(self):
        return super().__dir__() + list(self._fields.keys())


class User(Model):
    _struct_ = sdk.DiscordUser
    _fields_ = [
        ("id", int),
        ("username", str),
        ("discriminator", str),
        ("avatar", str),
        ("bot", bool),
    ]

    id: int
    username: str
    discriminator: str
    avatar: str
    bot: str


class ActivityTimestamps(Model):
    _struct_ = sdk.DiscordActivityTimestamps
    _fields_ = [
        ("start", int),
        ("end", int),
    ]

    start: int
    end: int


class ActivityAssets(Model):
    _struct_ = sdk.DiscordActivityAssets
    _fields_ = [
        ("large_image", str),
        ("large_text", str),
        ("small_image", str),
        ("small_text", str),
    ]

    large_image: str
    large_text: str
    small_image: str
    small_text: str


class PartySize(Model):
    _struct_ = sdk.DiscordPartySize
    _fields_ = [
        ("current_size", int),
        ("max_size", int),
    ]

    current_size: int
    max_size: int


class ActivityParty(Model):
    _struct_ = sdk.DiscordActivityParty
    _fields_ = [
        ("id", str),
        ("size", PartySize),
    ]

    id: str
    size: PartySize


class ActivitySecrets(Model):
    _struct_ = sdk.DiscordActivitySecrets
    _fields_ = [
        ("match", str),
        ("join", str),
        ("spectate", str),
    ]

    match: str
    join: str
    spectate: str


class Activity(Model):
    _struct_ = sdk.DiscordActivity
    _fields_ = [
        ("application_id", int),
        ("name", str),
        ("state", str),
        ("details", str),
        ("timestamps", ActivityTimestamps),
        ("assets", ActivityAssets),
        ("party", ActivityParty),
        ("secrets", ActivitySecrets),
        ("instance", bool),
    ]

    application_id: int
    name: str
    state: str
    details: str
    timestamps: ActivityTimestamps
    assets: ActivityAssets
    party: ActivityParty
    secrets: ActivitySecrets
    instance: bool


class Presence(Model):
    _struct_ = sdk.DiscordPresence
    _fields_ = [
        ("status", Status),
        ("activity", Activity),
    ]

    status: Status
    activity: Activity


class Relationship(Model):
    _struct_ = sdk.DiscordRelationship
    _fields_ = [
        ("type", RelationshipType),
        ("user", User),
        ("presence", Presence),
    ]

    type: RelationshipType
    user: User
    presence: Presence


class ImageDimensions(Model):
    _struct_ = sdk.DiscordImageDimensions
    _fields_ = [
        ("width", int),
        ("height", int),
    ]

    width: int
    height: int


class ImageHandle(Model):
    _struct_ = sdk.DiscordImageHandle
    _fields_ = [
        ("type", ImageType),
        ("id", int),
        ("size", int),
    ]

    type: ImageType
    id: int
    size: int


class OAuth2Token(Model):
    _struct_ = sdk.DiscordOAuth2Token
    _fields_ = [
        ("access_token", str),
        ("scopes", str),
        ("expires", int),
    ]

    access_token: str
    scopes: str
    expires: str


class Lobby(Model):
    _struct_ = sdk.DiscordLobby
    _fields_ = [
        ("id", int),
        ("type", LobbyType),
        ("owner_id", int),
        ("secret", str),
        ("capacity", int),
        ("locked", bool),
    ]

    id: int
    type: LobbyType
    owner_id: int
    secret: str
    capacity: int
    locked: bool


class InputMode(Model):
    _struct_ = sdk.DiscordInputMode
    _fields_ = [
        ("type", InputModeType),
        ("shortcut", str),
    ]

    type: InputModeType
    shortcut: str


class FileStat(Model):
    _struct_ = sdk.DiscordFileStat
    _fields_ = [
        ("filename", str),
        ("size", int),
        ("last_modified", int),
    ]

    filename: str
    size: int
    last_modified: int


class UserAchievement(Model):
    _struct_ = sdk.DiscordUserAchievement
    _fields_ = [
        ("user_id", str),
        ("achievement_id", int),
        ("percent_complete", int),
        ("unlocked_at", str),
    ]

    user_id: str
    achievement_id: int
    percent_complete: int
    unlocked_at: str


class SkuPrice(Model):
    _struct_ = sdk.DiscordSkuPrice
    _fields_ = [
        ("amount", int),
        ("currency", str),
    ]

    amount: int
    currency: str


class Sku(Model):
    _struct_ = sdk.DiscordSku
    _fields_ = [
        ("id", int),
        ("type", SkuType),
        ("name", str),
        ("price", SkuPrice),
    ]

    id: int
    type: SkuType
    name: str
    price: SkuPrice


class Entitlement(Model):
    _struct_ = sdk.DiscordEntitlement
    _fields_ = [
        ("id", int),
        ("type", EntitlementType),
        ("sku_id", int),
    ]

    id: int
    type: EntitlementType
    sku_id: int
