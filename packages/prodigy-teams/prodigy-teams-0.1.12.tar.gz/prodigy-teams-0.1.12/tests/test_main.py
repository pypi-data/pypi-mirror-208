import inspect
import json
from pathlib import Path

import pytest

from prodigy_teams.__main__ import FILE
from prodigy_teams.about import __version__
from prodigy_teams.cli import document_cli
from prodigy_teams.main import cli

ROOT_PATH = Path(__file__).parent.parent
README_PATH = ROOT_PATH / "README.md"


def test_readme_up_to_date():
    with README_PATH.open("r", encoding="utf8") as f:
        existing = f.read()
    docs = document_cli(cli, root=ROOT_PATH)
    assert docs == existing, "README.md out of date, re-run pdcli dev document-clis"


def test_static_up_to_date():
    """Test that the static JSON matches the current live CLI."""
    err = "static CLI doesn't match live CLI, re-run pdcli dev update-ptc"
    with FILE.open("r", encoding="utf8") as f:
        existing = f.read()
    current = json.dumps(cli.to_static_json())
    assert existing == current, err


def test_ptc_cli_help_texts(command):
    """Test that all commands provide docstrings and argument help texts."""
    assert command.description, f"no docstring for {command.display_name}"
    for arg in command.args:
        if arg.id == cli.extra_key:
            continue
        assert arg.arg.help, f"no help text for {command.display_name} -> {arg.id}"


def test_pt_cli_all_annotated(command_no_placeholder):
    """Assert that all function arguments are annotated."""
    command = command_no_placeholder
    sig = inspect.signature(command.func)
    args = [a.id for a in command.args]
    params = [p for p in sig.parameters]
    assert sorted(args) == sorted(params), f"arg mismatch in {command.display_name}"


def test_ptc_cli_default_help_info(capsys):
    with pytest.raises(SystemExit):
        cli.run(["ptc"])
    captured = capsys.readouterr()
    expected_output_slice = """Prodigy Teams Command Line Interface."""
    assert expected_output_slice in captured.out


def test_version(capsys):
    with pytest.raises(SystemExit):
        cli.run(["ptc", "--version"])
    captured = capsys.readouterr()
    assert captured.out.strip() == __version__
