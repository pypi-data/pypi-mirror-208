import os
from typing import Optional

from supabase import create_client

from ..config import Settings


# TODO: (@lawrlee) what is this URL used for?
def get_lamin_site_base_url():
    if "LAMIN_ENV" in os.environ:
        if os.environ["LAMIN_ENV"] == "local":
            return "http://localhost:3000"
        elif os.environ["LAMIN_ENV"] == "staging":
            return "https://staging.lamin.ai"
    return "https://lamin.ai"


def connect_hub():
    settings = Settings()
    return create_client(settings.supabase_api_url, settings.supabase_anon_key)
    # This is now handled in lnhub_rest.config.lamindb_client_config_settings
    # connector_file, _ = urlretrieve(
    #     "https://lamin-site-assets.s3.amazonaws.com/connector.env"
    # )
    # connector = Connector(_env_file=connector_file)
    # return create_client(connector.url, connector.key)


def connect_hub_with_auth(
    *,
    email: Optional[str] = None,
    password: Optional[str] = None,
    access_token: Optional[str] = None
):
    hub = connect_hub()
    if access_token is None:
        if email is None or password is None:
            from lndb._settings_load import load_or_create_user_settings

            user_settings = load_or_create_user_settings()
            email = user_settings.email
            password = user_settings.password
        access_token = get_access_token(email=email, password=password)
    hub.postgrest.auth(access_token)
    return hub


def connect_hub_with_service_role():
    settings = Settings()
    return create_client(settings.supabase_api_url, settings.service_key)


def get_access_token(email: Optional[str] = None, password: Optional[str] = None):
    hub = connect_hub()
    try:
        auth_response = hub.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        return auth_response.session.access_token
    finally:
        hub.auth.sign_out()
