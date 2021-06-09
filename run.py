import logging
import logging.handlers

from gw2rpc.gw2rpc import GW2RPC
from gw2rpc.settings import config

def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    handler = logging.handlers.RotatingFileHandler(
        filename="gw2rpc.log", maxBytes=5 * 1024 * 1024, encoding='utf-8')
    handler.setFormatter(formatter)
    #    stderr_hdlr = logging.StreamHandler()
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    #    logger.addHandler(stderr_hdlr)
    logger.addHandler(handler)


if __name__ == "__main__":
    setup_logging()
    rpc = GW2RPC()
    rpc.main_loop()
