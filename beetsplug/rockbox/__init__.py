import argparse
from collections.abc import Sequence

import enlighten
from beets import util
from beets.library import Library
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand, UserError, print_
from typing_extensions import Never

from beetsplug.rockbox.config import Config
from beetsplug.rockbox.database import Database


class RockboxPlugin(BeetsPlugin):
    def __init__(self):
        super().__init__()

    def setup(self):
        config_raw = self.config
        self._config: Config = Config(config_raw)
        self.manager = enlighten.get_manager()

    def commands(self):
        return [RockboxCommand(self)]

    def build(self, lib: Library, _: argparse.Namespace):
        self.setup()
        db = Database(self._log, lib, self._config)

        pbar = self.manager.counter(total=len(lib.items()), desc="Building DB", unit="songs")

        matched_ids = set()
        for album in lib.albums():
            if self._config.query.match(album):
                matched_items = album.items()
                matched_ids.update(item.id for item in matched_items)

        for item in lib.items():
            if item.id in matched_ids or self._config.query.match(item):
                db.add_item(item)
                pbar.update()

        db.sort()
        
        pbar = self.manager.counter(total=len(lib.items()), desc="Building Index", unit="songs")
        for item in lib.items():
            if item.id in matched_ids or self._config.query.match(item):
                db.add_index(item)
                pbar.update()

        db.write()

    def copy(self, lib: Library, _: argparse.Namespace):
        self.setup()
        db = Database(self._log, lib, self._config)
        rockbox = self._config.rockbox
        db_dir = self._config.db

        if not rockbox.is_dir():
            raise UserError(f"Could not find .rockbox folder: {rockbox!s}")

        util.copy(
            bytes(str(db_dir / "database_idx.tcd"), encoding="utf8"),
            bytes(str(rockbox / "database_idx.tcd"), encoding="utf8"),
            replace=True,
        )
        for file in db.tag_files.values():
            util.copy(
                bytes(str(file), encoding="utf8"),
                bytes(str(rockbox / file.name), encoding="utf8"),
                replace=True,
            )


class RockboxCommand(Subcommand):
    name = "rockbox"
    aliases = ("rock", "r")
    help = "build rockbox database"

    def __init__(self, plugin: RockboxPlugin):
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(prog=parser.prog + " rock")
        subparsers.required = True

        build = subparsers.add_parser("build")
        build.set_defaults(func=plugin.build)

        copy = subparsers.add_parser("copy")
        copy.set_defaults(func=plugin.copy)

        super().__init__(self.name, parser, self.help, self.aliases)

    def func(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, lib: Library, opts: argparse.Namespace, _
    ):
        opts.func(lib, opts)

    def parse_args(self, args: list[str]):  # pyright: ignore
        return self.parser.parse_args(args), []  # pyright: ignore


class ArgumentParser(argparse.ArgumentParser):
    """
    Facade for ``argparse.ArgumentParser`` so that beets can call
    `_get_all_options()` to generate shell completion.
    """

    def _get_all_options(self) -> Sequence[Never]:
        # FIXME return options like ``OptionParser._get_all_options``.
        return []
