import nox
from laminci import move_built_docs_to_docs_slash_project_slug
from laminci.nox import build_docs, login_testuser1, run_pre_commit, run_pytest

nox.options.default_venv_backend = "none"


@nox.session
def lint(session: nox.Session) -> None:
    run_pre_commit(session)


# @nox.session
# def docs(session: nox.Session):
#     import lamindb_setup as ln_setup

#     login_testuser1(session)
#     ln_setup.init(storage="./docsbuild")
#     build_docs(session)


@nox.session()
def build(session):
    session.run(*"pip install -e .[dev]".split())
    # session.run(*"pip install git+https://github.com/laminlabs/lamindb".split())
    # run_pytest(session, coverage=False)
    # docs(session)
    # move_built_docs_to_docs_slash_project_slug()
