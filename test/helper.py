# pyright: reportPrivateUsage=false

import os
import sys
from collections import defaultdict
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import beets
import beets.library
import beets.plugins
import beetsplug.convert
import beetsplug.hook
import pytest
from beets import ui
from beets.library import Item
from beets.util import MoveOperation

import beetsplug.rockbox

_beets_version = tuple(map(int, beets.__version__.split(".")[0:3]))


@contextmanager
def capture_stdout():
    r"""Collect stdout in a StringIO while still outputting it.

    >>> with capture_stdout() as output:
    ...     print('spam')
    ...
    spam
    >>> output.getvalue()
    'spam\n'
    """
    org = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer
    try:
        yield sys.stdout
    finally:
        sys.stdout = org
        sys.stdout.write(buffer.getvalue())


class TestHelper:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path: Path):
        self.config = beets.config
        self.config.clear()
        self.config.read()

        self.config["plugins"] = []
        self.config["verbose"] = True
        self.config["ui"]["color"] = False
        self.config["threaded"] = False
        self.config["import"]["copy"] = False

        self.config["rockbox"]["rockbox"] = str(tmp_path) + "/.rockbox"
        self.config["rockbox"]["db"] = str(tmp_path) + "/output"
        self.config["rockbox"]["music"] = "/<HDD0>/Music"

        self.libdir = tmp_path / "beets_lib"
        os.environ["BEETSDIR"] = str(self.libdir)
        self.config["directory"] = str(self.libdir)

        self.lib = beets.library.Library(
            ":memory:",
            str(self.libdir),
        )
        self.fixture_dir = Path(__file__).parent / "fixtures"

        if _beets_version > (2, 3, 1):
            beets.plugins._instances = [
                beetsplug.rockbox.RockboxPlugin(),
                beetsplug.convert.ConvertPlugin(),
                beetsplug.hook.HookPlugin(),
            ]
        else:
            beets.plugins._classes = {  # type: ignore (compatibility with beets<2.4)
                beetsplug.rockbox.RockboxPlugin,
                beetsplug.convert.ConvertPlugin,
                beetsplug.hook.HookPlugin,
            }
            beets.plugins._instances = {}

        yield

        if _beets_version > (2, 3, 1):
            beets.plugins.BeetsPlugin.listeners = defaultdict(list)
        else:
            for plugin in beets.plugins._classes:  # type: ignore (compatibility with beets<2.4)
                # Instantiating a plugin will modify register event listeners which
                # are stored in a class variable
                plugin.listeners = None  # type: ignore (compatibility with beets<2.4)

    def runcli(self, *args: str) -> str:
        # TODO mock stdin
        with capture_stdout() as out:
            ui._raw_main(list(args), self.lib)
        return out.getvalue()

    def add_track(self, **kwargs: str) -> Item:
        values = {}
        values.update(kwargs)

        item = Item.from_path(str(self.fixture_dir / "min.opus"))  # type: ignore
        item.add(self.lib)
        item.update(values)
        item.move(MoveOperation.COPY)
        item.write()
        return item
