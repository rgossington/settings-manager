import sys

sys.path.append("../")

import unittest
from settingsmanager import SettingsManager

reader = SettingsManager("settings_test.txt")


class TestConfigReader(unittest.TestCase):
    def test_heading_exists(self):
        #### Test true
        exists = reader.heading_exists("general")
        self.assertEqual(exists, True)

        #### Test false
        exists = reader.heading_exists("test")
        self.assertEqual(exists, False)

    def test_read_entry(self):
        #### Test no spaces
        entry = reader.read_entry("space-test", "test_no_spaces")
        self.assertEqual(entry, "testing1")

        #### Test spaces
        entry = reader.read_entry("space-test", "test_spaces")
        self.assertEqual(entry, "testing2")

        #### Test 1 space1
        entry = reader.read_entry("space-test", "test_one_space")
        self.assertEqual(entry, "testing3")

        #### Test parse boolean1
        entry = reader.read_entry("general", "test_parse_bool1", parse_bool=True)
        self.assertEqual(entry, True)

        #### Test parse boolean2
        entry = reader.read_entry("general", "test_parse_bool2", parse_bool=True)
        self.assertEqual(entry, True)

        #### Test parse boolean3
        entry = reader.read_entry("general", "test_parse_bool3", parse_bool=True)
        self.assertEqual(entry, False)

        #### Test parse boolean4
        entry = reader.read_entry("general", "test_parse_bool4", parse_bool=True)
        self.assertEqual(entry, False)

        #### Test parse int
        entry = reader.read_entry("general", "test_parse_int", parse_int=True)
        self.assertEqual(entry, 509)

        #### Test default
        entry = reader.read_entry("general", "test_default", default="default")
        self.assertEqual(entry, "default")


if __name__ == "__main__":
    unittest.main()