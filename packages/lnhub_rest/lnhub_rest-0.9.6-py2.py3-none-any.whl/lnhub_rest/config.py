import os
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlretrieve

from pydantic import BaseSettings, PostgresDsn


class Connector(BaseSettings):
    url: str
    key: str


def lamindb_client_config_settings(settings: BaseSettings) -> dict[str, Any]:
    connector_file, _ = urlretrieve(
        "https://lamin-site-assets.s3.amazonaws.com/connector.env"
    )
    connector = Connector(_env_file=connector_file)
    return dict(
        lamin_env="client",
        supabase_api_url=connector.url,
        supabase_anon_key=connector.key,
    )


class Settings(BaseSettings):
    lamin_env: str = "local"
    postgres_dsn: Optional[PostgresDsn]
    supabase_api_url: str
    supabase_anon_key: str
    supabase_service_key: Optional[str]
    ln_server_deploy: int = 0

    class Config:
        # This will look for an env file in the parent directory,
        # e.g. prod.env, staging.env, or local.env. Explicitly set
        # environment variables will take precendence over the ones
        # read in by file.

        env_file = (
            Path(__file__).parents[1] / f"lnhub-rest--{os.environ['LAMIN_ENV']}.env"
            if os.environ.get("LAMIN_ENV")
            else None
        )

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            # Following pattern here:
            # https://docs.pydantic.dev/usage/settings/#customise-settings-sources
            # in the absence of init and env settings, pull from S3
            return (init_settings, env_settings, lamindb_client_config_settings)
