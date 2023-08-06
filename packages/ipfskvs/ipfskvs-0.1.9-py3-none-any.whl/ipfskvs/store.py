from __future__ import annotations
__package__ = "ipfskvs"

import errno
import logging
import os
from dataclasses import dataclass
from types import FunctionType
from typing import Dict, Iterator, List, Self

from google.protobuf.message import Message

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index

import pandas as pd

LOG = logging.getLogger(__name__)


@dataclass
class Store():
    """A utility to read/write protobuf data to ipfs.

    Reading:
    ```py
        from ipfskvs.index import Index
        from ipfskvs.ipfs import Ipfs
        from ipfskvs.store import Store
        from myprotobuf_pb2 import MyProtobuf

        store = Store(
            Index.from_filename("myfile.txt"),
            ipfs=Ipfs(host="127.0.0.1", port="5001"),
            reader=MyProtobuf()
        )
        store.read()
        print(store.reader)
    ```

    Writing:
    ```py
        from ipfskvs.index import Index
        from ipfskvs.ipfs import Ipfs
        from ipfskvs.store import Store
        from myprotobuf_pb2 import MyProtobuf

        store = Store(
            Index.from_filename("myfile.txt"),
            ipfs=Ipfs(host="127.0.0.1", port="5001"),
            writer=MyProtobuf()
        )
        store.add()
    ```

    Write with multiple indexes.
    Create a tiered file structure based on IDs.
    ```
        ├── fashion/
            ├── designer_1.manufacturer_1
            ├── designer_2.manufacturer_1
                ├── deal_16.data
            ├── designer_4.manufacturer_3
                ├── deal_1.data
                ├── deal_2.data
    ```
    ```py
        from ipfskvs.index import Index
        from ipfskvs.ipfs import Ipfs
        from ipfskvs.store import Store
        from deal_pb2 import Deal

        index = Index(
            prefix="fashion",
            index={
                "designer": str(uuid.uuid4()),
                "manufacturer": str(uuid.uuid4())
            }, subindex=Index(
                index={
                    "deal":  str(uuid.uuid4())
                }
            )
        )

        data = Deal(type=Type.BUZZ, content="fizz")
        store = Store(index=index, ipfs=Ipfs(), writer=data)
        store.add()
    ```

    Query the multiple indexes:
    Ex: get all deals with designer id "123"
    ```py
        from ipfskvs.index import Index
        from ipfskvs.ipfs import Ipfs
        from ipfskvs.store import Store
        from deal_pb2 import Deal

        query_index = Index(
            prefix="fashion",
            index={
                "designer": "123"
            }
        )
        reader = Deal()
        store = Store.query(query_index, ipfs, reader)
        print(reader)
    ```
    """
    index: Index
    writer: Message
    reader: Message

    def __init__(
            self: Self,
            index: Index,
            ipfs: Ipfs,
            writer: Message = None,
            reader: Message = None) -> None:
        """Construct a Store object.

        Args:
            index (Index): An object representing the filepath
            ipfs (Ipfs): The IPFS client
            writer (Message, optional): The protobuf object with the
                data to write to ipfs on `.write()`. Defaults to None.
            reader (Message, optional): The protobuf object to populate
                when reading the data from ipfs with `.read()`.
                Defaults to None.
        """
        self.index = index
        self.ipfs = ipfs
        self.writer = writer
        self.reader = reader

    def read(self: Self) -> None:
        """Read the data from ipfs into `self.reader`.

        Raises:
            FileNotFoundError: An exception is raised if the file is
                not found on IPFS.
        """
        filename = self.index.get_filename()
        LOG.info(f"Reading {filename}")
        result = self.ipfs.read(filename)
        if not result:
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                filename
            )

        LOG.debug(result)
        self.reader = type(self.reader)()
        self.reader.ParseFromString(result)

    def add(self: Self) -> None:
        """Add the protobuf data from `self.writer` to IPFS."""
        filename = self.index.get_filename()
        data = self.writer.SerializeToString()
        LOG.info(f"Adding {data} to {filename}")
        self.ipfs.add(filename, data)

    def delete(self: Self) -> None:
        """Only needed for local testing."""
        filename = self.index.get_filename()
        LOG.info(f"Deleting file: {filename}")
        self.ipfs.delete(filename)

    @staticmethod
    def to_dataframe(
            data: List[Store],
            protobuf_parsers: Dict[str, FunctionType]) -> pd.DataFrame:
        """Convert a list of Store objects to a pandas dataframe.

        The data for each Store must be read into memory beforehand;
            using `store.read()`

        Args:
            data (List[Store]): The list of Store objects with Indexes
            protobuf_parsers: (Dict[str, function]): key, value pair of
                key (str) --> pandas column name
                value (function) --> how to extract the value from the store

                The function should accept a Store object and return Any

        Returns:
            pd.DataFrame: The index and subindex data
                reformatted into a dataframe
        """
        pandas_input = {}
        for store in data:
            metadata = store.index.get_metadata()
            for key in metadata:
                if key not in pandas_input:
                    pandas_input[key] = []
                pandas_input[key].append(metadata[key])

            for key in protobuf_parsers:
                if key not in pandas_input:
                    pandas_input[key] = []
                parsed_data = protobuf_parsers[key](store)
                pandas_input[key].append(parsed_data)

        # Transpose the data before creating the DataFrame
        pandas_input = {key: value for key, value in pandas_input.items()}
        return pd.DataFrame(pandas_input)

    @staticmethod
    def query_indexes(query_index: Index, ipfs: Ipfs) -> List[Index]:
        """Query ipfs based on the `query_index` param.

        Args:
            query_index (Index): The Index object to use for the query.
            ipfs (Ipfs): The IPFS client.

        Returns:
            List[Index]: The matching filenames found in ipfs, loaded
                into a list of Index objects
        """
        result = []

        # list the files in the directory
        path = query_index.get_filename()
        response = ipfs.list_files(path)
        LOG.debug("ipfs.list_files(%s): %s", path, response)

        filenames = [
            file['Name'] for file in response['Entries']
        ] if response and 'Entries' in response and response['Entries'] else []
        LOG.debug("ipfs.list_files filenames: %s", filenames)

        for filename in filenames:
            # Listing the same file twice indicates the base case
            #   ex:
            #       path = `ls dir1/dir2` --> filenames = ["filename"]
            #       path = `ls dir1/dir2/filename` --> filenames = ["filename"]
            if filename in path:
                return [query_index]

            # filter filenames based on the index
            full_filename = f"{path}/{filename}".replace("//", "/")
            LOG.debug(f"Current filename: {full_filename}")
            from_index = Index.from_filename(
                filename=full_filename,
                has_prefix=query_index.prefix
            )
            if query_index.matches(from_index):
                LOG.debug(f"Matched {from_index} with {query_index}")
                result += Store.query_indexes(from_index, ipfs)

        return result

    @staticmethod
    def query(
            query_index: Index,
            ipfs: Ipfs,
            reader: Message) -> Iterator[Store]:
        """Query ipfs based on the `query_index` param.

        Find the filenames matching the query_index.
        Read the file contents from ipfs for each matching filename.
        Parse the file contents into the reader protobuf object.

        Args:
            query_index (Index): The Index object to use for the query.
            ipfs (Ipfs): The IPFS client.
            reader (Message): _description_

        Yields:
            Iterator[Store]: The list of matching Store objects with
                file content loaded into the `reader` attribute
        """
        LOG.debug("query index: %s", query_index.to_dict())
        for response_index in Store.query_indexes(query_index, ipfs):
            reader = type(reader)()
            store = Store(index=response_index, reader=reader, ipfs=ipfs)
            store.read()
            LOG.debug("query result yield: %s", store)
            yield store
