import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from httpx import AsyncClient, Response, codes
from pydantic import BaseSettings, Field

from classiq.exceptions import ClassiqAuthenticationError


class AuthSettings(BaseSettings):
    domain: str = Field(default="classiq.eu.auth0.com", env="CLASSIQ_AUTH_DOMAIN")
    audience: str = Field(default="https://cadmium-be", env="CLASSIQ_AUTH_AUDIENCE")
    client_id: str = Field(
        default="f6721qMOVoDAOVkzrv8YaWassRKSFX6Y", env="CLASSIQ_AUTH_CLIENT_ID"
    )


@dataclass
class Tokens:
    access_token: str
    refresh_token: Optional[str]


class Auth0:
    _CONTENT_TYPE = "application/x-www-form-urlencoded"
    _HEADERS = {"content-type": _CONTENT_TYPE}

    def __init__(self) -> None:
        self._auth_settings = AuthSettings()

    @property
    def _base_url(self) -> str:
        return f"https://{self._auth_settings.domain}"

    @property
    def _client_id(self) -> str:
        return self._auth_settings.client_id

    async def _make_request(
        self,
        url: str,
        payload: Dict[str, str],
        allow_error: Union[bool, int] = False,
    ) -> Dict[str, Any]:
        encoded_payload = urllib.parse.urlencode(payload)
        client: AsyncClient
        async with AsyncClient(
            base_url=self._base_url, headers=self._HEADERS
        ) as client:
            response: Response = await client.post(url=url, content=encoded_payload)
            code = response.status_code
            error_code_allowed = allow_error is True or allow_error == code
            data = response.json()

        if code == codes.OK or error_code_allowed:
            return data

        raise ClassiqAuthenticationError(
            f"Request to Auth0 failed with error code {code}: {data.get('error')}"
        )

    async def get_device_data(self, get_refresh_token: bool = True) -> Dict[str, Any]:
        payload = {
            "client_id": self._auth_settings.client_id,
            "audience": self._auth_settings.audience,
        }
        if get_refresh_token:
            payload["scope"] = "offline_access"

        return await self._make_request(
            url="/oauth/device/code",
            payload=payload,
        )

    async def poll_tokens(self, device_code: str) -> Dict[str, Any]:
        payload = {
            "client_id": self._client_id,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }

        return await self._make_request(
            url="/oauth/token",
            payload=payload,
            allow_error=codes.FORBIDDEN,
        )

    async def refresh_access_token(self, refresh_token: str) -> Tokens:
        # TODO handle failure
        payload = {
            "client_id": self._client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        data = await self._make_request(
            url="/oauth/token",
            payload=payload,
        )

        return Tokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", None),
        )
