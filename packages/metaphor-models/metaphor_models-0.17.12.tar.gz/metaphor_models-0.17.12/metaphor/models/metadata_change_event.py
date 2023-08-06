# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = metadata_change_event_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, List, Union, TypeVar, Type, Callable, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


class AspectType(Enum):
    ASSET_CONTACTS = "ASSET_CONTACTS"
    ASSET_FOLLOWERS = "ASSET_FOLLOWERS"
    ASSET_GOVERNED_TAGS = "ASSET_GOVERNED_TAGS"
    ASSET_LIKES = "ASSET_LIKES"
    COMMON_COLUMN_DESCRIPTION_EXCLUSION = "COMMON_COLUMN_DESCRIPTION_EXCLUSION"
    CUSTOM_METADATA = "CUSTOM_METADATA"
    DASHBOARD_INFO = "DASHBOARD_INFO"
    DASHBOARD_UPSTREAM = "DASHBOARD_UPSTREAM"
    DATASET_DATA_QUALITY = "DATASET_DATA_QUALITY"
    DATASET_DOCUMENTATION = "DATASET_DOCUMENTATION"
    DATASET_FIELD_ASSOCIATIONS = "DATASET_FIELD_ASSOCIATIONS"
    DATASET_FIELD_STATISTICS = "DATASET_FIELD_STATISTICS"
    DATASET_INFO = "DATASET_INFO"
    DATASET_QUERY_HISTORY = "DATASET_QUERY_HISTORY"
    DATASET_SCHEMA = "DATASET_SCHEMA"
    DATASET_SODA_DATA_QUALITY = "DATASET_SODA_DATA_QUALITY"
    DATASET_STATISTICS = "DATASET_STATISTICS"
    DATASET_UPSTREAM = "DATASET_UPSTREAM"
    DATASET_USAGE = "DATASET_USAGE"
    DBT_METRIC = "DBT_METRIC"
    DBT_MODEL = "DBT_MODEL"
    ENTITY_UPSTREAM = "ENTITY_UPSTREAM"
    KNOWLEDGE_CARD_INFO = "KNOWLEDGE_CARD_INFO"
    KNOWLEDGE_CARD_VALIDATION = "KNOWLEDGE_CARD_VALIDATION"
    LOOKER_EXPLORE = "LOOKER_EXPLORE"
    LOOKER_VIEW = "LOOKER_VIEW"
    METRIC_INFO = "METRIC_INFO"
    NAMESPACE_ASSETS = "NAMESPACE_ASSETS"
    NAMESPACE_INFO = "NAMESPACE_INFO"
    PERSONALIZATION_OPTIONS = "PERSONALIZATION_OPTIONS"
    PERSON_ACTIVITY = "PERSON_ACTIVITY"
    PERSON_ORGANIZATION = "PERSON_ORGANIZATION"
    PERSON_PINS = "PERSON_PINS"
    PERSON_PROPERTIES = "PERSON_PROPERTIES"
    PERSON_SLACK_PROFILE = "PERSON_SLACK_PROFILE"
    PERSON_TEAMS_CONVERSION_REFERENCE = "PERSON_TEAMS_CONVERSION_REFERENCE"
    POWER_BI_DATASET = "POWER_BI_DATASET"
    SOURCE_INFO = "SOURCE_INFO"
    TABLEAU_DATASOURCE = "TABLEAU_DATASOURCE"
    THOUGHT_SPOT = "THOUGHT_SPOT"
    USER_DEFINED_RESOURCE_INFO = "USER_DEFINED_RESOURCE_INFO"


class ContactValueType(Enum):
    EMAIL = "EMAIL"
    PERSON = "PERSON"
    SLACK = "SLACK"
    UNKNOWN = "UNKNOWN"


@dataclass
class DesignatedContact:
    designation: Optional[str] = None
    value: Optional[str] = None
    value_type: Optional[ContactValueType] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DesignatedContact':
        assert isinstance(obj, dict)
        designation = from_union([from_str, from_none], obj.get("designation"))
        value = from_union([from_str, from_none], obj.get("value"))
        value_type = from_union([ContactValueType, from_none], obj.get("valueType"))
        return DesignatedContact(designation, value, value_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["designation"] = from_union([from_str, from_none], self.designation)
        result["value"] = from_union([from_str, from_none], self.value)
        result["valueType"] = from_union([lambda x: to_enum(ContactValueType, x), from_none], self.value_type)
        return result


@dataclass
class AuditStamp:
    """An AuditStamp containing creator and creation time attributes for the Aspect instance
    
    An AuditStamp containing modification and modifier attributes for the Aspect instance
    """
    actor: Optional[str] = None
    time: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AuditStamp':
        assert isinstance(obj, dict)
        actor = from_union([from_str, from_none], obj.get("actor"))
        time = from_union([from_datetime, from_none], obj.get("time"))
        return AuditStamp(actor, time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["actor"] = from_union([from_str, from_none], self.actor)
        result["time"] = from_union([lambda x: x.isoformat(), from_none], self.time)
        return result


@dataclass
class AssetContacts:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """Resolved on AssetContactResolver"""
    contacts: Optional[List[DesignatedContact]] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    asset_contacts_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetContacts':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        contacts = from_union([lambda x: from_list(DesignatedContact.from_dict, x), from_none], obj.get("contacts"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        asset_contacts_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        return AssetContacts(created_at, aspect_type, contacts, created, asset_contacts_created_at, entity_id, id, last_modified)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["contacts"] = from_union([lambda x: from_list(lambda x: to_class(DesignatedContact, x), x), from_none], self.contacts)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.asset_contacts_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        return result


@dataclass
class AssetFollowers:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    asset_followers_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    followed_by: Optional[List[str]] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetFollowers':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        asset_followers_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        followed_by = from_union([lambda x: from_list(from_str, x), from_none], obj.get("followedBy"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        return AssetFollowers(created_at, aspect_type, created, asset_followers_created_at, entity_id, followed_by, id, last_modified)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.asset_followers_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["followedBy"] = from_union([lambda x: from_list(from_str, x), from_none], self.followed_by)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        return result


@dataclass
class AssetGovernedTags:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    asset_governed_tags_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    governed_tag_ids: Optional[List[str]] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetGovernedTags':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        asset_governed_tags_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        governed_tag_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("governedTagIds"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        return AssetGovernedTags(created_at, aspect_type, created, asset_governed_tags_created_at, entity_id, governed_tag_ids, id, last_modified)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.asset_governed_tags_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["governedTagIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.governed_tag_ids)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        return result


class ChartType(Enum):
    AREA = "AREA"
    BAR = "BAR"
    BOX_PLOT = "BOX_PLOT"
    COLUMN = "COLUMN"
    DONUT = "DONUT"
    FUNNEL = "FUNNEL"
    LINE = "LINE"
    MAP = "MAP"
    OTHER = "OTHER"
    PIE = "PIE"
    SCATTER = "SCATTER"
    TABLE = "TABLE"
    TEXT = "TEXT"
    TIMELINE = "TIMELINE"
    UNKNOWN = "UNKNOWN"
    WATERFALL = "WATERFALL"


@dataclass
class Chart:
    chart_type: Optional[ChartType] = None
    description: Optional[str] = None
    preview: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Chart':
        assert isinstance(obj, dict)
        chart_type = from_union([ChartType, from_none], obj.get("chartType"))
        description = from_union([from_str, from_none], obj.get("description"))
        preview = from_union([from_str, from_none], obj.get("preview"))
        title = from_union([from_str, from_none], obj.get("title"))
        url = from_union([from_str, from_none], obj.get("url"))
        return Chart(chart_type, description, preview, title, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["chartType"] = from_union([lambda x: to_enum(ChartType, x), from_none], self.chart_type)
        result["description"] = from_union([from_str, from_none], self.description)
        result["preview"] = from_union([from_str, from_none], self.preview)
        result["title"] = from_union([from_str, from_none], self.title)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class PowerBIApp:
    id: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIApp':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        return PowerBIApp(id, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        return result


class PowerBIDashboardType(Enum):
    DASHBOARD = "DASHBOARD"
    REPORT = "REPORT"


@dataclass
class PowerBISensitivityLabel:
    description: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBISensitivityLabel':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        return PowerBISensitivityLabel(description, id, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class PowerBIWorkspace:
    id: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIWorkspace':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        return PowerBIWorkspace(id, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class PowerBIInfo:
    app: Optional[PowerBIApp] = None
    power_bi_dashboard_type: Optional[PowerBIDashboardType] = None
    sensitivity_label: Optional[PowerBISensitivityLabel] = None
    workspace: Optional[PowerBIWorkspace] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIInfo':
        assert isinstance(obj, dict)
        app = from_union([PowerBIApp.from_dict, from_none], obj.get("app"))
        power_bi_dashboard_type = from_union([PowerBIDashboardType, from_none], obj.get("powerBiDashboardType"))
        sensitivity_label = from_union([PowerBISensitivityLabel.from_dict, from_none], obj.get("sensitivityLabel"))
        workspace = from_union([PowerBIWorkspace.from_dict, from_none], obj.get("workspace"))
        return PowerBIInfo(app, power_bi_dashboard_type, sensitivity_label, workspace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["app"] = from_union([lambda x: to_class(PowerBIApp, x), from_none], self.app)
        result["powerBiDashboardType"] = from_union([lambda x: to_enum(PowerBIDashboardType, x), from_none], self.power_bi_dashboard_type)
        result["sensitivityLabel"] = from_union([lambda x: to_class(PowerBISensitivityLabel, x), from_none], self.sensitivity_label)
        result["workspace"] = from_union([lambda x: to_class(PowerBIWorkspace, x), from_none], self.workspace)
        return result


class ThoughtSpotDashboardType(Enum):
    ANSWER = "ANSWER"
    LIVEBOARD = "LIVEBOARD"
    UNKNOWN = "UNKNOWN"


@dataclass
class ThoughtSpotInfo:
    embed_url: Optional[str] = None
    tags: Optional[List[str]] = None
    type: Optional[ThoughtSpotDashboardType] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ThoughtSpotInfo':
        assert isinstance(obj, dict)
        embed_url = from_union([from_str, from_none], obj.get("embedUrl"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        type = from_union([ThoughtSpotDashboardType, from_none], obj.get("type"))
        return ThoughtSpotInfo(embed_url, tags, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["embedUrl"] = from_union([from_str, from_none], self.embed_url)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        result["type"] = from_union([lambda x: to_enum(ThoughtSpotDashboardType, x), from_none], self.type)
        return result


@dataclass
class DashboardInfo:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    charts: Optional[List[Chart]] = None
    dashboard_info_created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    power_bi: Optional[PowerBIInfo] = None
    thought_spot: Optional[ThoughtSpotInfo] = None
    title: Optional[str] = None
    view_count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DashboardInfo':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        charts = from_union([lambda x: from_list(Chart.from_dict, x), from_none], obj.get("charts"))
        dashboard_info_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        power_bi = from_union([PowerBIInfo.from_dict, from_none], obj.get("powerBi"))
        thought_spot = from_union([ThoughtSpotInfo.from_dict, from_none], obj.get("thoughtSpot"))
        title = from_union([from_str, from_none], obj.get("title"))
        view_count = from_union([from_float, from_none], obj.get("viewCount"))
        return DashboardInfo(created_at, aspect_type, charts, dashboard_info_created_at, description, entity_id, id, power_bi, thought_spot, title, view_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["charts"] = from_union([lambda x: from_list(lambda x: to_class(Chart, x), x), from_none], self.charts)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dashboard_info_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["powerBi"] = from_union([lambda x: to_class(PowerBIInfo, x), from_none], self.power_bi)
        result["thoughtSpot"] = from_union([lambda x: to_class(ThoughtSpotInfo, x), from_none], self.thought_spot)
        result["title"] = from_union([from_str, from_none], self.title)
        result["viewCount"] = from_union([to_float, from_none], self.view_count)
        return result


class EntityType(Enum):
    DASHBOARD = "DASHBOARD"
    DATASET = "DATASET"
    KNOWLEDGE_CARD = "KNOWLEDGE_CARD"
    METRIC = "METRIC"
    NAMESPACE = "NAMESPACE"
    PERSON = "PERSON"
    USER_DEFINED_RESOURCE = "USER_DEFINED_RESOURCE"
    VIRTUAL_VIEW = "VIRTUAL_VIEW"


class DataPlatform(Enum):
    BIGQUERY = "BIGQUERY"
    DOCUMENTDB = "DOCUMENTDB"
    DYNAMODB = "DYNAMODB"
    ELASTICSEARCH = "ELASTICSEARCH"
    EXTERNAL = "EXTERNAL"
    GLUE = "GLUE"
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    RDS = "RDS"
    REDIS = "REDIS"
    REDSHIFT = "REDSHIFT"
    S3 = "S3"
    SNOWFLAKE = "SNOWFLAKE"
    SYNAPSE = "SYNAPSE"
    UNITY_CATALOG = "UNITY_CATALOG"
    UNKNOWN = "UNKNOWN"


@dataclass
class DatasetLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    account: Optional[str] = None
    name: Optional[str] = None
    platform: Optional[DataPlatform] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetLogicalID':
        assert isinstance(obj, dict)
        account = from_union([from_str, from_none], obj.get("account"))
        name = from_union([from_str, from_none], obj.get("name"))
        platform = from_union([DataPlatform, from_none], obj.get("platform"))
        return DatasetLogicalID(account, name, platform)

    def to_dict(self) -> dict:
        result: dict = {}
        result["account"] = from_union([from_str, from_none], self.account)
        result["name"] = from_union([from_str, from_none], self.name)
        result["platform"] = from_union([lambda x: to_enum(DataPlatform, x), from_none], self.platform)
        return result


@dataclass
class SourceField:
    dataset: Optional[DatasetLogicalID] = None
    field: Optional[str] = None
    source_entity_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SourceField':
        assert isinstance(obj, dict)
        dataset = from_union([DatasetLogicalID.from_dict, from_none], obj.get("dataset"))
        field = from_union([from_str, from_none], obj.get("field"))
        source_entity_id = from_union([from_str, from_none], obj.get("sourceEntityId"))
        return SourceField(dataset, field, source_entity_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dataset"] = from_union([lambda x: to_class(DatasetLogicalID, x), from_none], self.dataset)
        result["field"] = from_union([from_str, from_none], self.field)
        result["sourceEntityId"] = from_union([from_str, from_none], self.source_entity_id)
        return result


@dataclass
class FieldMapping:
    destination: Optional[str] = None
    sources: Optional[List[SourceField]] = None
    transformation: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldMapping':
        assert isinstance(obj, dict)
        destination = from_union([from_str, from_none], obj.get("destination"))
        sources = from_union([lambda x: from_list(SourceField.from_dict, x), from_none], obj.get("sources"))
        transformation = from_union([from_str, from_none], obj.get("transformation"))
        return FieldMapping(destination, sources, transformation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["destination"] = from_union([from_str, from_none], self.destination)
        result["sources"] = from_union([lambda x: from_list(lambda x: to_class(SourceField, x), x), from_none], self.sources)
        result["transformation"] = from_union([from_str, from_none], self.transformation)
        return result


@dataclass
class FiveTranConnectorStatus:
    setup_state: Optional[str] = None
    sync_state: Optional[str] = None
    update_state: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FiveTranConnectorStatus':
        assert isinstance(obj, dict)
        setup_state = from_union([from_str, from_none], obj.get("setupState"))
        sync_state = from_union([from_str, from_none], obj.get("syncState"))
        update_state = from_union([from_str, from_none], obj.get("updateState"))
        return FiveTranConnectorStatus(setup_state, sync_state, update_state)

    def to_dict(self) -> dict:
        result: dict = {}
        result["setupState"] = from_union([from_str, from_none], self.setup_state)
        result["syncState"] = from_union([from_str, from_none], self.sync_state)
        result["updateState"] = from_union([from_str, from_none], self.update_state)
        return result


@dataclass
class FiveTranConnector:
    config: Optional[str] = None
    connector_logs_url: Optional[str] = None
    connector_name: Optional[str] = None
    connector_type_id: Optional[str] = None
    connector_type_name: Optional[str] = None
    connector_url: Optional[str] = None
    created_at: Optional[datetime] = None
    creator_email: Optional[str] = None
    icon_url: Optional[str] = None
    paused: Optional[bool] = None
    schema_metadata: Optional[str] = None
    source_entity_id: Optional[str] = None
    status: Optional[FiveTranConnectorStatus] = None
    succeeded_at: Optional[datetime] = None
    sync_interval_in_minute: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FiveTranConnector':
        assert isinstance(obj, dict)
        config = from_union([from_str, from_none], obj.get("config"))
        connector_logs_url = from_union([from_str, from_none], obj.get("connectorLogsUrl"))
        connector_name = from_union([from_str, from_none], obj.get("connectorName"))
        connector_type_id = from_union([from_str, from_none], obj.get("connectorTypeId"))
        connector_type_name = from_union([from_str, from_none], obj.get("connectorTypeName"))
        connector_url = from_union([from_str, from_none], obj.get("connectorUrl"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        creator_email = from_union([from_str, from_none], obj.get("creatorEmail"))
        icon_url = from_union([from_str, from_none], obj.get("iconUrl"))
        paused = from_union([from_bool, from_none], obj.get("paused"))
        schema_metadata = from_union([from_str, from_none], obj.get("schemaMetadata"))
        source_entity_id = from_union([from_str, from_none], obj.get("sourceEntityId"))
        status = from_union([FiveTranConnectorStatus.from_dict, from_none], obj.get("status"))
        succeeded_at = from_union([from_datetime, from_none], obj.get("succeededAt"))
        sync_interval_in_minute = from_union([from_float, from_none], obj.get("syncIntervalInMinute"))
        return FiveTranConnector(config, connector_logs_url, connector_name, connector_type_id, connector_type_name, connector_url, created_at, creator_email, icon_url, paused, schema_metadata, source_entity_id, status, succeeded_at, sync_interval_in_minute)

    def to_dict(self) -> dict:
        result: dict = {}
        result["config"] = from_union([from_str, from_none], self.config)
        result["connectorLogsUrl"] = from_union([from_str, from_none], self.connector_logs_url)
        result["connectorName"] = from_union([from_str, from_none], self.connector_name)
        result["connectorTypeId"] = from_union([from_str, from_none], self.connector_type_id)
        result["connectorTypeName"] = from_union([from_str, from_none], self.connector_type_name)
        result["connectorUrl"] = from_union([from_str, from_none], self.connector_url)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["creatorEmail"] = from_union([from_str, from_none], self.creator_email)
        result["iconUrl"] = from_union([from_str, from_none], self.icon_url)
        result["paused"] = from_union([from_bool, from_none], self.paused)
        result["schemaMetadata"] = from_union([from_str, from_none], self.schema_metadata)
        result["sourceEntityId"] = from_union([from_str, from_none], self.source_entity_id)
        result["status"] = from_union([lambda x: to_class(FiveTranConnectorStatus, x), from_none], self.status)
        result["succeededAt"] = from_union([lambda x: x.isoformat(), from_none], self.succeeded_at)
        result["syncIntervalInMinute"] = from_union([to_float, from_none], self.sync_interval_in_minute)
        return result


@dataclass
class EntityUpstream:
    """EntityUpstream captures upstream lineages from data sources to this entity"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    entity_upstream_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    executor_url: Optional[str] = None
    field_mappings: Optional[List[FieldMapping]] = None
    five_tran_connector: Optional[FiveTranConnector] = None
    id: Optional[str] = None
    source_code_url: Optional[str] = None
    source_entities: Optional[List[str]] = None
    transformation: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'EntityUpstream':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        entity_upstream_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        executor_url = from_union([from_str, from_none], obj.get("executorUrl"))
        field_mappings = from_union([lambda x: from_list(FieldMapping.from_dict, x), from_none], obj.get("fieldMappings"))
        five_tran_connector = from_union([FiveTranConnector.from_dict, from_none], obj.get("fiveTranConnector"))
        id = from_union([from_str, from_none], obj.get("id"))
        source_code_url = from_union([from_str, from_none], obj.get("sourceCodeUrl"))
        source_entities = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceEntities"))
        transformation = from_union([from_str, from_none], obj.get("transformation"))
        return EntityUpstream(created_at, aspect_type, entity_upstream_created_at, entity_id, executor_url, field_mappings, five_tran_connector, id, source_code_url, source_entities, transformation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.entity_upstream_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["executorUrl"] = from_union([from_str, from_none], self.executor_url)
        result["fieldMappings"] = from_union([lambda x: from_list(lambda x: to_class(FieldMapping, x), x), from_none], self.field_mappings)
        result["fiveTranConnector"] = from_union([lambda x: to_class(FiveTranConnector, x), from_none], self.five_tran_connector)
        result["id"] = from_union([from_str, from_none], self.id)
        result["sourceCodeUrl"] = from_union([from_str, from_none], self.source_code_url)
        result["sourceEntities"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_entities)
        result["transformation"] = from_union([from_str, from_none], self.transformation)
        return result


class Bsontype(Enum):
    OBJECT_ID = "ObjectID"


@dataclass
class ID:
    """The ObjectId bytes"""
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'ID':
        assert isinstance(obj, dict)
        return ID()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class ObjectID:
    """Native Mongo db BSON id instance
    
    A class representation of the BSON ObjectId type.
    """
    bsontype: Optional[Bsontype] = None
    """The generation time of this ObjectId instance"""
    generation_time: Optional[float] = None
    """The ObjectId bytes"""
    id: Optional[ID] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ObjectID':
        assert isinstance(obj, dict)
        bsontype = from_union([Bsontype, from_none], obj.get("_bsontype"))
        generation_time = from_union([from_float, from_none], obj.get("generationTime"))
        id = from_union([ID.from_dict, from_none], obj.get("id"))
        return ObjectID(bsontype, generation_time, id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_bsontype"] = from_union([lambda x: to_enum(Bsontype, x), from_none], self.bsontype)
        result["generationTime"] = from_union([to_float, from_none], self.generation_time)
        result["id"] = from_union([lambda x: to_class(ID, x), from_none], self.id)
        return result


class DashboardPlatform(Enum):
    LOOKER = "LOOKER"
    METABASE = "METABASE"
    POWER_BI = "POWER_BI"
    TABLEAU = "TABLEAU"
    THOUGHT_SPOT = "THOUGHT_SPOT"
    UNKNOWN = "UNKNOWN"


@dataclass
class DashboardLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    dashboard_id: Optional[str] = None
    platform: Optional[DashboardPlatform] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DashboardLogicalID':
        assert isinstance(obj, dict)
        dashboard_id = from_union([from_str, from_none], obj.get("dashboardId"))
        platform = from_union([DashboardPlatform, from_none], obj.get("platform"))
        return DashboardLogicalID(dashboard_id, platform)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dashboardId"] = from_union([from_str, from_none], self.dashboard_id)
        result["platform"] = from_union([lambda x: to_enum(DashboardPlatform, x), from_none], self.platform)
        return result


@dataclass
class SourceInfo:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    source_info_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    main_url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SourceInfo':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        source_info_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        main_url = from_union([from_str, from_none], obj.get("mainUrl"))
        return SourceInfo(created_at, aspect_type, source_info_created_at, entity_id, id, main_url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.source_info_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["mainUrl"] = from_union([from_str, from_none], self.main_url)
        return result


@dataclass
class DashboardUpstream:
    """DashboardUpstream captures upstream lineages from data sources to this dashboard"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dashboard_upstream_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    source_virtual_views: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DashboardUpstream':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dashboard_upstream_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        source_virtual_views = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceVirtualViews"))
        return DashboardUpstream(created_at, aspect_type, dashboard_upstream_created_at, entity_id, id, source_datasets, source_virtual_views)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dashboard_upstream_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["sourceVirtualViews"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_virtual_views)
        return result


@dataclass
class Dashboard:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """Native Mongo db BSON id instance"""
    id: Optional[ObjectID] = None
    """Optional protected internal field to store a versionId of the entity, if the instance is
    versioned
    """
    versioned_id: Optional[str] = None
    asset_contacts: Optional[AssetContacts] = None
    asset_followers: Optional[AssetFollowers] = None
    asset_governed_tags: Optional[AssetGovernedTags] = None
    dashboard_created_at: Optional[datetime] = None
    dashboard_info: Optional[DashboardInfo] = None
    deleted_at: Optional[datetime] = None
    display_name: Optional[str] = None
    entity_type: Optional[EntityType] = None
    """EntityUpstream captures upstream lineages from data sources to this entity"""
    entity_upstream: Optional[EntityUpstream] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    dashboard_id: Optional[str] = None
    last_ingested_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[DashboardLogicalID] = None
    source_info: Optional[SourceInfo] = None
    """DashboardUpstream captures upstream lineages from data sources to this dashboard"""
    upstream: Optional[DashboardUpstream] = None
    """Write-only api to set a versionId of the entity, if the instance is versioned
    This allows the versionedId to be maintained on the entity e.g. when an instance is
    created by the factory
    """
    dashboard_versioned_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Dashboard':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        versioned_id = from_union([from_str, from_none], obj.get("_versionedId"))
        asset_contacts = from_union([AssetContacts.from_dict, from_none], obj.get("assetContacts"))
        asset_followers = from_union([AssetFollowers.from_dict, from_none], obj.get("assetFollowers"))
        asset_governed_tags = from_union([AssetGovernedTags.from_dict, from_none], obj.get("assetGovernedTags"))
        dashboard_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dashboard_info = from_union([DashboardInfo.from_dict, from_none], obj.get("dashboardInfo"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        entity_upstream = from_union([EntityUpstream.from_dict, from_none], obj.get("entityUpstream"))
        dashboard_id = from_union([from_str, from_none], obj.get("id"))
        last_ingested_at = from_union([from_datetime, from_none], obj.get("lastIngestedAt"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([DashboardLogicalID.from_dict, from_none], obj.get("logicalId"))
        source_info = from_union([SourceInfo.from_dict, from_none], obj.get("sourceInfo"))
        upstream = from_union([DashboardUpstream.from_dict, from_none], obj.get("upstream"))
        dashboard_versioned_id = from_union([from_str, from_none], obj.get("versionedId"))
        return Dashboard(created_at, id, versioned_id, asset_contacts, asset_followers, asset_governed_tags, dashboard_created_at, dashboard_info, deleted_at, display_name, entity_type, entity_upstream, dashboard_id, last_ingested_at, last_modified_at, logical_id, source_info, upstream, dashboard_versioned_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_versionedId"] = from_union([from_str, from_none], self.versioned_id)
        result["assetContacts"] = from_union([lambda x: to_class(AssetContacts, x), from_none], self.asset_contacts)
        result["assetFollowers"] = from_union([lambda x: to_class(AssetFollowers, x), from_none], self.asset_followers)
        result["assetGovernedTags"] = from_union([lambda x: to_class(AssetGovernedTags, x), from_none], self.asset_governed_tags)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dashboard_created_at)
        result["dashboardInfo"] = from_union([lambda x: to_class(DashboardInfo, x), from_none], self.dashboard_info)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["entityUpstream"] = from_union([lambda x: to_class(EntityUpstream, x), from_none], self.entity_upstream)
        result["id"] = from_union([from_str, from_none], self.dashboard_id)
        result["lastIngestedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_ingested_at)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(DashboardLogicalID, x), from_none], self.logical_id)
        result["sourceInfo"] = from_union([lambda x: to_class(SourceInfo, x), from_none], self.source_info)
        result["upstream"] = from_union([lambda x: to_class(DashboardUpstream, x), from_none], self.upstream)
        result["versionedId"] = from_union([from_str, from_none], self.dashboard_versioned_id)
        return result


@dataclass
class CustomMetadataItem:
    """A single key-value pair entry for the custom metadata"""
    key: Optional[str] = None
    value: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'CustomMetadataItem':
        assert isinstance(obj, dict)
        key = from_union([from_str, from_none], obj.get("key"))
        value = from_union([from_str, from_none], obj.get("value"))
        return CustomMetadataItem(key, value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["key"] = from_union([from_str, from_none], self.key)
        result["value"] = from_union([from_str, from_none], self.value)
        return result


@dataclass
class CustomMetadata:
    """Captures custom metadata for an asset"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    custom_metadata_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None
    metadata: Optional[List[CustomMetadataItem]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'CustomMetadata':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        custom_metadata_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        metadata = from_union([lambda x: from_list(CustomMetadataItem.from_dict, x), from_none], obj.get("metadata"))
        return CustomMetadata(created_at, aspect_type, created, custom_metadata_created_at, entity_id, id, last_modified, metadata)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.custom_metadata_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["metadata"] = from_union([lambda x: from_list(lambda x: to_class(CustomMetadataItem, x), x), from_none], self.metadata)
        return result


class DataMonitorSeverity(Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    UNKNOWN = "UNKNOWN"


class DataMonitorStatus(Enum):
    ERROR = "ERROR"
    PASSED = "PASSED"
    UNKNOWN = "UNKNOWN"
    WARNING = "WARNING"


@dataclass
class DataMonitorTarget:
    column: Optional[str] = None
    dataset: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DataMonitorTarget':
        assert isinstance(obj, dict)
        column = from_union([from_str, from_none], obj.get("column"))
        dataset = from_union([from_str, from_none], obj.get("dataset"))
        return DataMonitorTarget(column, dataset)

    def to_dict(self) -> dict:
        result: dict = {}
        result["column"] = from_union([from_str, from_none], self.column)
        result["dataset"] = from_union([from_str, from_none], self.dataset)
        return result


@dataclass
class DataMonitor:
    description: Optional[str] = None
    last_run: Optional[datetime] = None
    owner: Optional[str] = None
    severity: Optional[DataMonitorSeverity] = None
    status: Optional[DataMonitorStatus] = None
    targets: Optional[List[DataMonitorTarget]] = None
    title: Optional[str] = None
    url: Optional[str] = None
    value: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DataMonitor':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        last_run = from_union([from_datetime, from_none], obj.get("lastRun"))
        owner = from_union([from_str, from_none], obj.get("owner"))
        severity = from_union([DataMonitorSeverity, from_none], obj.get("severity"))
        status = from_union([DataMonitorStatus, from_none], obj.get("status"))
        targets = from_union([lambda x: from_list(DataMonitorTarget.from_dict, x), from_none], obj.get("targets"))
        title = from_union([from_str, from_none], obj.get("title"))
        url = from_union([from_str, from_none], obj.get("url"))
        value = from_union([from_float, from_none], obj.get("value"))
        return DataMonitor(description, last_run, owner, severity, status, targets, title, url, value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["lastRun"] = from_union([lambda x: x.isoformat(), from_none], self.last_run)
        result["owner"] = from_union([from_str, from_none], self.owner)
        result["severity"] = from_union([lambda x: to_enum(DataMonitorSeverity, x), from_none], self.severity)
        result["status"] = from_union([lambda x: to_enum(DataMonitorStatus, x), from_none], self.status)
        result["targets"] = from_union([lambda x: from_list(lambda x: to_class(DataMonitorTarget, x), x), from_none], self.targets)
        result["title"] = from_union([from_str, from_none], self.title)
        result["url"] = from_union([from_str, from_none], self.url)
        result["value"] = from_union([to_float, from_none], self.value)
        return result


class DataQualityProvider(Enum):
    BIGEYE = "BIGEYE"
    LIGHTUP = "LIGHTUP"
    MONTE_CARLO = "MONTE_CARLO"
    SODA = "SODA"
    UNKNOWN = "UNKNOWN"


@dataclass
class DatasetDataQuality:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_data_quality_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    monitors: Optional[List[DataMonitor]] = None
    provider: Optional[DataQualityProvider] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetDataQuality':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_data_quality_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        monitors = from_union([lambda x: from_list(DataMonitor.from_dict, x), from_none], obj.get("monitors"))
        provider = from_union([DataQualityProvider, from_none], obj.get("provider"))
        url = from_union([from_str, from_none], obj.get("url"))
        return DatasetDataQuality(created_at, aspect_type, dataset_data_quality_created_at, entity_id, id, monitors, provider, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_data_quality_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["monitors"] = from_union([lambda x: from_list(lambda x: to_class(DataMonitor, x), x), from_none], self.monitors)
        result["provider"] = from_union([lambda x: to_enum(DataQualityProvider, x), from_none], self.provider)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class AssetDescription:
    author: Optional[str] = None
    description: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetDescription':
        assert isinstance(obj, dict)
        author = from_union([from_str, from_none], obj.get("author"))
        description = from_union([from_str, from_none], obj.get("description"))
        return AssetDescription(author, description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["author"] = from_union([from_str, from_none], self.author)
        result["description"] = from_union([from_str, from_none], self.description)
        return result


@dataclass
class DescriptionAssignment:
    asset_descriptions: Optional[List[AssetDescription]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DescriptionAssignment':
        assert isinstance(obj, dict)
        asset_descriptions = from_union([lambda x: from_list(AssetDescription.from_dict, x), from_none], obj.get("assetDescriptions"))
        return DescriptionAssignment(asset_descriptions)

    def to_dict(self) -> dict:
        result: dict = {}
        result["assetDescriptions"] = from_union([lambda x: from_list(lambda x: to_class(AssetDescription, x), x), from_none], self.asset_descriptions)
        return result


@dataclass
class FieldDocumentation:
    documentation: Optional[str] = None
    field_path: Optional[str] = None
    tests: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldDocumentation':
        assert isinstance(obj, dict)
        documentation = from_union([from_str, from_none], obj.get("documentation"))
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        tests = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tests"))
        return FieldDocumentation(documentation, field_path, tests)

    def to_dict(self) -> dict:
        result: dict = {}
        result["documentation"] = from_union([from_str, from_none], self.documentation)
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["tests"] = from_union([lambda x: from_list(from_str, x), from_none], self.tests)
        return result


@dataclass
class DatasetDocumentation:
    """Captures dataset documentations from other tools outside the data source, e.g. dbt
    documentation on source datasets
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_documentation_created_at: Optional[datetime] = None
    dataset_documentations: Optional[List[str]] = None
    entity_id: Optional[str] = None
    field_documentations: Optional[List[FieldDocumentation]] = None
    id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetDocumentation':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_documentation_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dataset_documentations = from_union([lambda x: from_list(from_str, x), from_none], obj.get("datasetDocumentations"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        field_documentations = from_union([lambda x: from_list(FieldDocumentation.from_dict, x), from_none], obj.get("fieldDocumentations"))
        id = from_union([from_str, from_none], obj.get("id"))
        return DatasetDocumentation(created_at, aspect_type, dataset_documentation_created_at, dataset_documentations, entity_id, field_documentations, id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_documentation_created_at)
        result["datasetDocumentations"] = from_union([lambda x: from_list(from_str, x), from_none], self.dataset_documentations)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fieldDocumentations"] = from_union([lambda x: from_list(lambda x: to_class(FieldDocumentation, x), x), from_none], self.field_documentations)
        result["id"] = from_union([from_str, from_none], self.id)
        return result


@dataclass
class FieldTagAssociations:
    field_path: Optional[str] = None
    """Stores Entity IDs for the Governed Tags that are associated with this schema field"""
    governed_tag_ids: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldTagAssociations':
        assert isinstance(obj, dict)
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        governed_tag_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("governedTagIds"))
        return FieldTagAssociations(field_path, governed_tag_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["governedTagIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.governed_tag_ids)
        return result


@dataclass
class DatasetFieldAssociations:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    dataset_field_associations_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    governed_tag_fields: Optional[List[FieldTagAssociations]] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetFieldAssociations':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        dataset_field_associations_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        governed_tag_fields = from_union([lambda x: from_list(FieldTagAssociations.from_dict, x), from_none], obj.get("governedTagFields"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        return DatasetFieldAssociations(created_at, aspect_type, created, dataset_field_associations_created_at, entity_id, governed_tag_fields, id, last_modified)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_field_associations_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["governedTagFields"] = from_union([lambda x: from_list(lambda x: to_class(FieldTagAssociations, x), x), from_none], self.governed_tag_fields)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        return result


@dataclass
class FieldStatistics:
    """The statistics of a field/column, e.g. values count, min/max/avg, etc',"""
    average: Optional[float] = None
    distinct_value_count: Optional[float] = None
    field_path: Optional[str] = None
    max_value: Optional[float] = None
    min_value: Optional[float] = None
    nonnull_value_count: Optional[float] = None
    null_value_count: Optional[float] = None
    std_dev: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldStatistics':
        assert isinstance(obj, dict)
        average = from_union([from_float, from_none], obj.get("average"))
        distinct_value_count = from_union([from_float, from_none], obj.get("distinctValueCount"))
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        max_value = from_union([from_float, from_none], obj.get("maxValue"))
        min_value = from_union([from_float, from_none], obj.get("minValue"))
        nonnull_value_count = from_union([from_float, from_none], obj.get("nonnullValueCount"))
        null_value_count = from_union([from_float, from_none], obj.get("nullValueCount"))
        std_dev = from_union([from_float, from_none], obj.get("stdDev"))
        return FieldStatistics(average, distinct_value_count, field_path, max_value, min_value, nonnull_value_count, null_value_count, std_dev)

    def to_dict(self) -> dict:
        result: dict = {}
        result["average"] = from_union([to_float, from_none], self.average)
        result["distinctValueCount"] = from_union([to_float, from_none], self.distinct_value_count)
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["maxValue"] = from_union([to_float, from_none], self.max_value)
        result["minValue"] = from_union([to_float, from_none], self.min_value)
        result["nonnullValueCount"] = from_union([to_float, from_none], self.nonnull_value_count)
        result["nullValueCount"] = from_union([to_float, from_none], self.null_value_count)
        result["stdDev"] = from_union([to_float, from_none], self.std_dev)
        return result


@dataclass
class DatasetFieldStatistics:
    """DatasetStatistics captures operational information about the dataset, e.g. the number of
    records or the last refresh time.
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_field_statistics_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    field_statistics: Optional[List[FieldStatistics]] = None
    id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetFieldStatistics':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_field_statistics_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        field_statistics = from_union([lambda x: from_list(FieldStatistics.from_dict, x), from_none], obj.get("fieldStatistics"))
        id = from_union([from_str, from_none], obj.get("id"))
        return DatasetFieldStatistics(created_at, aspect_type, dataset_field_statistics_created_at, entity_id, field_statistics, id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_field_statistics_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fieldStatistics"] = from_union([lambda x: from_list(lambda x: to_class(FieldStatistics, x), x), from_none], self.field_statistics)
        result["id"] = from_union([from_str, from_none], self.id)
        return result


@dataclass
class Ownership:
    contact_designation_name: Optional[str] = None
    person: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Ownership':
        assert isinstance(obj, dict)
        contact_designation_name = from_union([from_str, from_none], obj.get("contactDesignationName"))
        person = from_union([from_str, from_none], obj.get("person"))
        return Ownership(contact_designation_name, person)

    def to_dict(self) -> dict:
        result: dict = {}
        result["contactDesignationName"] = from_union([from_str, from_none], self.contact_designation_name)
        result["person"] = from_union([from_str, from_none], self.person)
        return result


@dataclass
class OwnershipAssignment:
    ownerships: Optional[List[Ownership]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'OwnershipAssignment':
        assert isinstance(obj, dict)
        ownerships = from_union([lambda x: from_list(Ownership.from_dict, x), from_none], obj.get("ownerships"))
        return OwnershipAssignment(ownerships)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ownerships"] = from_union([lambda x: from_list(lambda x: to_class(Ownership, x), x), from_none], self.ownerships)
        return result


@dataclass
class QueryInfo:
    """Captures the information associated with a specific query."""
    elapsed_time: Optional[float] = None
    issued_at: Optional[datetime] = None
    issued_by: Optional[str] = None
    query: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryInfo':
        assert isinstance(obj, dict)
        elapsed_time = from_union([from_float, from_none], obj.get("elapsedTime"))
        issued_at = from_union([from_datetime, from_none], obj.get("issuedAt"))
        issued_by = from_union([from_str, from_none], obj.get("issuedBy"))
        query = from_union([from_str, from_none], obj.get("query"))
        return QueryInfo(elapsed_time, issued_at, issued_by, query)

    def to_dict(self) -> dict:
        result: dict = {}
        result["elapsedTime"] = from_union([to_float, from_none], self.elapsed_time)
        result["issuedAt"] = from_union([lambda x: x.isoformat(), from_none], self.issued_at)
        result["issuedBy"] = from_union([from_str, from_none], self.issued_by)
        result["query"] = from_union([from_str, from_none], self.query)
        return result


@dataclass
class DatasetQueryHistory:
    """A dataset's query history"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_query_history_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    recent_queries: Optional[List[QueryInfo]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetQueryHistory':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_query_history_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        recent_queries = from_union([lambda x: from_list(QueryInfo.from_dict, x), from_none], obj.get("recentQueries"))
        return DatasetQueryHistory(created_at, aspect_type, dataset_query_history_created_at, entity_id, id, recent_queries)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_query_history_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["recentQueries"] = from_union([lambda x: from_list(lambda x: to_class(QueryInfo, x), x), from_none], self.recent_queries)
        return result


@dataclass
class SchemaField:
    subfields: Union[List['SchemaField'], 'SchemaField', None]
    description: Optional[str] = None
    field_name: Optional[str] = None
    field_path: Optional[str] = None
    is_unique: Optional[bool] = None
    max_length: Optional[float] = None
    native_type: Optional[str] = None
    nullable: Optional[bool] = None
    precision: Optional[float] = None
    tags: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SchemaField':
        assert isinstance(obj, dict)
        subfields = from_union([SchemaField.from_dict, lambda x: from_list(SchemaField.from_dict, x), from_none], obj.get("subfields"))
        description = from_union([from_str, from_none], obj.get("description"))
        field_name = from_union([from_str, from_none], obj.get("fieldName"))
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        is_unique = from_union([from_bool, from_none], obj.get("isUnique"))
        max_length = from_union([from_float, from_none], obj.get("maxLength"))
        native_type = from_union([from_str, from_none], obj.get("nativeType"))
        nullable = from_union([from_bool, from_none], obj.get("nullable"))
        precision = from_union([from_float, from_none], obj.get("precision"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        return SchemaField(subfields, description, field_name, field_path, is_unique, max_length, native_type, nullable, precision, tags)

    def to_dict(self) -> dict:
        result: dict = {}
        result["subfields"] = from_union([lambda x: to_class(SchemaField, x), lambda x: from_list(lambda x: to_class(SchemaField, x), x), from_none], self.subfields)
        result["description"] = from_union([from_str, from_none], self.description)
        result["fieldName"] = from_union([from_str, from_none], self.field_name)
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["isUnique"] = from_union([from_bool, from_none], self.is_unique)
        result["maxLength"] = from_union([to_float, from_none], self.max_length)
        result["nativeType"] = from_union([from_str, from_none], self.native_type)
        result["nullable"] = from_union([from_bool, from_none], self.nullable)
        result["precision"] = from_union([to_float, from_none], self.precision)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        return result


class SchemaType(Enum):
    AVRO = "AVRO"
    DYNAMODB = "DYNAMODB"
    JSON = "JSON"
    ORC = "ORC"
    PARQUET = "PARQUET"
    PROTOBUF = "PROTOBUF"
    SCHEMALESS = "SCHEMALESS"
    SQL = "SQL"


@dataclass
class ForeignKey:
    field_path: Optional[str] = None
    parent: Optional[DatasetLogicalID] = None
    parent_field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ForeignKey':
        assert isinstance(obj, dict)
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        parent = from_union([DatasetLogicalID.from_dict, from_none], obj.get("parent"))
        parent_field = from_union([from_str, from_none], obj.get("parentField"))
        return ForeignKey(field_path, parent, parent_field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["parent"] = from_union([lambda x: to_class(DatasetLogicalID, x), from_none], self.parent)
        result["parentField"] = from_union([from_str, from_none], self.parent_field)
        return result


class MaterializationType(Enum):
    EXTERNAL = "EXTERNAL"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    TABLE = "TABLE"
    VIEW = "VIEW"


@dataclass
class SQLSchema:
    foreign_key: Optional[List[ForeignKey]] = None
    materialization: Optional[MaterializationType] = None
    primary_key: Optional[List[str]] = None
    table_schema: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SQLSchema':
        assert isinstance(obj, dict)
        foreign_key = from_union([lambda x: from_list(ForeignKey.from_dict, x), from_none], obj.get("foreignKey"))
        materialization = from_union([MaterializationType, from_none], obj.get("materialization"))
        primary_key = from_union([lambda x: from_list(from_str, x), from_none], obj.get("primaryKey"))
        table_schema = from_union([from_str, from_none], obj.get("tableSchema"))
        return SQLSchema(foreign_key, materialization, primary_key, table_schema)

    def to_dict(self) -> dict:
        result: dict = {}
        result["foreignKey"] = from_union([lambda x: from_list(lambda x: to_class(ForeignKey, x), x), from_none], self.foreign_key)
        result["materialization"] = from_union([lambda x: to_enum(MaterializationType, x), from_none], self.materialization)
        result["primaryKey"] = from_union([lambda x: from_list(from_str, x), from_none], self.primary_key)
        result["tableSchema"] = from_union([from_str, from_none], self.table_schema)
        return result


@dataclass
class DatasetSchema:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_schema_created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    fields: Optional[List[SchemaField]] = None
    id: Optional[str] = None
    last_modified: Optional[AuditStamp] = None
    schema_type: Optional[SchemaType] = None
    sql_schema: Optional[SQLSchema] = None
    tags: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetSchema':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_schema_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        fields = from_union([lambda x: from_list(SchemaField.from_dict, x), from_none], obj.get("fields"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        schema_type = from_union([SchemaType, from_none], obj.get("schemaType"))
        sql_schema = from_union([SQLSchema.from_dict, from_none], obj.get("sqlSchema"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        return DatasetSchema(created_at, aspect_type, dataset_schema_created_at, description, entity_id, fields, id, last_modified, schema_type, sql_schema, tags)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_schema_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fields"] = from_union([lambda x: from_list(lambda x: to_class(SchemaField, x), x), from_none], self.fields)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["schemaType"] = from_union([lambda x: to_enum(SchemaType, x), from_none], self.schema_type)
        result["sqlSchema"] = from_union([lambda x: to_class(SQLSchema, x), from_none], self.sql_schema)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        return result


@dataclass
class SodaDataMonitorTarget:
    column: Optional[str] = None
    dataset: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SodaDataMonitorTarget':
        assert isinstance(obj, dict)
        column = from_union([from_str, from_none], obj.get("column"))
        dataset = from_union([from_str, from_none], obj.get("dataset"))
        return SodaDataMonitorTarget(column, dataset)

    def to_dict(self) -> dict:
        result: dict = {}
        result["column"] = from_union([from_str, from_none], self.column)
        result["dataset"] = from_union([from_str, from_none], self.dataset)
        return result


@dataclass
class SodaDataMonitor:
    last_run: Optional[datetime] = None
    owner: Optional[str] = None
    status: Optional[DataMonitorStatus] = None
    targets: Optional[List[SodaDataMonitorTarget]] = None
    title: Optional[str] = None
    value: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SodaDataMonitor':
        assert isinstance(obj, dict)
        last_run = from_union([from_datetime, from_none], obj.get("lastRun"))
        owner = from_union([from_str, from_none], obj.get("owner"))
        status = from_union([DataMonitorStatus, from_none], obj.get("status"))
        targets = from_union([lambda x: from_list(SodaDataMonitorTarget.from_dict, x), from_none], obj.get("targets"))
        title = from_union([from_str, from_none], obj.get("title"))
        value = from_union([from_float, from_none], obj.get("value"))
        return SodaDataMonitor(last_run, owner, status, targets, title, value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["lastRun"] = from_union([lambda x: x.isoformat(), from_none], self.last_run)
        result["owner"] = from_union([from_str, from_none], self.owner)
        result["status"] = from_union([lambda x: to_enum(DataMonitorStatus, x), from_none], self.status)
        result["targets"] = from_union([lambda x: from_list(lambda x: to_class(SodaDataMonitorTarget, x), x), from_none], self.targets)
        result["title"] = from_union([from_str, from_none], self.title)
        result["value"] = from_union([to_float, from_none], self.value)
        return result


@dataclass
class SodaDataProfileMetrics:
    distinct: Optional[float] = None
    invalid: Optional[float] = None
    maximum: Optional[float] = None
    mean: Optional[float] = None
    minimum: Optional[float] = None
    missing: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SodaDataProfileMetrics':
        assert isinstance(obj, dict)
        distinct = from_union([from_float, from_none], obj.get("distinct"))
        invalid = from_union([from_float, from_none], obj.get("invalid"))
        maximum = from_union([from_float, from_none], obj.get("maximum"))
        mean = from_union([from_float, from_none], obj.get("mean"))
        minimum = from_union([from_float, from_none], obj.get("minimum"))
        missing = from_union([from_float, from_none], obj.get("missing"))
        return SodaDataProfileMetrics(distinct, invalid, maximum, mean, minimum, missing)

    def to_dict(self) -> dict:
        result: dict = {}
        result["distinct"] = from_union([to_float, from_none], self.distinct)
        result["invalid"] = from_union([to_float, from_none], self.invalid)
        result["maximum"] = from_union([to_float, from_none], self.maximum)
        result["mean"] = from_union([to_float, from_none], self.mean)
        result["minimum"] = from_union([to_float, from_none], self.minimum)
        result["missing"] = from_union([to_float, from_none], self.missing)
        return result


@dataclass
class SodaDataProfile:
    column: Optional[str] = None
    last_run: Optional[datetime] = None
    metrics: Optional[SodaDataProfileMetrics] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SodaDataProfile':
        assert isinstance(obj, dict)
        column = from_union([from_str, from_none], obj.get("column"))
        last_run = from_union([from_datetime, from_none], obj.get("lastRun"))
        metrics = from_union([SodaDataProfileMetrics.from_dict, from_none], obj.get("metrics"))
        return SodaDataProfile(column, last_run, metrics)

    def to_dict(self) -> dict:
        result: dict = {}
        result["column"] = from_union([from_str, from_none], self.column)
        result["lastRun"] = from_union([lambda x: x.isoformat(), from_none], self.last_run)
        result["metrics"] = from_union([lambda x: to_class(SodaDataProfileMetrics, x), from_none], self.metrics)
        return result


@dataclass
class DatasetSodaDataQuality:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_soda_data_quality_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    monitors: Optional[List[SodaDataMonitor]] = None
    profiles: Optional[List[SodaDataProfile]] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetSodaDataQuality':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_soda_data_quality_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        monitors = from_union([lambda x: from_list(SodaDataMonitor.from_dict, x), from_none], obj.get("monitors"))
        profiles = from_union([lambda x: from_list(SodaDataProfile.from_dict, x), from_none], obj.get("profiles"))
        url = from_union([from_str, from_none], obj.get("url"))
        return DatasetSodaDataQuality(created_at, aspect_type, dataset_soda_data_quality_created_at, entity_id, id, monitors, profiles, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_soda_data_quality_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["monitors"] = from_union([lambda x: from_list(lambda x: to_class(SodaDataMonitor, x), x), from_none], self.monitors)
        result["profiles"] = from_union([lambda x: from_list(lambda x: to_class(SodaDataProfile, x), x), from_none], self.profiles)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class DatasetStatistics:
    """DatasetStatistics captures operational information about the dataset, e.g. the number of
    records or the last refresh time.
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_statistics_created_at: Optional[datetime] = None
    data_size_bytes: Optional[float] = None
    entity_id: Optional[str] = None
    field_statistics: Optional[List[FieldStatistics]] = None
    id: Optional[str] = None
    last_updated: Optional[datetime] = None
    record_count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetStatistics':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_statistics_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        data_size_bytes = from_union([from_float, from_none], obj.get("dataSizeBytes"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        field_statistics = from_union([lambda x: from_list(FieldStatistics.from_dict, x), from_none], obj.get("fieldStatistics"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_updated = from_union([from_datetime, from_none], obj.get("lastUpdated"))
        record_count = from_union([from_float, from_none], obj.get("recordCount"))
        return DatasetStatistics(created_at, aspect_type, dataset_statistics_created_at, data_size_bytes, entity_id, field_statistics, id, last_updated, record_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_statistics_created_at)
        result["dataSizeBytes"] = from_union([to_float, from_none], self.data_size_bytes)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fieldStatistics"] = from_union([lambda x: from_list(lambda x: to_class(FieldStatistics, x), x), from_none], self.field_statistics)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastUpdated"] = from_union([lambda x: x.isoformat(), from_none], self.last_updated)
        result["recordCount"] = from_union([to_float, from_none], self.record_count)
        return result


@dataclass
class DatasetStructure:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_structure_created_at: Optional[datetime] = None
    database: Optional[str] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetStructure':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_structure_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        database = from_union([from_str, from_none], obj.get("database"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        schema = from_union([from_str, from_none], obj.get("schema"))
        table = from_union([from_str, from_none], obj.get("table"))
        return DatasetStructure(created_at, aspect_type, dataset_structure_created_at, database, entity_id, id, schema, table)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_structure_created_at)
        result["database"] = from_union([from_str, from_none], self.database)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["schema"] = from_union([from_str, from_none], self.schema)
        result["table"] = from_union([from_str, from_none], self.table)
        return result


@dataclass
class ColumnTagAssignment:
    column_name: Optional[str] = None
    tag_names: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ColumnTagAssignment':
        assert isinstance(obj, dict)
        column_name = from_union([from_str, from_none], obj.get("columnName"))
        tag_names = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tagNames"))
        return ColumnTagAssignment(column_name, tag_names)

    def to_dict(self) -> dict:
        result: dict = {}
        result["columnName"] = from_union([from_str, from_none], self.column_name)
        result["tagNames"] = from_union([lambda x: from_list(from_str, x), from_none], self.tag_names)
        return result


@dataclass
class TagAssignment:
    column_tag_assignments: Optional[List[ColumnTagAssignment]] = None
    tag_names: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TagAssignment':
        assert isinstance(obj, dict)
        column_tag_assignments = from_union([lambda x: from_list(ColumnTagAssignment.from_dict, x), from_none], obj.get("columnTagAssignments"))
        tag_names = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tagNames"))
        return TagAssignment(column_tag_assignments, tag_names)

    def to_dict(self) -> dict:
        result: dict = {}
        result["columnTagAssignments"] = from_union([lambda x: from_list(lambda x: to_class(ColumnTagAssignment, x), x), from_none], self.column_tag_assignments)
        result["tagNames"] = from_union([lambda x: from_list(from_str, x), from_none], self.tag_names)
        return result


@dataclass
class DatasetUpstream:
    """DatasetUpstream captures upstream lineages from data sources to this dataset"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_upstream_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    executor_url: Optional[str] = None
    field_mappings: Optional[List[FieldMapping]] = None
    five_tran_connector: Optional[FiveTranConnector] = None
    id: Optional[str] = None
    source_code_url: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    transformation: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetUpstream':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_upstream_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        executor_url = from_union([from_str, from_none], obj.get("executorUrl"))
        field_mappings = from_union([lambda x: from_list(FieldMapping.from_dict, x), from_none], obj.get("fieldMappings"))
        five_tran_connector = from_union([FiveTranConnector.from_dict, from_none], obj.get("fiveTranConnector"))
        id = from_union([from_str, from_none], obj.get("id"))
        source_code_url = from_union([from_str, from_none], obj.get("sourceCodeUrl"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        transformation = from_union([from_str, from_none], obj.get("transformation"))
        return DatasetUpstream(created_at, aspect_type, dataset_upstream_created_at, entity_id, executor_url, field_mappings, five_tran_connector, id, source_code_url, source_datasets, transformation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_upstream_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["executorUrl"] = from_union([from_str, from_none], self.executor_url)
        result["fieldMappings"] = from_union([lambda x: from_list(lambda x: to_class(FieldMapping, x), x), from_none], self.field_mappings)
        result["fiveTranConnector"] = from_union([lambda x: to_class(FiveTranConnector, x), from_none], self.five_tran_connector)
        result["id"] = from_union([from_str, from_none], self.id)
        result["sourceCodeUrl"] = from_union([from_str, from_none], self.source_code_url)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["transformation"] = from_union([from_str, from_none], self.transformation)
        return result


@dataclass
class FieldQueryCount:
    """Query count number and statistics of a dataset field"""
    count: Optional[float] = None
    field: Optional[str] = None
    percentile: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldQueryCount':
        assert isinstance(obj, dict)
        count = from_union([from_float, from_none], obj.get("count"))
        field = from_union([from_str, from_none], obj.get("field"))
        percentile = from_union([from_float, from_none], obj.get("percentile"))
        return FieldQueryCount(count, field, percentile)

    def to_dict(self) -> dict:
        result: dict = {}
        result["count"] = from_union([to_float, from_none], self.count)
        result["field"] = from_union([from_str, from_none], self.field)
        result["percentile"] = from_union([to_float, from_none], self.percentile)
        return result


@dataclass
class FieldQueryCounts:
    """Captures field/column query counts in last day/week/month/year."""
    last24_hours: Optional[List[FieldQueryCount]] = None
    last30_days: Optional[List[FieldQueryCount]] = None
    last365_days: Optional[List[FieldQueryCount]] = None
    last7_days: Optional[List[FieldQueryCount]] = None
    last90_days: Optional[List[FieldQueryCount]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldQueryCounts':
        assert isinstance(obj, dict)
        last24_hours = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last24Hours"))
        last30_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last30Days"))
        last365_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last365Days"))
        last7_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last7Days"))
        last90_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last90Days"))
        return FieldQueryCounts(last24_hours, last30_days, last365_days, last7_days, last90_days)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last24Hours"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last24_hours)
        result["last30Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last30_days)
        result["last365Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last365_days)
        result["last7Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last7_days)
        result["last90Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last90_days)
        return result


@dataclass
class QueryCount:
    """Query count number and statistics"""
    count: Optional[float] = None
    percentile: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryCount':
        assert isinstance(obj, dict)
        count = from_union([from_float, from_none], obj.get("count"))
        percentile = from_union([from_float, from_none], obj.get("percentile"))
        return QueryCount(count, percentile)

    def to_dict(self) -> dict:
        result: dict = {}
        result["count"] = from_union([to_float, from_none], self.count)
        result["percentile"] = from_union([to_float, from_none], self.percentile)
        return result


@dataclass
class QueryCounts:
    """Captures query counts in last day/week/month/year."""
    """Query count number and statistics"""
    last24_hours: Optional[QueryCount] = None
    """Query count number and statistics"""
    last30_days: Optional[QueryCount] = None
    """Query count number and statistics"""
    last365_days: Optional[QueryCount] = None
    """Query count number and statistics"""
    last7_days: Optional[QueryCount] = None
    """Query count number and statistics"""
    last90_days: Optional[QueryCount] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryCounts':
        assert isinstance(obj, dict)
        last24_hours = from_union([QueryCount.from_dict, from_none], obj.get("last24Hours"))
        last30_days = from_union([QueryCount.from_dict, from_none], obj.get("last30Days"))
        last365_days = from_union([QueryCount.from_dict, from_none], obj.get("last365Days"))
        last7_days = from_union([QueryCount.from_dict, from_none], obj.get("last7Days"))
        last90_days = from_union([QueryCount.from_dict, from_none], obj.get("last90Days"))
        return QueryCounts(last24_hours, last30_days, last365_days, last7_days, last90_days)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last24Hours"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last24_hours)
        result["last30Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last30_days)
        result["last365Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last365_days)
        result["last7Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last7_days)
        result["last90Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last90_days)
        return result


@dataclass
class TableColumnsUsage:
    """The columns used in the table join, either in join criteria or filter criteria."""
    columns: Optional[List[str]] = None
    count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TableColumnsUsage':
        assert isinstance(obj, dict)
        columns = from_union([lambda x: from_list(from_str, x), from_none], obj.get("columns"))
        count = from_union([from_float, from_none], obj.get("count"))
        return TableColumnsUsage(columns, count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["columns"] = from_union([lambda x: from_list(from_str, x), from_none], self.columns)
        result["count"] = from_union([to_float, from_none], self.count)
        return result


@dataclass
class TableJoinScenario:
    """Table join scenario, including the tables involved, joining columns, filtering columns,
    etc.
    """
    count: Optional[float] = None
    datasets: Optional[List[str]] = None
    filtering_columns: Optional[List[TableColumnsUsage]] = None
    joining_columns: Optional[List[TableColumnsUsage]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TableJoinScenario':
        assert isinstance(obj, dict)
        count = from_union([from_float, from_none], obj.get("count"))
        datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("datasets"))
        filtering_columns = from_union([lambda x: from_list(TableColumnsUsage.from_dict, x), from_none], obj.get("filteringColumns"))
        joining_columns = from_union([lambda x: from_list(TableColumnsUsage.from_dict, x), from_none], obj.get("joiningColumns"))
        return TableJoinScenario(count, datasets, filtering_columns, joining_columns)

    def to_dict(self) -> dict:
        result: dict = {}
        result["count"] = from_union([to_float, from_none], self.count)
        result["datasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.datasets)
        result["filteringColumns"] = from_union([lambda x: from_list(lambda x: to_class(TableColumnsUsage, x), x), from_none], self.filtering_columns)
        result["joiningColumns"] = from_union([lambda x: from_list(lambda x: to_class(TableColumnsUsage, x), x), from_none], self.joining_columns)
        return result


@dataclass
class TableJoin:
    """Table join usage statistics"""
    scenarios: Optional[List[TableJoinScenario]] = None
    total_join_count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TableJoin':
        assert isinstance(obj, dict)
        scenarios = from_union([lambda x: from_list(TableJoinScenario.from_dict, x), from_none], obj.get("scenarios"))
        total_join_count = from_union([from_float, from_none], obj.get("totalJoinCount"))
        return TableJoin(scenarios, total_join_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["scenarios"] = from_union([lambda x: from_list(lambda x: to_class(TableJoinScenario, x), x), from_none], self.scenarios)
        result["totalJoinCount"] = from_union([to_float, from_none], self.total_join_count)
        return result


@dataclass
class TableJoins:
    """Captures table join usage info in last day/week/month/year."""
    """Table join usage statistics"""
    last24_hours: Optional[TableJoin] = None
    """Table join usage statistics"""
    last30_days: Optional[TableJoin] = None
    """Table join usage statistics"""
    last365_days: Optional[TableJoin] = None
    """Table join usage statistics"""
    last7_days: Optional[TableJoin] = None
    """Table join usage statistics"""
    last90_days: Optional[TableJoin] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TableJoins':
        assert isinstance(obj, dict)
        last24_hours = from_union([TableJoin.from_dict, from_none], obj.get("last24Hours"))
        last30_days = from_union([TableJoin.from_dict, from_none], obj.get("last30Days"))
        last365_days = from_union([TableJoin.from_dict, from_none], obj.get("last365Days"))
        last7_days = from_union([TableJoin.from_dict, from_none], obj.get("last7Days"))
        last90_days = from_union([TableJoin.from_dict, from_none], obj.get("last90Days"))
        return TableJoins(last24_hours, last30_days, last365_days, last7_days, last90_days)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last24Hours"] = from_union([lambda x: to_class(TableJoin, x), from_none], self.last24_hours)
        result["last30Days"] = from_union([lambda x: to_class(TableJoin, x), from_none], self.last30_days)
        result["last365Days"] = from_union([lambda x: to_class(TableJoin, x), from_none], self.last365_days)
        result["last7Days"] = from_union([lambda x: to_class(TableJoin, x), from_none], self.last7_days)
        result["last90Days"] = from_union([lambda x: to_class(TableJoin, x), from_none], self.last90_days)
        return result


@dataclass
class UserQueryCount:
    """Query count number and statistics from a user/account"""
    count: Optional[float] = None
    user: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'UserQueryCount':
        assert isinstance(obj, dict)
        count = from_union([from_float, from_none], obj.get("count"))
        user = from_union([from_str, from_none], obj.get("user"))
        return UserQueryCount(count, user)

    def to_dict(self) -> dict:
        result: dict = {}
        result["count"] = from_union([to_float, from_none], self.count)
        result["user"] = from_union([from_str, from_none], self.user)
        return result


@dataclass
class UserQueryCounts:
    """Captures user query counts in last day/week/month/year."""
    last24_hours: Optional[List[UserQueryCount]] = None
    last24_hours_queried_by_count: Optional[float] = None
    last30_days: Optional[List[UserQueryCount]] = None
    last30_days_queried_by_count: Optional[float] = None
    last365_days: Optional[List[UserQueryCount]] = None
    last365_days_queried_by_count: Optional[float] = None
    last7_days: Optional[List[UserQueryCount]] = None
    last7_days_queried_by_count: Optional[float] = None
    last90_days: Optional[List[UserQueryCount]] = None
    last90_days_queried_by_count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'UserQueryCounts':
        assert isinstance(obj, dict)
        last24_hours = from_union([lambda x: from_list(UserQueryCount.from_dict, x), from_none], obj.get("last24Hours"))
        last24_hours_queried_by_count = from_union([from_float, from_none], obj.get("last24HoursQueriedByCount"))
        last30_days = from_union([lambda x: from_list(UserQueryCount.from_dict, x), from_none], obj.get("last30Days"))
        last30_days_queried_by_count = from_union([from_float, from_none], obj.get("last30DaysQueriedByCount"))
        last365_days = from_union([lambda x: from_list(UserQueryCount.from_dict, x), from_none], obj.get("last365Days"))
        last365_days_queried_by_count = from_union([from_float, from_none], obj.get("last365DaysQueriedByCount"))
        last7_days = from_union([lambda x: from_list(UserQueryCount.from_dict, x), from_none], obj.get("last7Days"))
        last7_days_queried_by_count = from_union([from_float, from_none], obj.get("last7DaysQueriedByCount"))
        last90_days = from_union([lambda x: from_list(UserQueryCount.from_dict, x), from_none], obj.get("last90Days"))
        last90_days_queried_by_count = from_union([from_float, from_none], obj.get("last90DaysQueriedByCount"))
        return UserQueryCounts(last24_hours, last24_hours_queried_by_count, last30_days, last30_days_queried_by_count, last365_days, last365_days_queried_by_count, last7_days, last7_days_queried_by_count, last90_days, last90_days_queried_by_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last24Hours"] = from_union([lambda x: from_list(lambda x: to_class(UserQueryCount, x), x), from_none], self.last24_hours)
        result["last24HoursQueriedByCount"] = from_union([to_float, from_none], self.last24_hours_queried_by_count)
        result["last30Days"] = from_union([lambda x: from_list(lambda x: to_class(UserQueryCount, x), x), from_none], self.last30_days)
        result["last30DaysQueriedByCount"] = from_union([to_float, from_none], self.last30_days_queried_by_count)
        result["last365Days"] = from_union([lambda x: from_list(lambda x: to_class(UserQueryCount, x), x), from_none], self.last365_days)
        result["last365DaysQueriedByCount"] = from_union([to_float, from_none], self.last365_days_queried_by_count)
        result["last7Days"] = from_union([lambda x: from_list(lambda x: to_class(UserQueryCount, x), x), from_none], self.last7_days)
        result["last7DaysQueriedByCount"] = from_union([to_float, from_none], self.last7_days_queried_by_count)
        result["last90Days"] = from_union([lambda x: from_list(lambda x: to_class(UserQueryCount, x), x), from_none], self.last90_days)
        result["last90DaysQueriedByCount"] = from_union([to_float, from_none], self.last90_days_queried_by_count)
        return result


@dataclass
class DatasetUsage:
    """Captures dataset usage statistic, e.g. the query counts."""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dataset_usage_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    field_query_counts: Optional[FieldQueryCounts] = None
    id: Optional[str] = None
    query_counts: Optional[QueryCounts] = None
    table_joins: Optional[TableJoins] = None
    user_query_counts: Optional[UserQueryCounts] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetUsage':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dataset_usage_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        field_query_counts = from_union([FieldQueryCounts.from_dict, from_none], obj.get("fieldQueryCounts"))
        id = from_union([from_str, from_none], obj.get("id"))
        query_counts = from_union([QueryCounts.from_dict, from_none], obj.get("queryCounts"))
        table_joins = from_union([TableJoins.from_dict, from_none], obj.get("tableJoins"))
        user_query_counts = from_union([UserQueryCounts.from_dict, from_none], obj.get("userQueryCounts"))
        return DatasetUsage(created_at, aspect_type, dataset_usage_created_at, entity_id, field_query_counts, id, query_counts, table_joins, user_query_counts)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_usage_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fieldQueryCounts"] = from_union([lambda x: to_class(FieldQueryCounts, x), from_none], self.field_query_counts)
        result["id"] = from_union([from_str, from_none], self.id)
        result["queryCounts"] = from_union([lambda x: to_class(QueryCounts, x), from_none], self.query_counts)
        result["tableJoins"] = from_union([lambda x: to_class(TableJoins, x), from_none], self.table_joins)
        result["userQueryCounts"] = from_union([lambda x: to_class(UserQueryCounts, x), from_none], self.user_query_counts)
        return result


@dataclass
class Dataset:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """Native Mongo db BSON id instance"""
    id: Optional[ObjectID] = None
    """Optional protected internal field to store a versionId of the entity, if the instance is
    versioned
    """
    versioned_id: Optional[str] = None
    asset_contacts: Optional[AssetContacts] = None
    asset_followers: Optional[AssetFollowers] = None
    asset_governed_tags: Optional[AssetGovernedTags] = None
    dataset_created_at: Optional[datetime] = None
    """Captures custom metadata for an asset"""
    custom_metadata: Optional[CustomMetadata] = None
    data_quality: Optional[DatasetDataQuality] = None
    deleted_at: Optional[datetime] = None
    description_assignment: Optional[DescriptionAssignment] = None
    display_name: Optional[str] = None
    """Captures dataset documentations from other tools outside the data source, e.g. dbt
    documentation on source datasets
    """
    documentation: Optional[DatasetDocumentation] = None
    entity_type: Optional[EntityType] = None
    """EntityUpstream captures upstream lineages from data sources to this entity"""
    entity_upstream: Optional[EntityUpstream] = None
    field_associations: Optional[DatasetFieldAssociations] = None
    """DatasetStatistics captures operational information about the dataset, e.g. the number of
    records or the last refresh time.
    """
    field_statistics: Optional[DatasetFieldStatistics] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    dataset_id: Optional[str] = None
    last_ingested_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[DatasetLogicalID] = None
    ownership_assignment: Optional[OwnershipAssignment] = None
    """A dataset's query history"""
    query_history: Optional[DatasetQueryHistory] = None
    schema: Optional[DatasetSchema] = None
    soda_data_quality: Optional[DatasetSodaDataQuality] = None
    source_info: Optional[SourceInfo] = None
    """DatasetStatistics captures operational information about the dataset, e.g. the number of
    records or the last refresh time.
    """
    statistics: Optional[DatasetStatistics] = None
    structure: Optional[DatasetStructure] = None
    tag_assignment: Optional[TagAssignment] = None
    """DatasetUpstream captures upstream lineages from data sources to this dataset"""
    upstream: Optional[DatasetUpstream] = None
    """Captures dataset usage statistic, e.g. the query counts."""
    usage: Optional[DatasetUsage] = None
    """Write-only api to set a versionId of the entity, if the instance is versioned
    This allows the versionedId to be maintained on the entity e.g. when an instance is
    created by the factory
    """
    dataset_versioned_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Dataset':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        versioned_id = from_union([from_str, from_none], obj.get("_versionedId"))
        asset_contacts = from_union([AssetContacts.from_dict, from_none], obj.get("assetContacts"))
        asset_followers = from_union([AssetFollowers.from_dict, from_none], obj.get("assetFollowers"))
        asset_governed_tags = from_union([AssetGovernedTags.from_dict, from_none], obj.get("assetGovernedTags"))
        dataset_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        custom_metadata = from_union([CustomMetadata.from_dict, from_none], obj.get("customMetadata"))
        data_quality = from_union([DatasetDataQuality.from_dict, from_none], obj.get("dataQuality"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        description_assignment = from_union([DescriptionAssignment.from_dict, from_none], obj.get("descriptionAssignment"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        documentation = from_union([DatasetDocumentation.from_dict, from_none], obj.get("documentation"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        entity_upstream = from_union([EntityUpstream.from_dict, from_none], obj.get("entityUpstream"))
        field_associations = from_union([DatasetFieldAssociations.from_dict, from_none], obj.get("fieldAssociations"))
        field_statistics = from_union([DatasetFieldStatistics.from_dict, from_none], obj.get("fieldStatistics"))
        dataset_id = from_union([from_str, from_none], obj.get("id"))
        last_ingested_at = from_union([from_datetime, from_none], obj.get("lastIngestedAt"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([DatasetLogicalID.from_dict, from_none], obj.get("logicalId"))
        ownership_assignment = from_union([OwnershipAssignment.from_dict, from_none], obj.get("ownershipAssignment"))
        query_history = from_union([DatasetQueryHistory.from_dict, from_none], obj.get("queryHistory"))
        schema = from_union([DatasetSchema.from_dict, from_none], obj.get("schema"))
        soda_data_quality = from_union([DatasetSodaDataQuality.from_dict, from_none], obj.get("sodaDataQuality"))
        source_info = from_union([SourceInfo.from_dict, from_none], obj.get("sourceInfo"))
        statistics = from_union([DatasetStatistics.from_dict, from_none], obj.get("statistics"))
        structure = from_union([DatasetStructure.from_dict, from_none], obj.get("structure"))
        tag_assignment = from_union([TagAssignment.from_dict, from_none], obj.get("tagAssignment"))
        upstream = from_union([DatasetUpstream.from_dict, from_none], obj.get("upstream"))
        usage = from_union([DatasetUsage.from_dict, from_none], obj.get("usage"))
        dataset_versioned_id = from_union([from_str, from_none], obj.get("versionedId"))
        return Dataset(created_at, id, versioned_id, asset_contacts, asset_followers, asset_governed_tags, dataset_created_at, custom_metadata, data_quality, deleted_at, description_assignment, display_name, documentation, entity_type, entity_upstream, field_associations, field_statistics, dataset_id, last_ingested_at, last_modified_at, logical_id, ownership_assignment, query_history, schema, soda_data_quality, source_info, statistics, structure, tag_assignment, upstream, usage, dataset_versioned_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_versionedId"] = from_union([from_str, from_none], self.versioned_id)
        result["assetContacts"] = from_union([lambda x: to_class(AssetContacts, x), from_none], self.asset_contacts)
        result["assetFollowers"] = from_union([lambda x: to_class(AssetFollowers, x), from_none], self.asset_followers)
        result["assetGovernedTags"] = from_union([lambda x: to_class(AssetGovernedTags, x), from_none], self.asset_governed_tags)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_created_at)
        result["customMetadata"] = from_union([lambda x: to_class(CustomMetadata, x), from_none], self.custom_metadata)
        result["dataQuality"] = from_union([lambda x: to_class(DatasetDataQuality, x), from_none], self.data_quality)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["descriptionAssignment"] = from_union([lambda x: to_class(DescriptionAssignment, x), from_none], self.description_assignment)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["documentation"] = from_union([lambda x: to_class(DatasetDocumentation, x), from_none], self.documentation)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["entityUpstream"] = from_union([lambda x: to_class(EntityUpstream, x), from_none], self.entity_upstream)
        result["fieldAssociations"] = from_union([lambda x: to_class(DatasetFieldAssociations, x), from_none], self.field_associations)
        result["fieldStatistics"] = from_union([lambda x: to_class(DatasetFieldStatistics, x), from_none], self.field_statistics)
        result["id"] = from_union([from_str, from_none], self.dataset_id)
        result["lastIngestedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_ingested_at)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(DatasetLogicalID, x), from_none], self.logical_id)
        result["ownershipAssignment"] = from_union([lambda x: to_class(OwnershipAssignment, x), from_none], self.ownership_assignment)
        result["queryHistory"] = from_union([lambda x: to_class(DatasetQueryHistory, x), from_none], self.query_history)
        result["schema"] = from_union([lambda x: to_class(DatasetSchema, x), from_none], self.schema)
        result["sodaDataQuality"] = from_union([lambda x: to_class(DatasetSodaDataQuality, x), from_none], self.soda_data_quality)
        result["sourceInfo"] = from_union([lambda x: to_class(SourceInfo, x), from_none], self.source_info)
        result["statistics"] = from_union([lambda x: to_class(DatasetStatistics, x), from_none], self.statistics)
        result["structure"] = from_union([lambda x: to_class(DatasetStructure, x), from_none], self.structure)
        result["tagAssignment"] = from_union([lambda x: to_class(TagAssignment, x), from_none], self.tag_assignment)
        result["upstream"] = from_union([lambda x: to_class(DatasetUpstream, x), from_none], self.upstream)
        result["usage"] = from_union([lambda x: to_class(DatasetUsage, x), from_none], self.usage)
        result["versionedId"] = from_union([from_str, from_none], self.dataset_versioned_id)
        return result


@dataclass
class EventHeader:
    app_name: Optional[str] = None
    server: Optional[str] = None
    time: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'EventHeader':
        assert isinstance(obj, dict)
        app_name = from_union([from_str, from_none], obj.get("appName"))
        server = from_union([from_str, from_none], obj.get("server"))
        time = from_union([from_datetime, from_none], obj.get("time"))
        return EventHeader(app_name, server, time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["appName"] = from_union([from_str, from_none], self.app_name)
        result["server"] = from_union([from_str, from_none], self.server)
        result["time"] = from_union([lambda x: x.isoformat(), from_none], self.time)
        return result


@dataclass
class AssetLikes:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    asset_likes_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None
    """This is stored as an additional separate field on the document, as opposed to resolved,
    to enable sorting at the database layer
    Mongo does not support sorting on properties of an array such as length
    Note: Although this is a getter, the wrapper withEnumerableGettersTrait will allow the
    field to be enumerable when the instance is iterated
    for example, when assigning / copying
    """
    like_count: Optional[float] = None
    liked_by: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetLikes':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        asset_likes_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        like_count = from_union([from_float, from_none], obj.get("likeCount"))
        liked_by = from_union([lambda x: from_list(from_str, x), from_none], obj.get("likedBy"))
        return AssetLikes(created_at, aspect_type, created, asset_likes_created_at, entity_id, id, last_modified, like_count, liked_by)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.asset_likes_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["likeCount"] = from_union([to_float, from_none], self.like_count)
        result["likedBy"] = from_union([lambda x: from_list(from_str, x), from_none], self.liked_by)
        return result


@dataclass
class AssetDescriptionTokenizedContent:
    description: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetDescriptionTokenizedContent':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        return AssetDescriptionTokenizedContent(description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        return result


@dataclass
class AssetDescriptionKnowledgeCard:
    description: Optional[str] = None
    title: Optional[str] = None
    tokenized_content: Optional[AssetDescriptionTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AssetDescriptionKnowledgeCard':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([AssetDescriptionTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return AssetDescriptionKnowledgeCard(description, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(AssetDescriptionTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class AcknowledgeChangeRequest:
    acknowledged_by: Optional[AuditStamp] = None
    entity_id: Optional[str] = None
    message: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AcknowledgeChangeRequest':
        assert isinstance(obj, dict)
        acknowledged_by = from_union([AuditStamp.from_dict, from_none], obj.get("acknowledgedBy"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        message = from_union([from_str, from_none], obj.get("message"))
        return AcknowledgeChangeRequest(acknowledged_by, entity_id, message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["acknowledgedBy"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.acknowledged_by)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["message"] = from_union([from_str, from_none], self.message)
        return result


class ChangeRequestType(Enum):
    """Change Request types that can be supplied
    Note: Types are Entity type agnostic, the entity type can be derived from the
    Entity the request is being made against e.g. CONTENT_UPDATE against a DATA_DOCUMENT is a
    document content change request
    """
    ASSET_ACCESS = "ASSET_ACCESS"
    COLUMN_UPDATE = "COLUMN_UPDATE"
    CONTACTS_UPDATE = "CONTACTS_UPDATE"
    CONTENT_UPDATE = "CONTENT_UPDATE"
    DESCRIPTION_UPDATE = "DESCRIPTION_UPDATE"
    TAGS_UPDATE = "TAGS_UPDATE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ChangeRequestTokenizedContent:
    message: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ChangeRequestTokenizedContent':
        assert isinstance(obj, dict)
        message = from_union([from_str, from_none], obj.get("message"))
        return ChangeRequestTokenizedContent(message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["message"] = from_union([from_str, from_none], self.message)
        return result


@dataclass
class ChangeRequestKnowledgeCard:
    acknowledged: Optional[AcknowledgeChangeRequest] = None
    message: Optional[str] = None
    recipient_id: Optional[str] = None
    request_type: Optional[ChangeRequestType] = None
    title: Optional[str] = None
    tokenized_content: Optional[ChangeRequestTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ChangeRequestKnowledgeCard':
        assert isinstance(obj, dict)
        acknowledged = from_union([AcknowledgeChangeRequest.from_dict, from_none], obj.get("acknowledged"))
        message = from_union([from_str, from_none], obj.get("message"))
        recipient_id = from_union([from_str, from_none], obj.get("recipientId"))
        request_type = from_union([ChangeRequestType, from_none], obj.get("requestType"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([ChangeRequestTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return ChangeRequestKnowledgeCard(acknowledged, message, recipient_id, request_type, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["acknowledged"] = from_union([lambda x: to_class(AcknowledgeChangeRequest, x), from_none], self.acknowledged)
        result["message"] = from_union([from_str, from_none], self.message)
        result["recipientId"] = from_union([from_str, from_none], self.recipient_id)
        result["requestType"] = from_union([lambda x: to_enum(ChangeRequestType, x), from_none], self.request_type)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(ChangeRequestTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class ColumnDescriptionKnowledgeCard:
    description: Optional[str] = None
    field_path: Optional[str] = None
    title: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ColumnDescriptionKnowledgeCard':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ColumnDescriptionKnowledgeCard(description, field_path, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class CommentTokenizedContent:
    """Output value conditionally resolved by CommentResolver"""
    comment: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'CommentTokenizedContent':
        assert isinstance(obj, dict)
        comment = from_union([from_str, from_none], obj.get("comment"))
        return CommentTokenizedContent(comment)

    def to_dict(self) -> dict:
        result: dict = {}
        result["comment"] = from_union([from_str, from_none], self.comment)
        return result


@dataclass
class Comment:
    """Output value conditionally resolved by CommentResolver"""
    comment: Optional[str] = None
    """A copy of the entity id for the Knowledge Card, not exposed in the GraphQL schema
    Internally used by resolvers or other processes to obtain a reference to the the
    comment's
    Knowledge Card entity
    """
    entity_id: Optional[str] = None
    """parentCommentId is a reference to the comment that the comment is a reply to.
    parentCommentId presence also implies that a comment is a reply.
    The composite of the parentCommentId and the entityId allows retrieval of all reply
    comments for a
    top-level comment and easily collating the total number of comments (incl. replies) on
    the asset.
    This is because all comments (top-level and replies) are stored in a flat hierarchy in
    the database.
    """
    parent_comment_id: Optional[str] = None
    title: Optional[str] = None
    """Output value conditionally resolved by CommentResolver"""
    tokenized_content: Optional[CommentTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Comment':
        assert isinstance(obj, dict)
        comment = from_union([from_str, from_none], obj.get("comment"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        parent_comment_id = from_union([from_str, from_none], obj.get("parentCommentId"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([CommentTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return Comment(comment, entity_id, parent_comment_id, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["comment"] = from_union([from_str, from_none], self.comment)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["parentCommentId"] = from_union([from_str, from_none], self.parent_comment_id)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(CommentTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class DataDocumentTokenizedContent:
    content: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DataDocumentTokenizedContent':
        assert isinstance(obj, dict)
        content = from_union([from_str, from_none], obj.get("content"))
        return DataDocumentTokenizedContent(content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["content"] = from_union([from_str, from_none], self.content)
        return result


@dataclass
class DataDocument:
    content: Optional[str] = None
    title: Optional[str] = None
    tokenized_content: Optional[DataDocumentTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DataDocument':
        assert isinstance(obj, dict)
        content = from_union([from_str, from_none], obj.get("content"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([DataDocumentTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return DataDocument(content, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["content"] = from_union([from_str, from_none], self.content)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(DataDocumentTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class DeprecationTokenizedContent:
    detail: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DeprecationTokenizedContent':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        return DeprecationTokenizedContent(detail)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        return result


@dataclass
class DeprecationKnowledgeCard:
    detail: Optional[str] = None
    planned_date: Optional[datetime] = None
    title: Optional[str] = None
    tokenized_content: Optional[DeprecationTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DeprecationKnowledgeCard':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        planned_date = from_union([from_datetime, from_none], obj.get("plannedDate"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([DeprecationTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return DeprecationKnowledgeCard(detail, planned_date, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        result["plannedDate"] = from_union([lambda x: x.isoformat(), from_none], self.planned_date)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(DeprecationTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class IncidentTokenizedContent:
    detail: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'IncidentTokenizedContent':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        return IncidentTokenizedContent(detail)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        return result


@dataclass
class IncidentKnowledgeCard:
    detail: Optional[str] = None
    title: Optional[str] = None
    tokenized_content: Optional[IncidentTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'IncidentKnowledgeCard':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([IncidentTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return IncidentKnowledgeCard(detail, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(IncidentTokenizedContent, x), from_none], self.tokenized_content)
        return result


class KnowledgeCardType(Enum):
    ASSET_DESCRIPTION = "ASSET_DESCRIPTION"
    CHANGE_REQUEST = "CHANGE_REQUEST"
    COLUMN_DESCRIPTION = "COLUMN_DESCRIPTION"
    COMMENT = "COMMENT"
    DATA_DOCUMENT = "DATA_DOCUMENT"
    DEPRECATION = "DEPRECATION"
    HOW_TO_USE = "HOW_TO_USE"
    INCIDENT = "INCIDENT"
    UNKNOWN = "UNKNOWN"


@dataclass
class HowToUseTokenizedContent:
    detail: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'HowToUseTokenizedContent':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        return HowToUseTokenizedContent(detail)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        return result


@dataclass
class UsageKnowledgeCard:
    detail: Optional[str] = None
    example: Optional[str] = None
    title: Optional[str] = None
    tokenized_content: Optional[HowToUseTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'UsageKnowledgeCard':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        example = from_union([from_str, from_none], obj.get("example"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([HowToUseTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return UsageKnowledgeCard(detail, example, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        result["example"] = from_union([from_str, from_none], self.example)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(HowToUseTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class KnowledgeCardDetail:
    asset_description: Optional[AssetDescriptionKnowledgeCard] = None
    change_request: Optional[ChangeRequestKnowledgeCard] = None
    column_description: Optional[ColumnDescriptionKnowledgeCard] = None
    comment: Optional[Comment] = None
    data_document: Optional[DataDocument] = None
    deprecation: Optional[DeprecationKnowledgeCard] = None
    incident: Optional[IncidentKnowledgeCard] = None
    type: Optional[KnowledgeCardType] = None
    usage: Optional[UsageKnowledgeCard] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardDetail':
        assert isinstance(obj, dict)
        asset_description = from_union([AssetDescriptionKnowledgeCard.from_dict, from_none], obj.get("assetDescription"))
        change_request = from_union([ChangeRequestKnowledgeCard.from_dict, from_none], obj.get("changeRequest"))
        column_description = from_union([ColumnDescriptionKnowledgeCard.from_dict, from_none], obj.get("columnDescription"))
        comment = from_union([Comment.from_dict, from_none], obj.get("comment"))
        data_document = from_union([DataDocument.from_dict, from_none], obj.get("dataDocument"))
        deprecation = from_union([DeprecationKnowledgeCard.from_dict, from_none], obj.get("deprecation"))
        incident = from_union([IncidentKnowledgeCard.from_dict, from_none], obj.get("incident"))
        type = from_union([KnowledgeCardType, from_none], obj.get("type"))
        usage = from_union([UsageKnowledgeCard.from_dict, from_none], obj.get("usage"))
        return KnowledgeCardDetail(asset_description, change_request, column_description, comment, data_document, deprecation, incident, type, usage)

    def to_dict(self) -> dict:
        result: dict = {}
        result["assetDescription"] = from_union([lambda x: to_class(AssetDescriptionKnowledgeCard, x), from_none], self.asset_description)
        result["changeRequest"] = from_union([lambda x: to_class(ChangeRequestKnowledgeCard, x), from_none], self.change_request)
        result["columnDescription"] = from_union([lambda x: to_class(ColumnDescriptionKnowledgeCard, x), from_none], self.column_description)
        result["comment"] = from_union([lambda x: to_class(Comment, x), from_none], self.comment)
        result["dataDocument"] = from_union([lambda x: to_class(DataDocument, x), from_none], self.data_document)
        result["deprecation"] = from_union([lambda x: to_class(DeprecationKnowledgeCard, x), from_none], self.deprecation)
        result["incident"] = from_union([lambda x: to_class(IncidentKnowledgeCard, x), from_none], self.incident)
        result["type"] = from_union([lambda x: to_enum(KnowledgeCardType, x), from_none], self.type)
        result["usage"] = from_union([lambda x: to_class(UsageKnowledgeCard, x), from_none], self.usage)
        return result


@dataclass
class InputOrOutputType:
    value: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'InputOrOutputType':
        assert isinstance(obj, dict)
        value = from_union([from_str, from_none], obj.get("value"))
        return InputOrOutputType(value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["value"] = from_union([from_str, from_none], self.value)
        return result


@dataclass
class KnowledgeCardInfo:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    """backing store for related Entities which contains
    related entity ids excluding the anchor Entity id
    Note: Cannot be a native private field since it's shared between input and output
    """
    non_anchoring_ids_backing_store: Optional[List[str]] = None
    """The global id for the Entity the associated Knowledge Card was created for. Must be
    provided on Knowledge Card creation for cards that are anchored to an Entity
    Specified on the Input Type KnowledgeCardInfoInput
    """
    anchor_entity_id: Optional[str] = None
    archived: Optional[AuditStamp] = None
    aspect_type: Optional[AspectType] = None
    created: Optional[AuditStamp] = None
    knowledge_card_info_created_at: Optional[datetime] = None
    detail: Optional[KnowledgeCardDetail] = None
    entity_id: Optional[str] = None
    hashtags: Optional[List[InputOrOutputType]] = None
    id: Optional[str] = None
    is_draft: Optional[bool] = None
    last_modified: Optional[AuditStamp] = None
    protected: Optional[bool] = None
    published: Optional[AuditStamp] = None
    """Getter and setter interface to protected _nonAnchoringIdsBackingStore
    Includes the non-empty anchorEntityId as the first item in the list
    of relatedEntityIds
    """
    related_entity_ids: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardInfo':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        non_anchoring_ids_backing_store = from_union([lambda x: from_list(from_str, x), from_none], obj.get("_nonAnchoringIdsBackingStore"))
        anchor_entity_id = from_union([from_str, from_none], obj.get("anchorEntityId"))
        archived = from_union([AuditStamp.from_dict, from_none], obj.get("archived"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        knowledge_card_info_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        detail = from_union([KnowledgeCardDetail.from_dict, from_none], obj.get("detail"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        hashtags = from_union([lambda x: from_list(InputOrOutputType.from_dict, x), from_none], obj.get("hashtags"))
        id = from_union([from_str, from_none], obj.get("id"))
        is_draft = from_union([from_bool, from_none], obj.get("isDraft"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        protected = from_union([from_bool, from_none], obj.get("protected"))
        published = from_union([AuditStamp.from_dict, from_none], obj.get("published"))
        related_entity_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("relatedEntityIds"))
        return KnowledgeCardInfo(created_at, non_anchoring_ids_backing_store, anchor_entity_id, archived, aspect_type, created, knowledge_card_info_created_at, detail, entity_id, hashtags, id, is_draft, last_modified, protected, published, related_entity_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_nonAnchoringIdsBackingStore"] = from_union([lambda x: from_list(from_str, x), from_none], self.non_anchoring_ids_backing_store)
        result["anchorEntityId"] = from_union([from_str, from_none], self.anchor_entity_id)
        result["archived"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.archived)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.knowledge_card_info_created_at)
        result["detail"] = from_union([lambda x: to_class(KnowledgeCardDetail, x), from_none], self.detail)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["hashtags"] = from_union([lambda x: from_list(lambda x: to_class(InputOrOutputType, x), x), from_none], self.hashtags)
        result["id"] = from_union([from_str, from_none], self.id)
        result["isDraft"] = from_union([from_bool, from_none], self.is_draft)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["protected"] = from_union([from_bool, from_none], self.protected)
        result["published"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.published)
        result["relatedEntityIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.related_entity_ids)
        return result


@dataclass
class ValidationConfirmation:
    confirmed_by: Optional[AuditStamp] = None
    knowledge_card_id: Optional[str] = None
    message: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ValidationConfirmation':
        assert isinstance(obj, dict)
        confirmed_by = from_union([AuditStamp.from_dict, from_none], obj.get("confirmedBy"))
        knowledge_card_id = from_union([from_str, from_none], obj.get("knowledgeCardId"))
        message = from_union([from_str, from_none], obj.get("message"))
        return ValidationConfirmation(confirmed_by, knowledge_card_id, message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["confirmedBy"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.confirmed_by)
        result["knowledgeCardId"] = from_union([from_str, from_none], self.knowledge_card_id)
        result["message"] = from_union([from_str, from_none], self.message)
        return result


@dataclass
class ValidationRequest:
    knowledge_card_id: Optional[str] = None
    message: Optional[str] = None
    recipient_id: Optional[str] = None
    requested_by: Optional[AuditStamp] = None
    requester_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ValidationRequest':
        assert isinstance(obj, dict)
        knowledge_card_id = from_union([from_str, from_none], obj.get("knowledgeCardId"))
        message = from_union([from_str, from_none], obj.get("message"))
        recipient_id = from_union([from_str, from_none], obj.get("recipientId"))
        requested_by = from_union([AuditStamp.from_dict, from_none], obj.get("requestedBy"))
        requester_id = from_union([from_str, from_none], obj.get("requesterId"))
        return ValidationRequest(knowledge_card_id, message, recipient_id, requested_by, requester_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["knowledgeCardId"] = from_union([from_str, from_none], self.knowledge_card_id)
        result["message"] = from_union([from_str, from_none], self.message)
        result["recipientId"] = from_union([from_str, from_none], self.recipient_id)
        result["requestedBy"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.requested_by)
        result["requesterId"] = from_union([from_str, from_none], self.requester_id)
        return result


@dataclass
class KnowledgeCardValidation:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    confirmation: Optional[ValidationConfirmation] = None
    knowledge_card_validation_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    request: Optional[ValidationRequest] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardValidation':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        confirmation = from_union([ValidationConfirmation.from_dict, from_none], obj.get("confirmation"))
        knowledge_card_validation_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        request = from_union([ValidationRequest.from_dict, from_none], obj.get("request"))
        return KnowledgeCardValidation(created_at, aspect_type, confirmation, knowledge_card_validation_created_at, entity_id, id, request)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["confirmation"] = from_union([lambda x: to_class(ValidationConfirmation, x), from_none], self.confirmation)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.knowledge_card_validation_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["request"] = from_union([lambda x: to_class(ValidationRequest, x), from_none], self.request)
        return result


@dataclass
class KnowledgeCardLogicalID:
    """Implemented in {@link KnowledgeCard} output type
    Definite assignment assertion is safe since it is defined in output subtype.
    This is due to unresolved TypeScript bug preventing this class from being defined as an
    abstract class, and
    then being used in a mixin {@see https://github.com/microsoft/TypeScript/issues/37142}
    """
    id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardLogicalID':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        return KnowledgeCardLogicalID(id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_str, from_none], self.id)
        return result


@dataclass
class KnowledgeCard:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """Native Mongo db BSON id instance"""
    id: Optional[ObjectID] = None
    """Optional protected internal field to store a versionId of the entity, if the instance is
    versioned
    """
    versioned_id: Optional[str] = None
    asset_contacts: Optional[AssetContacts] = None
    asset_followers: Optional[AssetFollowers] = None
    asset_governed_tags: Optional[AssetGovernedTags] = None
    asset_likes: Optional[AssetLikes] = None
    knowledge_card_created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    """Implement a dummy accessor here, the children class will implement the correct one."""
    display_name: Optional[str] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    knowledge_card_id: Optional[str] = None
    knowledge_card_info: Optional[KnowledgeCardInfo] = None
    knowledge_card_validation: Optional[KnowledgeCardValidation] = None
    last_ingested_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    """Implemented in {@link KnowledgeCard} output type
    Definite assignment assertion is safe since it is defined in output subtype.
    This is due to unresolved TypeScript bug preventing this class from being defined as an
    abstract class, and
    then being used in a mixin {@see https://github.com/microsoft/TypeScript/issues/37142}
    """
    logical_id: Optional[KnowledgeCardLogicalID] = None
    """Write-only api to set a versionId of the entity, if the instance is versioned
    This allows the versionedId to be maintained on the entity e.g. when an instance is
    created by the factory
    """
    knowledge_card_versioned_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCard':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        versioned_id = from_union([from_str, from_none], obj.get("_versionedId"))
        asset_contacts = from_union([AssetContacts.from_dict, from_none], obj.get("assetContacts"))
        asset_followers = from_union([AssetFollowers.from_dict, from_none], obj.get("assetFollowers"))
        asset_governed_tags = from_union([AssetGovernedTags.from_dict, from_none], obj.get("assetGovernedTags"))
        asset_likes = from_union([AssetLikes.from_dict, from_none], obj.get("assetLikes"))
        knowledge_card_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        knowledge_card_id = from_union([from_str, from_none], obj.get("id"))
        knowledge_card_info = from_union([KnowledgeCardInfo.from_dict, from_none], obj.get("knowledgeCardInfo"))
        knowledge_card_validation = from_union([KnowledgeCardValidation.from_dict, from_none], obj.get("knowledgeCardValidation"))
        last_ingested_at = from_union([from_datetime, from_none], obj.get("lastIngestedAt"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([KnowledgeCardLogicalID.from_dict, from_none], obj.get("logicalId"))
        knowledge_card_versioned_id = from_union([from_str, from_none], obj.get("versionedId"))
        return KnowledgeCard(created_at, id, versioned_id, asset_contacts, asset_followers, asset_governed_tags, asset_likes, knowledge_card_created_at, deleted_at, display_name, entity_type, knowledge_card_id, knowledge_card_info, knowledge_card_validation, last_ingested_at, last_modified_at, logical_id, knowledge_card_versioned_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_versionedId"] = from_union([from_str, from_none], self.versioned_id)
        result["assetContacts"] = from_union([lambda x: to_class(AssetContacts, x), from_none], self.asset_contacts)
        result["assetFollowers"] = from_union([lambda x: to_class(AssetFollowers, x), from_none], self.asset_followers)
        result["assetGovernedTags"] = from_union([lambda x: to_class(AssetGovernedTags, x), from_none], self.asset_governed_tags)
        result["assetLikes"] = from_union([lambda x: to_class(AssetLikes, x), from_none], self.asset_likes)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.knowledge_card_created_at)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.knowledge_card_id)
        result["knowledgeCardInfo"] = from_union([lambda x: to_class(KnowledgeCardInfo, x), from_none], self.knowledge_card_info)
        result["knowledgeCardValidation"] = from_union([lambda x: to_class(KnowledgeCardValidation, x), from_none], self.knowledge_card_validation)
        result["lastIngestedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_ingested_at)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(KnowledgeCardLogicalID, x), from_none], self.logical_id)
        result["versionedId"] = from_union([from_str, from_none], self.knowledge_card_versioned_id)
        return result


@dataclass
class MetricFilter:
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MetricFilter':
        assert isinstance(obj, dict)
        field = from_union([from_str, from_none], obj.get("field"))
        operator = from_union([from_str, from_none], obj.get("operator"))
        value = from_union([from_str, from_none], obj.get("value"))
        return MetricFilter(field, operator, value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["field"] = from_union([from_str, from_none], self.field)
        result["operator"] = from_union([from_str, from_none], self.operator)
        result["value"] = from_union([from_str, from_none], self.value)
        return result


@dataclass
class DbtMetric:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    dbt_metric_created_at: Optional[datetime] = None
    description: Optional[str] = None
    dimensions: Optional[List[str]] = None
    entity_id: Optional[str] = None
    filters: Optional[List[MetricFilter]] = None
    id: Optional[str] = None
    label: Optional[str] = None
    package_name: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    source_models: Optional[List[str]] = None
    sql: Optional[str] = None
    tags: Optional[List[str]] = None
    time_grains: Optional[List[str]] = None
    timestamp: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DbtMetric':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        dbt_metric_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        dimensions = from_union([lambda x: from_list(from_str, x), from_none], obj.get("dimensions"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        filters = from_union([lambda x: from_list(MetricFilter.from_dict, x), from_none], obj.get("filters"))
        id = from_union([from_str, from_none], obj.get("id"))
        label = from_union([from_str, from_none], obj.get("label"))
        package_name = from_union([from_str, from_none], obj.get("packageName"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        source_models = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceModels"))
        sql = from_union([from_str, from_none], obj.get("sql"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        time_grains = from_union([lambda x: from_list(from_str, x), from_none], obj.get("timeGrains"))
        timestamp = from_union([from_str, from_none], obj.get("timestamp"))
        type = from_union([from_str, from_none], obj.get("type"))
        url = from_union([from_str, from_none], obj.get("url"))
        return DbtMetric(created_at, aspect_type, dbt_metric_created_at, description, dimensions, entity_id, filters, id, label, package_name, source_datasets, source_models, sql, tags, time_grains, timestamp, type, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dbt_metric_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["dimensions"] = from_union([lambda x: from_list(from_str, x), from_none], self.dimensions)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["filters"] = from_union([lambda x: from_list(lambda x: to_class(MetricFilter, x), x), from_none], self.filters)
        result["id"] = from_union([from_str, from_none], self.id)
        result["label"] = from_union([from_str, from_none], self.label)
        result["packageName"] = from_union([from_str, from_none], self.package_name)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["sourceModels"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_models)
        result["sql"] = from_union([from_str, from_none], self.sql)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        result["timeGrains"] = from_union([lambda x: from_list(from_str, x), from_none], self.time_grains)
        result["timestamp"] = from_union([from_str, from_none], self.timestamp)
        result["type"] = from_union([from_str, from_none], self.type)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


class MetricType(Enum):
    DBT_METRIC = "DBT_METRIC"
    UNKNOWN = "UNKNOWN"


@dataclass
class MetricLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    name: Optional[str] = None
    type: Optional[MetricType] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MetricLogicalID':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        type = from_union([MetricType, from_none], obj.get("type"))
        return MetricLogicalID(name, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_union([from_str, from_none], self.name)
        result["type"] = from_union([lambda x: to_enum(MetricType, x), from_none], self.type)
        return result


@dataclass
class MetricInfo:
    """The input or output type for the MetricInfo aspect field"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    created: Optional[AuditStamp] = None
    metric_info_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    last_modified: Optional[AuditStamp] = None
    related_entity_ids: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MetricInfo':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        metric_info_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        related_entity_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("relatedEntityIds"))
        return MetricInfo(created_at, aspect_type, created, metric_info_created_at, entity_id, id, last_modified, related_entity_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.metric_info_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["relatedEntityIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.related_entity_ids)
        return result


@dataclass
class Metric:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """Native Mongo db BSON id instance"""
    id: Optional[ObjectID] = None
    """Optional protected internal field to store a versionId of the entity, if the instance is
    versioned
    """
    versioned_id: Optional[str] = None
    asset_contacts: Optional[AssetContacts] = None
    asset_followers: Optional[AssetFollowers] = None
    asset_governed_tags: Optional[AssetGovernedTags] = None
    metric_created_at: Optional[datetime] = None
    dbt_metric: Optional[DbtMetric] = None
    deleted_at: Optional[datetime] = None
    display_name: Optional[str] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    metric_id: Optional[str] = None
    last_ingested_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[MetricLogicalID] = None
    """The input or output type for the MetricInfo aspect field"""
    metric_info: Optional[MetricInfo] = None
    """Write-only api to set a versionId of the entity, if the instance is versioned
    This allows the versionedId to be maintained on the entity e.g. when an instance is
    created by the factory
    """
    metric_versioned_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Metric':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        versioned_id = from_union([from_str, from_none], obj.get("_versionedId"))
        asset_contacts = from_union([AssetContacts.from_dict, from_none], obj.get("assetContacts"))
        asset_followers = from_union([AssetFollowers.from_dict, from_none], obj.get("assetFollowers"))
        asset_governed_tags = from_union([AssetGovernedTags.from_dict, from_none], obj.get("assetGovernedTags"))
        metric_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dbt_metric = from_union([DbtMetric.from_dict, from_none], obj.get("dbtMetric"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        metric_id = from_union([from_str, from_none], obj.get("id"))
        last_ingested_at = from_union([from_datetime, from_none], obj.get("lastIngestedAt"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([MetricLogicalID.from_dict, from_none], obj.get("logicalId"))
        metric_info = from_union([MetricInfo.from_dict, from_none], obj.get("metricInfo"))
        metric_versioned_id = from_union([from_str, from_none], obj.get("versionedId"))
        return Metric(created_at, id, versioned_id, asset_contacts, asset_followers, asset_governed_tags, metric_created_at, dbt_metric, deleted_at, display_name, entity_type, metric_id, last_ingested_at, last_modified_at, logical_id, metric_info, metric_versioned_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_versionedId"] = from_union([from_str, from_none], self.versioned_id)
        result["assetContacts"] = from_union([lambda x: to_class(AssetContacts, x), from_none], self.asset_contacts)
        result["assetFollowers"] = from_union([lambda x: to_class(AssetFollowers, x), from_none], self.asset_followers)
        result["assetGovernedTags"] = from_union([lambda x: to_class(AssetGovernedTags, x), from_none], self.asset_governed_tags)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.metric_created_at)
        result["dbtMetric"] = from_union([lambda x: to_class(DbtMetric, x), from_none], self.dbt_metric)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.metric_id)
        result["lastIngestedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_ingested_at)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(MetricLogicalID, x), from_none], self.logical_id)
        result["metricInfo"] = from_union([lambda x: to_class(MetricInfo, x), from_none], self.metric_info)
        result["versionedId"] = from_union([from_str, from_none], self.metric_versioned_id)
        return result


class Context(Enum):
    """Easily extract the type of a given object's values"""
    DASHBOARDS = "dashboards"
    DATASETS = "datasets"
    DATA_DOCUMENT = "DATA_DOCUMENT"
    DATA_GROUP = "DATA_GROUP"
    DBT_MODEL = "DBT_MODEL"
    KNOWLEDGE_CARDS = "knowledge_cards"
    LOOKER_EXPLORE = "LOOKER_EXPLORE"
    LOOKER_VIEW = "LOOKER_VIEW"
    METRICS = "metrics"
    PERSONS = "persons"
    POWER_BI_DATASET = "POWER_BI_DATASET"
    TABLEAU_DATASOURCE = "TABLEAU_DATASOURCE"
    THOUGHT_SPOT_DATA_OBJECT = "THOUGHT_SPOT_DATA_OBJECT"


@dataclass
class SearchQuery:
    """Easily extract the type of a given object's values"""
    context: Optional[Context] = None
    keyword: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SearchQuery':
        assert isinstance(obj, dict)
        context = from_union([Context, from_none], obj.get("context"))
        keyword = from_union([from_str, from_none], obj.get("keyword"))
        return SearchQuery(context, keyword)

    def to_dict(self) -> dict:
        result: dict = {}
        result["context"] = from_union([lambda x: to_enum(Context, x), from_none], self.context)
        result["keyword"] = from_union([from_str, from_none], self.keyword)
        return result


@dataclass
class ViewedEntityHistory:
    date: Optional[datetime] = None
    entity_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ViewedEntityHistory':
        assert isinstance(obj, dict)
        date = from_union([from_datetime, from_none], obj.get("date"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        return ViewedEntityHistory(date, entity_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["date"] = from_union([lambda x: x.isoformat(), from_none], self.date)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        return result


@dataclass
class PersonActivity:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    person_activity_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    recently_viewed_history: Optional[List[ViewedEntityHistory]] = None
    recent_searches: Optional[List[SearchQuery]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonActivity':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        person_activity_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        recently_viewed_history = from_union([lambda x: from_list(ViewedEntityHistory.from_dict, x), from_none], obj.get("recentlyViewedHistory"))
        recent_searches = from_union([lambda x: from_list(SearchQuery.from_dict, x), from_none], obj.get("recentSearches"))
        return PersonActivity(created_at, aspect_type, person_activity_created_at, entity_id, id, recently_viewed_history, recent_searches)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_activity_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["recentlyViewedHistory"] = from_union([lambda x: from_list(lambda x: to_class(ViewedEntityHistory, x), x), from_none], self.recently_viewed_history)
        result["recentSearches"] = from_union([lambda x: from_list(lambda x: to_class(SearchQuery, x), x), from_none], self.recent_searches)
        return result


@dataclass
class PersonLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    email: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonLogicalID':
        assert isinstance(obj, dict)
        email = from_union([from_str, from_none], obj.get("email"))
        return PersonLogicalID(email)

    def to_dict(self) -> dict:
        result: dict = {}
        result["email"] = from_union([from_str, from_none], self.email)
        return result


@dataclass
class GroupID:
    group_name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'GroupID':
        assert isinstance(obj, dict)
        group_name = from_union([from_str, from_none], obj.get("groupName"))
        return GroupID(group_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["groupName"] = from_union([from_str, from_none], self.group_name)
        return result


@dataclass
class PersonOrganization:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    person_organization_created_at: Optional[datetime] = None
    department: Optional[str] = None
    division: Optional[str] = None
    employee_number: Optional[str] = None
    entity_id: Optional[str] = None
    groups: Optional[List[GroupID]] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None
    manager: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonOrganization':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        person_organization_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        department = from_union([from_str, from_none], obj.get("department"))
        division = from_union([from_str, from_none], obj.get("division"))
        employee_number = from_union([from_str, from_none], obj.get("employeeNumber"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        groups = from_union([lambda x: from_list(GroupID.from_dict, x), from_none], obj.get("groups"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        manager = from_union([from_str, from_none], obj.get("manager"))
        name = from_union([from_str, from_none], obj.get("name"))
        title = from_union([from_str, from_none], obj.get("title"))
        return PersonOrganization(created_at, aspect_type, created, person_organization_created_at, department, division, employee_number, entity_id, groups, id, last_modified, manager, name, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_organization_created_at)
        result["department"] = from_union([from_str, from_none], self.department)
        result["division"] = from_union([from_str, from_none], self.division)
        result["employeeNumber"] = from_union([from_str, from_none], self.employee_number)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["groups"] = from_union([lambda x: from_list(lambda x: to_class(GroupID, x), x), from_none], self.groups)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["manager"] = from_union([from_str, from_none], self.manager)
        result["name"] = from_union([from_str, from_none], self.name)
        result["title"] = from_union([from_str, from_none], self.title)
        return result


class InAppOnboardingCompletionStep(Enum):
    """Identifier for the current stage(s) a Person has completed in the getting started
    onboarding experience
    """
    INSTALLED_CHAT_CLIENT_APP = "InstalledChatClientApp"
    WATCHED_GET_STARTED_VIDEO = "WatchedGetStartedVideo"


@dataclass
class OnboardingExperience:
    get_started_step_completions: Optional[List[InAppOnboardingCompletionStep]] = None
    has_dismissed_get_started_steps: Optional[bool] = None

    @staticmethod
    def from_dict(obj: Any) -> 'OnboardingExperience':
        assert isinstance(obj, dict)
        get_started_step_completions = from_union([lambda x: from_list(InAppOnboardingCompletionStep, x), from_none], obj.get("getStartedStepCompletions"))
        has_dismissed_get_started_steps = from_union([from_bool, from_none], obj.get("hasDismissedGetStartedSteps"))
        return OnboardingExperience(get_started_step_completions, has_dismissed_get_started_steps)

    def to_dict(self) -> dict:
        result: dict = {}
        result["getStartedStepCompletions"] = from_union([lambda x: from_list(lambda x: to_enum(InAppOnboardingCompletionStep, x), x), from_none], self.get_started_step_completions)
        result["hasDismissedGetStartedSteps"] = from_union([from_bool, from_none], self.has_dismissed_get_started_steps)
        return result


@dataclass
class PersonalizationOptions:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    personalization_options_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None
    onboarding: Optional[OnboardingExperience] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonalizationOptions':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        personalization_options_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        onboarding = from_union([OnboardingExperience.from_dict, from_none], obj.get("onboarding"))
        return PersonalizationOptions(created_at, aspect_type, created, personalization_options_created_at, entity_id, id, last_modified, onboarding)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.personalization_options_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["onboarding"] = from_union([lambda x: to_class(OnboardingExperience, x), from_none], self.onboarding)
        return result


@dataclass
class PersonPins:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """An AuditStamp containing creator and creation time attributes for the Aspect instance"""
    created: Optional[AuditStamp] = None
    person_pins_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    """An AuditStamp containing modification and modifier attributes for the Aspect instance"""
    last_modified: Optional[AuditStamp] = None
    pinned_ids: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonPins':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        person_pins_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        pinned_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("pinnedIds"))
        return PersonPins(created_at, aspect_type, created, person_pins_created_at, entity_id, id, last_modified, pinned_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_pins_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["pinnedIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.pinned_ids)
        return result


class Role(Enum):
    ADMIN = "ADMIN"
    API_KEY = "API_KEY"
    CONTRIBUTOR = "CONTRIBUTOR"
    DATA_ADMIN = "DATA_ADMIN"
    TECH_SUPPORT = "TECH_SUPPORT"


@dataclass
class PersonProperties:
    """Object / output type for PersonProperties aspect contains the full aspect fields
    
    Input type for PersonProperties aspect, contains just the common fields across input and
    output
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    avatar_url: Optional[str] = None
    person_properties_created_at: Optional[datetime] = None
    display_name: Optional[str] = None
    entity_id: Optional[str] = None
    first_name: Optional[str] = None
    full_name: Optional[str] = None
    id: Optional[str] = None
    issuer: Optional[str] = None
    last_login: Optional[str] = None
    last_name: Optional[str] = None
    mobile_phone: Optional[str] = None
    occupation: Optional[str] = None
    primary_phone: Optional[str] = None
    provider_name: Optional[str] = None
    role: Optional[Role] = None
    status: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonProperties':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        avatar_url = from_union([from_str, from_none], obj.get("avatarUrl"))
        person_properties_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        first_name = from_union([from_str, from_none], obj.get("firstName"))
        full_name = from_union([from_str, from_none], obj.get("fullName"))
        id = from_union([from_str, from_none], obj.get("id"))
        issuer = from_union([from_str, from_none], obj.get("issuer"))
        last_login = from_union([from_str, from_none], obj.get("lastLogin"))
        last_name = from_union([from_str, from_none], obj.get("lastName"))
        mobile_phone = from_union([from_str, from_none], obj.get("mobilePhone"))
        occupation = from_union([from_str, from_none], obj.get("occupation"))
        primary_phone = from_union([from_str, from_none], obj.get("primaryPhone"))
        provider_name = from_union([from_str, from_none], obj.get("providerName"))
        role = from_union([Role, from_none], obj.get("role"))
        status = from_union([from_str, from_none], obj.get("status"))
        return PersonProperties(created_at, aspect_type, avatar_url, person_properties_created_at, display_name, entity_id, first_name, full_name, id, issuer, last_login, last_name, mobile_phone, occupation, primary_phone, provider_name, role, status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["avatarUrl"] = from_union([from_str, from_none], self.avatar_url)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_properties_created_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["firstName"] = from_union([from_str, from_none], self.first_name)
        result["fullName"] = from_union([from_str, from_none], self.full_name)
        result["id"] = from_union([from_str, from_none], self.id)
        result["issuer"] = from_union([from_str, from_none], self.issuer)
        result["lastLogin"] = from_union([from_str, from_none], self.last_login)
        result["lastName"] = from_union([from_str, from_none], self.last_name)
        result["mobilePhone"] = from_union([from_str, from_none], self.mobile_phone)
        result["occupation"] = from_union([from_str, from_none], self.occupation)
        result["primaryPhone"] = from_union([from_str, from_none], self.primary_phone)
        result["providerName"] = from_union([from_str, from_none], self.provider_name)
        result["role"] = from_union([lambda x: to_enum(Role, x), from_none], self.role)
        result["status"] = from_union([from_str, from_none], self.status)
        return result


@dataclass
class PersonSlackProfile:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    person_slack_profile_created_at: Optional[datetime] = None
    deleted: Optional[bool] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    real_name: Optional[str] = None
    slack_id: Optional[str] = None
    team_id: Optional[str] = None
    username: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonSlackProfile':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        person_slack_profile_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted = from_union([from_bool, from_none], obj.get("deleted"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        real_name = from_union([from_str, from_none], obj.get("realName"))
        slack_id = from_union([from_str, from_none], obj.get("slackId"))
        team_id = from_union([from_str, from_none], obj.get("teamId"))
        username = from_union([from_str, from_none], obj.get("username"))
        return PersonSlackProfile(created_at, aspect_type, person_slack_profile_created_at, deleted, entity_id, id, real_name, slack_id, team_id, username)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_slack_profile_created_at)
        result["deleted"] = from_union([from_bool, from_none], self.deleted)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["realName"] = from_union([from_str, from_none], self.real_name)
        result["slackId"] = from_union([from_str, from_none], self.slack_id)
        result["teamId"] = from_union([from_str, from_none], self.team_id)
        result["username"] = from_union([from_str, from_none], self.username)
        return result


@dataclass
class TeamsChannelAccount:
    aad_object_id: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TeamsChannelAccount':
        assert isinstance(obj, dict)
        aad_object_id = from_union([from_str, from_none], obj.get("aadObjectId"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        return TeamsChannelAccount(aad_object_id, id, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["aadObjectId"] = from_union([from_str, from_none], self.aad_object_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class TeamsConversationAccount:
    conversation_type: Optional[str] = None
    id: Optional[str] = None
    tenant_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TeamsConversationAccount':
        assert isinstance(obj, dict)
        conversation_type = from_union([from_str, from_none], obj.get("conversationType"))
        id = from_union([from_str, from_none], obj.get("id"))
        tenant_id = from_union([from_str, from_none], obj.get("tenantId"))
        return TeamsConversationAccount(conversation_type, id, tenant_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["conversationType"] = from_union([from_str, from_none], self.conversation_type)
        result["id"] = from_union([from_str, from_none], self.id)
        result["tenantId"] = from_union([from_str, from_none], self.tenant_id)
        return result


@dataclass
class TeamsConversionReference:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    bot: Optional[TeamsChannelAccount] = None
    channel_id: Optional[str] = None
    conversation: Optional[TeamsConversationAccount] = None
    teams_conversion_reference_created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    locale: Optional[str] = None
    service_url: Optional[str] = None
    user: Optional[TeamsChannelAccount] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TeamsConversionReference':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        bot = from_union([TeamsChannelAccount.from_dict, from_none], obj.get("bot"))
        channel_id = from_union([from_str, from_none], obj.get("channelId"))
        conversation = from_union([TeamsConversationAccount.from_dict, from_none], obj.get("conversation"))
        teams_conversion_reference_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        locale = from_union([from_str, from_none], obj.get("locale"))
        service_url = from_union([from_str, from_none], obj.get("serviceUrl"))
        user = from_union([TeamsChannelAccount.from_dict, from_none], obj.get("user"))
        return TeamsConversionReference(created_at, aspect_type, bot, channel_id, conversation, teams_conversion_reference_created_at, entity_id, id, locale, service_url, user)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["bot"] = from_union([lambda x: to_class(TeamsChannelAccount, x), from_none], self.bot)
        result["channelId"] = from_union([from_str, from_none], self.channel_id)
        result["conversation"] = from_union([lambda x: to_class(TeamsConversationAccount, x), from_none], self.conversation)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.teams_conversion_reference_created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["locale"] = from_union([from_str, from_none], self.locale)
        result["serviceUrl"] = from_union([from_str, from_none], self.service_url)
        result["user"] = from_union([lambda x: to_class(TeamsChannelAccount, x), from_none], self.user)
        return result


@dataclass
class Person:
    """A person entity represents any individual who is a member of the organization (or beyond)
    and can
    potentially have some relation to the other entities in our application
    """
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """Native Mongo db BSON id instance"""
    id: Optional[ObjectID] = None
    """Optional protected internal field to store a versionId of the entity, if the instance is
    versioned
    """
    versioned_id: Optional[str] = None
    activity: Optional[PersonActivity] = None
    asset_followers: Optional[AssetFollowers] = None
    person_created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    display_name: Optional[str] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    person_id: Optional[str] = None
    last_ingested_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[PersonLogicalID] = None
    organization: Optional[PersonOrganization] = None
    personalization: Optional[PersonalizationOptions] = None
    pinned_assets: Optional[PersonPins] = None
    properties: Optional[PersonProperties] = None
    slack_profile: Optional[PersonSlackProfile] = None
    teams_conversion_reference: Optional[TeamsConversionReference] = None
    """Write-only api to set a versionId of the entity, if the instance is versioned
    This allows the versionedId to be maintained on the entity e.g. when an instance is
    created by the factory
    """
    person_versioned_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Person':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        versioned_id = from_union([from_str, from_none], obj.get("_versionedId"))
        activity = from_union([PersonActivity.from_dict, from_none], obj.get("activity"))
        asset_followers = from_union([AssetFollowers.from_dict, from_none], obj.get("assetFollowers"))
        person_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        person_id = from_union([from_str, from_none], obj.get("id"))
        last_ingested_at = from_union([from_datetime, from_none], obj.get("lastIngestedAt"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([PersonLogicalID.from_dict, from_none], obj.get("logicalId"))
        organization = from_union([PersonOrganization.from_dict, from_none], obj.get("organization"))
        personalization = from_union([PersonalizationOptions.from_dict, from_none], obj.get("personalization"))
        pinned_assets = from_union([PersonPins.from_dict, from_none], obj.get("pinnedAssets"))
        properties = from_union([PersonProperties.from_dict, from_none], obj.get("properties"))
        slack_profile = from_union([PersonSlackProfile.from_dict, from_none], obj.get("slackProfile"))
        teams_conversion_reference = from_union([TeamsConversionReference.from_dict, from_none], obj.get("teamsConversionReference"))
        person_versioned_id = from_union([from_str, from_none], obj.get("versionedId"))
        return Person(created_at, id, versioned_id, activity, asset_followers, person_created_at, deleted_at, display_name, entity_type, person_id, last_ingested_at, last_modified_at, logical_id, organization, personalization, pinned_assets, properties, slack_profile, teams_conversion_reference, person_versioned_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_versionedId"] = from_union([from_str, from_none], self.versioned_id)
        result["activity"] = from_union([lambda x: to_class(PersonActivity, x), from_none], self.activity)
        result["assetFollowers"] = from_union([lambda x: to_class(AssetFollowers, x), from_none], self.asset_followers)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_created_at)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.person_id)
        result["lastIngestedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_ingested_at)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(PersonLogicalID, x), from_none], self.logical_id)
        result["organization"] = from_union([lambda x: to_class(PersonOrganization, x), from_none], self.organization)
        result["personalization"] = from_union([lambda x: to_class(PersonalizationOptions, x), from_none], self.personalization)
        result["pinnedAssets"] = from_union([lambda x: to_class(PersonPins, x), from_none], self.pinned_assets)
        result["properties"] = from_union([lambda x: to_class(PersonProperties, x), from_none], self.properties)
        result["slackProfile"] = from_union([lambda x: to_class(PersonSlackProfile, x), from_none], self.slack_profile)
        result["teamsConversionReference"] = from_union([lambda x: to_class(TeamsConversionReference, x), from_none], self.teams_conversion_reference)
        result["versionedId"] = from_union([from_str, from_none], self.person_versioned_id)
        return result


@dataclass
class Parsing:
    error_message: Optional[str] = None
    success: Optional[bool] = None
    time: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Parsing':
        assert isinstance(obj, dict)
        error_message = from_union([from_str, from_none], obj.get("errorMessage"))
        success = from_union([from_bool, from_none], obj.get("success"))
        time = from_union([from_datetime, from_none], obj.get("time"))
        return Parsing(error_message, success, time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["errorMessage"] = from_union([from_str, from_none], self.error_message)
        result["success"] = from_union([from_bool, from_none], self.success)
        result["time"] = from_union([lambda x: x.isoformat(), from_none], self.time)
        return result


@dataclass
class QueriedDataset:
    columns: Optional[List[str]] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueriedDataset':
        assert isinstance(obj, dict)
        columns = from_union([lambda x: from_list(from_str, x), from_none], obj.get("columns"))
        database = from_union([from_str, from_none], obj.get("database"))
        schema = from_union([from_str, from_none], obj.get("schema"))
        table = from_union([from_str, from_none], obj.get("table"))
        return QueriedDataset(columns, database, schema, table)

    def to_dict(self) -> dict:
        result: dict = {}
        result["columns"] = from_union([lambda x: from_list(from_str, x), from_none], self.columns)
        result["database"] = from_union([from_str, from_none], self.database)
        result["schema"] = from_union([from_str, from_none], self.schema)
        result["table"] = from_union([from_str, from_none], self.table)
        return result


class TypeEnum(Enum):
    ALTER_TABLE = "ALTER_TABLE"
    ALTER_VIEW = "ALTER_VIEW"
    CREATE_TABLE = "CREATE_TABLE"
    CREATE_VIEW = "CREATE_VIEW"
    DDL = "DDL"
    DELETE = "DELETE"
    DML = "DML"
    DROP_TABLE = "DROP_TABLE"
    DROP_VIEW = "DROP_VIEW"
    EXPORT = "EXPORT"
    INSERT = "INSERT"
    LOAD = "LOAD"
    MERGE = "MERGE"
    OTHER = "OTHER"
    SELECT = "SELECT"
    TRUNCATE = "TRUNCATE"
    UPDATE = "UPDATE"


@dataclass
class QueryLog:
    id: Optional[str] = None
    account: Optional[str] = None
    bytes_read: Optional[float] = None
    bytes_written: Optional[float] = None
    cost: Optional[float] = None
    default_database: Optional[str] = None
    default_schema: Optional[str] = None
    duration: Optional[float] = None
    email: Optional[str] = None
    metadata: Optional[str] = None
    parsing: Optional[Parsing] = None
    platform: Optional[DataPlatform] = None
    query_id: Optional[str] = None
    rows_read: Optional[float] = None
    rows_written: Optional[float] = None
    sources: Optional[List[QueriedDataset]] = None
    sql: Optional[str] = None
    sql_hash: Optional[str] = None
    start_time: Optional[datetime] = None
    targets: Optional[List[QueriedDataset]] = None
    type: Optional[TypeEnum] = None
    user_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryLog':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("_id"))
        account = from_union([from_str, from_none], obj.get("account"))
        bytes_read = from_union([from_float, from_none], obj.get("bytesRead"))
        bytes_written = from_union([from_float, from_none], obj.get("bytesWritten"))
        cost = from_union([from_float, from_none], obj.get("cost"))
        default_database = from_union([from_str, from_none], obj.get("defaultDatabase"))
        default_schema = from_union([from_str, from_none], obj.get("defaultSchema"))
        duration = from_union([from_float, from_none], obj.get("duration"))
        email = from_union([from_str, from_none], obj.get("email"))
        metadata = from_union([from_str, from_none], obj.get("metadata"))
        parsing = from_union([Parsing.from_dict, from_none], obj.get("parsing"))
        platform = from_union([DataPlatform, from_none], obj.get("platform"))
        query_id = from_union([from_str, from_none], obj.get("queryId"))
        rows_read = from_union([from_float, from_none], obj.get("rowsRead"))
        rows_written = from_union([from_float, from_none], obj.get("rowsWritten"))
        sources = from_union([lambda x: from_list(QueriedDataset.from_dict, x), from_none], obj.get("sources"))
        sql = from_union([from_str, from_none], obj.get("sql"))
        sql_hash = from_union([from_str, from_none], obj.get("sqlHash"))
        start_time = from_union([from_datetime, from_none], obj.get("startTime"))
        targets = from_union([lambda x: from_list(QueriedDataset.from_dict, x), from_none], obj.get("targets"))
        type = from_union([TypeEnum, from_none], obj.get("type"))
        user_id = from_union([from_str, from_none], obj.get("userId"))
        return QueryLog(id, account, bytes_read, bytes_written, cost, default_database, default_schema, duration, email, metadata, parsing, platform, query_id, rows_read, rows_written, sources, sql, sql_hash, start_time, targets, type, user_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([from_str, from_none], self.id)
        result["account"] = from_union([from_str, from_none], self.account)
        result["bytesRead"] = from_union([to_float, from_none], self.bytes_read)
        result["bytesWritten"] = from_union([to_float, from_none], self.bytes_written)
        result["cost"] = from_union([to_float, from_none], self.cost)
        result["defaultDatabase"] = from_union([from_str, from_none], self.default_database)
        result["defaultSchema"] = from_union([from_str, from_none], self.default_schema)
        result["duration"] = from_union([to_float, from_none], self.duration)
        result["email"] = from_union([from_str, from_none], self.email)
        result["metadata"] = from_union([from_str, from_none], self.metadata)
        result["parsing"] = from_union([lambda x: to_class(Parsing, x), from_none], self.parsing)
        result["platform"] = from_union([lambda x: to_enum(DataPlatform, x), from_none], self.platform)
        result["queryId"] = from_union([from_str, from_none], self.query_id)
        result["rowsRead"] = from_union([to_float, from_none], self.rows_read)
        result["rowsWritten"] = from_union([to_float, from_none], self.rows_written)
        result["sources"] = from_union([lambda x: from_list(lambda x: to_class(QueriedDataset, x), x), from_none], self.sources)
        result["sql"] = from_union([from_str, from_none], self.sql)
        result["sqlHash"] = from_union([from_str, from_none], self.sql_hash)
        result["startTime"] = from_union([lambda x: x.isoformat(), from_none], self.start_time)
        result["targets"] = from_union([lambda x: from_list(lambda x: to_class(QueriedDataset, x), x), from_none], self.targets)
        result["type"] = from_union([lambda x: to_enum(TypeEnum, x), from_none], self.type)
        result["userId"] = from_union([from_str, from_none], self.user_id)
        return result


@dataclass
class QueryLogs:
    logs: Optional[List[QueryLog]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryLogs':
        assert isinstance(obj, dict)
        logs = from_union([lambda x: from_list(QueryLog.from_dict, x), from_none], obj.get("logs"))
        return QueryLogs(logs)

    def to_dict(self) -> dict:
        result: dict = {}
        result["logs"] = from_union([lambda x: from_list(lambda x: to_class(QueryLog, x), x), from_none], self.logs)
        return result


@dataclass
class DbtMacroArgument:
    description: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DbtMacroArgument':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        name = from_union([from_str, from_none], obj.get("name"))
        type = from_union([from_str, from_none], obj.get("type"))
        return DbtMacroArgument(description, name, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["name"] = from_union([from_str, from_none], self.name)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


@dataclass
class DbtMacro:
    arguments: Optional[List[DbtMacroArgument]] = None
    depends_on_macros: Optional[List[str]] = None
    description: Optional[str] = None
    name: Optional[str] = None
    package_name: Optional[str] = None
    sql: Optional[str] = None
    unique_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DbtMacro':
        assert isinstance(obj, dict)
        arguments = from_union([lambda x: from_list(DbtMacroArgument.from_dict, x), from_none], obj.get("arguments"))
        depends_on_macros = from_union([lambda x: from_list(from_str, x), from_none], obj.get("dependsOnMacros"))
        description = from_union([from_str, from_none], obj.get("description"))
        name = from_union([from_str, from_none], obj.get("name"))
        package_name = from_union([from_str, from_none], obj.get("packageName"))
        sql = from_union([from_str, from_none], obj.get("sql"))
        unique_id = from_union([from_str, from_none], obj.get("uniqueId"))
        return DbtMacro(arguments, depends_on_macros, description, name, package_name, sql, unique_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["arguments"] = from_union([lambda x: from_list(lambda x: to_class(DbtMacroArgument, x), x), from_none], self.arguments)
        result["dependsOnMacros"] = from_union([lambda x: from_list(from_str, x), from_none], self.depends_on_macros)
        result["description"] = from_union([from_str, from_none], self.description)
        result["name"] = from_union([from_str, from_none], self.name)
        result["packageName"] = from_union([from_str, from_none], self.package_name)
        result["sql"] = from_union([from_str, from_none], self.sql)
        result["uniqueId"] = from_union([from_str, from_none], self.unique_id)
        return result


class DbtMaterializationType(Enum):
    EPHEMERAL = "EPHEMERAL"
    INCREMENTAL = "INCREMENTAL"
    OTHER = "OTHER"
    TABLE = "TABLE"
    VIEW = "VIEW"


@dataclass
class DbtMaterialization:
    target_dataset: Optional[str] = None
    type: Optional[DbtMaterializationType] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DbtMaterialization':
        assert isinstance(obj, dict)
        target_dataset = from_union([from_str, from_none], obj.get("targetDataset"))
        type = from_union([DbtMaterializationType, from_none], obj.get("type"))
        return DbtMaterialization(target_dataset, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["targetDataset"] = from_union([from_str, from_none], self.target_dataset)
        result["type"] = from_union([lambda x: to_enum(DbtMaterializationType, x), from_none], self.type)
        return result


@dataclass
class DbtTest:
    columns: Optional[List[str]] = None
    depends_on_macros: Optional[List[str]] = None
    name: Optional[str] = None
    sql: Optional[str] = None
    unique_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DbtTest':
        assert isinstance(obj, dict)
        columns = from_union([lambda x: from_list(from_str, x), from_none], obj.get("columns"))
        depends_on_macros = from_union([lambda x: from_list(from_str, x), from_none], obj.get("dependsOnMacros"))
        name = from_union([from_str, from_none], obj.get("name"))
        sql = from_union([from_str, from_none], obj.get("sql"))
        unique_id = from_union([from_str, from_none], obj.get("uniqueId"))
        return DbtTest(columns, depends_on_macros, name, sql, unique_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["columns"] = from_union([lambda x: from_list(from_str, x), from_none], self.columns)
        result["dependsOnMacros"] = from_union([lambda x: from_list(from_str, x), from_none], self.depends_on_macros)
        result["name"] = from_union([from_str, from_none], self.name)
        result["sql"] = from_union([from_str, from_none], self.sql)
        result["uniqueId"] = from_union([from_str, from_none], self.unique_id)
        return result


@dataclass
class DbtModel:
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    compiled_sql: Optional[str] = None
    dbt_model_created_at: Optional[datetime] = None
    description: Optional[str] = None
    docs_url: Optional[str] = None
    entity_id: Optional[str] = None
    fields: Optional[List[SchemaField]] = None
    id: Optional[str] = None
    macros: Optional[List[DbtMacro]] = None
    materialization: Optional[DbtMaterialization] = None
    owners: Optional[List[str]] = None
    package_name: Optional[str] = None
    raw_sql: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    source_models: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    tests: Optional[List[DbtTest]] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DbtModel':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        compiled_sql = from_union([from_str, from_none], obj.get("compiledSql"))
        dbt_model_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        docs_url = from_union([from_str, from_none], obj.get("docsUrl"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        fields = from_union([lambda x: from_list(SchemaField.from_dict, x), from_none], obj.get("fields"))
        id = from_union([from_str, from_none], obj.get("id"))
        macros = from_union([lambda x: from_list(DbtMacro.from_dict, x), from_none], obj.get("macros"))
        materialization = from_union([DbtMaterialization.from_dict, from_none], obj.get("materialization"))
        owners = from_union([lambda x: from_list(from_str, x), from_none], obj.get("owners"))
        package_name = from_union([from_str, from_none], obj.get("packageName"))
        raw_sql = from_union([from_str, from_none], obj.get("rawSql"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        source_models = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceModels"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        tests = from_union([lambda x: from_list(DbtTest.from_dict, x), from_none], obj.get("tests"))
        url = from_union([from_str, from_none], obj.get("url"))
        return DbtModel(created_at, aspect_type, compiled_sql, dbt_model_created_at, description, docs_url, entity_id, fields, id, macros, materialization, owners, package_name, raw_sql, source_datasets, source_models, tags, tests, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["compiledSql"] = from_union([from_str, from_none], self.compiled_sql)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dbt_model_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["docsUrl"] = from_union([from_str, from_none], self.docs_url)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fields"] = from_union([lambda x: from_list(lambda x: to_class(SchemaField, x), x), from_none], self.fields)
        result["id"] = from_union([from_str, from_none], self.id)
        result["macros"] = from_union([lambda x: from_list(lambda x: to_class(DbtMacro, x), x), from_none], self.macros)
        result["materialization"] = from_union([lambda x: to_class(DbtMaterialization, x), from_none], self.materialization)
        result["owners"] = from_union([lambda x: from_list(from_str, x), from_none], self.owners)
        result["packageName"] = from_union([from_str, from_none], self.package_name)
        result["rawSql"] = from_union([from_str, from_none], self.raw_sql)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["sourceModels"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_models)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        result["tests"] = from_union([lambda x: from_list(lambda x: to_class(DbtTest, x), x), from_none], self.tests)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


class VirtualViewType(Enum):
    DBT_MODEL = "DBT_MODEL"
    LOOKER_EXPLORE = "LOOKER_EXPLORE"
    LOOKER_VIEW = "LOOKER_VIEW"
    POWER_BI_DATASET = "POWER_BI_DATASET"
    TABLEAU_DATASOURCE = "TABLEAU_DATASOURCE"
    THOUGHT_SPOT_DATA_OBJECT = "THOUGHT_SPOT_DATA_OBJECT"
    UNKNOWN = "UNKNOWN"


@dataclass
class VirtualViewLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    name: Optional[str] = None
    type: Optional[VirtualViewType] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VirtualViewLogicalID':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        type = from_union([VirtualViewType, from_none], obj.get("type"))
        return VirtualViewLogicalID(name, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_union([from_str, from_none], self.name)
        result["type"] = from_union([lambda x: to_enum(VirtualViewType, x), from_none], self.type)
        return result


@dataclass
class LookerExploreFilter:
    allowed_values: Optional[str] = None
    field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerExploreFilter':
        assert isinstance(obj, dict)
        allowed_values = from_union([from_str, from_none], obj.get("allowedValues"))
        field = from_union([from_str, from_none], obj.get("field"))
        return LookerExploreFilter(allowed_values, field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["allowedValues"] = from_union([from_str, from_none], self.allowed_values)
        result["field"] = from_union([from_str, from_none], self.field)
        return result


@dataclass
class LookerExploreJoin:
    fields: Optional[List[str]] = None
    on_clause: Optional[str] = None
    relationship: Optional[str] = None
    type: Optional[str] = None
    """The Looker View that is joined in the Explore"""
    view: Optional[str] = None
    where_clause: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerExploreJoin':
        assert isinstance(obj, dict)
        fields = from_union([lambda x: from_list(from_str, x), from_none], obj.get("fields"))
        on_clause = from_union([from_str, from_none], obj.get("onClause"))
        relationship = from_union([from_str, from_none], obj.get("relationship"))
        type = from_union([from_str, from_none], obj.get("type"))
        view = from_union([from_str, from_none], obj.get("view"))
        where_clause = from_union([from_str, from_none], obj.get("whereClause"))
        return LookerExploreJoin(fields, on_clause, relationship, type, view, where_clause)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fields"] = from_union([lambda x: from_list(from_str, x), from_none], self.fields)
        result["onClause"] = from_union([from_str, from_none], self.on_clause)
        result["relationship"] = from_union([from_str, from_none], self.relationship)
        result["type"] = from_union([from_str, from_none], self.type)
        result["view"] = from_union([from_str, from_none], self.view)
        result["whereClause"] = from_union([from_str, from_none], self.where_clause)
        return result


@dataclass
class LookerExplore:
    """Captures information of a Looker Explore,
    https://docs.looker.com/reference/explore-reference
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    """The Looker View which the Explore is based on"""
    base_view: Optional[str] = None
    looker_explore_created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    extends: Optional[List[str]] = None
    fields: Optional[List[str]] = None
    filters: Optional[List[LookerExploreFilter]] = None
    id: Optional[str] = None
    joins: Optional[List[LookerExploreJoin]] = None
    label: Optional[str] = None
    model_name: Optional[str] = None
    tags: Optional[List[str]] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerExplore':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        base_view = from_union([from_str, from_none], obj.get("baseView"))
        looker_explore_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        extends = from_union([lambda x: from_list(from_str, x), from_none], obj.get("extends"))
        fields = from_union([lambda x: from_list(from_str, x), from_none], obj.get("fields"))
        filters = from_union([lambda x: from_list(LookerExploreFilter.from_dict, x), from_none], obj.get("filters"))
        id = from_union([from_str, from_none], obj.get("id"))
        joins = from_union([lambda x: from_list(LookerExploreJoin.from_dict, x), from_none], obj.get("joins"))
        label = from_union([from_str, from_none], obj.get("label"))
        model_name = from_union([from_str, from_none], obj.get("modelName"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        url = from_union([from_str, from_none], obj.get("url"))
        return LookerExplore(created_at, aspect_type, base_view, looker_explore_created_at, description, entity_id, extends, fields, filters, id, joins, label, model_name, tags, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["baseView"] = from_union([from_str, from_none], self.base_view)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.looker_explore_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["extends"] = from_union([lambda x: from_list(from_str, x), from_none], self.extends)
        result["fields"] = from_union([lambda x: from_list(from_str, x), from_none], self.fields)
        result["filters"] = from_union([lambda x: from_list(lambda x: to_class(LookerExploreFilter, x), x), from_none], self.filters)
        result["id"] = from_union([from_str, from_none], self.id)
        result["joins"] = from_union([lambda x: from_list(lambda x: to_class(LookerExploreJoin, x), x), from_none], self.joins)
        result["label"] = from_union([from_str, from_none], self.label)
        result["modelName"] = from_union([from_str, from_none], self.model_name)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class LookerViewDimension:
    data_type: Optional[str] = None
    field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerViewDimension':
        assert isinstance(obj, dict)
        data_type = from_union([from_str, from_none], obj.get("dataType"))
        field = from_union([from_str, from_none], obj.get("field"))
        return LookerViewDimension(data_type, field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dataType"] = from_union([from_str, from_none], self.data_type)
        result["field"] = from_union([from_str, from_none], self.field)
        return result


@dataclass
class LookerViewFilter:
    field: Optional[str] = None
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerViewFilter':
        assert isinstance(obj, dict)
        field = from_union([from_str, from_none], obj.get("field"))
        type = from_union([from_str, from_none], obj.get("type"))
        return LookerViewFilter(field, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["field"] = from_union([from_str, from_none], self.field)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


@dataclass
class LookerViewMeasure:
    field: Optional[str] = None
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerViewMeasure':
        assert isinstance(obj, dict)
        field = from_union([from_str, from_none], obj.get("field"))
        type = from_union([from_str, from_none], obj.get("type"))
        return LookerViewMeasure(field, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["field"] = from_union([from_str, from_none], self.field)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


@dataclass
class LookerView:
    """Captures information of a Looker View, https://docs.looker.com/reference/view-reference"""
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    looker_view_created_at: Optional[datetime] = None
    dimensions: Optional[List[LookerViewDimension]] = None
    entity_id: Optional[str] = None
    extends: Optional[List[str]] = None
    filters: Optional[List[LookerViewFilter]] = None
    id: Optional[str] = None
    label: Optional[str] = None
    measures: Optional[List[LookerViewMeasure]] = None
    source_datasets: Optional[List[str]] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LookerView':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        looker_view_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dimensions = from_union([lambda x: from_list(LookerViewDimension.from_dict, x), from_none], obj.get("dimensions"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        extends = from_union([lambda x: from_list(from_str, x), from_none], obj.get("extends"))
        filters = from_union([lambda x: from_list(LookerViewFilter.from_dict, x), from_none], obj.get("filters"))
        id = from_union([from_str, from_none], obj.get("id"))
        label = from_union([from_str, from_none], obj.get("label"))
        measures = from_union([lambda x: from_list(LookerViewMeasure.from_dict, x), from_none], obj.get("measures"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        url = from_union([from_str, from_none], obj.get("url"))
        return LookerView(created_at, aspect_type, looker_view_created_at, dimensions, entity_id, extends, filters, id, label, measures, source_datasets, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.looker_view_created_at)
        result["dimensions"] = from_union([lambda x: from_list(lambda x: to_class(LookerViewDimension, x), x), from_none], self.dimensions)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["extends"] = from_union([lambda x: from_list(from_str, x), from_none], self.extends)
        result["filters"] = from_union([lambda x: from_list(lambda x: to_class(LookerViewFilter, x), x), from_none], self.filters)
        result["id"] = from_union([from_str, from_none], self.id)
        result["label"] = from_union([from_str, from_none], self.label)
        result["measures"] = from_union([lambda x: from_list(lambda x: to_class(LookerViewMeasure, x), x), from_none], self.measures)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class PowerBIColumn:
    """Captures column name of a dataset table,
    https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-result#column
    """
    field: Optional[str] = None
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIColumn':
        assert isinstance(obj, dict)
        field = from_union([from_str, from_none], obj.get("field"))
        type = from_union([from_str, from_none], obj.get("type"))
        return PowerBIColumn(field, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["field"] = from_union([from_str, from_none], self.field)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


@dataclass
class PowerBIMeasure:
    """Captures Power BI measure of a dataset table,
    https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-result#measure
    """
    description: Optional[str] = None
    expression: Optional[str] = None
    field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIMeasure':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        expression = from_union([from_str, from_none], obj.get("expression"))
        field = from_union([from_str, from_none], obj.get("field"))
        return PowerBIMeasure(description, expression, field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["expression"] = from_union([from_str, from_none], self.expression)
        result["field"] = from_union([from_str, from_none], self.field)
        return result


@dataclass
class PowerBIDatasetTable:
    """Captures dataset table information of a Power BI Dataset,
    https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-result#table
    """
    columns: Optional[List[PowerBIColumn]] = None
    measures: Optional[List[PowerBIMeasure]] = None
    name: Optional[str] = None
    sources: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIDatasetTable':
        assert isinstance(obj, dict)
        columns = from_union([lambda x: from_list(PowerBIColumn.from_dict, x), from_none], obj.get("columns"))
        measures = from_union([lambda x: from_list(PowerBIMeasure.from_dict, x), from_none], obj.get("measures"))
        name = from_union([from_str, from_none], obj.get("name"))
        sources = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sources"))
        return PowerBIDatasetTable(columns, measures, name, sources)

    def to_dict(self) -> dict:
        result: dict = {}
        result["columns"] = from_union([lambda x: from_list(lambda x: to_class(PowerBIColumn, x), x), from_none], self.columns)
        result["measures"] = from_union([lambda x: from_list(lambda x: to_class(PowerBIMeasure, x), x), from_none], self.measures)
        result["name"] = from_union([from_str, from_none], self.name)
        result["sources"] = from_union([lambda x: from_list(from_str, x), from_none], self.sources)
        return result


@dataclass
class PowerBIDataset:
    """Captures information of a Power BI Dataset using admin API,
    https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-result#workspaceinfodataset
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    power_bi_dataset_created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    last_refreshed: Optional[datetime] = None
    name: Optional[str] = None
    sensitivity_label: Optional[PowerBISensitivityLabel] = None
    source_datasets: Optional[List[str]] = None
    tables: Optional[List[PowerBIDatasetTable]] = None
    url: Optional[str] = None
    workspace: Optional[PowerBIWorkspace] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PowerBIDataset':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        power_bi_dataset_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        last_refreshed = from_union([from_datetime, from_none], obj.get("lastRefreshed"))
        name = from_union([from_str, from_none], obj.get("name"))
        sensitivity_label = from_union([PowerBISensitivityLabel.from_dict, from_none], obj.get("sensitivityLabel"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        tables = from_union([lambda x: from_list(PowerBIDatasetTable.from_dict, x), from_none], obj.get("tables"))
        url = from_union([from_str, from_none], obj.get("url"))
        workspace = from_union([PowerBIWorkspace.from_dict, from_none], obj.get("workspace"))
        return PowerBIDataset(created_at, aspect_type, power_bi_dataset_created_at, description, entity_id, id, last_refreshed, name, sensitivity_label, source_datasets, tables, url, workspace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.power_bi_dataset_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["lastRefreshed"] = from_union([lambda x: x.isoformat(), from_none], self.last_refreshed)
        result["name"] = from_union([from_str, from_none], self.name)
        result["sensitivityLabel"] = from_union([lambda x: to_class(PowerBISensitivityLabel, x), from_none], self.sensitivity_label)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["tables"] = from_union([lambda x: from_list(lambda x: to_class(PowerBIDatasetTable, x), x), from_none], self.tables)
        result["url"] = from_union([from_str, from_none], self.url)
        result["workspace"] = from_union([lambda x: to_class(PowerBIWorkspace, x), from_none], self.workspace)
        return result


@dataclass
class TableauField:
    description: Optional[str] = None
    field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TableauField':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        field = from_union([from_str, from_none], obj.get("field"))
        return TableauField(description, field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["field"] = from_union([from_str, from_none], self.field)
        return result


@dataclass
class TableauDatasource:
    """Modeling Tableau Datasource as a virtual view.
    https://help.tableau.com/current/server/en-us/datasource.htm
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    tableau_datasource_created_at: Optional[datetime] = None
    description: Optional[str] = None
    embedded: Optional[bool] = None
    entity_id: Optional[str] = None
    fields: Optional[List[TableauField]] = None
    id: Optional[str] = None
    name: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    source_virtual_views: Optional[List[str]] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'TableauDatasource':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        tableau_datasource_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        embedded = from_union([from_bool, from_none], obj.get("embedded"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        fields = from_union([lambda x: from_list(TableauField.from_dict, x), from_none], obj.get("fields"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        source_virtual_views = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceVirtualViews"))
        url = from_union([from_str, from_none], obj.get("url"))
        return TableauDatasource(created_at, aspect_type, tableau_datasource_created_at, description, embedded, entity_id, fields, id, name, source_datasets, source_virtual_views, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.tableau_datasource_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["embedded"] = from_union([from_bool, from_none], self.embedded)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fields"] = from_union([lambda x: from_list(lambda x: to_class(TableauField, x), x), from_none], self.fields)
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["sourceVirtualViews"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_virtual_views)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class ThoughtSpotColumn:
    description: Optional[str] = None
    field: Optional[str] = None
    formula: Optional[str] = None
    name: Optional[str] = None
    optional_type: Optional[str] = None
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ThoughtSpotColumn':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        field = from_union([from_str, from_none], obj.get("field"))
        formula = from_union([from_str, from_none], obj.get("formula"))
        name = from_union([from_str, from_none], obj.get("name"))
        optional_type = from_union([from_str, from_none], obj.get("optionalType"))
        type = from_union([from_str, from_none], obj.get("type"))
        return ThoughtSpotColumn(description, field, formula, name, optional_type, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["field"] = from_union([from_str, from_none], self.field)
        result["formula"] = from_union([from_str, from_none], self.formula)
        result["name"] = from_union([from_str, from_none], self.name)
        result["optionalType"] = from_union([from_str, from_none], self.optional_type)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


class ThoughtSpotDataObjectType(Enum):
    TABLE = "TABLE"
    UNKNOWN = "UNKNOWN"
    VIEW = "VIEW"
    WORKSHEET = "WORKSHEET"


@dataclass
class ThoughtSpotDataObject:
    """Modeling ThoughtSpot DataSource or DataObject in the API into a virtual view.
    DataSource: https://docs.thoughtspot.com/software/latest/data-sources
    """
    """Backing store for the aspect creation date"""
    created_at: Optional[datetime] = None
    aspect_type: Optional[AspectType] = None
    columns: Optional[List[ThoughtSpotColumn]] = None
    thought_spot_data_object_created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    source_virtual_views: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    type: Optional[ThoughtSpotDataObjectType] = None
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ThoughtSpotDataObject':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        columns = from_union([lambda x: from_list(ThoughtSpotColumn.from_dict, x), from_none], obj.get("columns"))
        thought_spot_data_object_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        source_virtual_views = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceVirtualViews"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        type = from_union([ThoughtSpotDataObjectType, from_none], obj.get("type"))
        url = from_union([from_str, from_none], obj.get("url"))
        return ThoughtSpotDataObject(created_at, aspect_type, columns, thought_spot_data_object_created_at, description, entity_id, id, name, source_datasets, source_virtual_views, tags, type, url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["columns"] = from_union([lambda x: from_list(lambda x: to_class(ThoughtSpotColumn, x), x), from_none], self.columns)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.thought_spot_data_object_created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["sourceVirtualViews"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_virtual_views)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        result["type"] = from_union([lambda x: to_enum(ThoughtSpotDataObjectType, x), from_none], self.type)
        result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class VirtualView:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """Native Mongo db BSON id instance"""
    id: Optional[ObjectID] = None
    """Optional protected internal field to store a versionId of the entity, if the instance is
    versioned
    """
    versioned_id: Optional[str] = None
    asset_contacts: Optional[AssetContacts] = None
    asset_followers: Optional[AssetFollowers] = None
    asset_governed_tags: Optional[AssetGovernedTags] = None
    virtual_view_created_at: Optional[datetime] = None
    dbt_model: Optional[DbtModel] = None
    deleted_at: Optional[datetime] = None
    display_name: Optional[str] = None
    entity_type: Optional[EntityType] = None
    """EntityUpstream captures upstream lineages from data sources to this entity"""
    entity_upstream: Optional[EntityUpstream] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    virtual_view_id: Optional[str] = None
    last_ingested_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[VirtualViewLogicalID] = None
    """Captures information of a Looker Explore,
    https://docs.looker.com/reference/explore-reference
    """
    looker_explore: Optional[LookerExplore] = None
    """Captures information of a Looker View, https://docs.looker.com/reference/view-reference"""
    looker_view: Optional[LookerView] = None
    ownership_assignment: Optional[OwnershipAssignment] = None
    """Captures information of a Power BI Dataset using admin API,
    https://docs.microsoft.com/en-us/rest/api/power-bi/admin/workspace-info-get-scan-result#workspaceinfodataset
    """
    power_bi_dataset: Optional[PowerBIDataset] = None
    """Modeling Tableau Datasource as a virtual view.
    https://help.tableau.com/current/server/en-us/datasource.htm
    """
    tableau_datasource: Optional[TableauDatasource] = None
    tag_assignment: Optional[TagAssignment] = None
    """Modeling ThoughtSpot DataSource or DataObject in the API into a virtual view.
    DataSource: https://docs.thoughtspot.com/software/latest/data-sources
    """
    thought_spot: Optional[ThoughtSpotDataObject] = None
    """Write-only api to set a versionId of the entity, if the instance is versioned
    This allows the versionedId to be maintained on the entity e.g. when an instance is
    created by the factory
    """
    virtual_view_versioned_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VirtualView':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        versioned_id = from_union([from_str, from_none], obj.get("_versionedId"))
        asset_contacts = from_union([AssetContacts.from_dict, from_none], obj.get("assetContacts"))
        asset_followers = from_union([AssetFollowers.from_dict, from_none], obj.get("assetFollowers"))
        asset_governed_tags = from_union([AssetGovernedTags.from_dict, from_none], obj.get("assetGovernedTags"))
        virtual_view_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dbt_model = from_union([DbtModel.from_dict, from_none], obj.get("dbtModel"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        entity_upstream = from_union([EntityUpstream.from_dict, from_none], obj.get("entityUpstream"))
        virtual_view_id = from_union([from_str, from_none], obj.get("id"))
        last_ingested_at = from_union([from_datetime, from_none], obj.get("lastIngestedAt"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([VirtualViewLogicalID.from_dict, from_none], obj.get("logicalId"))
        looker_explore = from_union([LookerExplore.from_dict, from_none], obj.get("lookerExplore"))
        looker_view = from_union([LookerView.from_dict, from_none], obj.get("lookerView"))
        ownership_assignment = from_union([OwnershipAssignment.from_dict, from_none], obj.get("ownershipAssignment"))
        power_bi_dataset = from_union([PowerBIDataset.from_dict, from_none], obj.get("powerBIDataset"))
        tableau_datasource = from_union([TableauDatasource.from_dict, from_none], obj.get("tableauDatasource"))
        tag_assignment = from_union([TagAssignment.from_dict, from_none], obj.get("tagAssignment"))
        thought_spot = from_union([ThoughtSpotDataObject.from_dict, from_none], obj.get("thoughtSpot"))
        virtual_view_versioned_id = from_union([from_str, from_none], obj.get("versionedId"))
        return VirtualView(created_at, id, versioned_id, asset_contacts, asset_followers, asset_governed_tags, virtual_view_created_at, dbt_model, deleted_at, display_name, entity_type, entity_upstream, virtual_view_id, last_ingested_at, last_modified_at, logical_id, looker_explore, looker_view, ownership_assignment, power_bi_dataset, tableau_datasource, tag_assignment, thought_spot, virtual_view_versioned_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_versionedId"] = from_union([from_str, from_none], self.versioned_id)
        result["assetContacts"] = from_union([lambda x: to_class(AssetContacts, x), from_none], self.asset_contacts)
        result["assetFollowers"] = from_union([lambda x: to_class(AssetFollowers, x), from_none], self.asset_followers)
        result["assetGovernedTags"] = from_union([lambda x: to_class(AssetGovernedTags, x), from_none], self.asset_governed_tags)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.virtual_view_created_at)
        result["dbtModel"] = from_union([lambda x: to_class(DbtModel, x), from_none], self.dbt_model)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["entityUpstream"] = from_union([lambda x: to_class(EntityUpstream, x), from_none], self.entity_upstream)
        result["id"] = from_union([from_str, from_none], self.virtual_view_id)
        result["lastIngestedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_ingested_at)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(VirtualViewLogicalID, x), from_none], self.logical_id)
        result["lookerExplore"] = from_union([lambda x: to_class(LookerExplore, x), from_none], self.looker_explore)
        result["lookerView"] = from_union([lambda x: to_class(LookerView, x), from_none], self.looker_view)
        result["ownershipAssignment"] = from_union([lambda x: to_class(OwnershipAssignment, x), from_none], self.ownership_assignment)
        result["powerBIDataset"] = from_union([lambda x: to_class(PowerBIDataset, x), from_none], self.power_bi_dataset)
        result["tableauDatasource"] = from_union([lambda x: to_class(TableauDatasource, x), from_none], self.tableau_datasource)
        result["tagAssignment"] = from_union([lambda x: to_class(TagAssignment, x), from_none], self.tag_assignment)
        result["thoughtSpot"] = from_union([lambda x: to_class(ThoughtSpotDataObject, x), from_none], self.thought_spot)
        result["versionedId"] = from_union([from_str, from_none], self.virtual_view_versioned_id)
        return result


@dataclass
class MetadataChangeEvent:
    dashboard: Optional[Dashboard] = None
    dataset: Optional[Dataset] = None
    event_header: Optional[EventHeader] = None
    knowledge_card: Optional[KnowledgeCard] = None
    metric: Optional[Metric] = None
    """A person entity represents any individual who is a member of the organization (or beyond)
    and can
    potentially have some relation to the other entities in our application
    """
    person: Optional[Person] = None
    query_logs: Optional[QueryLogs] = None
    virtual_view: Optional[VirtualView] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MetadataChangeEvent':
        assert isinstance(obj, dict)
        dashboard = from_union([Dashboard.from_dict, from_none], obj.get("dashboard"))
        dataset = from_union([Dataset.from_dict, from_none], obj.get("dataset"))
        event_header = from_union([EventHeader.from_dict, from_none], obj.get("eventHeader"))
        knowledge_card = from_union([KnowledgeCard.from_dict, from_none], obj.get("knowledgeCard"))
        metric = from_union([Metric.from_dict, from_none], obj.get("metric"))
        person = from_union([Person.from_dict, from_none], obj.get("person"))
        query_logs = from_union([QueryLogs.from_dict, from_none], obj.get("queryLogs"))
        virtual_view = from_union([VirtualView.from_dict, from_none], obj.get("virtualView"))
        return MetadataChangeEvent(dashboard, dataset, event_header, knowledge_card, metric, person, query_logs, virtual_view)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dashboard"] = from_union([lambda x: to_class(Dashboard, x), from_none], self.dashboard)
        result["dataset"] = from_union([lambda x: to_class(Dataset, x), from_none], self.dataset)
        result["eventHeader"] = from_union([lambda x: to_class(EventHeader, x), from_none], self.event_header)
        result["knowledgeCard"] = from_union([lambda x: to_class(KnowledgeCard, x), from_none], self.knowledge_card)
        result["metric"] = from_union([lambda x: to_class(Metric, x), from_none], self.metric)
        result["person"] = from_union([lambda x: to_class(Person, x), from_none], self.person)
        result["queryLogs"] = from_union([lambda x: to_class(QueryLogs, x), from_none], self.query_logs)
        result["virtualView"] = from_union([lambda x: to_class(VirtualView, x), from_none], self.virtual_view)
        return result


def metadata_change_event_from_dict(s: Any) -> MetadataChangeEvent:
    return MetadataChangeEvent.from_dict(s)


def metadata_change_event_to_dict(x: MetadataChangeEvent) -> Any:
    return to_class(MetadataChangeEvent, x)
