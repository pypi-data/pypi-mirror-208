import json
from abc import abstractmethod
from datetime import datetime

from pydantic import BaseModel

from .common import AttributionModel, GroupBy, TypeReport, FilterCategory
from .utils import normalize_date


class ChannelItem(BaseModel):
    id: int
    title: str


class Channels(BaseModel):
    channels: list[ChannelItem]


class Channel(BaseModel):
    id: int
    title: str
    channel_id: int


class Placement(BaseModel):
    id: int
    title: str
    channel: Channel


class Placements(BaseModel):
    placements: list[Placement]


class Campaign(BaseModel):
    id: int
    placement_id: int
    title: str


class Campaigns(BaseModel):
    campaigns: list[Campaign]


class Keyword(BaseModel):
    id: int
    keyword: str


class Keywords(BaseModel):
    keywords: list[Keyword]


class Ad(BaseModel):
    id: int
    external_id: str
    placement_id: int
    campaign_id: int | None
    external_campaign_id: str | None
    type: str
    title: str | None
    text: str | None
    text1: str | None
    text2: str | None
    preview_url: str | None
    href: str | None
    device: str | None
    created_at: str


class Ads(BaseModel):
    ads: list[Ad]


class Attribution:

    def __init__(self, model_id: AttributionModel, period: int, with_direct: bool):
        self.model_id = model_id.value
        self.period = period
        self.with_direct = with_direct

    def __str__(self):
        return f"{self.model_id} {self.period} {self.with_direct}"


class Filter:
    def __init__(self, category: FilterCategory, value: int, operand: str = "="):
        self.category = category.value
        self.value = value
        self.operand = operand


@abstractmethod
class Payload:
    """Базовый класс параметров для генерации параметров к запросам"""

    def __init__(self, project: str, metrics: [str], datetime_from: datetime, datetime_to: datetime,
                 group_by: GroupBy, attribution: Attribution, type_report: TypeReport = TypeReport.AGGREGATED,
                 filters: list[Filter] | None = None, fields: list[str] | None = None):
        self.project = project
        self.metrics = ";".join(metrics) if metrics else ""
        self.datetime_from: str = normalize_date(datetime_from)
        self.datetime_to: str = normalize_date(datetime_to)
        self.group_by = group_by
        self.type = type_report
        self.filters = filters
        self.attribution = attribution
        self.fields = ";".join(fields) if fields else ""

    def __str__(self):
        return f"{self.datetime_from}//{self.datetime_to}"

    @abstractmethod
    def to_json(self) -> str:
        payload = {"project": self.project,
                   "metrics": self.metrics,
                   "datetimeFrom": self.datetime_from,
                   "datetimeTo": self.datetime_to,
                   "groupBy": self.group_by.value,
                   "type": self.type.value}
        if self.filters:
            payload["filters"] = self.filters

        payload["attribution"] = self.attribution.__dict__

        if self.fields:
            payload["fields"] = self.fields
        return json.dumps(payload)
