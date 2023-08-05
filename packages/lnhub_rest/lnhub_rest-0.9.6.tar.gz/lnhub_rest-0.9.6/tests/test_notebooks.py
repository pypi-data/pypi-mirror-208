import os
from pathlib import Path

import pytest
from nbproject._logger import logger
from nbproject.dev import test

from lnhub_rest._ci import start_local_supabase

# assuming this is in the tests folder
DOCS_FOLDER = Path(__file__).parents[1] / "docs/"
LAMIN_ENV = os.environ.get("LAMIN_ENV", "local")


@pytest.fixture(scope="session", autouse=True)
def supabase():
    start_local_supabase()
    logger.debug(os.environ)


@pytest.mark.local
def test_local():
    logger.debug("\nmigrate")
    test.execute_notebooks(DOCS_FOLDER, write=True)

    logger.debug("\nchecks")
    test.execute_notebooks(DOCS_FOLDER / "01-checks/", write=True)

    logger.debug("\naccount")
    test.execute_notebooks(DOCS_FOLDER / "02-account/", write=True)

    logger.debug("\norganization")
    test.execute_notebooks(DOCS_FOLDER / "05-organization/", write=True)


@pytest.mark.integration
def test_integrations():
    logger.debug("\ninstance")
    test.execute_notebooks(DOCS_FOLDER / "03-instance/", write=True)

    logger.debug("\nstorage")
    test.execute_notebooks(DOCS_FOLDER / "04-storage/", write=True)

    logger.debug("\nintegrations")
    test.execute_notebooks(DOCS_FOLDER / "06-integration/", write=True)
