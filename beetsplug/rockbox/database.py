import logging
import os
import struct
from io import BufferedWriter
from pathlib import Path
from typing import Any, cast

from beets.library import Item, Library
from beets.ui import print_

from beetsplug.rockbox.config import Config


# <- len   -> | <- idx   -> |  A  U  R  O | R  A \0
# 08 00 00 00 | FF FF FF FF | 41 55 52 4F | 52 41 00 58
#
# 10 00 00 00 | FF FF FF FF | 42 61 72 6F | 6E 20 42 6C | 61 63 6B 00 | 58 58 58 58
# 10 00 00 00 | FF FF FF FF | 42 65 61 20 | 4D 69 6C 6C | 65 72 00 58 | 58 58 58 58 | 58
# 10 00 00 00 | FF FF FF FF | 42 6C 75 65 | 20 53 74 61 | 68 6C 69 00 | 58 58 58 58
# 10 00 00 00 | FF FF FF FF | 42 4F 4E 45 | 53 20 55 4B | 00 58 58 58 | 58 58 58 58
# 10 00 00 00 | FF FF FF FF | 43 61 72 61 | 76 61 6E 20 | 50 61 6C 61 | 63 65 00 58
# 10 00 00 00 | FF FF FF FF | 43 68 72 69 | 73 20 43 61 | 72 64 65 6E | 61 00 58 58
# 18 00 00 00 | FF FF FF FF | 43 68 72 69 | 73 20 43 68 | 72 69 73 74 | 6F 64 6F 75 | 6C 6F 75 00 | 58 58 58 58
# 10 00 00 00 | FF FF FF FF | E9 99 B3 E5 | A5 95 E8 BF | 85 00 58 58 | 58 58 58 58
class TagfileEntry:
    """Single entry in the database file containing the string length, index id and tag string data
    MAYBE the length is padded to the multiplier of 4 bytes and the str padded with X
    """

    tag_length: int
    idx_id: int = 0xFFFFFFFF
    tag_data: bytes

    """byte offset used for computing seek positions"""
    seek: int

    def __init__(self, tag_data: str, offset: int, idx: int | None = None):
        self.tag_data = bytes(tag_data + "\0", encoding="utf8")
        self.tag_length = len(self.tag_data)
        self.seek = offset

        if idx is not None:
            self.idx_id = idx

    def length(self) -> int:
        return 8 + self.tag_length

    def write(self, f: BufferedWriter):
        f.write(struct.pack("<I", self.tag_length))
        f.write(struct.pack("<I", self.idx_id))
        f.write(self.tag_data)


#
# 15 26 9E FB artist
# FD 5A BE 6F album
# D9 8A EF 99 genre
# 67 72 6A F5 title
# 99 B8 B2 E8 filename
# 8C 3E C6 24 composer
# 8C 3E C6 24 comment
# 15 26 9E FB albumartist
# 67 72 6A F5 grouping
# E9 07 00 00 ?year
# 01 00 00 00 ?discnumber
# 04 00 00 00 ?tracknumber
# 15 26 9E FB canonicalartist
# 83 00 00 00 ?bitrate
# 3F 52 04 00 ?length
# 00 00 00 00 ?playcount
# 00 00 00 00 ?rating
# 00 00 00 00 ?playtime
# 00 00 00 00 ?lastplayed
# 00 00 00 00 ?commitid
# 7E 3D 09 69 ?mtime?
# 00 00 00 00 ?lastelapsed
# 00 00 00 00 ?lastoffset

Seek = int

INDEX_ENTRY_SIZE: int = 24 * 4


class IndexEntry:
    artist: Seek
    album: Seek
    genre: Seek
    title: Seek
    filename: Seek
    composer: Seek
    comment: Seek
    albumartist: Seek
    grouping: Seek
    canonicalartist: Seek

    year: int = 0
    discnumber: int = 0
    tracknumber: int = 0
    bitrate: int = 0
    length: int = 0
    playcount: int = 0
    rating: int = 0
    playtime: int = 0
    lastplayed: int = 0
    commitid: int = 0
    mtime: int = 0
    lastelapsed: int = 0
    lastoffset: int = 0

    flag: int = 0

    def __init__(
        self,
        artist: Seek,
        album: Seek,
        genre: Seek,
        title: Seek,
        filename: Seek,
        composer: Seek,
        comment: Seek,
        albumartist: Seek,
        grouping: Seek,
        canonicalatist: Seek,
        item: Item,
    ):
        self.artist = artist
        self.album = album
        self.genre = genre
        self.title = title
        self.filename = filename
        self.composer = composer
        self.comment = comment
        self.albumartist = albumartist
        self.grouping = grouping
        self.canonicalartist = canonicalatist
        self.from_item(item)

    def write(self, f: BufferedWriter):
        f.write(struct.pack("<I", self.artist))
        f.write(struct.pack("<I", self.album))
        f.write(struct.pack("<I", self.genre))
        f.write(struct.pack("<I", self.title))
        f.write(struct.pack("<I", self.filename))
        f.write(struct.pack("<I", self.composer))
        f.write(struct.pack("<I", self.comment))
        f.write(struct.pack("<I", self.albumartist))
        f.write(struct.pack("<I", self.grouping))

        f.write(struct.pack("<I", self.year))
        f.write(struct.pack("<I", self.discnumber))
        f.write(struct.pack("<I", self.tracknumber))

        f.write(struct.pack("<I", self.canonicalartist))

        f.write(struct.pack("<I", self.bitrate))
        f.write(struct.pack("<I", self.length))
        f.write(struct.pack("<I", self.playcount))
        f.write(struct.pack("<I", self.rating))
        f.write(struct.pack("<I", self.playtime))
        f.write(struct.pack("<I", self.lastplayed))
        f.write(struct.pack("<I", self.commitid))
        f.write(struct.pack("<I", self.mtime))
        f.write(struct.pack("<I", self.lastelapsed))
        f.write(struct.pack("<I", self.lastoffset))

        f.write(struct.pack("<I", self.flag))

    def from_item(self, item: Item):
        self.year = _get_tag(item, "year")
        if _get_tag(item, "disctotal") > 1:
            self.discnumber = _get_tag(item, "disc")
        self.tracknumber = _get_tag(item, "track")
        self.bitrate = round(_get_tag(item, "bitrate") / 1000)
        self.length = round(_get_tag(item, "length") * 1000)
        self.mtime = int(_get_tag(item, "mtime"))


def _get_tag(item: Item, tag: str) -> int:
    t = item.get(tag)
    if t and (isinstance(t, (int, float))):
        return cast(int, t)
    else:
        return 0


HEADER_SIZE = 12


class Header:
    magic: bytes = bytes.fromhex("10 48 43 54")
    datasize: int = 0
    entry_count: int = 0

    """Static byte offset used for computing seek positions"""
    offset: int = HEADER_SIZE

    def __init__(self, datasize: int, entry_count: int):
        self.datasize = datasize
        self.entry_count = entry_count

    def write(self, f: BufferedWriter):
        f.write(self.magic)
        f.write(struct.pack("<I", self.datasize))
        f.write(struct.pack("<I", self.entry_count))


MASTER_HEADER_SIZE = HEADER_SIZE + 12


class MasterHeader(Header):
    serial: int = 0
    commitid: int = 1
    dirty: int = 0

    def __init__(self, datasize: int, entry_count: int, serial: int, commitid: int, dirty: bool):
        super().__init__(datasize, entry_count)
        self.serial = serial
        self.commitid = commitid
        self.dirty = int(dirty)

    def write(self, f: BufferedWriter):
        super().write(f)
        f.write(struct.pack("<I", self.serial))
        f.write(struct.pack("<I", self.commitid))
        f.write(struct.pack("<I", self.dirty))


class Database:
    def __init__(self, log: logging.Logger, lib: Library, config: Config):
        self._log = log
        self._config = config
        self.lib = lib

        self.tag_files: dict[str, Path] = {
            "artist": self._config.db / "database_0.tcd",
            "album": self._config.db / "database_1.tcd",
            "genre": self._config.db / "database_2.tcd",
            "title": self._config.db / "database_3.tcd",
            "filename": self._config.db / "database_4.tcd",
            "composer": self._config.db / "database_5.tcd",
            "comment": self._config.db / "database_6.tcd",
            "albumartist": self._config.db / "database_7.tcd",
            "grouping": self._config.db / "database_8.tcd",
            "canonicalartist": self._config.db / "database_12.tcd",
        }

        # Initialize tag data storage
        self.tag_data: dict[str, dict[str, TagfileEntry]] = {key: {} for key in self.tag_files}

        # initialize seek offsets with base of 12 to account for the header
        self.seek: dict[str, int] = {}
        for key in self.tag_files:
            self.seek[key] = HEADER_SIZE

        self.index: list[IndexEntry] = []

    def add_tag(self, tag: str, value: str, idx: int | None = None):
        if value not in self.tag_data[tag]:
            entry = TagfileEntry(value, 0, idx)
            self.tag_data[tag][value] = entry

    def get_str(self, item: Item, key: str) -> str:  # type: ignore
        cast(str, item.get(key))  # type: ignore

    def set_tag(self, tag_a: str, tag_b: str, item: Item, idx: int | None = None):
        t = item.get(tag_b)
        if t and isinstance(t, str):
            self.add_tag(tag_a, t, idx)
        elif self._config.unknown not in self.tag_data[tag_a]:
            self.add_tag(tag_a, self._config.unknown)

    def set_list_tag(self, tag_a: str, tag_b: str, item: Item):
        t = item.get(tag_b)
        if t and isinstance(t, list):
            self.add_tag(tag_a, t[0])

    def get_tag_seek(self, item: Item, tag_a: str, tag_b: str | None = None) -> Seek:
        if not tag_b:
            tag_b = tag_a

        t = item.get(tag_b)
        if t and isinstance(t, str):
            return self.tag_data[tag_a][t].seek
        else:
            return self.tag_data[tag_a][self._config.unknown].seek

    def add_item(self, item: Item):
        """Add an items tags to the tag databases"""
        self.set_tag("artist", "artist", item)
        self.set_tag("album", "album", item)
        self.set_tag("genre", "genre", item)

        self.set_tag("title", "title", item)

        # Absolute Path
        # TODO understand path formats
        self.add_tag("filename", str(self.get_filename(item)))

        self.set_tag("composer", "composer", item)
        self.set_tag("comment", "comments", item)
        self.set_tag("albumartist", "albumartist", item)
        self.set_tag("grouping", "grouping", item)

        self.set_tag("canonicalartist", "artist_sort", item)

    def get_filename(self, item: Item) -> str:
        filename = item.destination(path_formats=None, relative_to_libdir=True)  # type: ignore
        filename = Path(self._config.music) / Path(str(filename, "utf8"))

        if self._config.formats is not None and filename.suffix[1:] not in self._config.formats:
            filename = filename.with_suffix("." + self._config.formats[0])

        self._log.debug(f"writing filename to db: {filename}")
        return str(filename)

    def sort(self):
        """Sort the tag databases to be in alphabetical order"""
        for tag in self.tag_files:
            self.tag_data[tag] = dict(sorted(self.tag_data[tag].items()))

            # Set seek values in order
            for v in self.tag_data[tag].values():
                offset = self.seek[tag]
                v.seek = offset
                self.seek[tag] += v.length()

    def add_index(self, item: Item):
        """Build the index entry for item to reference the already added tags"""

        idx = len(self.index)
        self.tag_data["title"][item.get("title")].idx_id = idx  # type: ignore

        filename = self.get_filename(item)
        self.tag_data["filename"][filename].idx_id = idx
        filename_seek = self.tag_data["filename"][filename].seek

        index = IndexEntry(
            self.get_tag_seek(item, "artist"),
            self.get_tag_seek(item, "album"),
            self.get_tag_seek(item, "genre"),
            self.get_tag_seek(item, "title"),
            filename_seek,
            self.get_tag_seek(item, "composer"),
            self.get_tag_seek(item, "comment"),
            self.get_tag_seek(item, "albumartist"),
            self.get_tag_seek(item, "grouping"),
            self.get_tag_seek(item, "canonicalartist", "artist_sort"),
            item,
        )
        self.index.append(index)

    def write_index(self):
        count = len(self.index)
        index_size = MASTER_HEADER_SIZE + (INDEX_ENTRY_SIZE * count)
        data_size = 0
        for x in self.seek.values():
            data_size += x

        header = MasterHeader(index_size + data_size, count, 0, 0, False)
        with (self._config.db / "database_idx.tcd").open(mode="wb") as f:
            header.write(f)
            for i in self.index:
                i.write(f)

    def write_tag(self, tag: str):
        header = Header(self.seek[tag], len(self.tag_data[tag]))
        with (self._config.db / self.tag_files[tag]).open(mode="wb") as f:
            header.write(f)
            for t in self.tag_data[tag].values():
                t.write(f)

    def write(self):
        self._config.db.mkdir(parents=True, exist_ok=True)

        self.write_index()
        for tag in self.tag_files:
            self.write_tag(tag)
