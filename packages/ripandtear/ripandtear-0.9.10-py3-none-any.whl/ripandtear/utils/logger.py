import logging
import sys
from rich.logging import RichHandler


def create_logger(level=50):

    logging.basicConfig(level=level,
                        # stream=sys.stdout,
                        format="%(name)s — %(funcName)s:%(lineno)d — %(message)s",
                        datefmt='%Y/%m/%d %H:%M:%S',
                        handlers=[RichHandler()]
                        )
    httpx = logging.getLogger('httpx')
    httpx.setLevel(logging.WARNING)
