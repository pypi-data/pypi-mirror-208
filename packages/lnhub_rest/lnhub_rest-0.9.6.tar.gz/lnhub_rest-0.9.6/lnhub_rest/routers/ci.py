from fastapi import APIRouter

from lnhub_rest._clean_ci import clean_ci as clean_ci_base
from lnhub_rest._clean_ci import clean_ci_by_run_id as clean_ci_by_run_id_base
from lnhub_rest._clean_ci import delete_ci_accounts, delete_ci_auth_users

router = APIRouter(prefix="/ci")


@router.delete("/clean/run")
def clean_ci_by_run_id(id: str):
    clean_ci_by_run_id_base(id)


@router.delete("/clean")
def clean_ci():
    clean_ci_base()


@router.delete("/users")
def delete_ci_users():
    delete_ci_accounts()
    delete_ci_auth_users()
