import datetime

from typing import Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl

from .. import Gender
from ..client import SDKClient, SDKResponse


MC_URL_BY_ID = {
    1: "https://sm.mm/",
    2: "https://dm.mm/",
    3: "https://tm.mm/",
    4: "https://fm.mm/",
}


class GetClient(BaseModel):
    uuid: str


class Client(BaseModel):
    uuid: str
    phone: str
    last_name: str = Field(alias="lname")
    first_name: str = Field(alias="fname")
    middle_name: Optional[str] = Field(alias="mname", default="")
    birth: datetime.date
    email: Optional[str]
    sex: Gender

    class Config:
        use_enum_values = True


class ClientResultsRequest(BaseModel):
    client_uuid: str
    mc_id: int
    pre_record_number: int
    lab_number: int


class ClientResultsResponse(BaseModel):
    lab_results_url: Optional[str]
    covid_results_url: Optional[str]
    flg_results_url: Optional[str]


class ClientService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_client(self, query: GetClient, timeout=3) -> SDKResponse[Client]:
        return self._client.get(
            urljoin(str(self._url), f"mobil/rest/client/{query.uuid}/"),
            Client,
            timeout=timeout,
        )

    def get_results(self, query: ClientResultsRequest, timeout=3):
        params = {
            "lab_number": query.lab_number,
            "pre_record_number": query.pre_record_number,
        }
        return self._client.get(
            urljoin(
                MC_URL_BY_ID[query.mc_id], f"mobil/client/{query.client_uuid}/results/"
            ),
            ClientResultsResponse,
            params=params,
            timeout=timeout,
        )
