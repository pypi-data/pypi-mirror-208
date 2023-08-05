import datetime

from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl, validator

from ..client import SDKClient, SDKResponse


class Client(BaseModel):
    phone_number: Optional[str]
    email: Optional[str]
    last_name: str
    first_name: str
    middle_name: Optional[str]
    birth: str
    post: Optional[str] = Field(alias="job")


class Trace(BaseModel):
    uuid: str
    label: str
    dt: Optional[datetime.date]
    description: str

    @validator("dt", pre=True)
    def ignore_time(cls, value):
        if value:
            return datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
        return


class LmkTraceResponse(BaseModel):
    client: Client
    trace: List[Trace]


class Medicine(BaseModel):
    latest_date: datetime.date
    next_date: Optional[datetime.date]
    nearest_expired_date: Optional[datetime.date]


class Attestation(BaseModel):
    latest_date: Optional[datetime.date]
    next_date: Optional[datetime.date]
    reg_date: Optional[datetime.date]


class Lmk(BaseModel):
    reg_number: Optional[str]
    blank_number: str
    job: str
    category: str
    type: str


class LmkError(str, Enum):
    not_all_medicine = "not_all_medicine"
    attestation_not_found = "attestation_not_found"


class CheckLmkResponse(BaseModel):
    lmk: Lmk
    medicine: Medicine
    attestation: Optional[Attestation]
    client: Client
    warnings: List[LmkError]

    class Config:
        use_enum_values = True


class OrderTraceRequest(BaseModel):
    phone: str
    lab_number: str


class CheckLmkRequest(BaseModel):
    blank_number: str
    last_name: str
    first_name: str


class LmkService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def order_trace(
        self, query: OrderTraceRequest, timeout=3
    ) -> SDKResponse[LmkTraceResponse]:
        return self._client.get(
            urljoin(str(self._url), "lmk/rest/order_detailed_trace_step/"),
            LmkTraceResponse,
            params=query.dict(),
            timeout=timeout,
        )

    def check_lmk(
        self, query: CheckLmkRequest, timeout=3
    ) -> SDKResponse[CheckLmkResponse]:
        return self._client.get(
            urljoin(str(self._url), "lmk/rest/check_lmk_v2/"),
            CheckLmkResponse,
            params=query.dict(),
            timeout=timeout,
        )
