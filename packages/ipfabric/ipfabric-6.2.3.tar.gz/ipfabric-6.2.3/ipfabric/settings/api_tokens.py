import logging
from secrets import token_hex
from typing import Any, Union, Optional, List

from pydantic import Field, BaseModel

from ipfabric.settings.user_mgmt import UserMgmt
from ipfabric.tools.shared import date_parser

logger = logging.getLogger("ipfabric")


class Token(BaseModel):
    description: str
    usage: int
    username: str
    expires: Optional[int] = None
    secret: Optional[str] = None
    user_id: str = Field(alias="userId")
    user_role_ids: Optional[List[str]] = Field(alias="userRoleIds", default=None)
    token_id: str = Field(alias="id")
    is_expired: bool = Field(alias="isExpired")
    last_used: Optional[str] = Field(alias="lastUsed")
    role_ids: List[str] = Field(alias="roleIds")
    role_names: Optional[List[str]] = Field(alias="roleNames", default=None)


class APIToken:
    def __init__(self, client):
        self.client: Any = client
        self.tokens = self.get_tokens()

    @property
    def tokens_by_id(self):
        return {t.token_id: t for t in self.tokens}

    @property
    def tokens_by_description(self):
        return {t.description: t for t in self.tokens}

    def get_tokens(self):
        res = self.client.get("api-tokens")
        res.raise_for_status()
        return [Token(**t) for t in res.json()]

    def _check_roles(self, role_ids: list, role_names: list):
        if not role_names and not role_ids:
            raise SyntaxError("No Role Ids or Names provided.")
        roles = UserMgmt(self.client)
        checked_roles = list()
        for role in role_ids:
            if str(role) in roles.roles_by_id:
                checked_roles.append(str(role))
            else:
                raise ValueError(f"Role ID '{role}' does not exist.")
        for role in role_names:
            if str(role) in roles.roles_by_name:
                checked_roles.append(str(role))
            else:
                raise ValueError(f"Role Name '{role}' does not exist.")
        return checked_roles

    def add_token(
        self,
        descr: str,
        role_ids: Optional[list] = None,
        role_names: Optional[list] = None,
        expires: Optional[Union[str, int]] = None,
        token: str = None,
    ):
        if token and len(token) < 8:
            raise SyntaxError("Token must be 8 characters.")
        elif not token:
            token = token_hex(16)

        payload = dict(
            description=descr,
            expires=int(date_parser(expires).timestamp() * 1000) if expires else None,
            roleIds=self._check_roles(role_ids or list(), role_names or list()),
            token=token,
        )
        res = self.client.post("api-tokens", json=payload)
        res.raise_for_status()
        return Token(secret=token, **res.json())

    def delete_token(self, token_id: [int, str, Token]):
        token_id = token_id.token_id if isinstance(token_id, Token) else str(token_id)
        if token_id not in self.tokens_by_id:
            raise ValueError(f"Could not find token matching ID '{token_id}'.")
        res = self.client.delete("api-tokens/" + token_id)
        res.raise_for_status()
        self.tokens = self.get_tokens()
        return self.tokens

    def delete_token_by_description(self, token_description: str):
        if token_description not in self.tokens_by_description:
            raise ValueError(f"Could not find token matching description '{token_description}'.")
        return self.delete_token(self.tokens_by_description[token_description].token_id)
