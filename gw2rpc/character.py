from .api import api

PROFESSIONS = {
    1: "Guardian",
    2: "Warrior",
    3: "Engineer",
    4: "Ranger",
    5: "Thief",
    6: "Elementalist",
    7: "Mesmer",
    8: "Necromancer",
    9: "Revenant"
}

RACES = {0: "Asura", 1: "Charr", 2: "Human", 3: "Norn", 4: "Sylvari"}

ELITESPECS = {
    5: "Druid",
    7: "Daredevil",
    18: "Berserker",
    27: "Dragonhunter",
    34: "Reaper",
    40: "Chronomancer",
    43: "Scrapper",
    48: "Tempest",
    52: "Herald",
    55: "Soulbeast",
    56: "Weaver",
    57: "Holosmith",
    58: "Deadeye",
    59: "Mirage",
    60: "Scourge",
    61: "Spellbreaker",
    62: "Firebrand",
    63: "Renegade",
    64: "Harbinger",
    65: "Willbender",
    66: "Virtuoso",
    67: "Catalyst",
    68: "Bladesworn",
    69: "Vindicator",
    70: "Mechanist",
    71: "Specter",
    72: "Untamed"
}
# Images for specter and catalyst are missing


class Character:
    def __init__(self, mumble_data):
        self.__mumble_data = mumble_data
        self.name = mumble_data["name"]
        self.race = RACES[mumble_data["race"]]
        self.__api_info = None
        if api._authenticated:
            self.__api_info = api.get_character(self.name)
        self.profession = ELITESPECS[mumble_data["spec"]]
        self.profession_icon = "prof_{}".format(
            self.profession.lower().replace(" ", ""))
        self.guild_tag = self._get_guild_tag()

    def _get_guild_tag(self):
        tag = ""
        if self.__api_info:
            gid = self.__api_info.get("guild")
            if gid:
                try:
                    res = api.get_guild(gid)
                    tag = " [{}]".format(res["tag"])
                except:
                    pass
        return tag
