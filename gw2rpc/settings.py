import configparser
import os
import logging
from xmlrpc.client import boolean

log = logging.getLogger()


class Config:
    def __init__(self):
        def set_boolean(header, setting, fallback=False):
            try:
                value = self.config.getboolean(header, setting, fallback=fallback)
            except ValueError:
                value = False
            return value

        def set_string(header, setting, default):
            try:
                value = self.config[header][setting]
            except KeyError:
                value = default
            return value

        supported_languages = ["en", "es", "de", "fr"]

        self.config = configparser.ConfigParser(allow_no_value=True)
        if not os.path.exists("config.ini"):
            self.config["API"] = {"APIKey": ""}
            self.config["Settings"] = {
                "CloseWithGw2": False,
                "DisplayGuildTag": True,
                "Lang": "en",
                "HideCommanderTag": False,
                "HideMounts": False
            }
            self.config["PointsOfInterest"] = {
                "DisableInWvW": False,
                "DisableCompletely": False,
                "HidePoiButton": False
            }
            self.config["Webhooks"] = {
                "WebHook": "",
                "AnnounceRaid": True,
                "DisableInWvW": False
            }
            with open("config.ini", "w") as cfile:
                config.write(cfile)
        self.config.read("config.ini")
        self.api_keys = [
            k for k in map(str.strip, self.config["API"]["APIKey"].split(',')) if k
        ]
        self.webhooks = [
            k for k in map(str.strip, self.config["Webhooks"]["WebHook"].split(',')) if k
        ]
        self.close_with_gw2 = set_boolean("Settings", "CloseWithGw2")
        self.display_tag = set_boolean("Settings", "DisplayGuildTag")
        self.hide_commander_tag = set_boolean("Settings", "HideCommanderTag")
        self.hide_mounts = set_boolean("Settings", "HideMounts")
        try:
            self.lang = self.config["Settings"]["Lang"] if self.config["Settings"]["Lang"] in supported_languages else "en"
        except KeyError:
            log.error("Missing language parameter, defaulting to en. Add 'lang = en' for localization support to config.ini.")
            self.lang = "en"

        self.disable_pois = set_boolean("PointsOfInterest",
                                        "DisableCompletely")
        self.disable_pois_in_wvw = set_boolean("PointsOfInterest",
                                               "DisableInWvW")
        self.hide_poi_button = set_boolean("PointsOfInterest",
                                                "HidePoiButton")
        self.announce_raid = set_boolean("Webhooks", "AnnounceRaid", fallback=True)
        self.disable_raid_announce_in_wvw = set_boolean("Webhooks", "DisableInWvW")

    def change_boolean_item(self, section, item, value: boolean):
        self.config.set(section, item, str(value))
        try:
            with open('config.ini', 'w') as f:
                self.config.write(f)
        except:
            log.error("Could not write to config.ini")

config = Config()
