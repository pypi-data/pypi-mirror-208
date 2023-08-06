import logging
from typing import Optional, Dict, List, Any, Union

import deepdiff
from httpx import HTTPStatusError
from pydantic import BaseModel

from ipfabric.models import Devices
from ipfabric.settings import Attributes

logger = logging.getLogger("ipfabric")

IGNORE_COLUMNS = {"id"}


class BaseTable(BaseModel):
    """model for table data"""

    endpoint: str
    client: Any

    @property
    def name(self):
        return self.endpoint.split("/")[-1]

    @property
    def abs_endpoint(self):
        return self.endpoint if self.endpoint[0] == "/" else "/" + self.endpoint

    def fetch(
        self,
        columns: list = None,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        sort: Optional[dict] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
    ) -> list:
        """Gets all data from corresponding endpoint

        Args:
            columns: Optional columns to return, default is all
            filters: Optional filters'
            attr_filters: dict: Optional dictionary of Attribute filters
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            limit: Default to 1,000 rows
            start: Starts at 0

        Returns:
            list: List of Dictionaries
        """
        return self.client.fetch(
            self.endpoint,
            columns=columns,
            filters=filters,
            attr_filters=attr_filters,
            sort=sort,
            limit=limit,
            start=start,
            snapshot=False,
        )

    def all(
        self,
        columns: list = None,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        sort: Optional[dict] = None,
    ):
        """Gets all data from corresponding endpoint

        Args:
            columns: Optional columns to return, default is all
            filters: Optional filters
            attr_filters: dict: Optional dictionary of Attribute filters
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
        Returns:
            list: List of Dictionaries
        """
        return self.client.fetch_all(
            self.endpoint, columns=columns, filters=filters, attr_filters=attr_filters, sort=sort, snapshot=False
        )

    def count(
        self,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Gets count of table
        :param filters: dict: Optional filters
        :param attr_filters: dict: Optional dictionary of Attribute filters
        :return: int: Count
        """
        return self.client.get_count(self.endpoint, filters=filters, attr_filters=attr_filters, snapshot=False)


class Table(BaseTable, BaseModel):
    """model for table data"""

    def fetch(
        self,
        columns: list = None,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
    ) -> list:
        """Gets all data from corresponding endpoint

        Args:
            columns: Optional columns to return, default is all
            filters: Optional filters'
            attr_filters: dict: Optional dictionary of Attribute filters
            snapshot_id: Optional snapshot ID to override class
            reports: True to return Intent Rules (also accepts string of frontend URL) or a list of report IDs
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            limit: Default to 1,000 rows
            start: Starts at 0

        Returns:
            list: List of Dictionaries
        """
        return self.client.fetch(
            self.endpoint,
            columns=columns,
            filters=filters,
            attr_filters=attr_filters,
            snapshot_id=snapshot_id,
            reports=reports,
            sort=sort,
            limit=limit,
            start=start,
        )

    def all(
        self,
        columns: list = None,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
    ) -> list:
        """Gets all data from corresponding endpoint

        Args:
            columns: Optional columns to return, default is all
            filters: Optional filters
            attr_filters: dict: Optional dictionary of Attribute filters
            snapshot_id: Optional snapshot ID to override class
            reports: True to return Intent Rules (also accepts string of frontend URL) or a list of report IDs
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
        Returns:
            list: List of Dictionaries
        """
        return self.client.fetch_all(
            self.endpoint,
            columns=columns,
            filters=filters,
            attr_filters=attr_filters,
            snapshot_id=snapshot_id,
            reports=reports,
            sort=sort,
        )

    def count(
        self,
        filters: Optional[dict] = None,
        snapshot_id: Optional[str] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Gets count of table
        Args:
            filters: dict: Optional filters
            snapshot_id: str: Optional snapshot ID to override class
            attr_filters: dict: Optional dictionary of Attribute filters

        Returns:
            int: Count of rows
        """
        return self.client.get_count(self.endpoint, filters=filters, attr_filters=attr_filters, snapshot_id=snapshot_id)

    @staticmethod
    def _ignore_columns(columns: set, columns_ignore: set):
        """
        Determines which columns to use in the query.
        Args:
            columns: set : Set of columns to use
            columns_ignore: set : Set of columns to ignore

        Returns:
            list[str]: List of columns to use
        """
        cols_for_return = set()
        for col in columns:
            if col in columns_ignore and col != "id":
                logger.debug(f"Column {col} in columns_ignore, ignoring")
                continue
            cols_for_return.add(col)
        return cols_for_return

    def _compare_determine_columns(self, columns: set, columns_ignore: set, unique_keys: set, nested_keys: set):
        """
        Determines which columns to use in the query, and which columns to use
        Only supports a single nested column
        Args:
            columns: set : Set of columns to use
            columns_ignore: set : Set of columns to ignore
            unique_keys: set : Set of columns for unique keys
            nested_keys: set: Set of nested columns that belongs to a column in columns, columns_ignore, or unique_keys

        Returns:
            tuple[list, list]: List of columns to use in query, List of columns to use when sorting data
        """
        # get all columns for the table
        table_columns = set(self.client.get_columns(self.endpoint))

        # get any nested columns
        nested_cols_for_return = None
        # get a row of data
        one_row_of_data = self.fetch(limit=1)
        # loop over each column in the table columns
        for col in table_columns:
            # check if the data returned has nested columns
            if isinstance(one_row_of_data[0][col], list):
                # get all the nested column names
                nested_cols = set(one_row_of_data[0][col][0].keys())
                # create a set of nested column names requested by the user
                nested_cols_for_return = {col for col in nested_cols if col in nested_keys}

        # Must always ignore some columns
        columns_ignore.update(IGNORE_COLUMNS)

        cols_for_return = set()
        # user passes unique_keys
        if unique_keys:
            if not table_columns.issuperset(unique_keys):
                raise ValueError(f"Unique Key(s) {unique_keys - table_columns} not in table {self.name}")
            for u in unique_keys:
                cols_for_return.add(u)
            return list(cols_for_return), nested_cols_for_return
        # user passes columns
        if columns:
            if not table_columns.issuperset(columns):
                raise ValueError(f"Column(s) {columns - table_columns} not in table {self.name}")
            cols_for_return.update(self._ignore_columns(columns, columns_ignore))
            return list(cols_for_return), nested_cols_for_return
        # user does not pass columns
        # or only passed columns_ignore
        else:
            cols_for_return.update(self._ignore_columns(table_columns, columns_ignore))
            return list(cols_for_return), nested_cols_for_return

    @staticmethod
    def _remove_keys_from_dict(dict_object, keys_to_remove):
        if not keys_to_remove:
            return dict_object

        for v in dict_object.values():
            if not isinstance(v, list):
                continue

            for item in v:
                for key in keys_to_remove:
                    if key in item:
                        item.pop(key)

        return dict_object

    def _hash_data(self, json_data, unique_keys=None, nested_columns_ignore=None):
        """
        Hashes data. Turns any data into a string and hashes it, then returns the hash as a key for the data
        Args:
            json_data: list[dict] : List of dictionaries to hash
            unique_keys: list[str] : List of keys to use for hashing
            nested_columns_ignore: list[str]: List of nested column keys to filter data

        Returns:
            dict[str]: dictionary with hash as key and values as the original data
        """
        # loop over each obj, turn the obj into a string, and hash it
        return_json = dict()
        # user passes unique_keys
        if unique_keys:
            # loop over each response
            for dict_obj in json_data:
                dict_for_hash = self._remove_keys_from_dict(dict_object=dict_obj, keys_to_remove=nested_columns_ignore)
                # create a dictionary, of only the keys/columns requested
                hash_key = {key: dict_for_hash[key] for key in unique_keys}
                # hash the data
                unique_hash = deepdiff.DeepHash(hash_key)[hash_key]
                # check if the data has already been processed.
                if unique_hash in return_json:
                    # raise error if data has already been processed
                    raise KeyError(f"Unique Key(s) {unique_keys} are not unique, please adjust unique_keys input.")
                # store the data, using the hash as a key
                return_json[unique_hash] = dict_for_hash
        # user passes columns and/or column ignore
        else:
            # loop over each response
            for dict_obj in json_data:
                dict_for_hash = self._remove_keys_from_dict(dict_object=dict_obj, keys_to_remove=nested_columns_ignore)
                # hash each object, and store it in a dictionary, with the hash as the key
                return_json[deepdiff.DeepHash(dict_for_hash)[dict_for_hash]] = dict_for_hash
        return return_json

    @staticmethod
    def _make_set(data: Union[list, set, str] = None):
        if isinstance(data, str):
            return {data}
        elif data is None:
            return set()
        else:
            return set(data)

    def compare(
        self,
        snapshot_id: str = None,
        columns: Union[list, set] = None,
        columns_ignore: Union[list, set, str] = None,
        unique_keys: Union[list, set, str] = None,
        nested_columns_ignore: Union[list, set, str] = None,
        **kwargs,
    ):
        """
        Compares a table from the current snapshot to the snapshot_id passed.
        Args:
            snapshot_id: str : The snapshot_id to compare to.
            columns: list : List of columns to compare. If None, will compare all columns.
            columns_ignore: list : List of columns to ignore. If None, will always ignore 'id' column.
            unique_keys: list : List of columns to use as unique keys. If None, will use all columns as primary key.
            nested_columns_ignore: List of columns that belong to a nested columns
            **kwargs: dict : Optional Table.all() arguments to apply to the table before comparing.

        Returns:
            dict : dictionary containing the differences between the two snapshots.
                   Possible keys are 'added', 'removed' and 'changed'.
        """
        return_dict = dict()

        # determine which columns to use in query
        columns = self._make_set(columns)
        columns_ignore = self._make_set(columns_ignore)
        unique_keys = self._make_set(unique_keys)
        nested_columns_ignore = self._make_set(nested_columns_ignore)
        cols_for_query, nested_cols = self._compare_determine_columns(
            columns, columns_ignore, unique_keys, nested_columns_ignore
        )
        data = self.all(columns=cols_for_query, **kwargs)
        data_compare = self.all(snapshot_id=snapshot_id, columns=cols_for_query, **kwargs)

        # since we turned the values into a hash, we can just compare the keys
        if unique_keys:
            hashed_data_unique = self._hash_data(data, unique_keys, nested_cols)
            hashed_data_compare_unique = self._hash_data(data_compare, unique_keys, nested_cols)
            changed = [
                hashed_data_unique[hashed_str]
                for hashed_str in hashed_data_unique.keys()
                if hashed_str not in hashed_data_compare_unique.keys()
            ]
            return_dict["changed"] = changed
            return return_dict
        # compare both ways
        hashed_data = self._hash_data(data, nested_columns_ignore=nested_cols)
        hashed_data_compare = self._hash_data(data_compare, nested_columns_ignore=nested_cols)
        added = [
            hashed_data[hashed_str] for hashed_str in hashed_data.keys() if hashed_str not in hashed_data_compare.keys()
        ]
        removed = [
            hashed_data_compare[hashed_str]
            for hashed_str in hashed_data_compare.keys()
            if hashed_str not in hashed_data.keys()
        ]
        return_dict["added"] = added
        return_dict["removed"] = removed
        return return_dict


class DeviceTable(Table):
    """model for Device Table data"""

    endpoint = "tables/inventory/devices"

    def _as_model(self, devices, as_model):
        try:
            attributes = Attributes(client=self.client, snapshot_id=self.client.snapshot_id).all()
        except HTTPStatusError:
            logger.warning(
                self.client._api_insuf_rights
                + 'on POST "/tables/snapshot-attributes". Cannot load Attributes in Devices.'
            )
            attributes = None
        try:
            blob_keys = self.client.fetch_all("/tables/management/configuration/saved", columns=["sn", "blobKey"])
        except HTTPStatusError:
            logger.warning(
                self.client._api_insuf_rights + 'on POST "/tables/management/configuration/saved". '
                "You will not be able to pull device config from Device model."
            )
            blob_keys = None
        if as_model:
            devices = Devices(
                snapshot_id=self.client.snapshot_id, devices=devices, attributes=attributes, blob_keys=blob_keys
            )
        return devices

    def fetch(
        self,
        columns: list = None,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        as_model: Optional[bool] = False,
    ) -> Union[list, Devices]:
        """Gets all data from corresponding endpoint

        Args:
            columns: Optional columns to return, default is all
            filters: Optional filters'
            attr_filters: dict: Optional dictionary of Attribute filters
            snapshot_id: Optional snapshot ID to override class
            reports: True to return Intent Rules (also accepts string of frontend URL) or a list of report IDs
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            limit: Default to 1,000 rows
            start: Starts at 0
            as_model: bool: Default False, if True returns Devices model

        Returns:
            list: List of Dictionaries
        """
        devices = super(DeviceTable, self).fetch(
            columns=columns,
            filters=filters,
            attr_filters=attr_filters,
            snapshot_id=snapshot_id,
            reports=reports,
            sort=sort,
            limit=limit,
            start=start,
        )
        return self._as_model(devices, as_model)

    def all(
        self,
        columns: list = None,
        filters: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        as_model: Optional[bool] = False,
    ) -> Union[list, Devices]:
        """Gets all data from corresponding endpoint

        Args:
            columns: Optional columns to return, default is all
            filters: Optional filters
            attr_filters: dict: Optional dictionary of Attribute filters
            snapshot_id: Optional snapshot ID to override class
            reports: True to return Intent Rules (also accepts string of frontend URL) or a list of report IDs
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            as_model: bool: Default False, if True returns Devices model
        Returns:
            list: List of Dictionaries
        """
        devices = super(DeviceTable, self).all(
            columns=columns,
            filters=filters,
            attr_filters=attr_filters,
            snapshot_id=snapshot_id,
            reports=reports,
            sort=sort,
        )
        return self._as_model(devices, as_model)
