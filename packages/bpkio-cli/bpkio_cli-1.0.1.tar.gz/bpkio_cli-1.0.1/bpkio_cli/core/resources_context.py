from typing import Dict, Optional


class ResourcesContext:
    def __init__(self) -> None:
        self._resource_breadcrumbs: Dict[str, int] = dict()

    # TODO - this needs to be moved to a separate object,
    # directly linked to the RestResourceGroup
    def record_resource_id(self, key, value):
        """Records a REST resource id, against a key (usually the name
        of the resource type)"""
        self._resource_breadcrumbs[key] = value

    def extract_resource_id(self, key: Optional[str] = None, *, pos: int = -1):
        """Returns resource identifier by the name of the command,
        or the deepest one recorded

        Args:
            key (str, optional): The name of the key identifying the resource type.
                Defaults to None.
            pos (int, optional): The position of the resource in the breadcrumbs.
                Supports negative numbers for position from the back,
                eg. -1 for the last resource in the hierarchy.
                Ignored if `key` is provided
                Defaults to -1.

        Returns:
            int | str: The identifier, cast as `int` if possible

        Raises:
            UnknownResourceError: Any error, such as there being
            no corresponding resource to the request
        """

        val: int | None
        if key:
            if key in self._resource_breadcrumbs:
                val = self._resource_breadcrumbs.get(key)
            else:
                raise UnknownResourceError(
                    f"No resource of type '{key}' has been recorded"
                )
        else:
            values = list(self._resource_breadcrumbs.values())
            if values:
                val = values[pos]
            else:
                raise UnknownResourceError("No resources have been recorded")

        try:
            return int(val)  # type: ignore
        except Exception:
            return val

    def last(self) -> int | None:
        return self.extract_resource_id(pos=-1)

    def parent(self) -> int | None:
        return self.extract_resource_id(pos=-2)


class UnknownResourceError(ValueError):
    def __init__(self, message):
        super().__init__(message)
