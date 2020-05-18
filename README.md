# settings-manager

A package to manage settings files.

## Installation

```
pip install git+https://github.com/rgossington/settings-manager.git
```

## Usage

#### Import

```
from settingsmanager import SettingsManager
```

#### Creating a SettingsManager instance

```
settings = SettingsManager("settings.txt")
```
Reads the contents of 'settings.txt' into the settings instance.
Will create 'settings.txt' in the working directory if it does not already exist.

#### Adding sections

```
settings.add_section("general")
```

#### Adding keys

```
settings.add_entry("new_key", "new value", "general")
```
or
```
settings.add_entry("new_key", "new value", settings.general)
```
or
```
settings.general.add_entry("new_key", "new value")
```

#### Editing keys

```
settings.general.new_key = "edited value"
```
or
```
settings.general.set_value("new_key", "edited_value")
```
or
```
settings.set_value("new_key", "edited_value", "general")
```

#### Accessing values

```
settings.general.new_key
```
Will return the value of 'new_key'.

#### Gettings all sections

The following method returns a list of Section instances from the SettingsManager instance:
```
settings.get_sections()
```

#### Saving

```
settings.save()
```

#### Refreshing from file

The settings can be reloaded from the file by using:

```
settings.refresh()
```

The following method will return True if the file has changed since the last refresh:

```
settings.refresh_and_has_changed()
```

## Parsing

By default, all booleans, integers and floats will be parsed. These can be disabled individually when creating the SettingsManager instance:
```
settings = SettingsManager(file_path, parse_bool=False, parse_int=False, parse_float=False)
```

## Planned work

- Prevention of adding multiple sections with the same same
- Section and key removal methods
