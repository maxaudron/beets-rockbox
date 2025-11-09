from pathlib import Path

import confuse
from beets.dbcore import Query
from beets.library import Item, parse_query_string


class Config:
    db: Path
    """Directory to where the rockbox database_*.tcd files are written to."""

    rockbox: Path
    """Directory where your .rockbox folder is located. Used for copying over the database to the device"""

    music: str
    """Absolute path where music is stored on the rockbox device. Example: <HDD0>/Music"""

    extension: str | None = None
    """If set, overrides the extension of the filepaths to the one provided"""

    query: Query
    """Query to restrict which files are included in rockbox database
    e.g set this to the same value as the beets-alternatives library used
    """

    mount_command: str | None = None
    umount_command: str | None = None

    def __init__(self, config: confuse.ConfigView):
        self.db = config["db"].as_path()  # pyright: ignore
        assert isinstance(self.db, Path)
        
        self.rockbox = config["rockbox"].as_path()  # pyright: ignore
        assert isinstance(self.rockbox, Path)

        self.music = config["music"].as_str()  # pyright: ignore
        assert isinstance(self.music, str)

        if "extension" in config:
            self.extension = config["extension"].as_str()  # pyright: ignore

        query = config["query"].get(confuse.Optional(confuse.String(), default=""))
        self.query, _ = parse_query_string(query, Item)
