import importlib.util
import os
from pathlib import Path

import nox
from laminci import convert_executable_md_files, upload_docs_artifact
from laminci.nox import build_docs, install_lamindb, run, run_pre_commit

nox.options.default_venv_backend = "none"

IS_PR = os.getenv("GITHUB_EVENT_NAME") != "push"


def _entity_generation():
    spec = importlib.util.spec_from_file_location(
        "entity_generation_generate",
        Path(__file__).parent / "scripts/entity_generation/generate.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def update_entity_docs(session: nox.Session) -> None:
    """Regenerate public-ontology guides and commit them on CI if they changed.

    We commit the generated markdown so a clone is immediately readable —
    including by an agent — without having to run entity-generation first,
    and so git history versions each guide transparently. Same pattern as
    lamindb's `clidocs` session for `docs/cli.md`: generate, compare with
    the repo copy, and on CI commit + push if it changed.
    """
    generate = _entity_generation()
    GENERATED_DOC_STEMS = generate.GENERATED_DOC_STEMS
    generate_entity_docs = generate.generate_entity_docs

    paths = [Path("./docs") / f"{stem}.md" for stem in GENERATED_DOC_STEMS]
    current = {path: path.read_text() if path.exists() else None for path in paths}
    generate_entity_docs()
    changed = any(path.read_text() != current[path] for path in paths)
    if changed and os.getenv("CI"):
        run(session, "git add " + " ".join(str(path) for path in paths))
        run(
            session,
            "git -c user.name='bionty-docs-bot' -c user.email='open-source@lamin.ai' "
            "commit -m '📝 Re-generated the public ontology docs'",
        )
        branch = os.getenv("GITHUB_HEAD_REF") or os.getenv("GITHUB_REF_NAME")
        if branch:
            run(session, f"git push origin HEAD:{branch}")


@nox.session
def lint(session: nox.Session) -> None:
    run_pre_commit(session)


@nox.session
def entitydocs(session: nox.Session) -> None:
    update_entity_docs(session)


@nox.session
@nox.parametrize("group", ["bionty-base", "bionty-core", "bionty-docs"])
def build(session: nox.Session, group: str):
    branch = (
        "main" if IS_PR else "main"
    )  # point to "main" for PRs, to "release" for main
    install_lamindb(session, branch=branch)
    run(session, "uv pip install --system pertdb")
    session.run(*"uv pip install --system -e .[dev]".split())

    coverage_args = "--cov=bionty --cov-append --cov-report=term-missing"
    if group == "bionty-base":
        session.run(*f"pytest {coverage_args} ./tests/base".split())
    elif group == "bionty-core":
        session.run(*f"pytest {coverage_args} ./tests/core".split())
    elif group == "bionty-docs":
        update_entity_docs(session)
        convert_executable_md_files()
        session.run(
            *f"pytest -s {coverage_args} ./docs/guide ./tests/test_ontology_notebooks.py".split()
        )
        run(session, "lamin init --storage ./docsbuild --modules bionty")
        build_docs(session, strict=True)
        upload_docs_artifact()
