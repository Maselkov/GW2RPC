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
                        log.warning(
                            "API key missing required permission: {}".format(
                                p))
                        return False
                log.info("API key verified")
                return True
            except APIError:
                return False

        def get_account_and_world():
            try:
                res = self._call_api("account")
                ep = "worlds/{}".format(res["world"])
                return res["name"], self._call_api(ep)["name"]
            except (APIError, KeyError):
                return None, None

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
            self.account, self.world = get_account_and_world()
        else:
            self.account, self.world = None, None

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


class MultiApi:
    def __init__(self, keys):
        self._unauthenticated_client = GW2Api()
        self._clients = [GW2Api(k) for k in keys]
        self._clients = [c for c in self._clients if c._authenticated]
        self._authenticated = len(self._clients) != 0
        self._last_used_client = None
        self.account, self.world = (
            self._clients[0].account,
            self._clients[0].world) if self._authenticated else (None, None)

    def get_map_info(self, map_id):
        return self._unauthenticated_client.get_map_info(map_id)

    def get_character(self, name):
        if self._last_used_client:
            try:
                return self._last_used_client.get_character(name)
            except APIError:
                pass
        for client in self._clients:
            try:
                c = client.get_character(name)
                self._last_used_client = client
                self.account, self.world = client.account, client.world
                return c
            except APIError:
                pass
        # intentionally cause an error as no API key matches
        return self._unauthenticated_client.get_character(name)

    def get_guild(self, gid):
        if self._last_used_client:
            return self._last_used_client.get_guild(gid)
        # intentionally cause an error as there should have been a character request first
        return self._unauthenticated_client.get_guild(gid)


api = MultiApi(config.api_keys)
