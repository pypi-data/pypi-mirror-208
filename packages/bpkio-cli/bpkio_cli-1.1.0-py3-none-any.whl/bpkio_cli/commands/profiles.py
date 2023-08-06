import json as j

import click
import cloup
from bpkio_api.models import TranscodingProfile, TranscodingProfileIn
from InquirerPy import inquirer

import bpkio_cli.options as bic_options
from bpkio_cli.click_mods import ApiResourceGroup
from bpkio_cli.core.app_settings import AppContext
from bpkio_cli.utils.arrays import order_by_dict_keys
from bpkio_cli.utils.config_provider import ConfigProvider
from bpkio_cli.utils.json import is_json
from bpkio_cli.writers.breadcrumbs import display_resource_info
from bpkio_cli.writers.tables import display_table

default_fields = ["id", "name", "num_layers"]


# # --- TRANSCODING PROFILES Group
@cloup.group(
    cls=ApiResourceGroup,
    aliases=["prf", "profiles", "transcoding-profile"],
    show_subcommand_aliases=True,
    resource_class=TranscodingProfile,
)
@cloup.argument(
    "profile_id",
    help=(
        "The identifier of the transcoding profile to work with. "
        "Leave empty for commands operating on a list of profiles."
    ),
)
@click.pass_obj
def profile(obj, profile_id: str):
    """Manage Transcoding Profiles"""

    if profile_id:
        # TODO - find a way of passing the target tenant (admin mode)
        profile = obj.api.transcoding_profiles.retrieve(profile_id)
        display_resource_info(profile)


# --- LIST Command
@cloup.command(help="Retrieve a list of all Transcoding Profiles", aliases=["ls"])
@bic_options.json
@bic_options.list(default_fields=default_fields)
@bic_options.tenant
@click.pass_obj
def list(obj, json, select_fields, sort_fields, tenant):
    profiles = obj.api.transcoding_profiles.list(tenantId=tenant)

    obj.response_handler.treat_list_resources(
        profiles,
        select_fields=select_fields,
        sort_fields=sort_fields,
        json=json,
    )


# --- GET Command
@cloup.command(
    aliases=["retrieve"],
    help="Retrieve info about a single Transcoding Profile, by its ID",
)
@click.option(
    "--table/--no-table",
    "with_table",
    is_flag=True,
    default=True,
    help="Add or hide summary information about the content of the resource",
)
@bic_options.tenant
@bic_options.json
@click.pass_context
def get(ctx, tenant, json, with_table):
    id = ctx.obj.resources.last()
    profile = ctx.obj.api.transcoding_profiles.retrieve(id, tenantId=tenant)

    ctx.obj.response_handler.treat_single_resource(profile, json=json)

    if with_table and not json:
        ctx.invoke(table, header=False)


# --- TABLE Command
@cloup.command(help="Provide summary table of the content of the profile")
@bic_options.tenant
@click.pass_obj
def table(
    obj: AppContext,
    tenant,
    **kwargs,
):
    id = obj.resources.last()
    profile = obj.api.transcoding_profiles.retrieve(id, tenantId=tenant)
    common = {
        k: click.style(v, dim=True)
        for k, v in profile.json_content["transcoding"]["common"].items()
    }
    jobs = [dict(common, **job) for job in profile.json_content["transcoding"]["jobs"]]
    jobs = order_by_dict_keys(jobs)

    display_table(jobs)


# --- JSON Command
@cloup.command(
    help="Get the JSON representation of a single Transcoding Profile "
    "or list of Transcoding Profiles"
)
@click.option(
    "-e",
    "--expand",
    is_flag=True,
    default=False,
    help="Extract the actual profile's JSON and pretty print it",
)
@bic_options.tenant
@click.pass_obj
def json(obj: AppContext, tenant, expand):
    try:
        id = obj.resources.last()
        profile = obj.api.transcoding_profiles.retrieve(id, tenantId=tenant)

        if expand:
            profile = profile.json_content

        obj.response_handler.treat_single_resource(profile, json=True)

    except Exception:
        profiles = obj.api.transcoding_profiles.list(tenantId=tenant)
        if expand:
            # TODO - Dirty code. Needs resolving, maybe at level of the SDK
            bare_profiles = []
            for profile in profiles:
                new_pro = j.loads(profile.json())
                new_pro["_expanded_content"] = profile.json_content
                bare_profiles.append(new_pro)
            profiles = bare_profiles

        obj.response_handler.treat_list_resources(
            profiles,
            json=True,
        )


# --- SEARCH Command
@cloup.command(
    help="Retrieve a list of all Transcoding Profiles that match given "
    "terms in all or selected fields"
)
@bic_options.search
@bic_options.json
@bic_options.list(default_fields=default_fields)
@bic_options.tenant
@click.pass_obj
def search(
    obj,
    tenant,
    single_term,
    search_terms,
    search_fields,
    json,
    select_fields,
    sort_fields,
):
    search_def = bic_options.validate_search(single_term, search_terms, search_fields)

    profiles = obj.api.transcoding_profiles.search(filters=search_def, tenantId=tenant)

    obj.response_handler.treat_list_resources(
        profiles,
        select_fields=select_fields,
        sort_fields=sort_fields,
        json=json,
    )


# --- CREATE Command
@cloup.command(help="[ADMIN] Create a Transcoding Profile")
@bic_options.tenant
@cloup.option("--from", "from_file", type=click.File("r"), required=False, default=None)
@cloup.option("--name", type=str, required=False, default=None)
@click.pass_obj
def create(obj: AppContext, tenant: int, from_file, name: str):
    if from_file:
        content = from_file.read()
    else:
        content = inquirer.text(
            message="Content of the profile: ",
            multiline=True,
            validate=lambda txt: is_json(txt),
            invalid_message="This is not a valid JSON payload",
        ).execute()

    if not name:
        name = inquirer.text(message="Name: ").execute()

    tpro = TranscodingProfileIn(content=content, name=name, tenantId=None)
    if tenant:
        tpro.tenantId = tenant

    out_profile = obj.api.transcoding_profiles.create(profile=tpro)
    obj.response_handler.treat_single_resource(out_profile)


# --- UPDATE Command
@cloup.command(aliases=["put"], help="Update a Transcoding Profile")
@bic_options.tenant
@click.pass_obj
def update(obj: AppContext, tenant: int):
    id = obj.resources.last()
    profile = obj.api.transcoding_profiles.retrieve(id, tenantId=tenant)
    profile.tenantId = tenant
    payload = j.dumps(j.loads(profile.json()), indent=2)

    updated_resource_json = click.edit(payload, editor=ConfigProvider().get("editor"))

    obj.api.transcoding_profiles.update(id, j.loads(updated_resource_json))

    click.secho(f"Resource {id} updated", fg="green")


# --- DELETE Command
@cloup.command(help="[ADMIN] Delete a Transcoding Profile, by its ID")
@click.pass_obj
def delete(obj: AppContext):
    id = obj.resources.last()
    obj.api.transcoding_profiles.delete(id)


profile.add_section(
    cloup.Section(
        "CRUD commands", [list, get, table, json, search, create, update, delete]
    )
)
