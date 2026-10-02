"""The path guards of read_file and list_files."""
from __future__ import annotations

import pytest

from harness import list_files, read_file, repo_root, set_repo_root
from harness.repo_tools import _resolve


def test_repo_root_holds_readme_and_module():
    root = repo_root()
    assert (root / "README.md").exists()
    assert (root / "M5 - Harness Engineering").is_dir()


def test_read_file_reads_a_repository_file():
    assert read_file("LICENSE").startswith("MIT License")


@pytest.mark.parametrize("path", [".env", "M5 - Harness Engineering/.env", "secrets.env", ".env.local", ".env.production"])
def test_read_file_refuses_env_files(path):
    with pytest.raises(ValueError, match="credentials"):
        read_file(path)


@pytest.mark.parametrize("path", ["../outside.txt", "../../etc/passwd", "/etc/passwd"])
def test_read_file_refuses_paths_outside_the_root(path):
    with pytest.raises(ValueError, match="outside"):
        read_file(path)


@pytest.mark.parametrize("path", [".git/config", ".claude/settings.json", ".venv/pyvenv.cfg"])
def test_read_file_refuses_protected_folders(path):
    with pytest.raises(ValueError, match="protected folder|outside"):
        read_file(path)


def test_env_example_template_is_not_treated_as_a_credentials_file():
    # The tracked template holds no key; the guard must not block it (it is still hidden from listings).
    assert _resolve(".env.example").name == ".env.example"


def test_list_files_shows_github_but_no_other_dotfiles():
    listing = list_files(".").splitlines()
    assert "docs/" in listing and ".github/" in listing
    assert [name for name in listing if name.startswith(".") and name != ".github/"] == []
    assert "__pycache__/" not in listing


def test_list_files_hides_local_scratch(tmp_path):
    (tmp_path / "README.md").write_text("x")
    for folder in ["M5 - Harness Engineering", ".github", "docs", ".codex-build", "__pycache__", ".ipynb_checkpoints", ".git"]:
        (tmp_path / folder).mkdir()
    for name in [".DS_Store", ".gitignore", ".env", ".env.example", "LICENSE"]:
        (tmp_path / name).write_text("x")
    set_repo_root(tmp_path)
    try:
        assert list_files(".").splitlines() == [".github/", "docs/", "M5 - Harness Engineering/", "LICENSE", "README.md"]
    finally:
        set_repo_root(None)


def test_missing_file_is_an_error_the_model_can_read():
    with pytest.raises(ValueError, match="not a file"):
        read_file("does-not-exist.md")
