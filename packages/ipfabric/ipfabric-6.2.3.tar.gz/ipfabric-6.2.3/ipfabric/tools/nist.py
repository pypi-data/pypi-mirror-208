from time import sleep
from typing import List

from httpx import Client, ReadTimeout, HTTPStatusError
from pydantic import BaseModel, Field


class CVE(BaseModel):
    cve_id: str
    description: str
    url: str

    def __repr__(self):
        return self.cve_id

    def __hash__(self):
        return hash(self.cve_id)


class CVEs(BaseModel):
    total_results: int
    cves: List[CVE]
    error: str = Field(default=None)


class NIST(Client):
    def __init__(self, nvd_api_key: str, timeout):
        """
        NIST updated to API v2.0.  You must request and pass an API Key which can be obtained at
        https://nvd.nist.gov/developers/request-an-api-key

        Args:
            nvd_api_key: str: https://nvd.nist.gov/developers/request-an-api-key
            timeout: int:
        """
        super().__init__(
            base_url="https://services.nvd.nist.gov/rest/json/cves/2.0",
            timeout=timeout,
            headers={"apiKey": nvd_api_key},
        )

    @property
    def params(self):
        return {"virtualMatchString": "cpe:2.3:*:", "startIndex": 0}

    def check_cve(self, vendor: str, family: str, version: str) -> CVEs:  # noqa: C901
        """returns CVE data about a specific product line

        Args:
        vendor: Vendor for the device to be checked
        family: Family of the device to be checked
        version: Software version of the device to be checked
        Returns:
            a list of CVEs
        """
        params = self.params
        if vendor in ["azure", "aws"]:
            return CVEs(total_results=0, cves=[], error="Unsupported")
        elif vendor == "juniper":
            version = version[: version.rfind("R") + 2].replace("R", ":r")
            params["virtualMatchString"] += vendor + ":" + family + ":" + version
        elif vendor == "paloalto":
            params["virtualMatchString"] += "palo_alto" + ":" + family + ":" + version
        elif vendor == "extreme":
            if "xos" in family:
                family = "extremexos"
            params["virtualMatchString"] += "extremenetworks" + ":" + family + ":" + version
        elif family and "aruba" in family:
            params["virtualMatchString"] += "arubanetworks:arubaos" + ":" + version
        elif vendor == "f5" and family == "big-ip":
            params["virtualMatchString"] += vendor + ":" + "big-ip_access_policy_manager" + ":" + version
        elif vendor == "cisco":
            if family == "meraki":
                return CVEs(total_results=0, cves=[], error="Unsupported")
            elif family == "wlc-air":
                family = "wireless_lan_controller_software"
            elif family == "ftd":
                family = "firepower"
                version = (version.replace("(Bu", ".Bu")).replace(")", ".").split(" .", 1)[0]
            elif family != "nx-os":
                family = family.replace("-", "_")
            version = (version.replace("(", ".")).replace(")", ".")
            params["virtualMatchString"] += vendor + ":" + family + ":" + version
        elif vendor == "fortinet" and family == "fortigate":
            params["virtualMatchString"] += "fortinet:fortios:" + version.replace(",", ".")
        elif vendor == "checkpoint" and family == "gaia":
            params["virtualMatchString"] += vendor + ":" + "gaia_os" + version.replace("R", ":r")
        elif vendor == "arista":
            params["virtualMatchString"] += vendor + ":" + family + ":" + version.lower()
        else:
            return CVEs(total_results=0, cves=[], error="Unsupported")

        try:
            sleep(0.3)  # NIST Rate Limit: 50 requests/30 seconds
            res = self.get("", params=params)
            res.raise_for_status()
            data = res.json()

            cves = CVEs(
                total_results=data["totalResults"],
                cves=[
                    CVE(
                        cve_id=i["cve"]["id"],
                        description=i["cve"]["descriptions"][0]["value"],
                        url=i["cve"]["references"][0]["url"],
                    )
                    for i in data["vulnerabilities"]
                ],
            )
            return cves
        except ReadTimeout:
            return CVEs(total_results=0, cves=[], error="Timeout")
        except HTTPStatusError:
            return CVEs(total_results=0, cves=[], error="HTTP Error")
