import logging

import requests

from .settings import config

log = logging.getLogger()


class APIError(Exception):
    def __init__(self, code):
        self.code = code

class GW2Api:
    def __init__(self, key=None):
        def check_key(key):
            try:
                res = self._call_api("tokeninfo", key=key)
                required_permissions = ["characters", "builds", "account"]
                for p in required_permissions:
                    if p not in res["permissions"]:
                        return False
                log.info("API key verified")
                return True
            except APIError:
                return False

        def get_world():
            try:
                res = self._call_api("account")
                ep = "worlds/{}".format(res["world"])
                return self._call_api(ep)["name"]
            except (APIError, KeyError):
                return None

        self.__session = requests.Session()
        self._base_url = "https://api.guildwars2.com/v2/"
        self.__headers = {
            'User-Agent': "GW2RPC - Discord Rich Presence addon",
            'Accept': 'application/json'
        }
        self._authenticated = False
        if key:
            if check_key(key):
                self.__headers.update(Authorization="Bearer " + key)
                self._authenticated = True
        self.__session.headers.update(self.__headers)
        if self._authenticated:
            self.world = get_world()
        else:
            self.world = None

    def get_map_info(self, map_id):
        return self._call_api("maps/" + str(map_id))

    def get_continent_info(self, map_info):
        ep = ("continents/{continent_id}/floors/{default_floor}/regi"
              "ons/{region_id}/maps/{id}".format(**map_info))
        print(ep)
        return self._call_api(ep)

    def get_character(self, name):
        if not self._authenticated:
            return None
        return self._call_api("characters/" + name)

    def get_guild(self, gid):
        return self._call_api("guild/" + gid)

    def _call_api(self, endpoint, *, key=None):
        url = self._base_url + endpoint
        if key:
            headers = {**self.__headers, **{"Authorization": "Bearer " + key}}
            r = requests.get(url, headers=headers)
        else:
            r = self.__session.get(url)
        if r.status_code != 200:
            raise APIError(r.status_code)
        return r.json()


api = GW2Api(config.api_key)
