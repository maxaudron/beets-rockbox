from pathlib import Path
from test.helper import TestHelper
from typing import cast

import pytest
from beets.ui import UserError


class TestCli(TestHelper):
    def test_build(self):
        self.add_track(title="Test 1")
        self.add_track(title="Test 2")
        self.runcli("rock", "build")

        output = cast(Path, self.config["rockbox"]["db"].as_path())

        assert (output / "database_0.tcd").is_file()
        assert (output / "database_1.tcd").is_file()
        assert (output / "database_2.tcd").is_file()
        assert (output / "database_3.tcd").is_file()
        assert (output / "database_4.tcd").is_file()
        assert (output / "database_5.tcd").is_file()
        assert (output / "database_6.tcd").is_file()
        assert (output / "database_7.tcd").is_file()
        assert (output / "database_8.tcd").is_file()
        assert (output / "database_12.tcd").is_file()
        assert (output / "database_idx.tcd").is_file()

    def test_copy(self):
        rockbox = cast(Path, self.config["rockbox"]["rockbox"].as_path())

        self.add_track(title="Test 1")
        self.add_track(title="Test 2")
        self.runcli("rock", "build")

        with pytest.raises(UserError):
            self.runcli("rock", "copy")

        rockbox.mkdir(parents=True, exist_ok=True)
        self.runcli("rock", "copy")

        assert (rockbox / "database_0.tcd").is_file()
        assert (rockbox / "database_1.tcd").is_file()
        assert (rockbox / "database_2.tcd").is_file()
        assert (rockbox / "database_3.tcd").is_file()
        assert (rockbox / "database_4.tcd").is_file()
        assert (rockbox / "database_5.tcd").is_file()
        assert (rockbox / "database_6.tcd").is_file()
        assert (rockbox / "database_7.tcd").is_file()
        assert (rockbox / "database_8.tcd").is_file()
        assert (rockbox / "database_12.tcd").is_file()
        assert (rockbox / "database_idx.tcd").is_file()
