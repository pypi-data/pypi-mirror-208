import json
import os
from subprocess import CalledProcessError, run

from lamin_logger import logger


def start_local_supabase():
    """Start local supabase.

    Starts the local Supabase server and/or grabs the connection info. We
    set the environment variables so lnhub_rest.config.Settings can pick them up.
    """
    sb_status = supabase()
    os.environ["POSTGRES_DSN"] = sb_status["DB_URL"]
    os.environ["SUPABASE_API_URL"] = sb_status["API_URL"]
    os.environ["SUPABASE_ANON_KEY"] = sb_status["ANON_KEY"]
    os.environ["SUPABASE_SERVICE_KEY"] = sb_status["SERVICE_ROLE_KEY"]


def supabase(retry: int = 3, stop: bool = False):
    if stop:
        run("supabase stop")
    if retry == 0:
        raise RuntimeError("Failed to set up Supabase local instance or get status")
    try:
        return _get_supabase_status()
    except CalledProcessError as cpe:
        logger.error(cpe.stderr)
        _start_local_supabase()
        return supabase(retry=retry - 1)


def _get_supabase_status():
    status = run("supabase status -o json", shell=True, check=True, capture_output=True)
    return json.loads(status.stdout)


def _start_local_supabase():
    run("supabase start -x imgproxy -x storage-api -x realtime", shell=True, check=True)
