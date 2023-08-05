from lamin_logger import logger

from lnhub_rest import check_breaks_lndb_and_error
from lnhub_rest.orm._sbclient import connect_hub, get_lamin_site_base_url
from lnhub_rest.utils._id import secret


def sign_up_hub(email) -> str:
    from lndb._settings_store import settings_dir

    hub = connect_hub()
    check_breaks_lndb_and_error(hub)
    password = secret()  # generate new password
    auth_response = hub.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {"redirect_to": f"{get_lamin_site_base_url()}/signup"},
        }
    )
    user = auth_response.user
    # if user already exists a fake user object without identity is returned
    if auth_response.user.identities:
        # if user had called sign-up before, but not confirmed their email
        # the user has an identity with a wrong ID
        # we can check for it by comparing time stamps
        # see design note uL8Sjht0y4qg
        diff = user.confirmation_sent_at - user.identities[0].last_sign_in_at
        if (
            diff.total_seconds() > 0.1
        ):  # the first time, this is on the order of microseconds
            raise RuntimeError(
                "It seems you already signed up with this email. Please click on the"
                " link in the confirmation email that you should have received from"
                " lamin.ai."
            )
        usettings_file = settings_dir / f"user-{email}.env"
        logger.info(
            "Please *confirm* the sign-up email. After that, login with `lndb login"
            f" {email}`!\n\n"
            f"Generated password: {password}\n"
            f"Email & password are cached: {usettings_file}\n"  # noqa
            "Going forward, credentials are auto-loaded! "  # noqa
            "In case of loss, recover your password via email: https://lamin.ai"
        )
        return password
    else:
        return "user-exists"


def sign_in_hub(email, password, handle=None):
    hub = connect_hub()
    check_breaks_lndb_and_error(hub)
    try:
        auth_response = hub.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
                "options": {"redirect_to": f"{get_lamin_site_base_url()}/signup"},
            }
        )
    except Exception as exception:  # this is bad, but I don't find APIError right now
        logger.error(exception)
        logger.error(
            "Could not login. Probably your password is wrong or you didn't complete"
            " signup."
        )
        return "could-not-login"
    data = hub.table("account").select("*").eq("id", auth_response.user.id).execute()
    if len(data.data) > 0:  # user is completely registered
        user_id = data.data[0]["lnid"]
        user_handle = data.data[0]["handle"]
        user_name = data.data[0]["name"]
        if handle is not None and handle != user_handle:
            logger.warning(
                f"Using account handle {user_handle} (cached handle was {handle})"
            )
    else:  # user did not complete signup as usermeta has no matching row
        logger.error("Complete signup on your account page.")
        return "complete-signup"
    hub.auth.sign_out()
    return user_id, user_handle, user_name, auth_response.session.access_token
