"""This file only exists for lazy-loading the CLI in __main__.py"""
from .cli import cli
from .commands import *  # noqa

__all__ = ["cli"]
