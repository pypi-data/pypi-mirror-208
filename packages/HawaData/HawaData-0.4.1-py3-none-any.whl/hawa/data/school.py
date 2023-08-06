from dataclasses import dataclass

from hawa.paper.health import HealthReportData
from hawa.paper.mht import MhtWebData


@dataclass
class SchoolMixin:
    """为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前"""
    meta_unit_type: str = 'school'


@dataclass
class SchoolHealthReportData(SchoolMixin, HealthReportData):
    pass


@dataclass
class SchoolMhtWebData(SchoolMixin, MhtWebData):
    meta_unit_type: str = 'school'
    pass
