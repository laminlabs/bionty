import os

import nox
from laminci.nox import build_docs, install_lamindb, run, run_pre_commit

nox.options.default_venv_backend = "none"

IS_PR = os.getenv("GITHUB_EVENT_NAME") != "push"


@nox.session
def lint(session: nox.Session) -> None:
    run_pre_commit(session)


@nox.session
@nox.parametrize("group", ["bionty-base", "bionty-core", "bionty-docs"])
def build(session: nox.Session, group: str):
    branch = "main" if IS_PR else "release"  # point back to "release"
    install_lamindb(session, branch=branch)
    run(session, "uv pip install --system wetlab")
    session.run(*"uv pip install --system -e .[dev]".split())

    coverage_args = "--cov=bionty --cov-append --cov-report=term-missing"
    if group == "bionty-base":
        session.run(*f"pytest {coverage_args} ./tests/base".split())
    elif group == "bionty-core":
        session.run(*f"pytest {coverage_args} ./tests/core".split())
    elif group == "bionty-docs":
        session.run(*f"pytest -s {coverage_args} ./docs/guide".split())
        run(session, "lamin init --storage ./docsbuild --modules bionty")
        build_docs(session, strict=False)
