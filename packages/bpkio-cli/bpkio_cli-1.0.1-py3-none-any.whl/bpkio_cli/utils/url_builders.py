from typing import List, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import click
import InquirerPy.inquirer as inquirer
from bpkio_api.helpers.handlers import ContentHandler, factory
from bpkio_api.models import (
    AdInsertionService,
    AdServerSourceIn,
    AssetCatalogSourceIn,
    BaseResource,
    SourceIn,
    SourceType,
)

from bpkio_cli.utils.urls import add_query_parameters


def get_source_handler(
    source: SourceIn, extra_url: Optional[str], subplaylist_index: Optional[int]
) -> ContentHandler:
    if isinstance(source, AssetCatalogSourceIn):
        # Ask for extra portion of URL if it wasn't supplied
        if not extra_url:
            extra_url = source.assetSample

            extra_url = inquirer.text(message="Sub-path", default=extra_url).execute()

    url_to_read = source.make_full_url(extra_url)

    if isinstance(source, AdServerSourceIn):
        # Fill query parameters
        if not extra_url or "?" not in url_to_read:
            filled_params = dict()
            params = source.queries
            if params:
                params = params.split("&")
                for p in params:
                    (k, val) = p.split("=")
                    if val.startswith("$arg_"):
                        input_param = val.replace("$arg_", "")
                        input_val = inquirer.text(
                            message=f"Parameter '{input_param}'"
                        ).execute()
                        filled_params[input_param] = input_val
            url_to_read = add_query_parameters(url_to_read, filled_params)

    handler: ContentHandler = factory.create_handler(url_to_read)
    if subplaylist_index:
        if not handler.has_children():
            raise click.UsageError(
                "`--sub` cannot be used with this source, as it has no children URLs"
            )
        handler = handler.get_child(subplaylist_index)

    return handler


def get_service_handler(
    service,
    api,
    replacement_fqdn: Optional[str],
    extra_url: Optional[str],
    subplaylist_index: Optional[int],
) -> ContentHandler:
    """Calculates the URL to call for a Service, based on its type and Source"""
    url_to_read = service.make_full_url()

    if isinstance(service, AdInsertionService):
        source_type = service.source.type
        source_id = service.source.id

        if source_type == SourceType.ASSET_CATALOG:
            # Ask for extra portion of URL if it wasn't supplied
            if not extra_url:
                source = api.sources.asset_catalog.retrieve(source_id)
                extra_url = source.assetSample

                extra_url = inquirer.text(
                    message="Sub-path", default=extra_url
                ).execute()

            url_to_read = urljoin(service.url, extra_url)

        # In case it's an ad insertion service, and the ad server has query params,
        # prompt for values for the ones expected to be passed through
        ad_config = get_first_matching_key_value(
            service, ["vodAdInsertion", "liveAdPreRoll", "liveAdReplacement"]
        )
        if ad_config and ad_config.adServer:
            if not extra_url or "?" not in extra_url:
                filled_params = dict()
                params = ad_config.adServer.queries
                if params:
                    params = params.split("&")
                    for p in params:
                        (k, val) = p.split("=")
                        if val.startswith("$arg_"):
                            input_param = val.replace("$arg_", "")
                            input_val = inquirer.text(
                                message=f"Parameter '{input_param}'"
                            ).execute()
                            filled_params[input_param] = input_val

                url_to_read = add_query_parameters(url_to_read, filled_params)

    # replace the fqdn if necessary
    if replacement_fqdn:
        parsed_url = urlparse(url_to_read)
        url_to_read = urlunparse(parsed_url._replace(netloc=replacement_fqdn))

    handler: ContentHandler = factory.create_handler(url_to_read, from_url_only=True)
    if subplaylist_index:
        if not handler.has_children():
            raise click.UsageError(
                "`--sub` cannot be used with this source, as it has no children URLs"
            )
        handler = handler.get_child(subplaylist_index)

    return handler


def get_first_matching_key_value(resource: BaseResource, possible_keys: List[str]):
    for key in possible_keys:
        if getattr(resource, key):
            return getattr(resource, key)
    return None
