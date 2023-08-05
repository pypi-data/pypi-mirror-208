import logging

import fire

from . import LogQS

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  (%(levelname)s - %(name)s) : %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    fire.Fire(LogQS)
