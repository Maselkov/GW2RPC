import sys

if sys.version_info >= (3, 6):
    from enum import IntEnum, IntFlag
else:
    from enum import IntEnum, IntEnum as IntFlag


class Result(IntEnum):
    ok = 0
    service_unavailable = 1
    invalid_version = 2
    lock_failed = 3
    internal_error = 4
    invalid_payload = 5
    invalid_command = 6
    invalid_permissions = 7
    not_fetched = 8
    not_found = 9
    conflict = 10
    invalid_secret = 11
    invalid_join_secret = 12
    no_eligible_activity = 13
    invalid_invite = 14
    not_authenticated = 15
    invalid_access_token = 16
    application_mismatch = 17
    invalid_data_url = 18
    invalid_base_64 = 19
    not_filtered = 20
    lobby_full = 21
    invalid_lobby_secret = 22
    invalid_filename = 23
    invalid_file_size = 24
    invalid_entitlement = 25
    not_installed = 26
    not_running = 27
    insufficient_buffer = 28
    purchase_canceled = 29
    invalid_guild = 30
    invalid_event = 31
    invalid_channel = 32
    invalid_origin = 33
    rate_limited = 34
    oauth2_error = 35
    select_channel_timeout = 36
    get_guild_timeout = 37
    select_voice_force_required = 38
    capture_shortcut_already_listening = 39
    unauthorized_for_achievement = 40
    invalid_gift_code = 41
    purchase_error = 42
    transaction_aborted = 43
    drawing_init_failed = 44


class LogLevel(IntEnum):
    error = 0
    warning = 1
    info = 2
    debug = 3


class CreateFlags(IntFlag):
    default = 0
    no_require_discord = 1


class UserFlag(IntFlag):
    partner = 2
    hype_squad_events = 4
    hype_squad_house_1 = 64
    hype_squad_house_2 = 128
    hype_squad_house_3 = 256


class PremiumType(IntEnum):
    none_ = 0
    tier_1 = 1
    tier_2 = 2


class ActivityType(IntEnum):
    playing = 0
    streaming = 1
    listening = 2
    custom = 4


class ActivityJoinRequestReply(IntEnum):
    no = 0
    yes = 1
    ignore = 2


class ActivityActionType(IntEnum):
    join = 1
    spectate = 2


class RelationshipType(IntEnum):
    none_ = 0
    friend = 1
    blocked = 2
    pending_incoming = 3
    pending_outgoing = 4
    implicit = 5


class Status(IntEnum):
    offline = 0
    online = 1
    idle = 2
    do_not_disturb = 3


class ImageType(IntEnum):
    user = 0


class LobbyType(IntEnum):
    private = 1
    public = 2


class LobbySearchComparison(IntEnum):
    LessThanOrEqual = -2
    LessThan = -1
    Equal = 0
    GreaterThan = 1
    GreaterThanOrEqual = 2
    NotEqual = 3


class LobbySearchCast(IntEnum):
    String = 1
    Number = 2


class LobbySearchDistance(IntEnum):
    Local = 0
    Default = 1
    Extended = 2
    Global = 3


class InputModeType(IntEnum):
    VoiceActivity = 0
    PushToTalk = 1


class SkuType(IntEnum):
    Application = 1
    DLC = 2
    Consumable = 3
    Bundle = 4


class EntitlementType(IntEnum):
    Purchase = 1
    PremiumSubscription = 2
    DeveloperGift = 3
    TestModePurchase = 4
    FreePurchase = 5
    UserGift = 6
    PremiumPurchase = 7
