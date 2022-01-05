import ctypes
import logging
import os
import sys
import threading
import time
import webbrowser
import math

import psutil
import requests
from infi.systray import SysTrayIcon
import gettext
import urllib.parse

from .api import APIError, api  # TODO
from .character import Character
from .mumble import MumbleData
from .rpc import DiscordRPC
from .settings import config

import sys
import os
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

VERSION = 2.21

GW2RPC_BASE_URL = "https://gw2rpc.info/api/v2/"
#GW2RPC_BASE_URL = "http://localhost:5000/api/v2/"

GW2RPC_APP_ID = "385475290614464513"

log = logging.getLogger()

# First one only for building
#locales_path = resource_path("./locales")
locales_path = resource_path("../locales")

lang = gettext.translation('base', localedir=locales_path, languages=[config.lang])
lang.install()
_ = lang.gettext

class GameNotRunningError(Exception):
    pass


worlds = {
    'NA': [
        _('Anvil Rock'), _('Blackgate'), _('Borlis Pass'), _('Crystal Desert'),
        _('Darkhaven'), _("Devona's Rest"), _('Dragonbrand'), _('Ehmry Bay'),
        _('Eredon Terrace'), _("Ferguson's Crossing"), _('Fort Aspenwood'),
        _('Gate of Madness'), _('Henge of Denravi'), _('Isle of Janthir'),
        _('Jade Quarry'), _('Kaineng'), _('Maguuma'), _('Northern Shiverpeaks'),
        _('Sanctum of Rall'), _('Sea of Sorrows'), _("Sorrow's Furnace"),
        _('Stormbluff Isle'), _('Tarnished Coast'), _("Yak's Bend")
    ],
    'EU': [
        _('Aurora Glade'), _('Blacktide'), _('Desolation'), _('Far Shiverpeaks'),
        _('Fissure of Woe'), _('Gandara'), _("Gunnar's Hold"), _('Piken Square'),
        _('Ring of Fire'), _('Ruins of Surmia'), _("Seafarer's Rest"), _('Underworld'),
        _('Vabbi'), _('Whiteside Ridge'), _('Arborstone [FR]'), _('Augury Rock [FR]'),
        _('Fort Ranik [FR]'), _('Jade Sea [FR]'), _('Vizunah Square [FR]'),
        _("Abaddon's Mouth [DE]"), _('Drakkar Lake [DE]'), _('Dzagonur [DE]'),
        _('Elona Reach [DE]'), _('Kodash [DE]'), _("Miller's Sound [DE]"),
        _('Riverside [DE]'), _('Baruch Bay [SP]')
    ]
}


def create_msgbox(description, *, title='GW2RPC', code=0):
    MessageBox = ctypes.windll.user32.MessageBoxW
    return MessageBox(None, description, title, code)


class GW2RPC:
    def __init__(self):

        def get_mumble_links():
            """
            Search for running Gw2 processes and check for their mumbleLink Parameter field
            Adds them to a list, or adds the default 'MumbleLink' if there are no parameters
            """
            mumble_links = set()
            try:
                for process in psutil.process_iter():
                    pinfo = process.as_dict(attrs=['pid', 'name', 'cmdline'])
                    if pinfo['name'] in ("Gw2-64.exe", "Gw2.exe"):
                        cmdline = pinfo['cmdline']
                        try:
                            mumble_links.add(cmdline[cmdline.index('-mumble') + 1])
                        except ValueError:
                            mumble_links.add("MumbleLink")
            except psutil.NoSuchProcess:
                pass
            return mumble_links

        def create_mumble_objects():
            """
            Creates the datastructure MumbleData for all known mumble_link names
            """
            mumble_links = get_mumble_links()
            mumble_objects = []
            for m in mumble_links:
                o = MumbleData(m)
                if not o.memfile:
                    o.create_map()
                mumble_objects.append(o)
            return mumble_objects

        def fetch_registry():
            
            # First one only for building
            # Only used for debugging without the web based API
            #registry_path = resource_path('./data/registry.json')
            #registry_path = resource_path('../data/registry.json')
            #registry = json.loads(open(registry_path).read())
            #return registry

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
                return requests.get(GW2RPC_BASE_URL +
                                    "support").json()["support"]
            except:
                return None

        self.rpc = DiscordRPC(GW2RPC_APP_ID)
        self.game = MumbleData()
        self.registry = fetch_registry()
        self.support_invite = fetch_support_invite()
        menu_options = ((_("About"), None, self.about), )
        if self.support_invite:
            menu_options += ((_("Join support server"), None, self.join_guild), )
        self.systray = SysTrayIcon(
            icon_path(),
            _("Guild Wars 2 with Discord"),
            menu_options,
            on_quit=self.shutdown)
        self.systray.start()
        self.process = None
        self.last_map_info = None
        self.last_continent_info = None
        self.last_boss = None
        self.boss_timestamp = None
        self.no_pois = set()
        self.check_for_updates()
        self.mumble_objects = create_mumble_objects()

    def shutdown(self, _=None):
        os._exit(0)  # Nuclear option

    def about(self, _):
        message = (
            "Version: {}\n\nhttps://gw2rpc.info\n\nBy Maselkov & "
            "N1tR0\nIcons by Zebban\nWebsite by Penemue\nTranslations by Seshu (de), TheRaytheone (es), z0n3g (fr)".format(VERSION))
        threading.Thread(target=create_msgbox, args=[message]).start()

    def join_guild(self, _):
        try:
            webbrowser.open(self.support_invite)
        except webbrowser.Error:
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
                _("Could not check for updates - check your connection!"))
            return
        if build > VERSION:
            log.info("New version found! Current: {} New: {}".format(
                VERSION, build))
            res = create_msgbox(
                _("There is a new update for GW2 Rich Presence available. "
                "Would you like to be taken to the download page now?"),
                code=68)
            if res == 6:
                webbrowser.open("https://gw2rpc.info/")

    def get_active_instance(self):
        """
        Iterates through all known Mumble Links, reads data from memfile and checks whether the instance is active
        """
        for o in self.mumble_objects:
            o.get_mumble_data()
            if o.in_focus:
                return o

    def get_map_asset(self, map_info, mount_index=None):
        map_id = map_info["id"]
        map_name = map_info["name"]
        region = str(map_info.get("region_id", "thanks_anet"))

        position = self.game.get_position()
        #print("{} {}".format(position.x, position.y))
        #print("{} {}".format(map_id, map_name))
        #print("{} {}".format(position.x, position.y))
        
        if self.registry:
            if region == "26":  #  Fractals of the Mists 
                image = "fotm"
                for fractal in self.registry["fractals"]:
                    state = self.find_fractal_boss(map_id, fractal, position)
                    if state:
                        break

                    if fractal["id"] == map_id:
                        state = _("in ") + _("fractal") + ": " + _(fractal["name"]) 
                        break
                else:
                    if not state:
                        state = _("in ") + _("Fractals of the Mists")
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
                mounts = self.registry["mounts"].keys()
                if mount_index and str(mount_index) in mounts:
                    mount = self.registry["mounts"][str(mount_index)]
                    state = _("on") + " " + _(mount) + " " + _("in ") + name
                else:
                    state = _("in ") + name
        else:
            # Fallback for api
            special = {
                "1068": "gh_hollow", 
                "1101": "gh_hollow", 
                "1107": "gh_hollow", 
                "1108": "gh_hollow", 
                "1121": "gh_hollow", 
                "1069": "gh_precipice", 
                "1076": "gh_precipice", 
                "1071": "gh_precipice", 
                "1104": "gh_precipice", 
                "1124": "gh_precipice", 
                "882": "wintersday_snowball",
                "877": "wintersday_snowball", 
                "1155": "1155", 
                "1214": "gh_haven", 
                "1215": "gh_haven", 
                "1232": "gh_haven", 
                "1224": "gh_haven", 
                "1243": "gh_haven", 
                "1250": "gh_haven"
            }.get(map_info["id"])
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
            state = _("in ") + name
        return state, {"large_image": str(image), "large_text":  _(name)}

    def get_raid_assets(self, map_info, mount_index=None):
        def readable_id(_id):
            _id = _id.split("_")
            dont_capitalize = ("of", "the", "in")
            return " ".join([
                x.capitalize() if x not in dont_capitalize else x for x in _id
            ])

        boss = self.find_closest_boss(map_info)
        if not boss:
            self.boss_timestamp = None
            return self.get_map_asset(map_info, mount_index)
        if boss["type"] == "boss":
            state = _("fighting ")
        else:
            state = _("completing ")
        name = _(readable_id(boss["id"]))
        state += name
        if self.last_boss != boss["id"]:
            self.boss_timestamp = int(time.time())
        self.last_boss = boss["id"]
        return state, {
            "large_image": boss["id"],
            "large_text": name + " - {}".format(map_info["name"])
        }

    def get_activity(self):
        def get_region():
            world = api.world
            if world:
                for k, v in worlds.items():
                    if world in v:
                        return " [{}]".format(k)
            return ""

        def get_closest_poi(map_info, continent_info):
            #region = map_info.get("region_name")
            region = map_info.get("region_id")
            if config.disable_pois:
                return None
            if config.disable_pois_in_wvw and region == 7:
                return None
            return self.find_closest_point(map_info, continent_info)

        buttons = []
        active = self.get_active_instance()
        self.game = active if active else self.game
        data = self.game.get_mumble_data()
        if not data:
            return None
        map_id = data["map_id"]
        is_commander = data["commander"]
        mount_index = data["mount_index"]
        try:
            if self.last_map_info and map_id == self.last_map_info["id"]:
                map_info = self.last_map_info
            else:
                map_info = api.get_map_info(map_id)
                self.last_map_info = map_info
            character = Character(data)
        except APIError:
            log.exception("API Error!")
            self.last_map_info = None
            return None
        state, map_asset = self.get_map_asset(map_info, mount_index=mount_index)
        tag = character.guild_tag if config.display_tag else ""
        try:
            if map_id in self.no_pois or "continent_id" not in map_info:
                raise APIError(404)
            if (self.last_continent_info
                    and map_id == self.last_continent_info["id"]):
                continent_info = self.last_continent_info
            else:
                continent_info = api.get_continent_info(map_info)
                self.last_continent_info = continent_info
        except APIError:
            self.last_continent_info = None
            self.no_pois.add(map_id)
        details = character.name + tag
        timestamp = self.game.last_timestamp
        if self.registry and str(map_id) in self.registry.get("raids", {}):
            state, map_asset = self.get_raid_assets(map_info, mount_index)
            timestamp = self.boss_timestamp or self.game.last_timestamp
        else:
            self.last_boss = None
            if self.last_continent_info:
                point = get_closest_poi(map_info, continent_info)
                if point:
                    map_asset["large_text"] += _(" near ") + point["name"]
                    if not config.hide_poi_button:
                        payload = {'chat_code': point["chat_link"], 'name': point["name"]}
                        url = "https://gw2rpc.info/copy-paste?" + urllib.parse.urlencode(payload)
                        buttons.append({"label": _("Closest") + " PoI: {}".format(point["chat_link"]), "url": url})
        map_asset["large_text"] += get_region()

        if not config.hide_commander_tag and is_commander:
            small_image = "commander_tag"
            details = "{}: {}".format(_("Commander"), details)
        else: 
            small_image = character.profession_icon
        small_text = "{} {} {}".format(_(character.race), _(character.profession), tag)
        buttons.append({"label": "GW2RPC.info ↗️", "url": "https://gw2rpc.info"})

        activity = {
            "state": _(state),
            "details": details,
            "timestamps": {
                'start': timestamp
            },
            "assets": {
                **map_asset, "small_image": small_image,
                "small_text": small_text
            },
            "buttons": buttons
        }
        return activity

    def in_character_selection(self):
        activity = {
            "state": _("in character selection"),
            "assets": {
                "large_image":
                "default",
                "large_text":
                _("Character Selection"),
                "small_image":
                "gw2rpclogo",
                "small_text":
                "GW2RPC Version {}\nhttps://gw2rpc.info".format(VERSION)
            },
            "buttons": [{"label": "GW2RPC.info ↗️", "url": "https://gw2rpc.info"}]
        }
        return activity

    def convert_mumble_coordinates(self, map_info, position):
        crect = map_info["continent_rect"]
        mrect = map_info["map_rect"]
        x = crect[0][0] + (position.x - mrect[0][0]) / 24
        y = crect[0][1] + (mrect[1][1] - position.y) / 24
        return x, y

    def find_closest_point(self, map_info, continent_info):
        position = self.game.get_position()
        x_coord, y_coord = self.convert_mumble_coordinates(map_info, position)
        lowest_distance = float("inf")
        point = None
        for item in continent_info["points_of_interest"].values():
            if "name" not in item:
                continue
            distance = (item["coord"][0] - x_coord)**2 + (
                item["coord"][1] - y_coord)**2
            if distance < lowest_distance:
                lowest_distance = distance
                point = item
        return point

    def find_closest_boss(self, map_info):
        position = self.game.get_position()
        x_coord, y_coord = self.convert_mumble_coordinates(map_info, position)
        closest = None
        for boss in self.registry["raids"][str(map_info["id"])]:
            distance = math.sqrt((boss["coord"][0] - x_coord)**2 +
                                 (boss["coord"][1] - y_coord)**2)
            if "radius" in boss and distance < boss["radius"]:
                if "height" in boss:
                    if position.z < boss["height"]:
                        closest = boss
                else:
                    closest = boss
        return closest

    def find_fractal_boss(self, map_id, fractal, position):
        state = None
        if fractal["id"] == map_id:
            try:
                for boss in fractal["bosses"]:
                    distance = math.sqrt((boss["coord"][0] - position.x)**2 +
                                (boss["coord"][1] - position.y)**2)
                    
                    if distance <= boss["radius"]:
                        state = _("fighting ") + _(boss["name"]) + " " + _("in ") + _(fractal["name"])
                        return state
                    else:
                        state = _("in ") + _("fractal") + ": " + _(fractal["name"])
            except KeyError:
                state = _("in ") + _("fractal") + ": " + _(fractal["name"])
        return state
        
    def main_loop(self):
        def update_gw2_process():
            shutdown = False
            if self.process:
                if self.process.is_running():
                    return
                else:
                    if config.close_with_gw2:
                        shutdown = True
            try:
                for process in psutil.process_iter(attrs=['name']):
                    name = process.info['name']
                    if name in ("Gw2-64.exe", "Gw2.exe"):
                        self.process = process
                        return
            except psutil.NoSuchProcess:
                log.debug("A process exited while iterating over the process list.")
                pass

            if shutdown:
                self.shutdown()
            self.process = None
            raise GameNotRunningError

        def start_rpc():
            while True:
                try:
                    self.rpc.start()
                    break
                except (FileNotFoundError, PermissionError) as e:
                    time.sleep(10)

        try:
            while True:
                try:
                    update_gw2_process()
                    if not self.game.memfile:
                        self.game.create_map()
                    if not self.rpc.running:
                        start_rpc()
                        log.debug("starting self.rpc")
                    try:
                        data = self.get_activity()
                    except requests.exceptions.ConnectionError:
                        raise GameNotRunningError
                    if not data:
                        data = self.in_character_selection()
                    log.debug(data)
                    try:
                        self.rpc.send_rich_presence(data, self.process.pid)
                    except BrokenPipeError:
                        raise GameNotRunningError  # To start a new connection
                except GameNotRunningError:
                    #  TODO
                    self.game.close_map()
                    if self.rpc.running:
                        self.rpc.close()
                        log.debug("Killing RPC")
                time.sleep(15)
        except Exception as e:
            log.critical("GW2RPC has crashed", exc_info=e)
            create_msgbox(
                "GW2 Rich Presence has crashed.\nPlease check your "
                "log file and report this to the author!",
                code=16)
            self.shutdown()
