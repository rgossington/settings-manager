import re


class BaseClass:
    def _get_keys(self):
        attrs = self.get_attributes()
        return attrs.keys()

    def get_attributes(self):
        attrs = self.__dict__
        attrs_filtered = {k: v for k, v in attrs.items() if not k.startswith("_")}
        return attrs_filtered

    @staticmethod
    def convert_to_list(string):
        items = []

        if string is not None and len(string) > 0:
            items = re.split(r", |,", string)

        return items

    @staticmethod
    def _is_key_or_section_name_valid(name):
        if name is None:
            raise ValueError(f"Key or section name must be a string, not None")
        if not isinstance(name, str):
            raise ValueError(f"Key or section name must be a string. {name} is type {type(name)}")
        if name[0] == "_":
            raise ValueError(f"Key or section name must not begin with '_'")
        if name[0].isnumeric():
            raise ValueError(f"Key or section name must not begin with a number")
        if re.search(r"[^a-zA-Z_0-9]", name) is not None:
            raise ValueError(f"Key or section name must only contain letters, numbers and underscores")

        return True

    @staticmethod
    def _is_line_a_heading(line):
        if len(line) < 2:
            return False

        return line[0] == "[" and line[-1] == "]"

    @staticmethod
    def _get_heading_from_line(line):
        return line[1:-1]

    @staticmethod
    def _is_line_an_entry(line):
        return line.count("=") > 0

    @staticmethod
    def _get_key_from_line(line):
        equal_index = line.index("=")
        return line[:equal_index]

    @classmethod
    def _get_value_from_line(cls, line, parse_bool, parse_float, parse_int):
        equal_index = line.index("=")
        value = line[equal_index + 1:]

        if parse_bool:
            value = cls._attempt_parse_bool(value)

        if parse_float:
            value = cls._attempt_parse_float(value)

        if parse_int and not isinstance(value, float):
            value = cls._attemp_parse_int(value)

        return value

    @staticmethod
    def _attempt_parse_bool(value):
        if isinstance(value, str):
            line_lower = value.lower()

            if line_lower == "true":
                return True
            if line_lower == "false":
                return False

        return value

    @staticmethod
    def _attemp_parse_int(value):
        if isinstance(value, str):
            if value.count(".") == 0:
                try:
                    return int(value)
                except ValueError:
                    pass

        return value

    @staticmethod
    def _attempt_parse_float(value):
        if isinstance(value, str):
            if value.count(".") > 0:
                try:
                    return float(value)
                except ValueError:
                    pass

        return value

    @staticmethod
    def _generate_file_line(key, value):
        return f"{key} = {value}\n"
