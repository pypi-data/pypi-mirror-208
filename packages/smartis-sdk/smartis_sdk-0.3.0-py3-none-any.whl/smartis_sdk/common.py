"""Словари используемые в модуле main."""
from collections import namedtuple
from enum import Enum


class Filter(Enum):
    SmartisID = 7071
    Channel = 1222
    Placement = 1223


MethodFields = namedtuple("MethodFields", "method location id")


class Method(Enum):
    get_projects = MethodFields("projects/get", "projects", "project")
    get_metrics = MethodFields("metrics/get", "metrics", "code")
    get_groupings = MethodFields("reports/getGroupings", "groupings", "code")
    get_attributions = MethodFields("reports/getModelAttributions", "modelAttributions", "id")
    get_channels = MethodFields("reports/getChannels", "", "")
    get_placements = MethodFields("reports/getPlacements", "", "")
    get_campaigns = MethodFields("reports/getCampaigns", "", "")
    get_ads = MethodFields("reports/getAds", "", "")
    get_keywords = MethodFields("reports/getKeywords", "", "")


class GroupBy(Enum):
    ADS = "ad_id"
    DAY = "day"
    PLACEMENT = "placement_id"
    CAMPAIGN = "campaigns"
    OBJECTS = "smartis_object"


class FilterCategory(Enum):
    SMARTIS_ID = 7071
    CHANNEL = 1222
    PLACEMENT = 1223


class AttributionModel(Enum):
    LINEAR = 3
    LINEAR_WITH_POSTVIEW = 10


class TypeReport(Enum):
    RAW = "raw"
    AGGREGATED = "aggregated"
