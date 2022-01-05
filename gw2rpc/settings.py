import configparser
import os
import logging

log = logging.getLogger()


class Config:
    def __init__(self):
        def set_boolean(header, setting):
            try:
                value = config.getboolean(header, setting, fallback=False)
            except ValueError:
                value = False
            return value

        def set_string(header, setting, default):
            try:
                value = config[header][setting]
            except KeyError:
                value = default
            return value

        supported_languages = ["en", "es", "de", "fr"]

        config = configparser.ConfigParser(allow_no_value=True)
        if not os.path.exists("config.ini"):
            config["API"] = {"APIKey": ""}
            config["Settings"] = {
                "CloseWithGw2": False,
                "DisplayGuildTag": True,
                "Lang" : "en",
                "HideCommanderTag": False
            }
            config["PointsOfInterest"] = {
                "DisableInWvW": False,
                "DisableCompletely": False,
                "HidePoiButton": False
            }
            with open("config.ini", "w") as cfile:
                config.write(cfile)
        config.read("config.ini")
        self.api_keys = [
            k for k in map(str.strip, config["API"]["APIKey"].split(',')) if k
        ]
        self.close_with_gw2 = set_boolean("Settings", "CloseWithGw2")
        self.display_tag = set_boolean("Settings", "DisplayGuildTag")
        self.hide_commander_tag = set_boolean("Settings", "HideCommanderTag")
        try:
            self.lang = config["Settings"]["Lang"] if config["Settings"]["Lang"] in supported_languages else "en"
        except KeyError:
            log.error("Missing language parameter, defaulting to en. Add 'lang = en' for localization support to config.ini.")
            self.lang = "en"
        self.disable_pois = set_boolean("PointsOfInterest",
                                        "DisableCompletely")
        self.disable_pois_in_wvw = set_boolean("PointsOfInterest",
                                               "DisableInWvW")
        self.hide_poi_button = set_boolean("PointsOfInterest",
                                                "HidePoiButton")


config = Config()
