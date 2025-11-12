## Database Format & Internals

The rockbox database is relativly simple consisting mainly of two components,
the numbered `+database_{0..8,12}.tcd+` files containing the tags and the
database index `+database_idx.tcd+`.

### Tags

The numbered databases contain the complex tags extracted from music files,
each containing one type of tag:

* `database_0.tcd`: artist
* `database_1.tcd`: album
* `database_2.tcd`: genre
* `database_3.tcd`: title
* `database_4.tcd`: filename
* `database_5.tcd`: composer
* `database_6.tcd`: comment
* `database_7.tcd`: albumartist
* `database_8.tcd`: grouping
* `database_12.tcd`: canonicalartist -> artist_sort

The database file is encoded in binary data and made up of two main components
defined by the following classes, whose values are serialized to little-endian
in the case of int or encoded to utf8 as raw bytes for str.

The file starts with a Header containing some base information

```python
class Header:
    magic: bytes # bytes.fromhex("10 48 43 54")
    """Static Header containing the string TCH and a version number, currently 0x10"""

    datasize: int # 0
    """Size of this file in bytes"""

    entry_count: int # 0
    """Number of entries in file"""
```

Each tag value is then appended:

```python
class TagfileEntry:
    tag_length: int
    """Length of the string of tag_data including the terminating \0"""

    idx_id: int # 0xFFFFFFFF
    """Index ID in the database index for this entry. Only set for title and
    filename, else defaults to MAX_INT"""

    tag_data: bytes
    """UTF-8 encoded string value of the tag, terminated with \0"""
```

### Index

The index database file also starts off with a header, but extended with
additional fields. The values do not matter for our case when building the
database externally and are mainly used for incremental database updates, thus
they are hardcoded here.

The Header's datasize field is instead also set to the total amount of bytes
used for all database files.

```python
class MasterHeader(Header):
    serial: int # 0
    commitid: int # 1
    dirty: int # 0
```

This is followed by an IndexEntry for each beets database item, which maps to
the tags defined in the database files as well as containing some additional
tags that are are ints.

IndexEntry is a fixed size, so will be read in by rockbox as a list and the
idx_id of the tag databases points to the index of that list.

```python
class IndexEntry:
    artist: Seek
    [...]

    year: int # 0
    [...]

    flag: int # 0
```

The database tags are addresses pointing to a byte location in the database file
for the tag. So e.g. the first item points to the first artist at byte 12

The int tags that are set from beets values are:

* year
* discnumber
* tracknumber
* bitrate
* length
* mtime

And the other tags are mostly used for internal state tracking if you have
statistics enabled (which does not vibe with our usecase):

* playcount
* rating
* playtime
* lastplayed
* commitid
* lastelapsed
* lastoffset

The flag is used to indicate if items where delete, or restored, etc. This is
unused for our case and hardcoded to 0
