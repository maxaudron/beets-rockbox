from pathlib import Path
from test.helper import TestHelper
from typing import cast


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
