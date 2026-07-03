"""Tests for session document enrichment."""

from whatwasit.models import Command, Session


def test_venv_session_includes_activation_and_path_hints():
    session = Session(
        cwd="~/projects/newtool",
        commands=[
            Command(raw_cmd="python3 -m venv .venv"),
            Command(raw_cmd="source .venv/bin/activate"),
            Command(raw_cmd="pip install -r requirements.txt"),
        ],
    )
    doc = session.to_document()
    assert "directory: newtool" in doc
    assert "directory: newtool" in doc
    assert "path: projects/newtool" in doc
    assert "python virtual environment" in doc
    assert "activate python virtual environment" in doc
    assert "requirements.txt" in doc


def test_env_path_session_includes_path_and_profile_hints():
    session = Session(
        cwd="~",
        commands=[
            Command(raw_cmd="which mytool"),
            Command(raw_cmd="echo $PATH"),
            Command(raw_cmd="vim ~/.bashrc"),
            Command(raw_cmd="source ~/.bashrc"),
        ],
    )
    doc = session.to_document()
    assert "shell PATH environment" in doc
    assert "shell startup profile" in doc
    assert "which" in doc


def test_find_session_includes_size_and_age_hints():
    session = Session(
        cwd="~",
        commands=[
            Command(raw_cmd="find . -type f -size +100M"),
            Command(raw_cmd="find /var -type f -mtime +90"),
        ],
    )
    doc = session.to_document()
    assert "large files disk space" in doc
    assert "old files modification age" in doc


def test_non_sparse_git_session_keeps_minimal_doc_shape():
    session = Session(
        cwd="~/projects/api",
        commands=[
            Command(raw_cmd="git fetch origin"),
            Command(raw_cmd="git rebase origin/main"),
            Command(raw_cmd="git status"),
            Command(raw_cmd="vim auth.py"),
        ],
    )
    doc = session.to_document()
    assert "path:" not in doc
    assert "tools:" not in doc
    assert "git fetch origin" in doc


def test_python_dependency_conflict_is_sparse():
    session = Session(
        cwd="~/projects/newtool",
        commands=[
            Command(raw_cmd="pip install 'urllib3<2'"),
            Command(raw_cmd="pip check"),
        ],
    )
    doc = session.to_document()
    assert "tools:" in doc
    assert "python package version conflict" in doc


def test_docker_volume_session_includes_mount_hints():
    session = Session(
        cwd="~/projects/webapp",
        commands=[
            Command(raw_cmd="docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres:15"),
            Command(raw_cmd="docker volume inspect pgdata"),
        ],
    )
    doc = session.to_document()
    assert "docker volume mount persist" in doc
    assert "postgres database data directory" in doc
