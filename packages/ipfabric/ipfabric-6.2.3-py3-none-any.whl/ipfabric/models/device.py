from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ipfabric import IPFClient

import re
import logging
from datetime import timedelta
from typing import Optional, List, Union, Dict, DefaultDict, Set, overload
from ipaddress import IPv4Interface
from collections import defaultdict
from case_insensitive_dict import CaseInsensitiveDict

from pydantic import BaseModel, Field, PrivateAttr


logger = logging.getLogger("ipfabric")


class DeviceConfig(BaseModel):
    status: str
    current: Optional[str]
    start: Optional[str]


class Device(BaseModel):
    attributes: dict
    domain: Optional[str]
    family: Optional[str]
    fqdn: Optional[str]
    hostname: str
    image: Optional[str]
    model: Optional[str]
    platform: Optional[str]
    processor: Optional[str]
    reload: Optional[str]
    sn: str
    uptime: Optional[timedelta]
    vendor: str
    version: str
    blob_key: Optional[str] = Field(alias="blobKey")
    config_reg: Optional[str] = Field(alias="configReg")
    dev_type: str = Field(alias="devType")
    hostname_original: Optional[str] = Field(alias="hostnameOriginal")
    hostname_processed: Optional[str] = Field(alias="hostnameProcessed")
    login_ip: Optional[IPv4Interface] = Field(alias="loginIp")
    login_type: str = Field(alias="loginType")
    mem_total_bytes: Optional[float] = Field(alias="memoryTotalBytes")
    mem_used_bytes: Optional[float] = Field(alias="memoryUsedBytes")
    mem_utilization: Optional[float] = Field(alias="memoryUtilization")
    object_id: Optional[str] = Field(alias="objectId")
    routing_domain: Optional[int] = Field(alias="rd")
    site: str = Field(alias="siteName")
    sn_hw: str = Field(alias="snHw")
    stp_domain: Optional[int] = Field(alias="stpDomain")
    task_key: Optional[str] = Field(alias="taskKey")

    def __repr__(self):
        return self.hostname

    def __str__(self):
        return self.hostname

    def __eq__(self, other):
        return self.sn == other.sn if isinstance(other, Device) else str(other)

    def __hash__(self):
        return hash(self.sn)

    @classmethod
    def check_attribute(cls, attribute) -> True:
        if attribute not in cls.__fields__:
            raise AttributeError(f"Attribute {attribute} not in Device class.")
        return True

    def get_log_file(self, client: IPFClient) -> str:
        res = client.get("/os/logs/task/" + self.task_key)
        res.raise_for_status()
        return res.text

    def get_config(self, client: IPFClient) -> Union[None, DeviceConfig]:
        if not self.blob_key:
            logger.warning("Device Config not in Snapshot File. Please try using ipfabric.tools.DeviceConfigs")
            return None
        res = client.get("blobs/device-configuration/" + str(self.blob_key))
        res.raise_for_status()
        return DeviceConfig(**res.json())

    def interfaces(self, client: IPFClient) -> list:
        return client.inventory.interfaces.all(filters={"sn": ["eq", self.sn]})

    def pn(self, client: IPFClient) -> list:
        return client.inventory.pn.all(filters={"deviceSn": ["eq", self.sn]})

    def switchport(self, client: IPFClient) -> list:
        return client.technology.interfaces.switchport.all(filters={"sn": ["eq", self.sn]})

    def managed_ip_ipv4(self, client: IPFClient) -> list:
        return client.technology.addressing.managed_ip_ipv4.all(filters={"sn": ["eq", self.sn]})

    def managed_ip_ipv6(self, client: IPFClient) -> list:
        return client.technology.addressing.managed_ip_ipv6.all(filters={"sn": ["eq", self.sn]})

    def mac_table(self, client: IPFClient) -> list:
        return client.technology.addressing.mac_table.all(filters={"sn": ["eq", self.sn]})

    def arp_table(self, client: IPFClient) -> list:
        return client.technology.addressing.arp_table.all(filters={"sn": ["eq", self.sn]})

    def routes_ipv4(self, client: IPFClient) -> list:
        return client.technology.routing.routes_ipv4.all(filters={"sn": ["eq", self.sn]})

    def routes_ipv6(self, client: IPFClient) -> list:
        return client.technology.routing.routes_ipv6.all(filters={"sn": ["eq", self.sn]})

    def neighbors_all(self, client: IPFClient) -> list:
        return client.technology.neighbors.neighbors_all.all(filters={"localSn": ["eq", self.sn]})

    def fetch_all(self, client: IPFClient, url: str) -> list:
        columns = client.get_columns(url)
        if "sn" not in columns:
            raise KeyError(f'Column "sn" not found in "{url}" table.')
        return client.fetch_all(url, filters={"sn": ["eq", self.sn]}, columns=columns)


class DeviceDict(CaseInsensitiveDict):
    """CaseInsensitiveDict with functions to search or regex on dictionary keys."""

    def __init__(self, attribute, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attribute = attribute

    @staticmethod
    def _new_dict(a):
        return DeviceDict[str, Device](attribute=a) if a == "sn" else DeviceDict[str, List[Device]](attribute=a)

    @overload
    def regex(self: DeviceDict[str, List[Device]], pattern: str, *flags: int) -> DeviceDict[str, List[Device]]:
        ...

    @overload
    def regex(self: DeviceDict[str, Device], pattern: str, *flags: int) -> DeviceDict[str, Device]:
        ...

    def regex(self, pattern: str, *flags: int) -> DeviceDict[str, Union[List[Device], Device]]:
        """
        Case-sensitive regex search on dictionary keys.
        Args:
            pattern: str: Regex string to search.
            *flags: int or re.RegexFlag: Regex flags to use.

        Returns:
            DeviceDict: New instance of DeviceDict (CaseInsensitiveDict)
        """
        regex = re.compile(pattern, flags=sum(flags))
        new_dict = self._new_dict(self.attribute)
        [new_dict.update({key: value}) for key, value in self._data.values() if key and regex.search(key)]
        return new_dict

    @overload
    def search(self: DeviceDict[str, List[Device]], pattern: Union[List[str], str]) -> DeviceDict[str, List[Device]]:
        ...

    @overload
    def search(self: DeviceDict[str, Device], pattern: Union[List[str], str]) -> DeviceDict[str, Device]:
        ...

    def search(self, pattern: Union[List[str], str]) -> DeviceDict[str, Union[List[Device], Device]]:
        """
        Case-insensitive search on dictionary keys.
        Args:
            pattern: Union[List[str], str]: String or List of strings to match on.

        Returns:
            DeviceDict: New instance of DeviceDict (CaseInsensitiveDict)
        """
        pattern = [pattern.lower()] if isinstance(pattern, str) else [p.lower() for p in pattern]
        new_dict = self._new_dict(self.attribute)
        [new_dict.update({o_key: value}) for key, (o_key, value) in self._data.items() if key in pattern]
        return new_dict

    def _flatten_devs(self) -> List[Device]:
        devices = list()
        for value in self.values():
            if isinstance(value, list):
                devices.extend(value)
            else:
                devices.append(value)
        return devices

    def sub_search(self, attribute: str, pattern: Union[List[str], str]) -> DeviceDict[str, List[Device]]:
        """
        Case-insensitive sub search of another Device attribute.
        Args:
            attribute: str: Attribute of Device class.
            pattern: Union[List[str], str]: String or List of strings to match on.

        Returns:
             DeviceDict: New instance of DeviceDict (CaseInsensitiveDict) grouped by new attribute.
        """
        Device.check_attribute(attribute)
        return Devices.group_dev_by_attr(self._flatten_devs(), attribute).search(pattern)

    def sub_regex(self, attribute: str, pattern: Union[List[str], str], *flags: int) -> DeviceDict[str, List[Device]]:
        """
        Case-sensitive regex sub search of another Device attribute.
        Args:
            attribute: str: Attribute of Device class.
            pattern: str: Regex string to search.
            *flags: int or re.RegexFlag: Regex flags to use.

        Returns:
            DeviceDict: New instance of DeviceDict (CaseInsensitiveDict) grouped by new attribute.
        """
        Device.check_attribute(attribute)
        return Devices.group_dev_by_attr(self._flatten_devs(), attribute).regex(pattern, *flags)


class Devices(BaseModel):
    snapshot_id: str
    _attrs: Optional[DefaultDict[str, Set[str]]] = PrivateAttr()
    _all: List[Device] = PrivateAttr()

    def __init__(
        self, snapshot_id: str, devices: List[dict], attributes: List[dict] = None, blob_keys: List[dict] = None
    ):
        super().__init__(snapshot_id=snapshot_id)
        self._attrs, dev_attr = self._parse_attrs(attributes)
        blob_keys = {b["sn"]: b["blobKey"] for b in blob_keys} if blob_keys else dict()
        self._all = [
            Device(**d, attributes=dev_attr.get(d["sn"], dict()), blobKey=blob_keys.get(d["sn"], None)) for d in devices
        ]

    @staticmethod
    def _parse_attrs(attributes: List[dict] = None):
        if not attributes:
            return None, dict()
        cls_attr, dev_attr = defaultdict(set), defaultdict(dict)
        for d in attributes:
            dev_attr[d["sn"]].update({d["name"]: d["value"]})
            cls_attr[d["name"]].add(d["value"])
        return cls_attr, dev_attr

    @property
    def all(self) -> List[Device]:
        """Returns List[Device]."""
        return self._all

    def _check_attr_name(self, name: str) -> bool:
        if self._attrs is None:
            logger.warning("Attributes were not loaded into devices.")
        elif name not in self._attrs:
            logger.warning(f'Attribute key "{name}" not found in snapshot "{self.snapshot_id}".')
        else:
            return True
        return False

    def _filter_attr(self, devs: Set[Device], name: str, values: Union[List[str], str]) -> Set[Device]:
        if not self._check_attr_name(name):
            return set()
        values = values if isinstance(values, list) else [values]
        for dev in devs.copy():
            dev_attr = dev.attributes.get(name, None)
            if not dev_attr or dev_attr not in values:
                devs.discard(dev)
        return devs

    def filter_by_attr(self, name: str, values: Union[List[str], str]) -> List[Device]:
        """
        Return list of devices with an attribute set to a value
        Args:
            name: str: Attribute name
            values: Union[List[str], str]: Single attribute value or list of values to match.
        Returns:
            List[Device]
        """
        return list(self._filter_attr(set(self.all.copy()), name, values))

    def filter_by_attrs(self, attr_filter: Dict[str, Union[List[str], str]]) -> List[Device]:
        """
        Return list of devices matching multiple key/value attribute pairs
        Args:
            attr_filter: dict: {'ATTR_1': 'VALUE_1', 'ATTR_2': ['VALUE_2', 'VALUE_3']}
        Returns:
            List[Device]
        """
        devs = set(self.all.copy())
        for k, v in attr_filter.items():
            devs = self._filter_attr(devs, k, v)
        return list(devs)

    def has_attr(self, name: str) -> List[Device]:
        """
        Return list of devices that has an attribute set matching name.
        Args:
            name: str: Attribute name
        Returns:
            List[Device]
        """
        return [d for d in self.all if d.attributes.get(name, None)] if self._check_attr_name(name) else list()

    def does_not_have_attr(self, name: str) -> List[Device]:
        """
        Return list of devices that does not have an attribute set matching name.
        Args:
            name: str: Attribute name
        Returns:
            List[Device]
        """
        return [d for d in self.all if not d.attributes.get(name, None)] if self._check_attr_name(name) else list()

    def _group_dev_by_attr(self, attribute: str) -> DeviceDict[str, List[Device]]:
        return self.group_dev_by_attr(self._all, attribute)

    @classmethod
    def group_dev_by_attr(cls, devices: List[Device], attribute: str) -> DeviceDict[str, List[Device]]:
        devs = defaultdict(list)
        [devs[getattr(d, attribute)].append(d) for d in devices]
        return DeviceDict[str, List[Device]](attribute=attribute, data=devs)

    @property
    def by_sn(self) -> DeviceDict[str, Device]:
        """Returns Case-insensitive DeviceDict {'sn': Device}."""
        return DeviceDict[str, Device](attribute="sn", data={d.sn: d for d in self._all})

    @property
    def by_hostname(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'hostname': [Device]}."""
        return self._group_dev_by_attr("hostname")

    @property
    def by_sn_hw(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'sn_hw': [Device]}."""
        return self._group_dev_by_attr("sn_hw")

    @property
    def by_site(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'site': [Device]}."""
        return self._group_dev_by_attr("site")

    @property
    def by_vendor(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'vendor': [Device]}."""
        return self._group_dev_by_attr("vendor")

    @property
    def by_family(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'family': [Device]}."""
        return self._group_dev_by_attr("family")

    @property
    def by_platform(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'platform': [Device]}."""
        return self._group_dev_by_attr("platform")

    @property
    def by_model(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'model': [Device]}."""
        return self._group_dev_by_attr("model")

    @property
    def by_version(self) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'version': [Device]}."""
        return self._group_dev_by_attr("version")

    def by_custom(self, attribute) -> DeviceDict[str, List[Device]]:
        """Returns Case-insensitive DeviceDict {'version': [Device]}."""
        Device.check_attribute(attribute)
        return self._group_dev_by_attr(attribute)
