import configparser
import os


class Config:
    def __init__(self):
        def set_boolean(header, setting):
            try:
                value = config.getboolean(header, setting, fallback=False)
            except ValueError:
                value = False
            return value

        #supported_languages = ["en", "es", "de", "fr"]
        supported_languages = ["en", "de"]

        config = configparser.ConfigParser(allow_no_value=True)
        if not os.path.exists("config.ini"):
            config["API"] = {"APIKey": ""}
            config["Settings"] = {
                "CloseWithGw2": False,
                "DisplayGuildTag": True,
                "Lang" : "en"
            }
            config["PointsOfInterest"] = {
                "DisableInWvW": False,
                "DisableCompletely": False
            }
            with open("config.ini", "w") as cfile:
                config.write(cfile)
        config.read("config.ini")
        self.api_keys = [
            k for k in map(str.strip, config["API"]["APIKey"].split(',')) if k
        ]
        self.close_with_gw2 = set_boolean("Settings", "CloseWithGw2")
        self.display_tag = set_boolean("Settings", "DisplayGuildTag")
        self.lang = config["Settings"]["Lang"] if config["Settings"]["Lang"] in supported_languages else "en"
        self.disable_pois = set_boolean("PointsOfInterest",
                                        "DisableCompletely")
        self.disable_pois_in_wvw = set_boolean("PointsOfInterest",
                                               "DisableInWvW")


config = Config()
