"""
기준정보 Services 패키지
- 모든 화면별 서비스 인스턴스를 re-export
- 사용법: from services.master import plant_service, factory_service, ...
"""
from services.master.plant import plant_service
from services.master.factory import factory_service
from services.master.dept import dept_service
from services.master.company import company_service
from services.master.warehouse import warehouse_service
from services.master.location import location_service
from services.master.line import line_service
from services.master.process import process_service
from services.master.goods import goods_service
from services.master.bom import bom_service
from services.master.process_user import process_user_service
from services.master.code import code_service
from services.master.failcode import failcode_service

__all__ = [
    "plant_service", "factory_service", "dept_service", "company_service",
    "warehouse_service", "location_service", "line_service", "process_service",
    "goods_service", "bom_service", "process_user_service", "code_service",
    "failcode_service",
]
