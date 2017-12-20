import configparser
import os


class Config:
    def __init__(self):
        config = configparser.ConfigParser(allow_no_value=True)
        if not os.path.exists("config.ini"):
            config["API"] = {"APIKey": ""}
            config["Discord"] = {"UpdateFrequency": 10}
            config["CloseWithGw2"] = {"CloseWithGw2": True}
            with open("config.ini", "w") as cfile:
                config.write(cfile)
        config.read("config.ini")
        self.api_key = config["API"]["APIKey"]
        self.update_frequency = config.getint("Discord", "UpdateFrequency")
        self.close_with_gw2 = config.getboolean("CloseWithGw2", "CloseWithGw2")


config = Config()
