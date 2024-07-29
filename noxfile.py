import nox
from laminci.nox import build_docs, run, run_pre_commit

nox.options.default_venv_backend = "none"


@nox.session
def lint(session: nox.Session) -> None:
    run_pre_commit(session)


@nox.session
@nox.parametrize("group", ["bionty-unit", "bionty-docs"])
def build(session: nox.Session, group: str):
    session.run(*"uv pip install --system -e .[dev]".split())
    # session.run(*"pip install git+https://github.com/laminlabs/lamindb".split())
    session.run(
        *"pip install git+https://github.com/laminlabs/lamindb-setup@single-bionty-repo".split()
    )
    # session.run(*"pip install git+https://github.com/laminlabs/lnschema-core".split())
    coverage_args = "--cov=bionty --cov-append --cov-report=term-missing"
    if group == "bionty-unit":
        session.run(*f"pytest {coverage_args} ./tests".split())
    elif group == "bionty-docs":
        session.run(*f"pytest -s {coverage_args} ./docs/guide".split())
        run(session, "lamin init --storage ./docsbuild --schema bionty")
        build_docs(session, strict=True)
