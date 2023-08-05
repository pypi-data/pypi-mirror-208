import os

import nox
from laminci.nox import login_testuser1, login_testuser2

nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.install("pre-commit")
    session.run("pre-commit", "install")
    session.run("pre-commit", "run", "--all-files")


@nox.session
@nox.parametrize("package", ["lnhub-rest", "lndb"])
def test_local(session: nox.Session, package: str):
    session.install("./lndb[dev,test]")
    session.install(".[dev,test]")
    session.run(
        "pytest",
        "-s",
        "-m",
        "not integration",
        "--cov=lnhub_rest",
        "--cov-append",
        "--cov-report=term-missing",
        env={"LN_SERVER_DEPLOY": "1", "LAMIN_ENV": "local"},
    )
    if package == "lndb":
        login_testuser1(session)
        login_testuser2(session)
        os.chdir(f"./{package}")
        session.run("pytest", "-s", "./tests", env={"LAMIN_ENV": "local"})


@nox.session
@nox.parametrize("package", ["lnhub-rest", "lndb"])
@nox.parametrize("lamin_env", ["staging"])
def test_integrations(session: nox.Session, package: str, lamin_env: str):
    session.install("./lndb[dev,test]")
    session.install(".[dev,test]")
    session.run(
        "pytest",
        "-s",
        "-m",
        "integration",
        "--cov=lnhub_rest",
        "--cov-append",
        "--cov-report=term-missing",
        env={"LN_SERVER_DEPLOY": "1", "LAMIN_ENV": lamin_env},
    )
    if package == "lndb":
        login_testuser1(session, env={"LAMIN_ENV": lamin_env})
        login_testuser2(session, env={"LAMIN_ENV": lamin_env})
        os.chdir(f"./{package}")
        session.run("pytest", "-s", "./tests", env={"LAMIN_ENV": lamin_env})
