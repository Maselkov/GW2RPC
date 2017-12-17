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
    63: "Renegade"
}


class Character:
    def __init__(self, mumble_data, api_info=None):
        self.__mumble_data = mumble_data
        self.__api_info = api_info
        self.name = mumble_data["name"]
        self.race = RACES[mumble_data["race"]]
        self.__api_info = None
        if api._authenticated:
            self.__api_info = api.get_character(self.name)
        self.profession = self._get_profession()
        self.profession_icon = "prof_{}".format(
            self.profession.lower().replace(" ", ""))

    def _get_profession(self):
        map_info = api.get_map_info(self.__mumble_data["map_id"])
        if self.__api_info:
            spec = self.get_spec(self.name, map_info)
            if spec:
                return spec
        return PROFESSIONS[self.__mumble_data["profession"]]

    def get_spec(self, name, map_info):
        character_info = self.__api_info
        if map_info["region_name"] == "Player vs. Player":
            return self.get_build(character_info, "pvp")
        if map_info["region_name"] == "World vs. World":
            return self.get_build(character_info, "wvw")
        return self.get_build(character_info, "pve")

    def get_build(self, character_info, gametype):
        if character_info["specializations"][gametype][2]:
            spec_id = character_info["specializations"][gametype][2]["id"]
            if spec_id in ELITESPECS.keys():
                profession = ELITESPECS[character_info["specializations"][
                    gametype][2]["id"]]
                return profession
        return None
