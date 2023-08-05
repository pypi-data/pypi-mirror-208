import json
import logging
import uuid
from typing import Dict, List

import bpkio_api.mappings as mappings
import bpkio_api.models as models
from bpkio_api.models.common import summary
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ResourcePackager:
    def __init__(self, api) -> None:
        self.api = api
        self.resources: List[models.BaseResource] = []
        self.id_mappings: Dict = {}
        self.in_resources: List = []

    def extract(self):
        pass

    # def discoverOLD(self, resource: BaseModel):
    #     # Keep a tally of all the resources (with identifiers)
    #     if isinstance(resource, models.BaseResource):
    #         self.resources.append(resource)

    #     if isinstance(resource, BaseModel):
    #         # then go through pydantic object and find dependents
    #         for key, field in resource.__fields__.items():
    #             val = getattr(resource, key)
    #             if val:
    #                 if issubclass(field.type_, models.BaseResource):
    #                     endpoint = mappings.model_to_endpoint(
    #                         self.api, model=field.type_
    #                     )
    #                     if endpoint and hasattr(endpoint, "retrieve"):
    #                         dependent = endpoint.retrieve(val.id)
    #                         print(f"Found dependent: {dependent}")
    #                         self.discover(dependent)
    #                     else:
    #                         print(
    #                             f"No retrieve endpoint for resource of type {field.type_}"
    #                         )

    #                 elif issubclass(field.type_, BaseModel):
    #                     self.discover(val)
    #                 elif isinstance(val, list):
    #                     for v in val:
    #                         self.discover(v)

    def package(self, root_resources: List[BaseModel]):
        for resource in root_resources:
            self._discover(resource)

        return self._prepare()

    def _discover(self, model):
        """Function to traverse a resource and retrieve all its dependents,
        in a recursive way.

        Args:
            model (BaseResource): The root resource (or model) to start from
        """
        # Keep a tally of all the resources (with identifiers)
        if isinstance(model, models.BaseResource):
            self.resources.append(model)

        if isinstance(model, BaseModel):
            # then go through pydantic object and find dependents
            for field_name, field_value in model:
                if field_value:
                    if isinstance(field_value, models.BaseResource):
                        endpoint = mappings.model_to_endpoint(
                            self.api, model=type(field_value)
                        )
                        if endpoint and hasattr(endpoint, "retrieve"):
                            dependent = endpoint.retrieve(field_value.id)
                            logger.info(
                                f"Found dependent: {summary(dependent, with_class=True)}"
                            )
                            self._discover(dependent)
                        else:
                            logger.error(
                                f"No retrieve endpoint for resource of type {field_value.__class__.__name__}"
                            )

                    elif isinstance(field_value, BaseModel):
                        self._discover(field_value)

                    elif isinstance(field_value, list):
                        for v in field_value:
                            self._discover(v)

    def _prepare(self):
        """Goes through the list of resources extracted by self._discover,
        find and generalises all relations, and prepares a JSON package
        that can be deployed.
        """

        def replace_guid_with_id(model):
            if isinstance(model, BaseModel):
                for field_name, field_value in model:
                    if field_name == "id" and field_value in self.id_mappings:
                        setattr(model, field_name, self.id_mappings[field_value])
                    else:
                        replace_guid_with_id(field_value)
            elif isinstance(model, list):
                for item in model:
                    replace_guid_with_id(item)

        for resource in reversed(self.resources):
            # Extract original ID
            orig_id = resource.id

            # Create a GUID to replace it with
            guid = str(uuid.uuid4())
            self.id_mappings[orig_id] = guid

            # Transform the resource into an IN model
            in_model: BaseModel = mappings.model_to_model_in(type(resource))
            in_obj = in_model.parse_obj(resource.dict())

            # Replace dependent IDs in it
            replace_guid_with_id(in_obj)

            # Make a JSON payload from it
            json_payload = json.loads(in_obj.json())

            # Record it
            self.in_resources.append(
                dict(guid=guid, model=in_model.__name__, payload=json_payload)
            )

        return self.in_resources


class PackageInstaller:
    statuses = {1: "created", 0: "existing", -1: "error"}

    def __init__(self, api, name_suffix: str | None = None) -> None:
        self.guid_mappings: Dict = {}
        self.resources: Dict = {}
        self.api = api
        self._suffix = name_suffix

    def deploy(self, package: list):
        def replace_guid_with_id(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "id" and value in self.guid_mappings:
                        obj[key] = self.guid_mappings[value]
                    else:
                        replace_guid_with_id(value)
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    replace_guid_with_id(value)

        for instruction in package:
            payload = instruction["payload"]

            # Replace the GUIDs with IDs (if any)
            replace_guid_with_id(payload)

            # Parse it into the pydantic model
            model: BaseModel = getattr(models, instruction["model"])
            in_obj = model.parse_obj(payload)

            # Ensure name unicity (for models that can be duplicated)
            if self._suffix and isinstance(in_obj, (models.ServiceIn)):
                in_obj.name = in_obj.name + " " + self._suffix

            # Create it
            try:
                message = ""
                endpoint = mappings.model_to_endpoint(self.api, model=model)

                # Special handling for objects that require admin access. We just check whether they exist (by name)
                if instruction["model"] in ("TranscodingProfileIn"):
                    resource_name = instruction["payload"]["name"]
                    existing_resources = endpoint.search(
                        value=resource_name, field="name"
                    )
                    if not len(existing_resources):
                        raise Exception(
                            f"The {instruction['model']} with name '{resource_name}' must "
                            "already exist and cannot be automatically created by this script"
                        )
                    else:
                        resource = existing_resources[0]
                        status = 0
                else:
                    if hasattr(endpoint, "upsert"):
                        (resource, status) = endpoint.upsert(
                            in_obj, if_exists="retrieve"
                        )
                    elif hasattr(endpoint, "create"):
                        resource = endpoint.create(in_obj)
                        status = 1
                    else:
                        raise Exception(f"No create endpoint for model {model}")
            except Exception as e:
                resource = in_obj
                status = -1
                message = e.args[0]

            logger.info(
                f"{self.statuses[status]}: {resource.__class__.__name__} {resource.name} {resource.id} ({message})"
            )

            # Record the new ID, and map it to the guid
            if hasattr(resource, "id"):
                self.guid_mappings[instruction["guid"]] = resource.id
                self.resources[resource.id] = (resource, status, message)
            else:
                self.resources[resource.name] = (resource, status, message)

        return self.resources
