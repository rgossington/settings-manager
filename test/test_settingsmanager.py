import sys

sys.path.append("../")

import unittest
from settingsmanager import SettingsManager

settings = SettingsManager("settings_test.txt")


class TestConfigReader(unittest.TestCase):
    def test_standard_read(self):
        value = settings.general.test
        self.assertEqual(value, "test value")

        value = settings.general.test_boolean
        self.assertEqual(value, True)

        value = settings.general.test_int
        self.assertEqual(value, 590)

        value = settings.general.test_float
        self.assertEqual(value, 1.989)

        value = settings.space_test.test_two_spaces
        self.assertEqual(value, "test3")

        value = settings.space_before_section.test
        self.assertEqual(value, "test value")

    def test_new_section(self):
        settings.add_section("new_section")
        self.assertEqual(settings.new_section._name, "new_section")

        settings.new_section.add_entry("new_key", "new value")
        self.assertEqual(settings.new_section.new_key, "new value")

        settings.add_entry("new_key2", "new value2", settings.new_section)
        self.assertEqual(settings.new_section.new_key2, "new value2")

    def test_add_to_exsiting_section(self):
        settings.general.add_entry("new_general_key", "new general value")
        self.assertEqual(settings.general.new_general_key, "new general value")

        settings.add_entry("new_general_key2", "new general value2", settings.general)
        self.assertEqual(settings.general.new_general_key2, "new general value2")

if __name__ == "__main__":
    unittest.main()