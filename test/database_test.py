# pyright: reportPrivateUsage=false
import logging

import pytest

from beetsplug.rockbox import Config
from beetsplug.rockbox.database import Database, IndexEntry

from .helper import TestHelper

LOGGER = logging.getLogger(__name__)


class TestDatabase(TestHelper):
    def _database(self):
        config = Config(self.config["rockbox"])
        self.db = Database(LOGGER, None, config)  # type: ignore

    def test_database_add(self):
        self.config["rockbox"]["formats"] = ["flac"]
        self._database()

        item1 = self.add_track(file="01 Looking Back.opus")
        item2 = self.add_track(file="01 Queendom.opus")

        filename1 = "/<HDD0>/Music/Lord Huron/The Cosmic Selector Vol. 1/01 Looking Back.flac"
        filename2 = "/<HDD0>/Music/AURORA/Infections of a Different Kind (Step I)/01 Queendom.flac"

        self.db.add_item(item1)
        self.db.add_item(item2)

        self.db.sort()

        assert "Lord Huron" in self.db.tag_data["artist"]
        assert "Lord Huron" in self.db.tag_data["canonicalartist"]
        assert "The Cosmic Selector Vol. 1" in self.db.tag_data["album"]
        assert "Looking Back" in self.db.tag_data["title"]
        assert filename1 in self.db.tag_data["filename"]
        assert len(self.db.tag_data["composer"]) == 1

        self.db.add_index(item1)
        self.db.add_index(item2)


        assert self.db.tag_data["title"]["Looking Back"].idx_id == 0
        assert self.db.tag_data["title"]["Queendom"].idx_id == 1
        
        assert self.db.tag_data["filename"][filename1].idx_id == 0
        assert self.db.tag_data["filename"][filename2].idx_id == 1

        assert self.db.index[0].artist == self.db.tag_data["artist"]["Lord Huron"].seek
        assert self.db.index[1].artist == self.db.tag_data["artist"]["AURORA"].seek

    def test_indexentry(self):
        self._database()
        item = self.add_track()
        self.db.add_item(item)
        index = IndexEntry(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, item)

        assert index.year == 2025
        assert index.discnumber == 0
        assert index.tracknumber == 1
        assert index.bitrate == 172
        assert index.length == 1914
        assert index.mtime != 0

    def test_build_all(self):
        self._database()

        track1 = self.add_track(file="01 Looking Back.opus")
        track2 = self.add_track(file="02 Bag of Bones.opus")
        track3 = self.add_track(file="01 Queendom.opus")
        track4 = self.add_track(file="02 Forgotten Love.opus")

        self.db.add_item(track1)
        self.db.add_item(track2)
        self.db.add_item(track3)
        self.db.add_item(track4)
        self.db.sort()
        self.db.add_index(track1)
        self.db.add_index(track2)
        self.db.add_index(track3)
        self.db.add_index(track4)
        self.db.write()
