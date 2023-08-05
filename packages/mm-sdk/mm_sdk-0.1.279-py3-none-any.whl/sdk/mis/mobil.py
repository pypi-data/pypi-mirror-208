from typing import Optional, List
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl

from ..client import SDKClient, SDKResponse


class UserRequest(BaseModel):
    username: str


class OrgResponse(BaseModel):
    id: int
    name: str
    base_org_id: Optional[int]


class MobilOrgService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_orgs_by_user(
        self, query: UserRequest, timeout=3
    ) -> SDKResponse[OrgResponse]:
        return self._client.get(
            urljoin(str(self._url), f"mobil/api/org_by_user/"),
            OrgResponse,
            params=query.dict(),
            timeout=timeout,
        )


class GetManagerRequest(UserRequest):
    name: str


class GetManagerResponse(BaseModel):
    username: str
    name: str
    email: Optional[str]
    groups: List[str] = []
    is_active: bool


class ManagerService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_superuser_managers(
        self, query: GetManagerRequest, timeout=3
    ) -> SDKResponse[GetManagerResponse]:
        return self._client.get(
            urljoin(str(self._url), f"mobil/api/user/search/"),
            GetManagerResponse,
            params=query.dict(),
            timeout=timeout,
        )
