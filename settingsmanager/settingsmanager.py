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

            setattr(self, key, value)

    def get_name(self):
        return self._name


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
        if section is None:
            raise ValueError(f"Entry {key} does not have a section")

        if not isinstance(section, Section):
            raise ValueError("A valid section instance was not provided. "
                                 "Create a section first using create_section")

        if not hasattr(self, section._name):
            raise AttributeError(f"{section._name} was not found in the settings instance")

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

        sections = self.get_sections()

        # Iterate through each section
        for section in sections:
            section_index = section._start_index_in_file

            # If it is missing, add to the raw file lines
            if section_index is None:
                section._start_index_in_file = len(self._lines_raw)
                section._end_index_in_file = section._start_index_in_file + 1
                self._lines_raw.append(f"[{section._name}")

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

    def get_section(self, section_name):
        sections = self.get_sections()

        for section in sections:
            if section.get_name() == section_name:
                return section

        return None

    def set_value(self, section, key, value):
        if isinstance(section, str):
            section = self.get_section(section)

        # todo: handle if key or section does not exist
        setattr(section, key, value)

    def has_changed(self):
        lines_before = self._lines_cleaned
        self.refresh()
        return lines_before != self._lines_cleaned

    def _read_file(self):
        try:
            with open(self._file_path, "r") as file:
                self._lines_raw = file.readlines()
                self._clean_file_lines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Settings file not found in {self._file_path}")

    def _clean_file_lines(self):
        lines_cleaned = []

        for line in self._lines_raw:
            line_cleaned = line.rstrip()
            line_cleaned = line_cleaned.replace("= ", "=")
            line_cleaned = line_cleaned.replace(" =", "=")
            lines_cleaned.append(line_cleaned)

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
        index = section._end_index_in_file + 1
        self._lines_raw.insert(index, value)
        section._end_index_in_file += 1

        # Shift later sections
        sections = self.get_sections()

        for section in sections:
            if section._start_index_in_file >= index:
                section._start_index_in_file += 1
                section._end_index_in_file += 1
