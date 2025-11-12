from pathlib import Path

import confuse
from beets.dbcore import Query
from beets.library import Item, parse_query_string


class Config:
    db: Path
    """Directory to where the rockbox database_*.tcd files are written to."""

    music: str
    """Absolute path where music is stored on the rockbox device. Example: "/<HDD0>/Music".
    This is used to set the filename references for Items.
    """

    formats: list[str] | None = None
    """If set, overrides the extension of any files with an extension not in this list
    with the first one provided.
    Example:
    extension: ["opus", "mp3"]
    """

    query: Query
    """Query to restrict which files are included in rockbox database
    e.g set this to the same value as the beets-alternatives library used
    """

    unknown: str = "<Unknown>"
    """String to use as placeholder for unknown values. Default: "<Unknown>"."""

    mount_command: str | None = None
    umount_command: str | None = None

    def __init__(self, config: confuse.ConfigView):
        self.db = config["db"].as_path()  # pyright: ignore
        assert isinstance(self.db, Path)
        
        self.music = config["music"].as_str()  # pyright: ignore
        assert isinstance(self.music, str)

        if "formats" in config:
            self.formats = config["formats"].get()  # pyright: ignore
        
        if "unknown" in config:
            self.unknown = config["unknown"].as_str()  # pyright: ignore

        query = config["query"].get(confuse.Optional(confuse.String(), default=""))
        self.query, _ = parse_query_string(query, Item)
