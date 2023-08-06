import pytest

from prodigy_teams.main import cli


@pytest.mark.xfail(reason="No dummy project")
def test_list_projects(capsys):
    with pytest.raises(SystemExit):
        cli.run(["ptc", "projects", "list"])
    captured = capsys.readouterr()
    assert "Test Project" in captured.out
