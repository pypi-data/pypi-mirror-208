import os

from fastapi import APIRouter

from .utils import supabase_client

router = APIRouter(prefix="/dev")


@router.delete("/env")
def env():
    if "LAMIN_ENV" in os.environ:
        return os.environ["LAMIN_ENV"]
    else:
        return None


@router.delete("/count/account")
def count_accounts():
    accounts = supabase_client.table("account").select("*").execute().data
    return len(accounts)
