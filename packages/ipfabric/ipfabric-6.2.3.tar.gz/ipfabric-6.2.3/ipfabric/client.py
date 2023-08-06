import logging
import re
from json import loads
from typing import Optional, Union, Dict, List, Any
from urllib.parse import urlparse

from httpx import HTTPStatusError

from ipfabric.api import IPFabricAPI
from ipfabric.models import Technology, Inventory, Jobs, Intent, Devices

logger = logging.getLogger("ipfabric")

RE_PATH = re.compile(r"^/?(api/)?v\d(\.\d)?/")
RE_TABLE = re.compile(r"^tables/")


class IPFClient(IPFabricAPI):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        auth: Optional[Any] = None,
        unloaded: bool = False,
        **kwargs,
    ):
        """Initializes the IP Fabric Client

        Args:
            base_url: IP Fabric instance provided in 'base_url' parameter, or the 'IPF_URL' environment variable
            api_version: [Optional] Version of IP Fabric API
            auth: API token, tuple (username, password), or custom Auth to pass to httpx
            snapshot_id: IP Fabric snapshot ID to use by default for database actions - defaults to '$last'
            **kwargs: Keyword args to pass to httpx
        """
        super().__init__(
            base_url=base_url,
            api_version=api_version,
            auth=auth,
            snapshot_id=snapshot_id,
            unloaded=unloaded,
            **kwargs,
        )
        self.technology = Technology(client=self)
        self.jobs = Jobs(client=self)
        self._devices = list()

    @property
    def snapshot_id(self) -> str:
        """get snapshot Id"""
        return self._snapshot_id

    @snapshot_id.setter
    def snapshot_id(self, snapshot_id):
        super(self.__class__, self.__class__).snapshot_id.fset(self, snapshot_id)
        self.intent = Intent(client=self)
        self.api_to_web = {intent.api_endpoint: intent.web_endpoint for intent in self.intent.intent_checks}
        self.inventory = Inventory(client=self)

    @property
    def devices(self) -> Devices:
        """get devices"""
        if not self._devices:
            logger.info("Devices not loaded, loading devices.")
            self._devices = self.load_devices()
        return self._devices

    @devices.setter
    def devices(self, devices):
        self._devices = devices

    def load_devices(self, device_filters: dict = None, device_attr_filters: dict = None):
        if self._no_loaded_snapshots:
            logger.warning("No loaded snapshots, cannot load devices.")
        else:
            if not device_attr_filters and self.attribute_filters:
                logger.warning(
                    f"Global `attribute_filters` is set; only pulling devices matching:\n{self.attribute_filters}."
                )
            try:
                self.devices = self.inventory.devices.all(
                    as_model=True, filters=device_filters, attr_filters=device_attr_filters
                )
                return self.devices
            except HTTPStatusError:
                logger.warning(self._api_insuf_rights + 'on POST "/tables/inventory/devices". Will not load Devices.')
        return list()

    @staticmethod
    def _check_url(url):
        path = urlparse(url).path
        r = RE_PATH.search(path)
        url = path[r.end():] if r else path  # fmt: skip
        url = url[1:] if url[0] == "/" else url
        return url

    def _check_url_payload(self, url, snapshot_id, snapshot, filters, reports, sort, attr_filters):
        url = self._check_url(url)
        payload = dict()
        if filters and isinstance(filters, str):
            filters = loads(filters)
        if snapshot:
            payload["snapshot"] = snapshot_id
        if filters:
            payload["filters"] = filters
        if isinstance(reports, (str, list)):
            payload["reports"] = reports
        elif reports is True and "/" + url in self.api_to_web:
            payload["reports"] = self.api_to_web["/" + url]
        elif reports is True and "/" + url not in self.api_to_web:
            logger.warning(
                f"Could not automatically discover Web Endpoint for Intent Data for table '/{url}'.\n"
                f"Table may not have any Intent Checks, please manually verify and enter to reports.\n"
                f"Returning results without Intent Rules."
            )
        if sort:
            payload["sort"] = sort
        if RE_TABLE.match(url) and (attr_filters or self.attribute_filters):
            payload["attributeFilters"] = attr_filters or self.attribute_filters
        return url, payload

    def fetch(
        self,
        url,
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
    ) -> List[dict]:
        """Gets data from IP Fabric for specified endpoint

        Args:
            url: Example tables/vlan/device-summary
            columns: Optional list of columns to return, None will return all
            filters: Optional dictionary of filters
            limit: Default to 1,000 rows
            start: Starts at 0
            snapshot_id: Optional snapshot_id to override default
            reports: String of frontend URL where the reports are displayed or a list of report IDs
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            attr_filters: Optional dictionary to apply an Attribute filter
            snapshot: Set to False for some tables like management endpoints.

        Returns:
            list: List of Dictionary objects.
        """
        snapshot_id = snapshot_id or self.snapshot_id
        url, payload = self._check_url_payload(url, snapshot_id, snapshot, filters, reports, sort, attr_filters)
        payload["columns"] = columns or self.get_columns(url, snapshot=snapshot)
        payload["pagination"] = dict(start=start, limit=limit)
        res = self.post(url, json=payload)
        res.raise_for_status()
        return res.json()["data"]

    def fetch_all(
        self,
        url: str,
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
    ) -> List[dict]:
        """Gets all data from IP Fabric for specified endpoint

        Args:
            url: Example tables/vlan/device-summary
            columns: Optional list of columns to return, None will return all
            filters: Optional dictionary of filters
            snapshot_id: Optional snapshot_id to override default
            reports: String of frontend URL where the reports are displayed or a list of report IDs
            sort: Optional dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            attr_filters: Optional dictionary to apply an Attribute filter
            snapshot: Set to False for some tables like management endpoints.

        Returns:
            list: List of Dictionary objects.
        """
        snapshot_id = snapshot_id or self.snapshot_id
        url, payload = self._check_url_payload(url, snapshot_id, snapshot, filters, reports, sort, attr_filters)
        payload["columns"] = columns or self.get_columns(url, snapshot=snapshot)
        return self._ipf_pager(url, payload)

    def query(self, url: str, payload: Union[str, dict], get_all: bool = True) -> List[dict]:
        """Submits a query, does no formatting on the parameters.  Use for copy/pasting from the webpage.

        Args:
            url: Example: https://demo1.ipfabric.io/api/v1/tables/vlan/device-summary or tables/vlan/device-summary
            payload: Dictionary to submit in POST or can be JSON string (i.e. read from file).
            get_all: Default use pager to get all results and ignore pagination information in the payload

        Returns:
            list: List of Dictionary objects.
        """
        url = self._check_url(url)
        if isinstance(payload, str):
            payload = loads(payload)
        if get_all:
            return self._ipf_pager(url, payload)
        else:
            res = self.post(url, json=payload)
            res.raise_for_status()
            return res.json()["data"]

    def _get_columns(self, url: str):  # TODO: Remove in v7
        logger.warning("""Use of _get_columns will be deprecated in a future release, please use get_columns""")
        return self.get_columns(url=url)

    def get_columns(self, url: str, snapshot: bool = True) -> List[str]:
        """Submits malformed payload and extracts column names from it

        Args:
            url: API url to post
            snapshot: Set to False for some tables like management endpoints.

        Returns:
            list: List of column names
        """
        url, payload = self._check_url_payload(url, self.snapshot_id, snapshot, None, None, None, None)
        payload["columns"] = ["*"]
        r = self.post(url, json=payload)
        if r.status_code == 422:
            msg = r.json()["errors"][0]["message"]
            return [x.strip() for x in re.match(r"\".*\".*\[(.*)]$", msg).group(1).split(",")]
        else:
            r.raise_for_status()

    def get_count(
        self,
        url: str,
        filters: Optional[Union[dict, str]] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot_id: Optional[str] = None,
        snapshot: bool = True,
    ) -> int:
        """Get a total number of rows
        Args:
            url: API URL to post to
            filters: Optional dictionary of filters
            attr_filters: Optional dictionary of attribute filters
            snapshot_id: Optional snapshot_id to override default
            snapshot: Set to False for some tables like management endpoints.
        Returns:
            int: a count of rows
        """
        snapshot_id = snapshot_id or self.snapshot_id
        url, payload = self._check_url_payload(url, snapshot_id, snapshot, filters, None, None, attr_filters)
        payload.update({"columns": ["id"], "pagination": {"limit": 1, "start": 0}})
        res = self.post(url, json=payload)
        res.raise_for_status()
        return res.json()["_meta"]["count"]
