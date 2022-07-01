import logging
from .lib.discordsdk import *

from .settings import config


log = logging.getLogger()
log.setLevel(config.log_level)

class DiscordSDK:
    def __init__(self, client_id) -> None:
        self.client_id = client_id
        self.start()
        self.activity = Activity()

    def start(self):
        try:
            self.app = Discord(int(self.client_id), CreateFlags.no_require_discord)
            self.activity_manager = self.app.get_activity_manager()
        except:
            self.app = None
            self.activity_manager = None
            log.debug("Discord not running.")

    def set_activity(self, a):
        self.activity.state = a["state"]
        self.activity.details = a["details"]
        if a["timestamps"]:
            self.activity.timestamps.start = a["timestamps"]["start"]
        self.activity.assets.small_image = a["assets"]["small_image"]
        self.activity.assets.small_text = a["assets"]["small_text"]
        self.activity.assets.large_image = a["assets"]["large_image"]
        self.activity.assets.large_text = a["assets"]["large_text"]

        #self.activity.buttons = a["buttons"][0]

        #self.activity.party.id = str(uuid.uuid4())
        #self.activity.secrets.join = str(uuid.uuid4())

        try:
            self.activity_manager.update_activity(self.activity, self.callback)
        except OSError:
            log.debug("Error reading activity manager.")
            pass

    def close(self):
        try:
            self.app = None
        except:
            pass

    def callback(self, result):
        if result == Result.ok:
            log.debug("Successfully set the activity!")
        else:
            pass
            #raise Exception(result)