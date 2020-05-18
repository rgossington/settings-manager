from settingsmanager.base import BaseClass


class Section(BaseClass):
    def __init__(self, heading_name):
        self._name = heading_name
        self._start_index_in_file = None
        self._end_index_in_file = None

    def add_entry(self, key, value):
        if self._is_key_or_section_name_valid(key):
            if hasattr(self, key):
                raise AttributeError(f"Duplicate key '{key}' in section '{self._name}'")

            self.set_value(key, value)

    def get_name(self):
        return self._name

    def set_value(self, key, value):
        if self._is_key_or_section_name_valid(key):
            setattr(self, key, value)


class SettingsManager(BaseClass):
    def __init__(self, file_path, parse_bool=True, parse_int=True, parse_float=True):
        self._parse_bool = parse_bool
        self._parse_int = parse_int
        self._parse_float = parse_float
        self._file_path = file_path

        self._lines_raw = None
        self._lines_cleaned = None

        self.refresh()

    def add_section(self, heading_name):
        if self._is_key_or_section_name_valid(heading_name):
            section = Section(heading_name)
            setattr(self, heading_name, section)
            return section

    def add_entry(self, key, value, section):
        section = self.get_section(section)
        section.add_entry(key, value)

    def refresh(self):
        self._clear_attributes()
        self._read_file()

        section = None

        for index, line in enumerate(self._lines_cleaned):
            # Create section
            if self._is_line_a_heading(line):
                if section is not None:
                    self._set_section_end_index(section, index)

                heading_name = self._get_heading_from_line(line)
                section = self.add_section(heading_name)
                section._start_index_in_file = index
                continue

            # Set up entry within the section, if one was found
            if self._is_line_an_entry(line):
                key = self._get_key_from_line(line)
                value = self._get_value_from_line(line, self._parse_bool, self._parse_float, self._parse_int)
                self.add_entry(key, value, section)

        if section is not None:
            self._set_section_end_index(section, len(self._lines_cleaned))

    def save(self, new_file_path=None):
        if new_file_path is None:
            new_file_path = self._file_path

        self._file_path = new_file_path
        sections = self.get_sections()

        # Add new sections to the file lines
        for section in sections:
            # If it is missing, add to the raw file lines
            if section._start_index_in_file is None:
                self._insert_new_section_line(section)

        # Iterate through each section and add/update keys
        for section in sections:
            # Update existing keys in the section and check for missing ones
            section_attrs_to_add = section.get_attributes()

            for index in range(section._start_index_in_file + 1, section._end_index_in_file):
                line = self._lines_cleaned[index]

                if self._is_line_an_entry(line):
                    key = self._get_key_from_line(line)
                    value = getattr(section, key)
                    self._lines_raw[index] = self._generate_file_line(key, value)

                    del section_attrs_to_add[key]

            # Add missing section keys
            for key in section_attrs_to_add:
                value = section_attrs_to_add.get(key)
                self._insert_line_into_section(section, self._generate_file_line(key, value))

        # Save lines
        with open(new_file_path, "w") as file:
            file.writelines(self._lines_raw)

    def get_sections(self):
        attrs = self.get_attributes()
        return [v for k, v in attrs.items() if isinstance(v, Section)]

    def get_section(self, section):
        if isinstance(section, Section):
            return section
        elif isinstance(section, str):
            section_name = section
        else:
            raise ValueError(f"Section parameter must be a string (ie the section name), not {type(section)}.")

        sections = self.get_sections()

        for section in sections:
            if section.get_name() == section_name:
                return section

        raise AttributeError(f"Section '{section_name}' not found.")

    def set_value(self, key, value, section):
        section = self.get_section(section)
        section.set_value(key, value)

    def refresh_and_has_changed(self):
        lines_before = self._lines_cleaned
        self.refresh()
        return lines_before != self._lines_cleaned

    def _read_file(self):
        try:
            with open(self._file_path, "r") as file:
                self._lines_raw = file.readlines()
                self._clean_file_lines()
        except FileNotFoundError:
            # creates file if not found
            with open(self._file_path, "w"):
                self._lines_raw = []
                self._clean_file_lines()
                pass

    def _clean_file_lines(self):
        lines_cleaned = []

        for line in self._lines_raw:
            lines_cleaned.append(self._clean_line(line))

        self._lines_cleaned = lines_cleaned

    def _clear_attributes(self):
        keys = self._get_keys()

        for key in keys:
            delattr(self, key)

    def _set_section_end_index(self, section, index):
        # Ignores blank lines at end of the section
        end_index = index

        while self._lines_cleaned[end_index-1] == "":
            end_index -= 1

        section._end_index_in_file = end_index

    def _insert_line_into_section(self, section, value):
        # Insert into this section
        index = section._end_index_in_file
        self._lines_raw.insert(index, value)
        self._lines_cleaned.insert(index, self._clean_line(value))
        section._end_index_in_file += 1

        # Shift later sections
        sections = self.get_sections()

        for section in sections:
            if section._start_index_in_file >= index:
                section._start_index_in_file += 1
                section._end_index_in_file += 1

    def _insert_new_section_line(self, section):
        section_name = section.get_name()
        self._lines_raw.append("\n")
        self._lines_cleaned.append("")
        self._lines_raw.append(f"[{section_name}]\n")
        self._lines_cleaned.append(f"[{section_name}]")

        section._start_index_in_file = len(self._lines_raw) - 1
        section._end_index_in_file = section._start_index_in_file + 1
