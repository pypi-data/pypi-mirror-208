"""env.py."""
import os
from typing import Optional

from strangeworks_core.config.base import ConfigSource
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.utils import is_empty_str


class EnvConfig(ConfigSource):
    """Obtain configuration from environment variables.

    Environment variables are expected to be in the following format:
        STRANGEWORKS_CONFIG_{profile}_{key}
    where `profile` and `key` are non-empty strings in uppercase
    letters.
    """

    def get(self, key: str, profile: str = "default") -> Optional[str]:
        """Retrieve the values from environment variables.

        The method will convert all lowercase key or profile values to uppercase.
        """
        if is_empty_str(key) or is_empty_str(profile):
            return None

        env_var = EnvConfig._get_envvar_name(key=key, profile=profile)
        return os.getenv(env_var)

    def set(self, profile: str = "default", overwrite: bool = False, **params):
        """Set method for environment variables.

        Since environment variables are set externally, this method will raise an
        exception to inform the caller to update the environment variable manually.
        """
        for key, _ in params.items():
            envvar_name = EnvConfig._get_envvar_name(key=key, profile=profile)
            if envvar_name in os.environ:
                raise StrangeworksError.invalid_argument(
                    message=(
                        f"{envvar_name} is already set and the update will be ignored. "
                        "Please update the value of this environment variable manually."
                    ),
                )

    @staticmethod
    def _get_envvar_name(key: str, profile: str = "default"):
        return f"STRANGEWORKS_CONFIG_{profile.upper()}_{key.upper()}"
