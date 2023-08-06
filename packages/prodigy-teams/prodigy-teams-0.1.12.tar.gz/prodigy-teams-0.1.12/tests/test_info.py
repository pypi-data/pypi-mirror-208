NO_INFO = ["config", "consul", "files"]


def test_info_commands(commands, subcommands):
    for name, command in commands.items():
        if name in subcommands and name not in NO_INFO:
            assert "info" in subcommands[name]
            info = subcommands[name]["info"]
            assert not info.allow_extra
            args = {a.id: a for a in command.args}
            valid_args = {"name_or_id", "project_id", "cluster_id", "as_json"}
            for name in args:
                assert name in valid_args
