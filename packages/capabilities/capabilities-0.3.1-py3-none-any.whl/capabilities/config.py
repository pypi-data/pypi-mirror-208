from dataclasses import dataclass
import os
from typing import Optional
import pydantic
from pathlib import Path
from rich import print
import sys

from capabilities.util.config import SecretPersist, get_app_config_dir

CONFIG_DIR = get_app_config_dir("capabilities")


class Config(pydantic.BaseSettings, SecretPersist):
    api_key: Optional[pydantic.SecretStr] = pydantic.Field(default=None, is_secret=True)
    api_url: str = "https://api.blazon.ai"

    @property
    def secrets_file(self) -> Path:
        return CONFIG_DIR / "secrets.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "CAPABILITIES_"
        secret_postfix = lambda self: self.api_url

    def get_api_key(self) -> Optional[str]:
        api_key = self.get_secret("api_key")
        if api_key is None and not getattr(self, "_api_key_warned", False):
            print(
                (
                    r" \[[red bold]warning[/]\] "
                    "CAPABILITIES_API_KEY not set, get one here: https://blazon.ai/signin"
                    "\n"
                ),
                file=sys.stderr,
            )
            self._api_key_warned = True
        assert isinstance(api_key, Optional[str])
        return api_key


CONFIG = Config()
