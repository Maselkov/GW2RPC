import ctypes
import logging
import os
import sys
import threading
import time
import webbrowser

import psutil
import requests
from infi.systray import SysTrayIcon

from .api import APIError, api  # TODO
from .character import Character
from .mumble import DataUnchangedError, MumbleData
from .rpc import DiscordRPC
from .settings import config

VERSION = 1.0

GW2RPC_BASE_URL = "https://gw2rpc.info/api/v1/"

log = logging.getLogger()


class GameNotRunningError(Exception):
    pass


worlds = {
    'NA': [
        'Anvil Rock', 'Blackgate', 'Borlis Pass', 'Crystal Desert',
        'Darkhaven', "Devona's Rest", 'Dragonbrand', 'Ehmry Bay',
        'Eredon Terrace', "Ferguson's Crossing", 'Fort Aspenwood',
        'Gate of Madness', 'Henge of Denravi', 'Isle of Janthir',
        'Jade Quarry', 'Kaineng', 'Maguuma', 'Northern Shiverpeaks',
        'Sanctum of Rall', 'Sea of Sorrows', "Sorrow's Furnace",
        'Stormbluff Isle', 'Tarnished Coast', "Yak's Bend"
    ],
    'EU': [
        'Aurora Glade', 'Blacktide', 'Desolation', 'Far Shiverpeaks',
        'Fissure of Woe', 'Gandara', "Gunnar's Hold", 'Piken Square',
        'Ring of Fire', 'Ruins of Surmia', "Seafarer's Rest", 'Underworld',
        'Vabbi', 'Whiteside Ridge', 'Arborstone [FR]', 'Augury Rock [FR]',
        'Fort Ranik [FR]', 'Jade Sea [FR]', 'Vizunah Square [FR]',
        "Abaddon's Mouth [DE]", 'Drakkar Lake [DE]', 'Dzagonur [DE]',
        'Elona Reach [DE]', 'Kodash [DE]', "Miller's Sound [DE]",
        'Riverside [DE]', 'Baruch Bay [SP]'
    ]
}


def create_msgbox(description, *, title='GW2RPC', code=0):
    MessageBox = ctypes.windll.user32.MessageBoxW
    return MessageBox(None, description, title, code)


class GW2RPC:
    def __init__(self):
        def fetch_registry():
            url = GW2RPC_BASE_URL + "registry"
            res = requests.get(url)
            if res.status_code != 200:
                log.error("Could not fetch the web registry")
                return None
            return res.json()

        def icon_path():
            try:
                return os.path.join(sys._MEIPASS, "icon.ico")
            except:
                return "icon.ico"

        def fetch_support_invite():
            try:
                return requests.get(GW2RPC_BASE_URL + "support").json()[
                    "support"]
            except:
                return None

        self.rpc = DiscordRPC("385475290614464513")
        self.game = MumbleData()
        self.registry = fetch_registry()
        self.support_invite = fetch_support_invite()
        menu_options = (("About", None, self.about), )
        if self.support_invite:
            menu_options += (("Join support server", None, self.join_guild), )
        self.systray = SysTrayIcon(
            icon_path(),
            "Guild Wars 2 with Discord",
            menu_options,
            on_quit=self.shutdown)
        self.systray.start()
        self.process = None
        self.check_for_updates()

    def shutdown(self, _=None):
        sys.exit()

    def about(self, _):
        message = (
            "Version: {}\n\nhttps://gw2rpc.info\n\nBy Maselkov & "
            "N1TR0\nIcons by Zebban\nWebsite by Penemue".format(VERSION))
        threading.Thread(target=create_msgbox, args=[message]).start()

    def join_guild(self, _):
        try:
            webbrowser.open(self.support_invite)
        except:
            pass

    def check_for_updates(self):
        def get_build():
            url = GW2RPC_BASE_URL + "build"
            r = requests.get(url)
            try:
                return r.json()["build"]
            except:
                return None

        build = get_build()
        if not build:
            log.error("Could not retrieve build!")
            create_msgbox(
                "Could not check for updates - check your connection!")
            return
        if build > VERSION:
            log.info("New version found! Current: {} New: {}".format(
                VERSION, build))
            res = create_msgbox(
                "There is a new update for GW2 Rich Presence available. "
                "Would you like to be taken to the download page now?",
                code=68)
            if res == 6:
                webbrowser.open("https://gw2rpc.info/")

    def update_gw2_process(self):
        if self.process:
            if self.process.is_running():
                return
            else:
                if config.close_with_gw2:
                    self.shutdown()
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
                pname = p.name()
                if pname == "Gw2-64.exe" or pname == "Gw2.exe":
                    self.process = p
                    return
            except:
                pass
        self.process = None

    def get_map_asset(self, map_info):
        def get_region():
            world = api.world
            if world:
                for k, v in worlds.items():
                    if world in v:
                        return " [{}]".format(k)
            return ""

        map_id = map_info["id"]
        map_name = map_info["name"]
        region = map_info["region_name"]
        if self.registry:
            if map_name == "Fractals of the Mists":
                for fractal in self.registry["fractals"]:
                    if fractal["id"] == map_id:
                        state = fractal["name"] + " fractal"
                        image = "fotm"
                        break
                else:
                    image = "fotm"
                    state = "Fractals of the Mists"
                name = "Fractals of the Mists"
            else:
                if map_name in self.registry["special"]:
                    image = self.registry["special"][map_name]
                elif map_id in self.registry["valid"]:
                    image = map_id
                elif region in self.registry["regions"]:
                    image = self.registry["regions"][region]
                else:
                    image = "default"
                name = map_name
                state = name
        else:
            special = {
                "Fractals of the Mists": "fotm",
                "Windswept Haven": "gh_haven",
                "Gilded Hollow": "gh_hollow",
                "Lost Precipice": "gh_precipice"
            }.get(map_info["name"])
            if special:
                return special
            if map_info["type"] == "Public":
                image = map_id
            else:
                valid_ids = [1062, 1149, 1156, 38, 1264]
                if map_id in valid_ids:
                    image = map_id
                else:
                    image = "default"
            name = map_name
            state = name
        return "in " + state, {
            "large_image": str(image),
            "large_text": name + get_region()
        }

    def get_activity(self):
        data = self.game.get_mumble_data()
        if not data:
            return None
        current_time = time.time()
        map_id = data["map_id"]
        try:
            map_info = api.get_map_info(map_id)
            character = Character(data)
        except APIError:
            log.exception("API Error!")
        state, map_asset = self.get_map_asset(map_info)
        activiy = {
            "state": state,
            "details": character.name,
            "timestamps": {
                'start': int(current_time)
            },
            "assets": {
                **map_asset,
                "small_image": character.profession_icon,
                "small_text": "{0.race} {0.profession}".format(character)
            }
        }
        return activiy

    def in_character_selection(self):
        current_time = time.time()
        activity = {
            "state": "in character selection",
            "timestamps": {
                'start': int(current_time)
            },
            "assets": {
                "large_image":
                "default",
                "large_text":
                "Character Selection",
                "small_image":
                "gw2rpclogo",
                "small_text":
                "GW2RPC Version {}\nhttps://gw2rpc.info".format(VERSION)
            }
        }
        return activity

    def main_loop(self):
        def gw2_running():
            if not self.process:
                return False
            if not self.process.is_running():
                return False
            return True

        try:
            while True:
                try:
                    self.update_gw2_process()
                    if not gw2_running():
                        raise GameNotRunningError
                    if not self.rpc.running:
                        self.rpc.start()
                        log.debug("starting self.rpc")
                    data = self.get_activity()
                    if not data:
                        data = self.in_character_selection()
                    log.debug(data)
                    self.rpc.send_rich_presence(data, self.process.pid)
                except GameNotRunningError:
                    #  TODO
                    if self.rpc.running:
                        self.rpc.last_payload = {}
                        self.rpc.last_pid = None
                        self.rpc.last_update = time.time()
                        self.game.last_character = None
                        self.game.last_map_id = None
                        self.rpc.close()
                        log.debug("Killing RPC")
                except DataUnchangedError:
                    pass
                time.sleep(config.update_frequency)
        except Exception as e:
            log.critical("GW2RPC has crashed", exc_info=e)
            create_msgbox(
                "GW2 Rich Presence has crashed.\nPlease check your "
                "log file and report this to the author!",
                code=16)
            self.shutdown()
