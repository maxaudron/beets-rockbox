# pyright: reportPrivateUsage=false
import logging

import pytest

from beetsplug.rockbox import Config
from beetsplug.rockbox.database import Database, IndexEntry

from .helper import TestHelper

LOGGER = logging.getLogger(__name__)

class TestDatabase(TestHelper):
    def _database(self):
        self.item = self.add_track()

        config = Config(self.config["rockbox"])
        self.db = Database(LOGGER, None, config)  # type: ignore

    def test_database_add(self):
        self.config["rockbox"]["extension"] = "flac"

        self._database()
        self.db.add(self.item)
        assert "Lord Huron" in self.db.tag_data["artist"]
        assert "Lord Huron" in self.db.tag_data["canonicalartist"]
        assert "The Cosmic Selector Vol. 1" in self.db.tag_data["album"]
        assert "Looking Back" in self.db.tag_data["title"]
        assert (
            "/<HDD0>/Music/Lord Huron/The Cosmic Selector Vol. 1/01 Looking Back.flac"
            in self.db.tag_data["filename"]
        )
        assert self.db.tag_data["composer"] == {}

        assert self.db.tag_data["title"]["Looking Back"].idx_id == 0

    def test_indexentry(self):
        self._database()
        self.db.add(self.item)
        index = IndexEntry(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, self.item)

        assert index.year == 2025
        assert index.discnumber == 0
        assert index.tracknumber == 1
        assert index.bitrate == 186
        assert index.length == 719
        assert index.mtime != 0

    def test_tag_seek(self):
        self._database()
        self.db.add_tag("artist", "Lord Huron")

        assert self.db.seek["artist"] == 31

    def test_write(self):
        self._database()
        self.db.add(self.item)

        assert len(self.db.index) == 1
        assert self.db.seek["artist"] == 31

        self.db.write()
