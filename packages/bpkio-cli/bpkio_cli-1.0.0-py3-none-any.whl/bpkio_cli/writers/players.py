import click
from InquirerPy import inquirer

from bpkio_cli.utils.config_provider import ConfigProvider


class StreamPlayer:
    def __init__(self):
        self.config_provider = ConfigProvider()
        self._player_templates = None

    @property
    def player_templates(self) -> dict[str, str]:
        if self._player_templates is None:
            self._player_templates = self.config_provider.list_players()
        return self._player_templates

    def launch(self, url: str, template: str = None, **kwargs):
        if template is None:
            full_url = url
        else:
            try:
                full_url = self.player_templates[template].format(url=url, **kwargs)
            except KeyError as e:
                key = str(e).strip("'")
                if ":" in key:
                    key, default = key.split(":", 1)
                    kwargs[key] = default
                    full_url = self.player_templates[template].format(url=url, **kwargs)
                else:
                    raise ValueError(
                        f"No value provided for the placeholder '{key}' in the template string."
                    )

        click.launch(full_url)

    def available_player_templates(self):
        return self.config_provider.list_players().keys()

    @staticmethod
    def prompt_player():
        player = inquirer.select(
            message="What (top-level) resources do you want to include in the package?  ",
            choices=[p for p in StreamPlayer().available_player_templates()],
        ).execute()
        return player
