import click
import cloup

from bpkio_cli.core.app_settings import AppContext


@cloup.group(aliases=["mem"], help="App resource registry comands")
@click.pass_obj
def memory(obj: AppContext):
    pass


@memory.command(help="Clear the app resource register")
@click.pass_obj
def clear(obj: AppContext):
    obj.cache.clear()


@memory.command(help="Check what is stored in the app's resource register")
@click.pass_obj
def read(obj: AppContext):
    click.secho("Last resources accessed", fg="yellow")
    for v in obj.cache.list_resources():
        click.secho(" · " + v.__class__.__name__ + " ", fg="green", nl=False)
        click.secho(v.summary if hasattr(v, "summary") else v)

    click.secho("Last lists retrieved", fg="yellow")
    for k, lst in obj.cache.list_lists().items():
        try:
            list_ids = [item.id for item in lst]
            click.secho(" · " + k + " ", fg="green", nl=False)
            click.secho(list_ids)
        except:
            pass
