from dataclasses import dataclass
from typing import Callable, Collection, List, Type
from uuid import UUID

from django.db.models import Model, QuerySet

from dhis2_etl.adx_transform.adx_models.adx_data import Period
from dhis2_etl.adx_transform.adx_models.adx_time_period import PeriodType


@dataclass
class ADXCategoryOptionDefinition:
    code: str
    filter: Callable[[QuerySet], QuerySet]  # Filtering function takes queryset instance as argument and returns another queryset


@dataclass
class ADXMappingCategoryDefinition:
    category_name: str
    category_options: List[ADXCategoryOptionDefinition]


@dataclass
class ADXMappingDataValueDefinition:
    data_element: str
    aggregation_func: Callable[[QuerySet], str]
    dataset_from_orgunit_func: Callable[[Model], QuerySet]
    period_filter_func: Callable[[QuerySet, Period], QuerySet]
    categories: List[ADXMappingCategoryDefinition]



@dataclass
class ADXMappingGroupDefinition:
    comment: str
    dataset: Type[Model]  # HF Etc.
    data_values: List[ADXMappingDataValueDefinition]
    to_org_unit_code_func: Callable[[Model], str]

    @property
    def dataset_repr(self) -> str:
        return str(self.dataset.__name__).upper()


@dataclass
class ADXMappingCubeDefinition:
    name: str
    period_type: PeriodType  # Currently handled in ISO Format
    groups: List[ADXMappingGroupDefinition]
    org_units: Collection[UUID] = None  # UUIDs of objects stored in Model, can be queryset result or list
