import ctypes
import logging
import os
import sys
import threading
import time
import webbrowser
import math
from datetime import datetime, timedelta
import time

import psutil
import requests
from infi.systray import SysTrayIcon
import gettext
import urllib.parse

from .api import APIError, api  
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

VERSION = 2.35
HEADERS = {'User-Agent': 'GW2RPC v{}'.format(VERSION)}

GW2RPC_BASE_URL = "https://gw2rpc.info/api/v2/"

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


        def fetch_registry():
            
            # First one only for building
            # Only used for debugging without the web based API
            #registry_path = resource_path('./data/registry.json')
            #registry_path = resource_path('../data/registry.json')
            #registry = json.loads(open(registry_path).read())
            #return registry

            url = GW2RPC_BASE_URL + "registry"
            try:
                res = requests.get(url, headers=HEADERS)
            except:
                # Client side error, mostly DNS failure or firewall blocking connection
                # -> fallback to local registry
                log.error(f"Could not open connection to {url}. Web API will not be available!")
                return None
            if res.status_code != 200:
                # Server side error, fall back to local registry
                log.error("Could not fetch the web registry")
                return None
            return res.json()


        def fetch_support_invite():
            try:
                return requests.get(GW2RPC_BASE_URL +
                                    "support", headers=HEADERS).json()["support"]
            except:
                return None

        self.rpc = DiscordRPC(GW2RPC_APP_ID)
        self.registry = fetch_registry()
        self.support_invite = fetch_support_invite()
        self.process = None
        self.last_map_info = None
        self.last_continent_info = None
        self.last_boss = None
        self.boss_timestamp = None
        self.commander_webhook_sent = False
        self.no_pois = set()
        self.check_for_updates()
        self.game = None
        self.mumble_links = self.get_mumble_links()
        self.mumble_objects = self.create_mumble_objects()
        # Select the first mumble object as initially in focus
        if len(self.mumble_objects) > 0:
            self.game = self.mumble_objects[0][0]
        #else:
        #    self.game = MumbleData()

    def get_systray_menu(self):
        menu_options = ((_("About"), None, self.about), )
        if self.support_invite:
            menu_options += ((_("Join support server"), None, self.join_guild), )
        if config.webhooks:
            yes_no = _("Yes") if config.announce_raid else _("No")
            menu_options += ((_("Announce raids:") + f" {yes_no}", None, self.toggle_announce_raid), )
        return menu_options

    def create_systray(self):
        def icon_path():
            try:
                return os.path.join(sys._MEIPASS, "icon.ico")
            except:
                return "icon.ico"
        menu_options = self.get_systray_menu()
        self.systray = SysTrayIcon(
            icon_path(),
            _("Guild Wars 2 with Discord"),
            menu_options,
            on_quit=self.shutdown)
        self.systray.start()

    def get_mumble_links(self):
        """
        Search for running Gw2 processes and check for their mumbleLink Parameter field
        Adds them to a list, or adds the default 'MumbleLink' if there are no parameters
        Returns a list of tuples of str: mumbleLink and process
        """
        mumble_links = set()
        try:
            for process in psutil.process_iter():
                pinfo = process.as_dict(attrs=['pid', 'name', 'cmdline'])
                if pinfo['name'] in ("Gw2-64.exe", "Gw2.exe"):
                    cmdline = pinfo['cmdline']
                    try:
                        mumble_links.add((cmdline[cmdline.index('-mumble') + 1], process))
                    except ValueError:
                        mumble_links.add(("MumbleLink", process))
                    except AttributeError:
                        log.error("GW2 process crashed!")
                        continue
        except psutil.NoSuchProcess:
            pass
        return mumble_links

    def create_mumble_objects(self):
        """
        Creates the datastructure MumbleData for all known mumble_link names
        Returns a list of tuples of mumble object and process
        """
        mumble_objects = []
        for m, p in self.mumble_links:
            o = MumbleData(m)
            if not o.memfile:
                o.create_map()
            mumble_objects.append((o, p))
        return mumble_objects

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

    def toggle_announce_raid(self, _):
        config.announce_raid = not config.announce_raid
        config.change_boolean_item("Webhooks", "AnnounceRaid", config.announce_raid)
        menu_options = self.get_systray_menu()
        self.systray.update(menu_options=menu_options)

    def check_for_updates(self):
        def get_build():
            url = GW2RPC_BASE_URL + "build"
            try:
                r = requests.get(url, headers=HEADERS)
            except:
                log.error(f"Could not open connection to {url}")
                return None
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
        for o, p in self.mumble_objects:
            o.get_mumble_data(process=p)
            if o.in_focus:
                return (o, p)
        return None, None

    def get_map_asset(self, map_info, mount_index=None):
        map_id = map_info["id"]
        map_name = map_info["name"]
        region = str(map_info.get("region_id", "thanks_anet"))

        position = self.game.get_position()
        #print("{} {} Region {}".format(map_id, map_name, region))
        #print("{} {} {}".format(position.x, position.y, position.z))
        #m_x, m_y = self.convert_mumble_coordinates(map_info, position)
        #print("Relative: {} {}".format(m_x, m_y))
        #print("--------------------------")
        
        if self.registry:
            if region == "26":  #  Fractals of the Mists 
                image = "fotm"
                for fractal in self.registry["fractals"]:
                    state, name = self.find_fractal_boss(map_id, fractal, position)
                    if name:
                        image = name.replace('.', "_").lower().replace(" ", "_")
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
                    # Not sure if this even works but i dont want to touch it
                    image = self.registry["special"][map_name]
                elif str(map_id) in self.registry["special"]:
                    # Many strike instances share the same ID, with this we only have to keep one asset in discord
                    image = self.registry["special"][str(map_id)]
                elif map_id in self.registry["valid"]:
                    image = map_id
                elif region in self.registry["regions"]:
                    image = self.registry["regions"][region]
                else:
                    image = "default"
                name = map_name
                mounts = self.registry["mounts"].keys()
                if not config.hide_mounts and mount_index and str(mount_index) in mounts:
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

        def update_mumble_links():
            all_links = self.get_mumble_links()
            new_links = all_links.difference(self.mumble_links)
            dead_links = self.mumble_links.difference(all_links)

            #print(f"Previous active links {self.mumble_links}")
            #print(f"All currently active links {all_links}")
            #print(f"Newly discovered links {new_links}")
            #print(f"Now dead links {dead_links}")

            # Remove dead links
            for m, p1 in dead_links:
                for o, p2 in self.mumble_objects:
                    # Kill the object
                    if o.mumble_link == m:
                        o.close_map
                        self.mumble_objects.remove((o, p2))
                        del o
                self.mumble_links.remove((m, p1))

            # Initialize the newly found Mumble Links
            for m, p in new_links:
                o = MumbleData(m)
                if not o.memfile:
                    o.create_map()
                self.mumble_objects.append((o, p))
                self.mumble_links.add((m, p))

            # Every found mumble link is new -> was empty before
            # Set the first object to game
            if all_links and all_links == new_links:
                self.game = self.mumble_objects[0][0]

        update_mumble_links()
        active, active_p = self.get_active_instance()
        self.game = active if active else self.game
        self.process = active_p if active_p else self.process
        # TODO maybe self.process instead of active_p here?
        data = self.game.get_mumble_data(process=active_p)
        if not data:
            return None
        buttons = []
        map_id = data["map_id"]
        is_commander = data["commander"]
        mount_index = data["mount_index"]
        in_combat = data["in_combat"]
        copy_paste_url = None
        point = None
        try:
            if self.last_map_info and map_id == self.last_map_info["id"]:
                map_info = self.last_map_info
            else:
                map_info = api.get_map_info(map_id)
                self.last_map_info = map_info
            character = Character(data)
        except APIError:
            log.error("API Error!")
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
        elif self.registry and map_id in [f["id"] for f in self.registry["fractals"]]:
            timestamp = self.boss_timestamp or self.game.last_timestamp
        else:
            self.last_boss = None
            if self.last_continent_info:
                point = get_closest_poi(map_info, continent_info)
                if point:
                    map_asset["large_text"] += _(" near ") + point["name"]
                    if not config.hide_poi_button:
                        payload = {'chat_code': point["chat_link"], 'name': point["name"], 'character': character.name}
                        copy_paste_url = "https://gw2rpc.info/copy-paste?" + urllib.parse.urlencode(payload)
                        buttons.append({"label": _("Closest") + " PoI: {}".format(point["chat_link"]), "url": copy_paste_url})
        map_asset["large_text"] += get_region()

        if not config.hide_commander_tag and is_commander:
            small_image = "commander_tag"
            details = "{}: {}".format(_("Commander"), details)
        elif character.race == "Jade Bot":
            small_image = "jade_bot"
        else: 
            small_image = character.profession_icon
        if in_combat:
            details = "{} {}".format(details, "⚔️")
        small_text = "{} {} {}".format(_(character.race), _(character.profession), tag)
        buttons.append({"label": "GW2RPC.info ↗️", "url": "https://gw2rpc.info"})

        if config.announce_raid and is_commander and not self.commander_webhook_sent:
            region = map_info.get("region_id")
            if not config.disable_raid_announce_in_wvw or region != 7:
                copy_paste_url = copy_paste_url or "https://gw2rpc.info"
                chat_link = f"*{point['name']}: `{point['chat_link']}`*" if point else None
                for u in config.webhooks:
                    self.send_webhook(u, character.name, _(state), copy_paste_url, character.profession, chat_link)
                self.commander_webhook_sent = True
        if not is_commander and self.commander_webhook_sent:
            self.commander_webhook_sent = False

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
            "state": _("in character selection") + " / " + _("loading screen"),
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
                        # z coordinate, only needed in uncategorized
                        if (len(boss["coord"]) > 2 and "height" in boss
                         and position.z - 1 >= boss["coord"][2] and position.z <= boss["coord"][2] + boss["height"]) or len(boss["coord"]) <= 2:
                            state = _("fighting ") + _(boss["name"]) + " " + _("in ") + _(fractal["name"])
                            if self.last_boss != boss["name"]:
                                self.boss_timestamp = int(time.time())
                            self.last_boss = boss["name"]
                            return state, boss["name"]
                else:
                    self.boss_timestamp = None
                    self.last_boss = None
                    state = _("in ") + _("fractal") + ": " + _(fractal["name"])
            except KeyError:
                self.boss_timestamp = None
                self.last_boss = None
                state = _("in ") + _("fractal") + ": " + _(fractal["name"])
        return state, None

    def send_webhook(self, url, name, map, website_url, profession, poi=None):
        # Get timestamp with utc offset
        timestamp = datetime.now()
        ts = time.time()
        utc_offset = (datetime.fromtimestamp(ts) -
              datetime.utcfromtimestamp(ts)).total_seconds()
        timestamp = (timestamp - timedelta(seconds=utc_offset)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        logo_url = "https://gw2rpc.info/static/img/logo.png"
        profession_url = f"https://gw2rpc.info/static/img/professions/prof_{profession.lower()}.png"

        data = {
            "username": "GW2RPC",
            "avatar_url": logo_url
        }
        data["embeds"] = [
            {
                "author": {
                    "name": _("GW2RPC Raid Announcer"),
                    "icon_url": profession_url,
                    "url": "https://gw2rpc.info"
                },
                "thumbnail": {
                    "url": "https://gw2rpc.info/static/img/professions/commander_tag.png"
                },
                "footer": {
                    "text": "by GW2RPC https://gw2rpc.info",
                    "icon_url": logo_url
                },
                "title" : f"{name} " + _("tagged up") + f" {map}",
                "url": website_url,
                "color": "12660011",
                "timestamp": timestamp,
                "fields": [
                    {
                        "name": _("Copy and paste the following to join"),
                        "value": f"`/sqjoin {name}`"
                    }
                ]
            }
        ]  
        if poi: 
            data["embeds"][0]["fields"].append({"name": _("Closest PoI"), "value": f"{poi}"})

        try:
            result = requests.post(url, json = data)
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            log.error(err)
        except:
            log.error(f"Invalid webhook url: {url}")

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

        def check_for_running_rpc():
            count = 0
            try:
                for process in psutil.process_iter(attrs=['name']):
                    name = process.info['name']
                    if name == "gw2rpc.exe":
                        count += 1
                    if count > 2:
                        break
                else:
                    return
            except psutil.NoSuchProcess:
                log.debug("A process exited while iterating over the process list.")
                pass   
            log.warning("Another gw2rpc process is already running, exiting.")
            if self.rpc.running:
                self.rpc.close()
                log.debug("Killing RPC")
            self.shutdown()

        try:
            check_for_running_rpc()
            self.create_systray()
            while True:
                try:
                    update_gw2_process()
                    if self.game and not self.game.memfile:
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
                    if self.game:
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
