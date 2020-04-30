from re import match


class SettingsManager:
    def __init__(self, file_dir):
        self.file = open(file_dir)
        lines_raw = self.file.readlines()
        self.file.close()
        self.length = len(lines_raw)
        self.lines = [item.rstrip().replace("= ", "=").replace(" =", "=") for item in lines_raw]  # remove line breaks

    def read_entry(self, heading, entry, parse_bool=False, parse_int=False, default=None):
        # reads an entry from the config file

        ###
        if not self.heading_exists(heading):
            if default is not None:
                return default
            else:
                print(f"[{heading}] not found in the settings file")
                raise Exception(f"[{heading}] not found in the settings file")

        ###
        in_heading = False
        output = None

        for line in self.lines:
            if not in_heading:
                # look for our heading if not already there
                if line == "[" + heading + "]":
                    in_heading = True
                    continue
            else:
                # if we are in our heading already
                if match("\[.*\]", line):
                    # if we get to the end of our heading, the entry has not been found
                    if default is not None:
                        return default
                    else:
                        print(f"{entry} not found in the settings file")
                        raise Exception(f"{entry} not found in the settings file")

                # if we find our entry
                if line.startswith(entry + "="):
                    output = line[len(entry) + 1:]
                    break

        if parse_bool:
            out_l = output.lower()

            true_list = ["true", "t", "yes", "y"]
            false_list = ["false", "f", "no", "n"]

            if out_l in true_list:
                output = True

            if out_l in false_list:
                output = False

        if parse_int:
            try:
                output = int(output)
            except ValueError:
                print(f"Invalid value for {entry}")
                exit()

        # if heading wasn't found return None
        return output

    def heading_exists(self, heading):
        heading_line = f"[{heading}]"
        return heading_line in self.lines
