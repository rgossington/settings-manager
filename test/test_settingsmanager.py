import sys

sys.path.append("../")

import unittest
from settingsmanager import SettingsManager
from settingsmanager import Section
import os
import shutil


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.settings = SettingsManager("settings_test.txt")

    def test_new_file(self):
        # Create file
        new_settings = SettingsManager("new_file.txt")
        file_exists = os.path.exists("new_file.txt")
        self.assertEqual(file_exists, True)

        # Add settings (save method is tested properly later)
        new_settings.add_section("new_section")
        new_settings.add_entry("new_key", "new value", "new_section")
        new_settings.save()

        file_exists = os.path.exists("new_file.txt")
        self.assertEqual(file_exists, True)

        # clean up file
        os.remove("new_file.txt")

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

    def test_refresh_and_has_changed(self):
        #### No change
        shutil.copy("settings_test.txt", "settings_test_has_changed.txt")
        settings_has_changed = SettingsManager("settings_test_has_changed.txt")
        self.assertEqual(settings_has_changed.refresh_and_has_changed(), False)

        #### Edited key
        with open("settings_test_has_changed.txt", "r") as file: lines = file.readlines()
        lines[1] = "test = edited value\n"
        with open("settings_test_has_changed.txt", "w") as file: file.writelines(lines)
        self.assertEqual(settings_has_changed.refresh_and_has_changed(), True)

        #### Added section and key
        lines.append("\n")
        lines.append("[new_section]\n")
        lines.append("new_key = new value\n")
        with open("settings_test_has_changed.txt", "w") as file: file.writelines(lines)
        self.assertEqual(settings_has_changed.refresh_and_has_changed(), True)

        #### Tidy files
        os.remove("settings_test_has_changed.txt")

    def test_read_file(self):
        #### Reset line lists
        self.settings._lines_raw = None
        self.settings._lines_cleaned = None
        self.settings._read_file()

        #### Spot check variables
        self.assertEqual(self.settings._lines_raw[0], "[general]\n")
        self.assertEqual(self.settings._lines_cleaned[0], "[general]")

        self.assertEqual(self.settings._lines_raw[11], "test_space = test2\n")
        self.assertEqual(self.settings._lines_cleaned[11], "test_space=test2")

        self.assertEqual(len(self.settings._lines_raw), 20)
        self.assertEqual(len(self.settings._lines_cleaned), 20)

    def test_clean_file_lines(self):
        self.assertEqual(self.settings._lines_cleaned[1], "test=test value")

    def test_clear_attributes(self):
        self.settings._clear_attributes()
        self.assertEqual(hasattr(self.settings, "general"), False)
        self.assertEqual(hasattr(self.settings, "space_test"), False)
        self.assertEqual(hasattr(self.settings, "space_before_section"), False)

    def test_set_section_end_index(self):
        self.assertEqual(self.settings.general._end_index_in_file, 6)
        self.assertEqual(self.settings.space_test._end_index_in_file, 15)
        self.assertEqual(self.settings.space_before_section._end_index_in_file, 20)

    def test_insert_line_into_section(self):
        #### Insert into first section
        self.settings._insert_line_into_section(self.settings.general, "test_line\n")
        self.assertEqual(self.settings.general._start_index_in_file, 0)
        self.assertEqual(self.settings.general._end_index_in_file, 7)
        self.assertEqual(self.settings.space_test._start_index_in_file, 8)
        self.assertEqual(self.settings.space_test._end_index_in_file, 16)
        self.assertEqual(self.settings.space_before_section._start_index_in_file, 19)
        self.assertEqual(self.settings.space_before_section._end_index_in_file, 21)

        #### Insert into later section
        self.settings._insert_line_into_section(self.settings.space_test, "test_line\n")
        self.assertEqual(self.settings.general._start_index_in_file, 0)
        self.assertEqual(self.settings.general._end_index_in_file, 7)
        self.assertEqual(self.settings.space_test._start_index_in_file, 8)
        self.assertEqual(self.settings.space_test._end_index_in_file, 17)
        self.assertEqual(self.settings.space_before_section._start_index_in_file, 20)
        self.assertEqual(self.settings.space_before_section._end_index_in_file, 22)

    def test_insert_new_section_line(self):
        new_section = Section("new_section")
        self.settings._insert_new_section_line(new_section)

        self.assertEqual(new_section._start_index_in_file, 21)
        self.assertEqual(new_section._end_index_in_file, 22)
        self.assertEqual(self.settings._lines_raw[20], "\n")
        self.assertEqual(self.settings._lines_cleaned[20], "")
        self.assertEqual(self.settings._lines_raw[21], "[new_section]\n")
        self.assertEqual(self.settings._lines_cleaned[21], "[new_section]")

    def test_get_name(self):
        self.assertEqual(self.settings.general.get_name(), "general")
        self.assertEqual(self.settings.space_test.get_name(), "space_test")


if __name__ == "__main__":
    unittest.main()
