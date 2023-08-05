import configparser
import os
from typing import Any, Dict, List


class ConfigProvider:
    def __init__(self, config_path="~/.bpkio/cli.cfg"):
        self.config_path = os.path.expanduser(config_path)
        self.config = configparser.ConfigParser()
        self.initialize()

    def initialize(self):
        default_values = {
            "settings": {"player": "browser"},
            "players": {
                "browser": "{url}",
                "demo": "https://theoplayer.ridgeline.fr/?url1={url}&title1={name}&autoplay=true",
                "hls": "https://hlsjs.video-dev.org/demo/?src={url}",
                "dash": "https://reference.dashif.org/dash.js/nightly/samples/dash-if-reference-player/index.html?mpd={url}",
            },
        }

        if not os.path.exists(self.config_path):
            self.config.read_dict(default_values)
            self.save_config()
        else:
            self.config.read(self.config_path)

            for section, values in default_values.items():
                if section not in self.config:
                    self.config.add_section(section)

                for key, value in values.items():
                    if key not in self.config[section]:
                        self._set(key, value, section)

    def get(self, key, cast_type=None, section="settings"):
        value = self.config.get(section, key)
        return self.cast_value(value, cast_type)

    def cast_value(self, value, cast_type):
        if cast_type is None:
            return value
        elif cast_type == bool:
            return value.lower() in {"true", "1"}
        elif cast_type.__class__.__name__ == "Type":
            return cast_type(value)
        elif cast_type.__origin__ == List:
            item_type = cast_type.__args__[0]
            return [item_type(item.strip()) for item in value.split(",")]
        else:
            raise ValueError(f"Unsupported cast_type: {cast_type}")

    def get_section_items(self, section: str) -> Dict[str, Any]:
        if section not in self.config.sections():
            raise ValueError(
                f"The [{section}] section is missing in the configuration file."
            )

        return {key: value for key, value in self.config.items(section)}

    def _set(self, key, value, section="settings"):
        self.config.set(section, key, value)
        self.save_config()

    def set_config(self, key, value):
        match key:
            case "player":
                self.set_player(value)
            case _:
                if key not in self.config["settings"]:
                    raise ValueError(f"There is no setting called '{key}'.")

                self._set(key, value)

    def save_config(self):
        with open(self.config_path, "w") as config_file:
            self.config.write(config_file)

    # --- Specific config parameters ---

    def set_player(self, value):
        if value in self.config["players"]:
            self._set("player", value)
        else:
            raise ValueError("The specified player is not in the [players] section.")

    def add_player(self, label, player_string):
        self.config.set("players", label, player_string)
        self.save_config()

    def list_players(self) -> Dict[str, Any]:
        return self.get_section_items("players")
