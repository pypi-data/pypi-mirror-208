from __future__ import annotations
__package__ = "ipfskvs"

import json
import logging
from typing import Dict, Self
from uuid import UUID


LOG = logging.getLogger(__name__)


class Index():
    """An object for storing a nested directory structure.

    Use the `Store` class to read or write the data for an Index.

    ### Convert a filename to an Index object
    ```py
        from ipfskvs.index import Index

        index = Index.from_filename("mydir/show_1/season_2/episode_6.mp4")
    ```

    ### Convert an Index object to a filename
    ```py
        filename = index.get_filename()
    ```
    """
    prefix: str
    index: Dict[str, UUID]
    size: int  # number of keys in this index (not including parent or subindex)  # noqa: E501
    subindex: Index

    def __init__(
            self: Self,
            index: Dict[str, UUID],
            subindex: Index = None,
            prefix: str = None,
            size: int = None) -> None:
        """Index Constructor.

        Index keys should be all one word lower case.
        Index values should be UUIDs.
        """
        self.prefix = prefix
        self.index = index
        self.subindex = subindex
        self.size = size if size else len(index.keys())

    def __str__(self: Self) -> str:
        """Convert an Index to a string with `str()`.

        This will recursively parse the subindexes and
        include them all in the response.

        Returns:
            str: The index object as a string
        """
        return json.dumps(self.to_dict(), sort_keys=True, indent=4)

    def __eq__(self: Self, other_index: Index) -> bool:
        """Compare two Index objects with `==`.

        Args:
            other_index (Index): The other index to compare

        Returns:
            bool: Returns true if self == other_index
        """
        result = \
            self.prefix == other_index.prefix and \
            self.size == other_index.size and \
            self.subindex == other_index.subindex and \
            self.index == other_index.index
        return result

    def to_dict(self: Self) -> dict:
        """Convert the Index object to a dictionary.

        This will recursively parse the subindexes and
        include them all in the response.

        Returns:
            dict: The index object as a dict
        """
        return {
            "prefix": self.prefix,
            "index": self.index,
            "subindex": self.subindex.to_dict() if self.subindex else None
        }

    def matches(self: Self, other_index: Index) -> bool:
        """Check if this index has a compatible index with another index.

        Args:
            other_index (Index): The other index object to compare against

        Returns:
            bool: Returns false if any self keys are not in the other index
                or if any values in self are not equal to the
                corresponding value in the other index
        """
        for key in self.index:
            if key not in other_index.index:
                LOG.debug(f"{self} != {other_index} due to a missing key")
                return False

            if str(self.index[key]) != str(other_index.index[key]):
                LOG.debug(f"{self} != {other_index} due to a value mismatch")
                return False

        return True

    def is_partial(self: Self) -> bool:
        """Check if the index has less keys than expected.

        Returns:
            bool: Returns true if some keys are missing
        """
        return self.size != len(self.index.keys())

    def get_metadata(self: Self) -> Dict[str, UUID]:
        """Parse the subindex/filename data.

        This will recursively parse the subindexes and
        include them all in the response.

        Returns:
            Dict[str, UUID]: A flat map of (key: value)
        """
        filename = self.get_filename()  # recursively get subindex data
        records = filename.split("/")
        if self.prefix:
            records.pop(0)

        result = {}
        for index_level in records:
            for index in index_level.split("."):
                result[index.split("_")[0]] = index.split("_")[1]

        return result

    def get_filename(self: Self) -> str:
        """Convert this object to a filename.

        Returns:
            str: The filename for this Index
        """
        result = ""

        # Add prefix
        if self.prefix:
            result += self.prefix + "/"

        # If not all index keys are known, don't add it to the filename
        if self.is_partial():
            LOG.debug(f"Skipping this index because it is partial: {self}")
            return result

        # Add current index
        cur_index = ".".join([
            f'{key}_{value}' for key, value in self.index.items()
        ])
        result += cur_index

        # Recursively add subindexes
        if self.subindex:
            result += "/" + self.subindex.get_filename()

        return result

    @staticmethod
    def from_filename(filename: str, has_prefix: bool = False) -> Index:
        """Convert a filename to an Index object.

        Args:
            filename (str): The filename to verify
            has_prefix (bool, optional): Does the filename have a prefix?
                Defaults to False.

        Raises:
            Exception: If the filename is unable to be parsed
                an exception will be raised

        Returns:
            Index: The index object with data corresponding to
                the input filename
        """
        directories = [file for file in filename.split("/") if file]

        # Get prefix
        prefix = directories.pop(0) if has_prefix else None

        # Get index
        try:
            index = {
                record.split("_")[0]: record.split("_")[1]
                for record in directories.pop(0).split(".")
            }
        except IndexError as e:
            raise Exception(f"Could not parse filename `{filename}` with prefix `{prefix}`") from e  # noqa: E501
        except KeyError as e:
            raise Exception(f"Could not parse filename `{filename}` with prefix `{prefix}`") from e  # noqa: E501

        # Recursively get the subindexes
        subindex = Index.from_filename("/".join(directories)) if len(directories) > 0 else None  # noqa: E501

        return Index(index, subindex, prefix)
