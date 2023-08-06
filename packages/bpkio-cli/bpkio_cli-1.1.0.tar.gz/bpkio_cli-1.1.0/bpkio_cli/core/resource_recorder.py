import os
import pickle
import re
import tempfile
from typing import List

from bpkio_cli.core.exceptions import BroadpeakIoCliError
from bpkio_cli.core.logger import get_child_logger

logger = get_child_logger(__name__)


class ResourceRecorder:
    def __init__(self, fqdn: str, tenant: str | int):
        temp_dir = tempfile.gettempdir()
        cache_dir = os.path.join(temp_dir, "bpkio_cli", fqdn, str(tenant))
        logger.debug("Cache folder: " + cache_dir)

        self._resources_file = os.path.join(cache_dir, "resources.pkl")
        self._lists_file = os.path.join(cache_dir, "lists.pkl")

        self._cache_singles: MoveToFrontList = self._read_file_or_new(
            self._resources_file, MoveToFrontList(50)
        )
        self._cache_lists: dict = self._read_file_or_new(self._lists_file, dict())

    def _read_file_or_new(self, file_path: str, default):
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                try:
                    content = pickle.load(file)
                    if isinstance(content, default.__class__):
                        return content
                except (
                    pickle.UnpicklingError,
                    EOFError,
                    AttributeError,
                    ModuleNotFoundError,
                ):
                    logger.warning(
                        "Issue encountered with loading the cache. No cache will be used"
                    )
                    pass

        return default

    def clear(self):
        self._cache_singles = MoveToFrontList(maxlen=50)
        self._cache_lists = dict()
        self.save()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self._resources_file), exist_ok=True)
            with open(
                self._resources_file,
                "wb",
            ) as file:
                pickle.dump(self._cache_singles, file)
        except IOError as e:
            logger.warn("Unable to write Resources file to cache")

        try:
            with open(self._lists_file, "wb") as file:
                pickle.dump(self._cache_lists, file)
        except IOError:
            logger.warn("Unable to write Lists file to cache")

    def record(self, value):
        if isinstance(value, List) and len(value) > 0:
            self._cache_lists[value[0].__class__.__name__] = value
        else:
            self._cache_singles.add(value)

    def resolve(self, value, target_type):
        """Resolve non-integer references from data in the cache"""
        if value == "$":
            last_id = self.last_id_by_type(target_type)
            if last_id:
                return str(last_id)
            else:
                raise ValueError(
                    "There is no resource in memory that can be found to "
                    "replace '$' for this context"
                )

        if value.startswith("@"):
            match = re.search(r"(-?\d+)", value)
            if match:
                pos = int(match.group(1))
                id = self.id_by_position_in_last_list_by_type(target_type, pos)
                if id:
                    return str(id)
                else:
                    raise ValueError(
                        f"There is no resource in position {pos} "
                        f"in the last list of {target_type.__name__}"
                    )

        return value

    def last_id(self):
        return getattr(self._cache_singles[0], "id", self._cache_singles[0])

    def last_id_by_type(self, type: type):
        candidates = [v for v in self._cache_singles.values() if isinstance(v, type)]
        if len(candidates):
            return getattr(candidates[0], "id", candidates[0])

    def id_by_position_in_last_list_by_type(self, type_: type, position: int):
        if type_.__name__ in self._cache_lists:
            # Try strict type first:
            list = self._cache_lists[type_.__name__]
        else:
            try:
                # Otherwise, find first list that contains super-types
                list = next(
                    l for l in self._cache_lists.values() if isinstance(l[0], type_)
                )
            except StopIteration:
                raise RecorderCacheError(
                    f"There is no list of resources of type {type_.__name__} in cache."
                )

        try:
            return list[position].id
        except IndexError:
            raise RecorderCacheError(
                f"The list of resources of type {type_.__name__} currently "
                f"in cache only contains {len(list)} resources"
            )

    def list_resources(self):
        return self._cache_singles.values()

    def list_lists(self):
        return self._cache_lists


class MoveToFrontList:
    def __init__(self, maxlen: int = None):
        self._list = []
        self._maxlen = maxlen

    def add(self, item):
        if item in self._list:
            self._list.remove(item)
        self._list.insert(0, item)

        if self._maxlen is not None and len(self._list) > self._maxlen:
            self._list.pop()

    def search(self, item):
        if item in self._list:
            self._list.remove(item)
            self._list.insert(0, item)
            return True
        return False

    def values(self):
        return self._list

    def __str__(self):
        return str(self._list)

    def __getitem__(self, key):
        return self._list[key]

    def __setitem__(self, key, value):
        self._list[key] = value

    def __delitem__(self, key):
        del self._list[key]


class RecorderCacheError(BroadpeakIoCliError):
    def __init__(self, message):
        super().__init__(message)
