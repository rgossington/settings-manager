import sys

sys.path.append("../")

import unittest
from settingsmanager import SettingsManager
import os


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.settings = SettingsManager("settings_test.txt")

    def test_standard_read(self):
        value = self.settings.general.test
        self.assertEqual(value, "test value")

        value = self.settings.general.test_boolean
        self.assertEqual(value, True)

        value = self.settings.general.test_int
        self.assertEqual(value, 590)

        value = self.settings.general.test_float
        self.assertEqual(value, 1.989)

        value = self.settings.space_test.test_two_spaces
        self.assertEqual(value, "test3")

        value = self.settings.space_before_section.test
        self.assertEqual(value, "test value")

    def test_new_section(self):
        self.settings.add_section("new_section")
        self.assertEqual(self.settings.new_section._name, "new_section")

        self.settings.new_section.add_entry("new_key", "new value")
        self.assertEqual(self.settings.new_section.new_key, "new value")

        self.settings.add_entry("new_key2", "new value2", self.settings.new_section)
        self.assertEqual(self.settings.new_section.new_key2, "new value2")

    def test_add_entry(self):
        #### Add to existing section
        # add to section instance
        self.settings.general.add_entry("new_key", "new value")
        self.assertEqual(hasattr(self.settings.general, "new_key"), True)
        self.assertEqual(self.settings.general.new_key, "new value")

        # add to settings instance, with section instance
        self.settings.add_entry("new_key2", "new value2", self.settings.general)
        self.assertEqual(hasattr(self.settings.general, "new_key2"), True)
        self.assertEqual(self.settings.general.new_key2, "new value2")

        # add to settings instance, with section name
        self.settings.add_entry("new_key3", "new value3", "general")
        self.assertEqual(hasattr(self.settings.general, "new_key3"), True)
        self.assertEqual(self.settings.general.new_key3, "new value3")

        #### Add to non-existing section
        self.assertRaises(ValueError, self.settings.add_entry, *["new_key", "new_value", None])
        self.assertRaises(AttributeError, self.settings.add_entry, *["new_key", "new_value", "section_does_not_exist"])

        #### Add an already existing key
        self.assertRaises(AttributeError, self.settings.general.add_entry, *["new_key", "attempt to re-add"])
        self.assertRaises(AttributeError, self.settings.add_entry, *["new_key2", "attempt to re-add", "general"])

    def test_refresh(self):
        #### Make changes and then reset to normal file
        self.settings.general.test = "edited value"  # changed from "test value"
        self.settings.add_section("added_section")
        self.settings.add_entry("added_key", "added value", "added_section")
        self.settings.refresh()

        self.assertEqual(self.settings.general.test, "test value")
        self.assertRaises(AttributeError, self.settings.add_entry, *["key", "value", "added_section"])

    def test_save(self):
        #### Save an exact copy
        self.settings.save("copied_settings_test.txt")
        with open("settings_test.txt") as file: lines_before = file.readlines()
        with open("copied_settings_test.txt") as file: lines_after = file.readlines()
        self.assertListEqual(lines_before, lines_after)

        #### Test file_path change after save
        self.assertEqual(self.settings._file_path, "copied_settings_test.txt")

        #### Save an edited copy
        self.settings.general.test = "edited value"
        self.settings.add_entry("new_key", "new value", "general")
        self.settings.space_test.add_entry("new_key_spaces", "new value spaces")
        self.settings.add_section("new_section")
        self.settings.add_entry("key", "value", "new_section")
        self.settings.add_entry("key2", "value2", "new_section")

        self.settings.save("edited_settings_test.txt")
        with open("settings_test.txt") as file: lines_before = file.readlines()
        with open("edited_settings_test.txt") as file: lines_after = file.readlines()

        self.assertNotEqual(lines_before, lines_after)
        self.assertEqual(lines_after[1], "test = edited value\n")
        self.assertEqual(lines_after[6], "new_key = new value\n")
        self.assertEqual(lines_after[16], "new_key_spaces = new value spaces\n")
        self.assertEqual(lines_after[23], "[new_section]\n")
        self.assertEqual(lines_after[24], "key = value\n")
        self.assertEqual(lines_after[25], "key2 = value2\n")

        #### Save over an edited copy
        self.settings.add_entry("key3", "value3", "new_section")
        self.settings.save("edited_settings_test.txt")
        with open("edited_settings_test.txt") as file: lines_after = file.readlines()

        self.assertEqual(lines_after[26], "key3 = value3\n")

        #### Clean up files
        os.remove("copied_settings_test.txt")
        os.remove("edited_settings_test.txt")

    def test_get_sections(self):
        sections = self.settings.get_sections()
        section_names = [section.get_name() for section in sections]
        expected_section_names = ["general", "space_test", "space_before_section"]
        self.assertListEqual(section_names, expected_section_names)

    def test_get_section(self):
        section = self.settings.get_section("general")
        self.assertEqual(section.get_name(), "general")

        #### None existant section
        self.assertRaises(AttributeError, self.settings.get_section, "does_not_exist")

    def test_set_value(self):
        self.settings.set_value("test", "changed value", "general")
        self.assertEqual(self.settings.general.test, "changed value")

        self.settings.set_value("test_boolean", False, self.settings.general)
        self.assertEqual(self.settings.general.test_boolean, False)

        self.settings.general.set_value("test_int", 999)
        self.assertEqual(self.settings.general.test_int, 999)

        #### New value
        self.settings.set_value("new_key", "new value", "general")
        self.assertEqual(self.settings.general.new_key, "new value")

        #### Test errors
        self.assertRaises(ValueError, self.settings.general.set_value, *[0, 0])
        self.assertRaises(AttributeError, self.settings.set_value, *["new_key", "new value", "does_not_exist"])



if __name__ == "__main__":
    unittest.main()
