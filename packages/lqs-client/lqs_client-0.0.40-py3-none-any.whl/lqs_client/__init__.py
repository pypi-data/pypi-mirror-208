import os
import logging
from distutils.util import strtobool

from dotenv import dotenv_values

logging.basicConfig(
    level=os.getenv("LQS_LOG_LEVEL") or logging.INFO,
    format="%(asctime)s  (%(levelname)s - %(name)s): %(message)s",
)
logger = logging.getLogger(__name__)

from .interface import (
    Lister,
    Getter,
    Creator,
    Updater,
    Deleter,
    S3,
    Utils,
    Node,
    Terminal,
)
from .gen import MessageGenerator


class LogQSClient:
    def __init__(
        self,
        api_url=None,
        api_key_id=None,
        api_key_secret=None,
        pretty=None,
        verbose=None,
        dry_run=None,
        retry_count=None,
        retry_delay=None,
        retry_aggressive=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_region=None,
        aws_session_token=None,
        aws_endpoint_url=None,
    ):
        self._env_config = {**dotenv_values(".env"), **os.environ}

        self._api_url = api_url if api_url else self._env_config.get("LQS_API_URL")
        if not self._api_url:
            raise ValueError("No API URL provided")
        self._api_key_id = (
            api_key_id if api_key_id else self._env_config.get("LQS_API_KEY_ID")
        )
        if not self._api_key_id:
            raise ValueError("No API Key ID provided")
        self._api_key_secret = (
            api_key_secret
            if api_key_secret
            else self._env_config.get("LQS_API_KEY_SECRET")
        )
        if not self._api_key_secret:
            raise ValueError("No API Key Secret provided")

        self._pretty = (
            pretty
            if pretty
            else bool(strtobool(self._env_config.get("LQS_PRETTY", "false")))
        )

        self._verbose = (
            verbose
            if verbose
            else bool(strtobool(self._env_config.get("LQS_VERBOSE", "false")))
        )

        if self._verbose:
            logger.setLevel(logging.DEBUG)

        self._dry_run = (
            dry_run
            if dry_run
            else bool(strtobool(self._env_config.get("LQS_DRY_RUN", "false")))
        )

        self._retry_count = (
            retry_count
            if retry_count is not None
            else int(self._env_config.get("LQS_RETRY_COUNT", 4))
        )
        if self._retry_count < 0:
            raise ValueError("Retry count must be greater than or equal to 0")

        self._retry_delay = (
            retry_delay
            if retry_delay is not None
            else int(self._env_config.get("LQS_RETRY_DELAY", 4))
        )
        if self._retry_delay < 0:
            raise ValueError("Retry delay must be greater than or equal to 0")

        self._retry_aggressive = (
            retry_aggressive
            if retry_aggressive is not None
            else bool(strtobool(self._env_config.get("LQS_RETRY_AGGRESSIVE", "false")))
        )

        self._aws_access_key_id = (
            aws_access_key_id
            if aws_access_key_id is not None
            else self._env_config.get("AWS_ACCESS_KEY_ID")
        )
        self._aws_secret_access_key = (
            aws_secret_access_key
            if aws_secret_access_key is not None
            else self._env_config.get("AWS_SECRET_ACCESS_KEY")
        )
        self._aws_region = (
            aws_region
            if aws_region is not None
            else self._env_config.get("AWS_DEFAULT_REGION")
        )
        self._aws_session_token = (
            aws_session_token
            if aws_session_token is not None
            else self._env_config.get("AWS_SESSION_TOKEN")
        )
        self._aws_endpoint_url = (
            aws_endpoint_url
            if aws_endpoint_url is not None
            else self._env_config.get("AWS_ENDPOINT_URL")
        )

        self.config = {
            "api_url": self._api_url,
            "api_key_id": self._api_key_id,
            "api_key_secret": self._api_key_secret,
            "pretty": self._pretty,
            "verbose": self._verbose,
            "dry_run": self._dry_run,
            "retry_count": self._retry_count,
            "retry_delay": self._retry_delay,
            "retry_aggressive": self._retry_aggressive,
            "aws_access_key_id": self._aws_access_key_id,
            "aws_secret_access_key": self._aws_secret_access_key,
            "aws_region": self._aws_region,
            "aws_session_token": self._aws_session_token,
            "aws_endpoint_url": self._aws_endpoint_url,
        }

        safe_config = {k: v for k, v in self.config.items()}

        obf_key = self._api_key_secret[:4] + "*" * (len(self._api_key_secret) - 4)
        safe_config["api_key_secret"] = obf_key

        if self._aws_secret_access_key:
            obf_aws_key = self._aws_secret_access_key[:4] + "*" * (
                len(self._aws_secret_access_key) - 4
            )
            safe_config["aws_secret_access_key"] = obf_aws_key

        logger.debug("config: %s", safe_config)

        self.list = Lister(config=self.config)
        self.get = Getter(config=self.config)
        self.create = Creator(config=self.config)
        self.update = Updater(config=self.config)
        self.delete = Deleter(config=self.config)

        self.s3 = S3(config=self.config, getter=self.get, creator=self.create)
        self.gen = MessageGenerator(getter=self.get, lister=self.list)
        self.utils = Utils(
            getter=self.get, s3=self.s3, gen=self.gen, config=self.config
        )
        self.node = Node(
            getter=self.get, lister=self.list, utils=self.utils, config=self.config
        )
        self.terminal = Terminal(getter=self.get, lister=self.list, config=self.config)


LogQS = LogQSClient
