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

        config = configparser.ConfigParser(allow_no_value=True)
        if not os.path.exists("config.ini"):
            config["API"] = {"APIKey": ""}
            config["Discord"] = {"UpdateFrequency": 10}
            config["AppSettings"] = {
                "CloseWithGw2": True,
                "DisplayGuildTag": True
            }
            with open("config.ini", "w") as cfile:
                config.write(cfile)
        config.read("config.ini")
        self.api_key = config["API"]["APIKey"]
        self.update_frequency = config.getint("Discord", "UpdateFrequency")
        self.close_with_gw2 = set_boolean("Settings", "CloseWithGw2")
        self.display_tag = set_boolean("Settings", "DisplayGuildTag")


config = Config()
