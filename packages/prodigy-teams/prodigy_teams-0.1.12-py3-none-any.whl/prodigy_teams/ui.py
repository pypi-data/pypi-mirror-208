import json
import os
import re
import shutil
import sys
import textwrap

from radicli import HelpFormatter
from radicli.util import format_arg_help
from wasabi import color, msg, table

from . import ty
from .about import __prog__
from .messages import Messages
from .prodigy_teams_pam_sdk.models import RecipeDetail
from .util import CYGWIN, WIN

LOGO = """
█▀█ █▀█ █▀█ █▀▄ █ █▀▀ █▄█
█▀▀ █▀▄ █▄█ █▄▀ █ █▄█ ░█░
"""

whitespace_re = re.compile(r"\s+", re.ASCII)
ansi_re = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


def is_silent() -> bool:
    # External environment variable to disable printing of info tables etc.
    return bool(os.environ.get("PRODIGY_TEAMS_CLI_SILENT", False))


def print_login_info(uri_complete: str, uri: str, code: str) -> None:
    print(LOGO)
    msg.info(Messages.T014)
    open_url(color(uri_complete, bold=True))
    msg.text(Messages.T015)
    msg.text(color(uri_complete, bold=True))
    print("")
    msg.text(Messages.T016)
    msg.text(color(uri, bold=True))
    msg.text(Messages.T017)
    msg.text(color(code, bold=True))


def print_as_json(data: ty.JSONableDict) -> None:
    if not is_silent():
        print(json.dumps(data, indent=2))


def print_logs(text: ty.Optional[str], as_json: bool = False) -> None:
    if is_silent():
        return
    if as_json:
        print_as_json({"logs": text})
    elif text is not None:
        msg.info("Logs")
        print(text)


def dicts_to_table(
    data: ty.Sequence[ty.Dict[str, ty.Any]],
    headers: ty.Optional[ty.List[str]] = None,
    exclude_dicts: bool = False,
) -> ty.Tuple[
    ty.List[str], ty.Union[ty.Sequence[ty.Dict[str, ty.Any]], ty.List[ty.List[str]]]
]:
    """
    Generate a tuple with headers and rows in the format wasabi expects from a list
    of dicts having column names as keys.
    """
    if not data:
        return [], data
    use_data = list(data)
    if headers is None:
        headers = list(use_data[0].keys())
    rows = []
    for item in data:
        if exclude_dicts:
            item = {k: v for k, v in item.items() if not isinstance(v, dict)}
        row = []
        for key in headers:
            val = item.get(key, None)
            if isinstance(val, ty.Enum):
                val = val.value
            row.append(str(val))
        rows.append(row)
    return headers, rows


def print_table_with_select(
    items: ty.Sequence[ty.Union[ty.BaseModel, dict]],
    select: ty.Optional[ty.List[str]] = None,
) -> None:
    if is_silent():
        return
    include: ty.Set[str] = set(select) if select is not None else None  # type: ignore

    def as_dict(r: ty.Any) -> ty.JSONableDict:
        if isinstance(r, ty.BaseModel):
            d = r.dict(include=include)
        elif hasattr(r, "as_dict"):
            d = r.as_dict()
        else:
            d = r
        if include:
            return {k: v for k, v in d.items() if k in include}
        return d

    data = [as_dict(r) for r in items]
    headers, rows = dicts_to_table(data)
    if rows:
        msg.table(rows, header=headers, divider=True, max_col=3000)


def print_info_table(
    item: ty.BaseModel,
    select: ty.Optional[ty.List[str]] = None,
    exclude: ty.Optional[ty.List[str]] = None,
    as_json: bool = False,
) -> None:
    if is_silent():
        return
    dict_kwargs = {}
    if select is not None:
        dict_kwargs["include"] = set(select)
    if exclude is not None:
        dict_kwargs["exclude"] = set(exclude)
    if as_json:
        print(item.json(**dict_kwargs, indent=2))
    else:
        serialized = {}
        for key, val in item._iter(**dict_kwargs, to_dict=True):
            if isinstance(val, ty.Enum):
                serialized[key] = val.value
            else:
                serialized[key] = val
        msg.table(serialized)


def print_args_table(
    args: ty.Dict[str, ty.Any], cli_names: ty.Optional[ty.Dict[str, str]] = None
) -> None:
    if is_silent():
        return
    data = {}
    cli_names_map = {v: k for k, v in cli_names.items()} if cli_names else {}
    for key, value in args.items():
        key = cli_names_map.get(key, key)
        value = str(value) if isinstance(value, ty.UUID) else repr(value)
        data[key] = value
    msg.table(data)


def print_recipes_help(
    schemas: ty.Dict[str, RecipeDetail], help: str, command: str
) -> None:
    data = []
    for name, schema in schemas.items():
        data.append((name, schema.title))
        if schema.description:
            data.append(("", format_arg_help(schema.description)))
    print(f"usage: {__prog__} {command} [-h] name [...]\n")
    print(
        f"{help}\nRun {__prog__} {command} [name] --help to view the recipe arguments."
    )
    print("")
    msg.text("Available recipes:")
    msg.table(data)


def get_recipe_desc(schema: RecipeDetail) -> str:
    width = max(shutil.get_terminal_size().columns - 2, 11)
    text = whitespace_re.sub(" ", schema.description).strip()
    desc = textwrap.fill(text, width, initial_indent="", subsequent_indent="")
    meta = {
        "ID": schema.id,
        "Source": schema.entry_point,
        "Created": schema.created.strftime("%Y-%m-%d, %H:%M:%S"),
    }
    meta_table = table(meta)
    return f"{schema.title} ({schema.name})\n{desc}\n{meta_table}"


class RecipeHelpFormatter(HelpFormatter):
    def _fill_text(self, text, width, indent) -> str:
        return "".join(indent + line for line in text.splitlines(keepends=True))


# Source: https://github.com/pallets/click/blob/cba52fa76135af2edf46c154203b47106f898eb3/src/click/_termui_impl.py#L551
def open_url(url: str, wait: bool = False, locate: bool = False) -> int:
    import subprocess

    def _unquote_file(url: str) -> str:
        from urllib.parse import unquote

        if url.startswith("file://"):
            url = unquote(url[7:])

        return url

    if sys.platform == "darwin":
        args = ["open"]
        if wait:
            args.append("-W")
        if locate:
            args.append("-R")
        args.append(_unquote_file(url))
        null = open("/dev/null", "w")
        try:
            return subprocess.Popen(args, stderr=null).wait()
        finally:
            null.close()
    elif WIN:
        if locate:
            url = _unquote_file(url.replace('"', ""))
            args = f'explorer /select,"{url}"'
        else:
            url = url.replace('"', "")
            wait_str = "/WAIT" if wait else ""
            args = f'start {wait_str} "" "{url}"'
        return os.system(args)
    elif CYGWIN:
        if locate:
            url = os.path.dirname(_unquote_file(url).replace('"', ""))
            args = f'cygstart "{url}"'
        else:
            url = url.replace('"', "")
            wait_str = "-w" if wait else ""
            args = f'cygstart {wait_str} "{url}"'
        return os.system(args)
    try:
        if locate:
            url = os.path.dirname(_unquote_file(url)) or "."
        else:
            url = _unquote_file(url)
        c = subprocess.Popen(["xdg-open", url])
        if wait:
            return c.wait()
        return 0
    except OSError:
        if url.startswith(("http://", "https://")) and not locate and not wait:
            import webbrowser

            webbrowser.open(url)
            return 0
        return 1


# Adapted from: https://github.com/pallets/click/blob/cba52fa76135af2edf46c154203b47106f898eb3/src/click/_termui_impl.py#L35
# Only supports sized sequences and basic percent / count
_BarT = ty.TypeVar("_BarT")


class Progress(ty.Generic[_BarT]):
    def __init__(
        self,
        iterable: ty.Union[ty.Iterable[_BarT], ty.Sequence[_BarT]],
        length: ty.Optional[int] = None,
        pc: bool = False,
        width: int = 36,
    ) -> None:
        self.show_pc = pc
        self.file = sys.stdout
        self._completed_intervals = 0
        self.width = width
        self.before_bar = "\r" if os.name == "nt" else "\r\033[?25l"
        self.after_bar = "\n" if os.name == "nt" else "\033[?25h\n"
        self.iter = iter(iterable)
        self.length = (
            length
            if length is not None
            else len(iterable)
            if isinstance(iterable, ty.Sequence)
            else 0
        )
        self.pos = 0
        self.finished = False
        self.max_width: ty.Optional[int] = None
        self.current_item: ty.Optional[_BarT] = None
        self.is_hidden = not isatty(self.file)
        self._last_line: ty.Optional[str] = None

    def __enter__(self) -> "Progress[_BarT]":
        self.render_progress()
        return self

    def __exit__(self, exc_type, exc_value, tb):  # type: ignore
        self.render_finish()

    def __iter__(self) -> ty.Iterator[_BarT]:
        self.render_progress()
        return self.generator()

    def __next__(self) -> _BarT:
        return next(iter(self))

    def render_finish(self) -> None:
        if self.is_hidden:
            return
        self.file.write(self.after_bar)
        self.file.flush()

    @property
    def pct(self) -> float:
        if self.length == 0:
            return 1.0
        return 1.0 if self.finished else min(self.pos / float(self.length), 1.0)

    def format_bar(self) -> str:
        empty_char = " "
        fill_char = "#"
        if self.finished:
            return fill_char * self.width
        bar_length = int(self.pct * self.width)
        bar = fill_char * bar_length
        bar += empty_char * (self.width - bar_length)
        return bar

    def render_progress(self) -> None:
        if self.is_hidden:
            return
        buf = []
        clear_width = self.width
        if self.max_width is not None:
            clear_width = self.max_width
        buf.append(self.before_bar)
        info = (
            f"{int(self.pct * 100): 4}%"[1:]
            if self.show_pc
            else f"{str(self.pos)}/{self.length}"
        )
        line = f"[{self.format_bar()}]  {info}".rstrip()
        line_len = len(ansi_re.sub("", line))
        if self.max_width is None or self.max_width < line_len:
            self.max_width = line_len
        buf.append(line)
        buf.append(" " * (clear_width - line_len))
        line = "".join(buf)
        if line != self._last_line:
            self._last_line = line
            self.file.write(line)
            self.file.flush()

    def make_step(self, n_steps: int) -> None:
        self.pos += n_steps
        if self.pos >= self.length:
            self.finished = True

    def update(self, n_steps: int, current_item: ty.Optional[_BarT] = None) -> None:
        if current_item is not None:
            self.current_item = current_item
        self._completed_intervals += n_steps
        if self._completed_intervals >= 1:
            self.make_step(self._completed_intervals)
            self.render_progress()
            self._completed_intervals = 0

    def finish(self) -> None:
        self.current_item = None
        self.finished = True

    def generator(self) -> ty.Iterator[_BarT]:
        if self.is_hidden:
            yield from self.iter
        else:
            for rv in self.iter:
                self.current_item = rv
                if self._completed_intervals == 0:
                    self.render_progress()
                yield rv
                self.update(1)
            self.finish()
            self.render_progress()


def isatty(stream: ty.IO) -> bool:
    try:
        return stream.isatty()
    except Exception:
        return False


class PageProgress(Progress[ty.Page]):
    def __init__(self, iterable: ty.Iterable[ty.Page], *args, length=1, **kwargs):
        super().__init__(iterable, *args, length=length, **kwargs)

        self._pos = 0

    def generator(self) -> ty.Iterator[ty.Page]:
        for page in super().generator():
            self.length = page.total
            self._pos += len(page.items)
            self.pos = self._pos - 1

            yield page
