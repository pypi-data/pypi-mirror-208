import contextlib
import io

from hypothesis import given
from hypothesis import strategies as st

from prodigy_teams import ui


@given(n=st.integers(min_value=0, max_value=100))
def test_progress(n):
    stdout = io.StringIO()

    with contextlib.redirect_stdout(stdout):
        progress = ui.Progress([i for i in range(n)])
        progress.before_bar = "\r"
        progress.after_bar = "\n"
        progress.is_hidden = False

        with progress as elements:
            for _ in elements:
                pass

    lines = stdout.getvalue().splitlines()
    assert lines.pop(0) == ""  # Not sure why this one is here but there you go
    assert len(lines) == n + 1
