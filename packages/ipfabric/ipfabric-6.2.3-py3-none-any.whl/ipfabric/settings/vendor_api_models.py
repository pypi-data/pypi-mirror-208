import re
from typing import Optional, List, Union

from pydantic import BaseModel, Field, validator, AnyHttpUrl

AWS_REGIONS = [
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-south-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ca-central-1",
    "eu-central-1",
    "eu-central-2",
    "eu-north-1",
    "eu-south-1",
    "eu-south-2",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "me-central-1",
    "me-south-1",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-gov-east-1",
    "us-gov-west-1",
    "us-west-1",
    "us-west-2",
]

SLUG = r"^[a-zA-Z0-9_\-.#:]*$"


class VendorAPI(BaseModel):
    """
    base Vendor API config
    """

    slug: str
    comment: str = ""
    isEnabled: bool = True

    @validator("slug")
    def check_slug(cls, slug):
        if not re.match(SLUG, slug):
            raise ValueError(f"{slug} is not a valid slug and must match regex {SLUG}")
        return slug


class SystemProxy(BaseModel):
    """
    support for Proxy Servers when utilizing Vendor APIs
    """

    respectSystemProxyConfiguration: bool = True


class RejectUnauthorized(SystemProxy, BaseModel):
    """
    support for credentials when utilizing Vendor APIs
    """

    rejectUnauthorized: bool = True


class UserAuthBaseUrl(BaseModel):
    """
    support for authentication when utilizing Vendor APIs
    """

    username: str
    password: str
    baseUrl: AnyHttpUrl


class AssumeRole(BaseModel):
    role: str


class AWS(VendorAPI, SystemProxy, BaseModel):
    """
    AWS vendor api support
    """

    apiKey: str
    apiSecret: str
    regions: list
    assumeRoles: Optional[List[Union[str, dict, AssumeRole]]] = Field(default=None)
    type: str = Field(default="aws-ec2", const=True)

    @validator("regions")
    def check_region(cls, regions):
        for r in regions:
            if r.lower() not in AWS_REGIONS:
                raise ValueError(f"{r} is not a valid AWS Region")
        return [r.lower() for r in regions]

    @validator("assumeRoles")
    def check_roles(cls, roles):
        validated_roles = list()
        for role in roles:
            if isinstance(role, str):
                validated_roles.append(AssumeRole(role=role))
            elif isinstance(role, dict):
                if "role" in role:
                    validated_roles.append(AssumeRole(**role))
                else:
                    raise SyntaxError(f'Role {role} not in \'{{"role": "<arn:aws:iam::*****:role/*****>"}}\' format.')
            elif isinstance(role, AssumeRole):
                validated_roles.append(role)
        return validated_roles


class Azure(VendorAPI, SystemProxy, BaseModel):
    """
    Azure vendor api support
    """

    clientId: str
    clientSecret: str
    subscriptionId: str
    tenantId: str
    type: str = Field(default="azure", const=True)


class CheckPointApiKey(VendorAPI, RejectUnauthorized, BaseModel):
    """
    Checkpoint vendor api support
    """

    apiKey: str
    baseUrl: AnyHttpUrl
    domains: Optional[List[str]] = Field(default_factory=list)
    type: str = Field(default="checkpoint-mgmt-api", const=True)


class CheckPointUserAuth(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    checkpoint authentication vendor api support
    """

    domains: Optional[List[str]] = Field(default_factory=list)
    type: str = Field(default="checkpoint-mgmt-api", const=True)


class CiscoAPIC(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    Cisco APIC vendor api support
    """

    type: str = Field(default="ciscoapic", const=True)


class CiscoFMC(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    Cisco FMC vendor api support
    """

    type: str = Field(default="ciscofmc", const=True)


class ForcePoint(VendorAPI, RejectUnauthorized, BaseModel):
    """
    ForcePoint vendor api support
    """

    authenticationKey: str
    baseUrl: AnyHttpUrl
    type: str = Field(default="forcepoint", const=True)


class JuniperMist(VendorAPI, RejectUnauthorized, BaseModel):
    """
    Juniper Mist vendor api support
    """

    apiToken: str
    apiVer: str = Field(default="v1", const=True)
    type: str = Field(default="juniper-mist", const=True)
    baseUrl: AnyHttpUrl = "https://api.mist.com"


class Merakiv1(VendorAPI, RejectUnauthorized, BaseModel):
    """
    Meraki v1 vendor api support
    """

    apiKey: str
    baseUrl: AnyHttpUrl
    organizations: Optional[List[str]] = Field(default_factory=list)
    apiVer: str = Field(default="v1", const=True)
    type: str = Field(default="meraki-v0", const=True)


class NSXT(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    NSXT vendor api support
    """

    type: str = Field(default="nsxT", const=True)


class Prisma(VendorAPI, RejectUnauthorized, BaseModel):
    """
    Prisma vendor api support
    """

    username: str
    password: str
    tsgid: str
    type: str = Field(default="prisma", const=True)


class RuckusVirtualSmartZone(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    Ruckus Virtual SmartZone vendor api support
    """

    apiVer: str = Field(default="v9_1", const=True)
    type: str = Field(default="ruckus-vsz", const=True)


class SilverPeak(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    SilverPeak vendor api support
    """

    loginType: str = "Local"
    type: str = Field(default="nsxT", const=True)

    @validator("loginType")
    def check_region(cls, login_type):
        if login_type not in ["Local", "RADIUS", "TACACS+"]:
            raise ValueError(f"{login_type} is not a valid login type must be in ['Local', 'RADIUS', 'TACACS+']")
        return login_type


class Versa(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    Versa vendor api support
    """

    type: str = Field(default="versa", const=True)


class Viptela(VendorAPI, RejectUnauthorized, UserAuthBaseUrl, BaseModel):
    """
    Viptela vendor api support
    """

    type: str = Field(default="viptela", const=True)
