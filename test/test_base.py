import sys

sys.path.append("../")

import unittest
from settingsmanager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.settings = SettingsManager("settings_test.txt")

    def test_get_keys(self):
        section_keys = self.settings._get_keys()
        self.assertListEqual(list(section_keys), ["general", "space_test", "space_before_section"])

        general_keys = self.settings.general._get_keys()
        self.assertListEqual(list(general_keys), ["test", "test_boolean", "test_boolean2", "test_int", "test_float"])

    def test_get_attributes(self):
        sections = self.settings.get_attributes()
        expected_sections = {
            "general": self.settings.general,
            "space_test": self.settings.space_test,
            "space_before_section": self.settings.space_before_section
        }
        self.assertDictEqual(sections, expected_sections)

        attributes = self.settings.general.get_attributes()
        expected_attributes = {
            "test": "test value",
            "test_boolean": True,
            "test_boolean2": False,
            "test_int": 590,
            "test_float": 1.989
        }
        self.assertDictEqual(attributes, expected_attributes)

    def test_convert_string_to_list(self):
        string = "item1, item2,item3,item4"
        expected_list = ["item1", "item2", "item3", "item4"]
        self.assertListEqual(self.settings.convert_string_to_list(string), expected_list)

    def test_is_key_or_section_name_valid(self):
        valid = self.settings._is_key_or_section_name_valid("valid_name")
        self.assertEqual(valid, True)

        valid = self.settings._is_key_or_section_name_valid("valid_with_numb3r5")
        self.assertEqual(valid, True)

        #### Exceptions
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, None)
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, 123)
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "_invalid")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "123_invalid")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid!")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid)")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid?")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid=")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid.")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid,")
        self.assertRaises(ValueError, self.settings._is_key_or_section_name_valid, "invalid*")

    def test_is_line_a_heading(self):
        string = "[is_heading]"
        self.assertEqual(self.settings._is_line_a_heading(string), True)

        string = "[y]"
        self.assertEqual(self.settings._is_line_a_heading(string), True)

        string = "[]"
        self.assertEqual(self.settings._is_line_a_heading(string), False)

        string = "[not_heading"
        self.assertEqual(self.settings._is_line_a_heading(string), False)

        string = "not_heading"
        self.assertEqual(self.settings._is_line_a_heading(string), False)

        string = "not a heading"
        self.assertEqual(self.settings._is_line_a_heading(string), False)

    def test_get_heading_from_line(self):
        string = "[heading]"
        self.assertEqual(self.settings._get_heading_from_line(string), "heading")

    def test_clean_line(self):
        line_before = "key = value  \n"
        line_after_expected = "key=value"
        self.assertEqual(self.settings._clean_line(line_before), line_after_expected)

        line_before = "key =  value  \n"
        line_after_expected = "key= value"
        self.assertEqual(self.settings._clean_line(line_before), line_after_expected)

    def test_is_line_an_entry(self):
        string = "key=value"
        self.assertEqual(self.settings._is_line_an_entry(string), True)

        string = "key = value"
        self.assertEqual(self.settings._is_line_an_entry(string), True)

        string = "valid_key0 = value"
        self.assertEqual(self.settings._is_line_an_entry(string), True)

        string = "key = value, with punctuation!"
        self.assertEqual(self.settings._is_line_an_entry(string), True)

        string = "# obvious comment"
        self.assertEqual(self.settings._is_line_an_entry(string), False)

        string = "# comment = comment"
        self.assertEqual(self.settings._is_line_an_entry(string), False)

        string = "no equals sign"
        self.assertEqual(self.settings._is_line_an_entry(string), False)

    def test_get_key_from_line(self):
        string = "key = value"
        self.assertEqual(self.settings._get_key_from_line(string), "key")

        string = "key=value"
        self.assertEqual(self.settings._get_key_from_line(string), "key")

        string = "valid_key012 = value"
        self.assertEqual(self.settings._get_key_from_line(string), "valid_key012")

        string = "# key = value commented out"
        self.assertEqual(self.settings._get_key_from_line(string), None)

    def test_get_value_from_line(self):
        string = "key = value"
        self.assertEqual(self.settings._get_value_from_line(string), "value")

        string = "key=value"
        self.assertEqual(self.settings._get_value_from_line(string), "value")

        string = "key = value with multiple words!"
        self.assertEqual(self.settings._get_value_from_line(string), "value with multiple words!")

        string = "boolean = True"
        self.assertEqual(self.settings._get_value_from_line(string), True)

        string = "integer = 12345"
        self.assertEqual(self.settings._get_value_from_line(string), 12345)

        string = "float = 12.345"
        self.assertEqual(self.settings._get_value_from_line(string), 12.345)

        string = "string = 12.345!"
        self.assertEqual(self.settings._get_value_from_line(string), "12.345!")

        string = "# commented_out = value"
        self.assertEqual(self.settings._get_value_from_line(string), None)

    def test_attempt_parse_bool(self):
        input = "True"
        self.assertEqual(self.settings._attempt_parse_bool(input), True)

        input = "False"
        self.assertEqual(self.settings._attempt_parse_bool(input), False)

        input = "string"
        self.assertEqual(self.settings._attempt_parse_bool(input), "string")

        input = 123
        self.assertEqual(self.settings._attempt_parse_bool(input), 123)

    def test_attempt_parse_int(self):
        input = "123"
        self.assertEqual(self.settings._attempt_parse_int(input), 123)

        input = 123
        self.assertEqual(self.settings._attempt_parse_int(input), 123)

        input = "string"
        self.assertEqual(self.settings._attempt_parse_int(input), "string")

        input = "True"
        self.assertEqual(self.settings._attempt_parse_int(input), "True")

    def test_attempt_parse_float(self):
        input = "123.456"
        self.assertEqual(self.settings._attempt_parse_float(input), 123.456)

        input = 123
        self.assertEqual(self.settings._attempt_parse_float(input), 123)

        input = "string"
        self.assertEqual(self.settings._attempt_parse_float(input), "string")

        input = "True"
        self.assertEqual(self.settings._attempt_parse_float(input), "True")

    def test_generate_file_line(self):
        self.assertEqual(self.settings._generate_file_line("key", "value"), "key = value\n")


if __name__ == "__main__":
    unittest.main()