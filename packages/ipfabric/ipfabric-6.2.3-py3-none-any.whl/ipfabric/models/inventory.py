import logging
from typing import Any

from pydantic import BaseModel

from .table import Table, DeviceTable

logger = logging.getLogger("ipfabric")

IGNORE_COLUMNS = {"id"}


class Inventory(BaseModel):
    """model for inventories"""

    client: Any

    @property
    def sites(self):
        return Table(client=self.client, endpoint="tables/inventory/sites")

    @property
    def vendors(self):
        return Table(client=self.client, endpoint="tables/inventory/summary/vendors")

    @property
    def devices(self):
        return DeviceTable(client=self.client)

    @property
    def models(self):
        return Table(client=self.client, endpoint="tables/inventory/summary/models")

    @property
    def os_version_consistency(self):
        return Table(client=self.client, endpoint="tables/management/osver-consistency")

    @property
    def eol_summary(self):
        return Table(client=self.client, endpoint="tables/reports/eof/summary")

    @property
    def eol_details(self):
        return Table(client=self.client, endpoint="tables/reports/eof/detail")

    @property
    def platforms(self):
        return Table(client=self.client, endpoint="tables/inventory/summary/platforms")

    @property
    def pn(self):
        return Table(client=self.client, endpoint="tables/inventory/pn")

    @property
    def families(self):
        return Table(client=self.client, endpoint="tables/inventory/summary/families")

    @property
    def interfaces(self):
        return Table(client=self.client, endpoint="tables/inventory/interfaces")

    @property
    def hosts(self):
        return Table(client=self.client, endpoint="tables/addressing/hosts")

    @property
    def phones(self):
        return Table(client=self.client, endpoint="tables/inventory/phones")

    @property
    def fans(self):
        return Table(client=self.client, endpoint="tables/inventory/fans")

    @property
    def modules(self):
        return Table(client=self.client, endpoint="tables/inventory/modules")
